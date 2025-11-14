"""
Non-code file checker - identifies and filters non-code files from repositories and local paths.
"""
import os
from pathlib import Path
from typing import Set, List, Union, Dict, Any
from app.utils.git_utils import get_repo, is_collaborative

# Extensions considered non-code
NON_CODE_EXTENSIONS: Set[str] = {
    ".pdf", ".docx", ".doc", ".txt", ".md", ".markdown",
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg",
    ".mp4", ".mov", ".avi", ".zip", ".tar", ".gz",
    ".ppt", ".pptx", ".xls", ".xlsx"
}


def is_non_code_file(file_path: Union[str, Path]) -> bool:
    """
    Check if a file is a non-code file based on its extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if file extension is in NON_CODE_EXTENSIONS, False otherwise
    """
    path = Path(file_path)
    extension = path.suffix.lower()
    return extension in NON_CODE_EXTENSIONS


def filter_non_code_files(file_paths: List[Union[str, Path]]) -> List[str]:
    """
    Filter a list of file paths to return only non-code files.
    
    This function is designed to work after scan_project_files() has already
    filtered out excluded directories and patterns.
    
    Args:
        file_paths: List of file paths (typically from scan_project_files())
        
    Returns:
        List of absolute paths to non-code files only
    
    Example:
        >>> from app.utils.scan_utils import scan_project_files
        >>> all_files = scan_project_files('/path/to/project')
        >>> non_code_files = filter_non_code_files(all_files)
    """
    non_code_files = []
    
    for file_path in file_paths:
        path = Path(file_path)
        
        # Skip if file doesn't exist (safety check)
        if not path.exists() or not path.is_file():
            continue
            
        if is_non_code_file(path):
            non_code_files.append(str(path.resolve()))
    
    return non_code_files

# ============================================================================
# Collect non-code files from git repo (metadata only, no classification)
# ============================================================================

def collect_git_non_code_files_with_metadata(repo_path: Union[str, Path]) -> Dict[str, Dict[str, Any]]:
    """
    Collect non-code files from a git repository with author and commit metadata.
    Does NOT classify collaboration - that's done by filter_non_code_files_by_collaboration().
    
    Returns: {file_path: {path: str, authors: [emails], commit_count: int}}
    """
    try:
        repo = get_repo(repo_path)
    except Exception:
        return {}
    
    file_info: Dict[str, Dict[str, Any]] = {}
    
    for commit in repo.iter_commits(rev="--all"):
        author_email = getattr(commit.author, "email", None) or "unknown"
        
        try:
            files = commit.stats.files or {}
        except Exception:
            continue
        
        for file_path in files.keys():
            if not is_non_code_file(file_path):
                continue
            
            if file_path not in file_info:
                file_info[file_path] = {
                    "path": str((Path(repo_path) / file_path).resolve()),
                    "authors": set(),
                    "commit_count": 0
                }
            
            file_info[file_path]["authors"].add(author_email)
            file_info[file_path]["commit_count"] += 1
    
    # Convert sets to lists for JSON serialization
    result = {}
    for file_path, info in file_info.items():
        result[file_path] = {
            "path": info["path"],
            "authors": sorted(list(info["authors"])),
            "commit_count": info["commit_count"]
        }
    
    return result

