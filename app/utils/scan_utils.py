from pathlib import Path
from typing import Union, List, Dict
import hashlib
import json

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
    for p in root_path.rglob("*"):
        if p.is_file() and not should_exclude(p, exclude_patterns):
            files.append(p)
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


def get_project_metadata_signature(metadata_list: List[Dict]) -> str:
    """
    Generate a unique signature for the project based on all file metadata.
    """
    # Sort metadata by file_path to ensure consistent order
    sorted_metadata = sorted(metadata_list, key=lambda x: x["file_path"])
    # Serialize and hash
    metadata_json = json.dumps(sorted_metadata, sort_keys=True)
    return hashlib.sha256(metadata_json.encode()).hexdigest()

def project_metadata_exists_in_db(signature: str) -> bool:
    """Dummy function to simulate checking for existing project metadata in the database."""
    # TODO: Replace with real DB lookup
    return False

def store_project_signature_in_db(signature: str):
    """Dummy function to simulate storing project signature in the database."""
    # TODO: Replace with real DB insert logic
    print(f"[Dummy] Would store project signature in DB: {signature}")