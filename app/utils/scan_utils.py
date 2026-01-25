from pathlib import Path
from typing import Union, List, Dict, Optional
import hashlib
import json
import time 
from datetime import datetime
from app.data.db import get_connection

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
    "lib"
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

def find_and_update_similar_project(current_signatures: List[str], threshold: float = 70.0) -> Optional[tuple]:
    """Find similar project and update it. Returns (project_name, similarity_percentage) or None."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT project_signature, name, file_signatures FROM PROJECT")
    projects = cursor.fetchall()
    
    for project_sig, project_name, file_sigs_json in projects:
        existing_sigs = json.loads(file_sigs_json) if file_sigs_json else []
        
        # Calculate similarity using helper function
        similarity = calculate_project_similarity(current_signatures, existing_sigs)
        
        if similarity >= threshold:
            # Update existing project
            merged_sigs = list(set(current_signatures).union(set(existing_sigs)))
            cursor.execute("UPDATE PROJECT SET file_signatures = ?, last_modified = CURRENT_TIMESTAMP WHERE project_signature = ?", 
                         (json.dumps(merged_sigs), project_sig))
            conn.commit()
            conn.close()
            return (project_name, similarity)
    
    conn.close()
    return None


def run_scan_flow(root: str, exclude: list = None, similarity_threshold: float = 70.0) -> dict:
    """
    Scans the project, stores signatures in DB, and returns analysis info.
    Returns dict with 'files', 'skip_analysis', 'score', 'signature' keys.
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
    
    # Check for similar projects and update
    result = find_and_update_similar_project(file_signatures, similarity_threshold)
    if result:
        project_name, similarity = result
        print(f"Updated existing project '{project_name}' with new files ({similarity:.1f}% similarity).")
        return {
            "files": files,
            "skip_analysis": False,
            "score": similarity,
            "reason": "updated_existing",
            "signature": None,
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
