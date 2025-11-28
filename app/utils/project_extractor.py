import zipfile
from pathlib import Path
from typing import Union, List

from app.utils.path_utils import extract_zipped_contents, is_zip_file
import os

EXCLUDE_PATTERNS = [
    "__pycache__", ".git", ".env", ".venv", "node_modules", "env", "venv",
    "build", "dist", ".pytest_cache", ".github", ".idea", ".vscode",
    ".mypy_cache", ".ruff_cache", ".tox", ".nox", "target", "_build", "deps",
    ".stack-work", ".dart_tool", "Pods", ".swiftpm", ".gradle", "gradle",
    "coverage", ".cache", ".parcel-cache", ".next", ".nuxt", "elm-stuff",
    ".svelte-kit", ".astro", ".serverless", ".terraform", "vendor", ".bazel",
    "bazel-bin", "bazel-out", "bazel-testlogs", "__pypackages__", ".uv"
]

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

def _identify_projects(root_dir: Union[str, Path]) -> List[str]:
    """
    Identify individual projects in a directory.
    
    Logic:
    - If 1 folder inside container → That folder is the project
    - If 0 folders inside container → No projects (return [])
    - If 2+ folders inside container → Multiple projects
    
    Returns list of project paths (strings).
    """
    root = Path(root_dir)
    projects = []
    
    # System/hidden folders to completely ignore
    system_folders = {
        "__MACOSX", ".DS_Store", "Thumbs.db", ".AppleDouble", ".LSOverride"
    }
    
    # Get all top-level directories (container folders like "projects")
    container_folders = []
    for item in root.iterdir():
        if item.is_dir():
            # Skip hidden directories and system folders
            if item.name.startswith(".") or item.name in system_folders:
                continue
            container_folders.append(item)
    
    # If NO directories found at all → No projects
    if not container_folders:
        return []
    
    # If only one container folder, look inside it for actual projects
    if len(container_folders) == 1:
        container = container_folders[0]
        
        # Look inside the container for actual projects
        nested_projects = []
        for project_item in container.iterdir():
            if project_item.is_dir():
                # Skip hidden directories and system folders
                if project_item.name.startswith(".") or project_item.name in system_folders:
                    continue
                nested_projects.append(str(project_item))
        
        # Clear logic based on your requirements:
        # - 0 folders inside container → No projects
        # - 1+ folders inside container → Those are the projects
        projects.extend(nested_projects)
    
    # If multiple container folders, treat each as a project
    elif len(container_folders) > 1:
        projects = [str(folder) for folder in container_folders]
    
    return projects


def get_project_top_level_dirs(root: Union[str, Path], exclude_patterns: List[str] = EXCLUDE_PATTERNS) -> list[str]:
    """
    Extracts high-level project names from a given folder path.
    A 'project' is defined as a top-level directory.
    """
    try:
        contents = os.listdir(root)
    except Exception:
        # Path invalid, inaccessible, or unreadable
        return []

    ignore_dirs = exclude_patterns
    project_names = []

    for item in contents:
        full_path = os.path.join(root, item)

        try:
            if os.path.isdir(full_path) and item not in ignore_dirs:
                project_names.append(item)
        except Exception:
            # In case of permission errors on specific items
            continue

    return sorted(project_names)