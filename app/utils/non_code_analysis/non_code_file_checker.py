"""
Non-code file checker - identifies and filters non-code files from repositories and local paths.
"""
import os
from pathlib import Path
from typing import Set, List, Union

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

def collect_local_non_code_files(root_path: Union[str, Path], 
                                  exclude_dirs: Set[str] = None) -> List[str]:
    """
    Recursively collect all non-code file paths from a local directory.
    
    Args:
        root_path: Root directory to scan
        exclude_dirs: Set of directory names to exclude (e.g., {'.git', 'node_modules'})
        
    Returns:
        List of absolute paths to non-code files
    """
    if exclude_dirs is None:
        exclude_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}
    
    non_code_files = []
    root = Path(root_path)
    
    if not root.exists() or not root.is_dir():
        return []
    
    for dirpath, dirnames, filenames in os.walk(root):
        # Remove excluded directories from traversal
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        
        for filename in filenames:
            file_path = Path(dirpath) / filename
            if is_non_code_file(file_path):
                non_code_files.append(str(file_path.resolve()))
    
    return non_code_files
