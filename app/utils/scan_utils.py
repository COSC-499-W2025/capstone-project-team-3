from pathlib import Path
from typing import Union, List, Dict
import hashlib
import json
import time 
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


def get_project_signature(file_signatures: List[str]) -> str:
    """
    Generate a unique signature for the project based on all file signatures.
    """
    sorted_sigs = sorted(file_signatures)
    sigs_json = json.dumps(sorted_sigs)
    return hashlib.sha256(sigs_json.encode()).hexdigest()


def extract_file_signature(file_path: Union[str, Path], project_root: Union[str, Path], retries: int = 2, delay: float = 0.1) -> str:
    """
    Generate a unique signature for a file (hash of relative path + size + last_modified).
    Handles errors if file is missing, unreadable, or path issues. Retries on error.
    """
    for attempt in range(1, retries + 1):
        try:
            p = Path(file_path)
            root = Path(project_root)
            stat = p.stat()
            rel_path = str(p.relative_to(root))
            sig_str = f"{rel_path}:{stat.st_size}:{stat.st_mtime}"
            return hashlib.sha256(sig_str.encode()).hexdigest()
        except (FileNotFoundError, PermissionError, ValueError) as e:
            print(f"Error extracting signature for {file_path} (attempt {attempt}/{retries}): {e}")
            if attempt < retries:
                time.sleep(delay)
    return "ERROR_SIGNATURE"

def store_project_in_db(signature: str, name: str, path: str, file_signatures: List[str], size_bytes: int):
    """Store project and its file signatures in the PROJECT table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO PROJECT (project_signature, name, path, file_signatures, size_bytes) VALUES (?, ?, ?, ?, ?)",
        (signature, name, path, json.dumps(file_signatures), size_bytes)
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

def calculate_project_score(current_file_signatures: List[str]) -> float:
    """Calculate what % of current project files have already been analyzed."""
    db_sigs = get_all_file_signatures_from_db()
    if not current_file_signatures:
        return 0.0
    already_analyzed = sum(1 for sig in current_file_signatures if sig in db_sigs)
    return round((already_analyzed / len(current_file_signatures)) * 100, 2)

def run_scan_flow(root: str, exclude: list = None) -> list:
    """
    Scans the project, stores signatures in DB, and returns the list of files for downstream use.
    """
    patterns = EXCLUDE_PATTERNS.copy()
    if exclude:
        patterns.extend(exclude)
    files = scan_project_files(root, exclude_patterns=patterns)
    if not files:
        print("No files found to scan in the specified directory. Skipping analysis.")
        return []

    # Print scanned files for user feedback
    print(f"Scanned files (excluding patterns {exclude}):")
    for f in files:
        print(f)

    # Store signatures in DB (internal use only)
    file_signatures = [extract_file_signature(f, root) for f in files]
    signature = get_project_signature(file_signatures)
    size_bytes = sum(extract_file_metadata(f)["size_bytes"] for f in files)
    name = Path(root).name
    path = str(Path(root).resolve())

    score = calculate_project_score(file_signatures)
    print(f"Project analysis score: {score}% of files already analyzed.")
    if not project_signature_exists(signature):
        store_project_in_db(signature, name, path, file_signatures, size_bytes)
        print("Stored project and file signatures in DB.")

    # return the files for downstream processing
    return files