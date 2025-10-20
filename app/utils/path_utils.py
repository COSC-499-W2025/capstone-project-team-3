from pathlib import Path
from typing import Union
import zipfile
import tempfile
import os

def is_existing_path(path: Union[str, Path]) -> bool:
    """
    Return True if `path` exists (file or directory).
    Raises ValueError if path is None.
    """
    if path is None:
        raise ValueError("path must be provided")

    p = Path(path)
    return p.exists()

def is_zip_file(path: Union[str, Path]) -> bool:
    """
    Check whether the given file is a valid zip file.

    Returns True if it is a valid zip file, False otherwise.
    Raises ValueError if path is None or does not exist.
    """

    if path is None:
        raise ValueError("path must be provided")

    p = Path(path)

    if not p.exists():
        raise ValueError(f"The path '{p}' does not exist.")

    if not p.is_file():
        raise ValueError(f"The path '{p}' is not a file.")

    # Check if the file is a valid ZIP
    return zipfile.is_zipfile(p)

def extract_zipped_contents(path: Union[str, Path]) -> bool:
    """
    Extracts the contents of the zipped file to a temporary folder.
    Returns True if the extraction of contents runs successfully
    Raises ValueError if path is None.
    Raise ValueError if it is not a valid zipped file or something went wrong during extraction
    """
    if path is None:
        raise ValueError("path must be provided")
    
    zipped_path = Path(path)
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        with zipfile.ZipFile(zipped_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        return True
    except zipfile.BadZipFile:
        raise ValueError(f"The file {zipped_path} is not a valid zip archive.")
    except Exception as e:
        raise RuntimeError(f"An error occured during extraction: {e}")
    
def validate_read_access(path: Union[str, Path], treat_as_dir: bool = False) -> dict:
    """
    Validate that `path` exists and is readable.
    Behavior:
    - Raises ValueError if `path` is None.
    - Returns {"status": "error", "reason": "..."} if the path does not exist or is not accessible.
    - If `treat_as_dir` is True, validates directory read/traverse access.
    - If path is a directory, validates directory read/traverse access.
    - Otherwise treats path as a file: checks parent traverse access, file read bit, and attempts open.
    Returns:
        {"status":"ok", "reason":"", "path":"<resolved>"} on success
        {"status":"error", "reason":"..."} on failure
    """
    if path is None:
        raise ValueError("path must be provided")

    p = Path(path)

    # Existence check via helper (prevents duplication)
    if not is_existing_path(p):
        return {"status": "error", "reason": "directory does not exist" if treat_as_dir else "file does not exist"}

    # Directory checks (explicit or inferred)
    if treat_as_dir or p.is_dir():
        if not p.is_dir():
            return {"status": "error", "reason": "path is not a directory"}
        if not os.access(str(p), os.R_OK | os.X_OK):
            return {"status": "error", "reason": "no read/traverse permission on directory"}
        return {"status": "ok", "reason": "", "path": str(p.resolve())}

    # File checks
    if not p.is_file():
        return {"status": "error", "reason": "path is not a file"}

    parent = p.parent
    if not os.access(str(parent), os.R_OK | os.X_OK):
        return {"status": "error", "reason": "no read/traverse permission on parent directory"}
    if not os.access(str(p), os.R_OK):
        return {"status": "error", "reason": "file is not readable (permission denied)"}

    try:
        with open(str(p), "rb"):
            pass
    except Exception as exc:
        return {"status": "error", "reason": f"cannot open file: {exc}"}

    return {"status": "ok", "reason": "", "path": str(p.resolve())}
