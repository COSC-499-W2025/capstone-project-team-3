from git import InvalidGitRepositoryError, NoSuchPathError, Repo
from pathlib import Path
from typing import Union

def detect_git(path: Union[str, Path]) -> bool:
    """Determines whether specified path is a git folder or not.

    Args:
        path (Union[str, Path]): Accepts a string as a path or a Path variable

    Returns:
        bool: Returns true if specificied path is a git repo otherwise, returns False.
    """
    try:
        Repo(path, search_parent_directories=True)
        return True
    except (InvalidGitRepositoryError, NoSuchPathError):
        return False
    

        