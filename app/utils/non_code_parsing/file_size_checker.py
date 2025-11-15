from pathlib import Path

MAX_FILE_SIZE_MB = 30 # Maximum allowed file size in megabytes, TODO: can be changed as it s placeholder for now

def is_file_too_large(file_path: Path, max_size_mb: int = MAX_FILE_SIZE_MB) -> bool:
    """Return True if the file size exceeds the allowed limit (in MB)."""
    try:
        size_mb = file_path.stat().st_size / (1024 * 1024)
        return size_mb > max_size_mb
    except Exception:
        # In case file_path is invalid or inaccessible
        return True
