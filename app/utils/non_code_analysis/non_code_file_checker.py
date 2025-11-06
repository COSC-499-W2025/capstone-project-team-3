"""
Non-code file checker - identifies and filters non-code files from repositories and local paths.
"""
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