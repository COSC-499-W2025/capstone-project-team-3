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
    
    Project markers: .git, package.json, setup.py, pom.xml, .gradle, requirements.txt, Gemfile
    Returns list of project paths (strings).
    """
    root = Path(root_dir)
    projects = []
    project_markers = {
        ".git", "package.json", "setup.py", "pom.xml", ".gradle",
        "requirements.txt", "Gemfile", "go.mod", "Cargo.toml", ".gitignore"
    }
    
    # Check if root itself is a project
    if any((root / marker).exists() for marker in project_markers):
        projects.append(str(root))
        return projects
    
    # Scan subdirectories (one level)
    for item in root.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            if any((item / marker).exists() for marker in project_markers):
                projects.append(str(item))
    
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