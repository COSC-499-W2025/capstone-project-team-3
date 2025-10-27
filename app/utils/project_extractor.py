import zipfile
from pathlib import Path
from typing import Union, List

from app.utils.path_utils import extract_zipped_contents, is_zip_file

def extract_and_list_projects(zip_path: Union[str, Path]) -> dict:
    """
    Extract a ZIP file and identify individual projects within it.
    
    - Raises ValueError if path is None or not a valid ZIP.
    - Returns {"status": "ok", "projects": [...], "extracted_dir": "...", "count": N}
    - Returns {"status": "error", "reason": "..."} on failure.
    """
    if zip_path is None:
        raise ValueError("zip_path must be provided")
    
    p = Path(zip_path)
    
    # Validate it's a ZIP file using existing helper
    try:
        if not is_zip_file(str(p)):
            return {"status": "error", "reason": "file is not a valid ZIP archive"}
    except ValueError as exc:
        return {"status": "error", "reason": str(exc)}
    
    # Extract ZIP using existing helper (now returns temp_dir path)
    try:
        temp_dir = extract_zipped_contents(str(p))
    except (ValueError, RuntimeError) as exc:
        return {"status": "error", "reason": str(exc)}
    
    # Scan for projects
    projects = _identify_projects(temp_dir)
    
    return {
        "status": "ok",
        "projects": projects,
        "extracted_dir": temp_dir,
        "count": len(projects)
    }
