from pathlib import Path
from typing import Union, List, Dict, Optional
import hashlib
import json
import time 
from datetime import datetime
from app.data.db import get_connection


def calculate_dynamic_threshold(
    file_count: int,
    base_threshold: float = 65.0,
    min_threshold: float = 50.0,
    max_threshold: float = 75.0
) -> float:
    """
    Calculate a dynamic similarity threshold based on project size (file count).
    
    Small projects need higher similarity to match (prevents false positives).
    Large projects use lower thresholds (allows flexibility for incremental changes).
    
    The thresholds are relaxed for very small projects to prevent common growth 
    cases like 3→4 or 4→5 files from being incorrectly blocked.
    
    Args:
        file_count: Number of files in the project
        base_threshold: The base threshold to adjust from (default 65.0)
        min_threshold: Minimum threshold floor (default 50.0)
        max_threshold: Maximum threshold ceiling (default 75.0, relaxed from 85.0)
    
    Returns:
        Adjusted threshold as a percentage (clamped to min/max bounds)
    
    Thresholds:
        < 10 files   → base (65%, relaxed from base+15 to allow incremental growth)
        10-29 files  → base + 5  (slightly strict, e.g., 70%)
        30-99 files  → base      (normal, e.g., 65%)
        100-299 files → base - 8 (lenient, e.g., 57%)
        300+ files   → base - 12 (very lenient, e.g., 53%)
    """
    if file_count < 10:
        # Very small projects: use base threshold (relaxed to allow incremental growth)
        # Previously was +15 which blocked common cases like 3→4 or 4→5 files
        adjustment = 0.0
    elif file_count < 30:
        # Small projects: slightly stricter (reduced from +8)
        adjustment = 5.0
    elif file_count < 100:
        # Medium projects: use base threshold
        adjustment = 0.0
    elif file_count < 300:
        # Large projects: slightly more lenient
        adjustment = -8.0
    else:
        # Very large projects: more lenient to handle natural growth
        adjustment = -12.0
    
    threshold = base_threshold + adjustment
    
    # Clamp to min/max bounds for safety (max capped at 75% to allow flexibility)
    return max(min_threshold, min(max_threshold, threshold))


EXCLUDE_PATTERNS = [
    # Python/system/dependency folders (not user content)
    "__pycache__",
    ".git",
    ".env",
    ".venv",
    "node_modules",
    "env",
    "venv",
    "build",
    "lib",
    "dist",
    ".pytest_cache",
    # Compiled/binary files (not analyzable)
    "*.pyc", "*.pyo", "*.pyd",
    "*.db", "*.sqlite3",
    # Video files (not analyzable for now)
    "*.mp4", "*.mov", "*.avi", "*.mkv", "*.flv", "*.wmv",
    # Audio files (not analyzable for now)
    "*.mp3", "*.wav", "*.aac", "*.ogg", "*.flac",
    # Image files (not analyzable for now)
    "*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp", "*.tiff", "*.svg", "*.webp",
    # Archives (optional: only if you don't want to process them yet)
    "*.zip", "*.tar", "*.gz", "*.rar",
]

def should_exclude(path: Path, patterns: List[str] = EXCLUDE_PATTERNS) -> bool:
    """Return True if path matches any exclusion pattern."""
    for pattern in patterns:
        if path.match(pattern) or pattern in path.parts:
            return True
    return False

def scan_project_files(root: Union[str, Path], exclude_patterns: List[str] = EXCLUDE_PATTERNS) -> List[Path]:
    """
    Recursively scan files under root, excluding files/folders matching exclude_patterns.
    Returns a list of file Paths.
    """
    root_path = Path(root)
    files = []
    try:
        for p in root_path.rglob("*"):
            if p.is_file() and not should_exclude(p, exclude_patterns):
                files.append(p)
    except Exception as e:
        print(f"Error scanning files in {root}: {e}")
    return files

def extract_file_metadata(file_path: Union[str, Path]) -> Dict:
    """Extract basic metadata from a file."""
    p = Path(file_path)
    stat = p.stat()
    return {
        "file_name": p.name,
        "file_path": str(p.resolve()),
        "size_bytes": stat.st_size,
        "created_at": stat.st_ctime,
        "last_modified": stat.st_mtime,
    }

def extract_project_timestamps(project_root: Union[str, Path], filtered_files: List[Path] = None) -> Dict[str, datetime]:
    """
    Compute project timestamps based on actual file modification times.
    Uses the already-filtered files to respect exclusions.
    """
    try:
        root_path = Path(project_root)
        
        # If filtered_files provided, use them; otherwise scan with exclusions
        if filtered_files is None:
            filtered_files = scan_project_files(root_path, EXCLUDE_PATTERNS)

        if not filtered_files:
            # Fallback to directory timestamp if no valid files
            stat = root_path.stat()
            t = datetime.fromtimestamp(stat.st_mtime)
            return {
                "created_at": t,
                "last_modified": t
            }

        file_mtimes = []
        for file_path in filtered_files:
            try:
                stat = file_path.stat()
                file_mtimes.append(stat.st_mtime)
            except (OSError, PermissionError):
                continue  # Skip files we can't read

        if not file_mtimes:
            # Fallback if no readable files
            stat = root_path.stat()
            t = datetime.fromtimestamp(stat.st_mtime)
            return {
                "created_at": t,
                "last_modified": t
            }

        earliest = min(file_mtimes)
        latest = max(file_mtimes)

        return {
            "created_at": datetime.fromtimestamp(earliest),
            "last_modified": datetime.fromtimestamp(latest)
        }

    except Exception as e:
        print(f"Error extracting project timestamps for {project_root}: {e}")
        now = datetime.now()
        return {
            "created_at": now,
            "last_modified": now
        }
        
def get_project_signature(file_signatures: List[str]) -> str:
    """
    Generate a unique signature for the project based on all file signatures.
    """
    sorted_sigs = sorted(file_signatures)
    sigs_json = json.dumps(sorted_sigs)
    return hashlib.sha256(sigs_json.encode()).hexdigest()


def extract_file_signature(file_path: Union[str, Path], project_root: Union[str, Path], retries: int = 2, delay: float = 0.1) -> str:
    """
    Generate a signature based on relative path + file size only.
    Ignores timestamps and absolute paths to be consistent across extractions.
    """
    for attempt in range(1, retries + 1):
        try:
            p = Path(file_path)
            root = Path(project_root)
            stat = p.stat()
            
            # Just use relative path + size (no timestamp)
            rel_path = str(p.relative_to(root))
            sig_str = f"{rel_path}:{stat.st_size}"
            return hashlib.sha256(sig_str.encode()).hexdigest()
            
        except (FileNotFoundError, PermissionError, ValueError) as e:
            print(f"Error extracting signature for {file_path} (attempt {attempt}/{retries}): {e}")
            if attempt < retries:
                time.sleep(delay)
    
    return "ERROR_SIGNATURE"

def store_project_in_db(signature: str, name: str, path: str, file_signatures: List[str], size_bytes: int, created_at: datetime = None, last_modified: datetime = None):
    """Store project and its file signatures in the PROJECT table with actual timestamps."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Use provided timestamps or current time as fallback
    if created_at is None:
        created_at = datetime.now()
    if last_modified is None:
        last_modified = datetime.now()
    
    # Convert to ISO format strings - these sort chronologically as strings!
    created_at_str = created_at.isoformat() if isinstance(created_at, datetime) else str(created_at)
    last_modified_str = last_modified.isoformat() if isinstance(last_modified, datetime) else str(last_modified)
    
    cursor.execute(
        """INSERT OR REPLACE INTO PROJECT 
           (project_signature, name, path, file_signatures, size_bytes, created_at, last_modified) 
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (signature, name, path, json.dumps(file_signatures), size_bytes, created_at_str, last_modified_str)
    )
    conn.commit()
    conn.close()
  

def project_signature_exists(signature: str) -> bool:
    """Check if a project signature exists in the DB."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM PROJECT WHERE project_signature = ?", (signature,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists
  

def get_all_file_signatures_from_db() -> set:
    """Get all file signatures from all projects in the DB."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT file_signatures FROM PROJECT")
    rows = cursor.fetchall()
    conn.close()
    sigs = set()
    for row in rows:
        if row[0]:
            sigs.update(json.loads(row[0]))
    return sigs

def calculate_project_similarity(current_signatures: List[str], existing_signatures: List[str]) -> float:
    """Calculate Jaccard similarity between two sets of file signatures.
    
    Returns:
        Similarity percentage (0-100) based on file overlap.
    """
    current_set = set(current_signatures)
    existing_set = set(existing_signatures)
    overlap = len(current_set.intersection(existing_set))
    total = len(current_set.union(existing_set))
    return (overlap / total) * 100 if total > 0 else 0.0


def calculate_containment_ratio(current_signatures: List[str], existing_signatures: List[str]) -> float:
    """Calculate containment ratio: what percentage of existing files are in the current upload.
    
    This helps identify incremental updates where most of the original project 
    is preserved but new files are added.
    
    Args:
        current_signatures: File signatures from the current upload
        existing_signatures: File signatures from an existing project in DB
    
    Returns:
        Containment percentage (0-100): overlap / len(existing_signatures)
        Returns 0.0 if existing_signatures is empty.
    """
    if not existing_signatures:
        return 0.0
    
    current_set = set(current_signatures)
    existing_set = set(existing_signatures)
    overlap = len(current_set.intersection(existing_set))
    
    return (overlap / len(existing_set)) * 100

def find_and_update_similar_project(current_signatures: List[str], new_project_sig: str, threshold: float = None, file_count: int = 0, containment_threshold: float = 90.0) -> Optional[tuple]:
    """
    Find a similar project and replace it with the new upload.
    
    Uses a dual-check approach:
    1. Jaccard similarity: Standard overlap measure
    2. Containment ratio: Checks if most existing files are preserved (≥90% by default)
    
    A project matches if EITHER the Jaccard similarity meets the threshold OR
    the containment ratio is ≥90% (most existing files are preserved).
    
    Args:
        current_signatures: File signatures from the current upload
        new_project_sig: The already-calculated project signature for the new upload
        threshold: Minimum similarity percentage to consider a match (if None, auto-calculates based on file count)
        file_count: Number of files in the current project (used for dynamic threshold)
        containment_threshold: Minimum containment ratio to consider a match (default 90.0%)
    
    Returns (project_name, similarity_percentage, new_project_signature) or None.
    """
    # Calculate dynamic threshold if not provided
    if threshold is None:
        threshold = calculate_dynamic_threshold(file_count)
        print(f"[INFO] Using dynamic threshold: {threshold}% (based on {file_count} files)")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT project_signature, name, file_signatures, path, size_bytes, created_at FROM PROJECT")
    projects = cursor.fetchall()
    
    for old_project_sig, project_name, file_sigs_json, path, size_bytes, created_at in projects:
        existing_sigs = json.loads(file_sigs_json) if file_sigs_json else []
        
        # Calculate Jaccard similarity
        similarity = calculate_project_similarity(current_signatures, existing_sigs)
        
        # Calculate containment ratio (what % of existing files are preserved)
        containment = calculate_containment_ratio(current_signatures, existing_sigs)
        
        # Debug: Print similarity and containment values for each comparison
        print(f"[DEBUG] Comparing with project '{project_name}':")
        print(f"        Jaccard similarity = {similarity:.2f}% (threshold: {threshold}%)")
        print(f"        Containment ratio = {containment:.2f}% (threshold: {containment_threshold}%)")
        
        # Match if EITHER Jaccard similarity meets threshold OR containment is high
        # High containment means most existing files are preserved (incremental update)
        is_match = similarity >= threshold or containment >= containment_threshold
        
        if is_match:
            match_reason = "Jaccard similarity" if similarity >= threshold else "containment ratio"
            print(f"[DEBUG] Match found via {match_reason}! Updating project '{project_name}'")
            print(f"[DEBUG] Old signature: {old_project_sig}")
            print(f"[DEBUG] New signature: {new_project_sig}")
            
            # Delete the old project entry (CASCADE will clean up related tables)
            cursor.execute("DELETE FROM PROJECT WHERE project_signature = ?", (old_project_sig,))
            conn.commit()
            conn.close()
            
            # Use existing function to store the updated project
            store_project_in_db(
                signature=new_project_sig,
                name=project_name,
                path=path,
                file_signatures=current_signatures,
                size_bytes=size_bytes,
                created_at=created_at,  # Preserve original creation date
                last_modified=datetime.now()  # Update modification time
            )
            
            return (project_name, similarity, new_project_sig)
    
    conn.close()
    return None


def run_scan_flow(root: str, exclude: list = None, similarity_threshold: float = None, base_threshold: float = 65.0) -> dict:
    """
    Scans the project, stores signatures in DB, and returns analysis info.
    Returns dict with 'files', 'skip_analysis', 'score', 'signature' keys.
    
    Args:
        root: Root directory to scan
        exclude: List of patterns to exclude
        similarity_threshold: Fixed threshold (if None, auto-calculates based on project size)
        base_threshold: Base threshold for dynamic calculation (default 65.0)
    """
    patterns = EXCLUDE_PATTERNS.copy()
    if exclude:
        patterns.extend(exclude)
    files = scan_project_files(root, exclude_patterns=patterns)
    if not files:
        print("No files found to scan in the specified directory. Skipping analysis.")
        return {
            "files": [], 
            "skip_analysis": True, 
            "score": 0.0, 
            "reason": "no_files",
            "signature": None
        }

    # Print scanned files for user feedback
    print(f"Scanned files (excluding patterns {exclude}):")
    for f in files:
        print(f)

    # Extract project timestamps
    timestamps = extract_project_timestamps(root, filtered_files=files)
    
    file_signatures = [extract_file_signature(f, root) for f in files]
    project_signature = get_project_signature(file_signatures)
    
    # Count files for dynamic threshold calculation
    file_count = len(files)
    
    # Check if exact project already exists
    if project_signature_exists(project_signature):
        print("100.0% of this Project was analyzed in the past.")
        return {
            "files": files,
            "skip_analysis": True,
            "score": 100.0,
            "reason": "already_analyzed",
            "signature": project_signature
        }
    
    # Check for similar projects and update (use dynamic threshold if not provided)
    result = find_and_update_similar_project(
        file_signatures, 
        project_signature, 
        threshold=similarity_threshold,
        file_count=file_count
    )
    if result:
        project_name, similarity, new_sig = result
        print(f"Updated existing project '{project_name}' with new files ({similarity:.1f}% similarity).")
        return {
            "files": files,
            "skip_analysis": False,
            "score": similarity,
            "reason": "updated_existing",
            "signature": new_sig,
            "updated_project": project_name
        }
    
    # Project is new - store it
    size_bytes = sum(extract_file_metadata(f)["size_bytes"] for f in files)
    name = Path(root).name
    path = str(Path(root).resolve())
    store_project_in_db(
            project_signature, 
            name, 
            path, 
            file_signatures, 
            size_bytes,
            timestamps["created_at"],
            timestamps["last_modified"]
        )
    print("Stored project and file signatures in DB.")
    return {
        "files": files,
        "skip_analysis": False,
        "score": 0.0,
        "reason": "new_project",
        "signature": project_signature
    }
