from git import InvalidGitRepositoryError, NoSuchPathError, Repo, GitCommandError
from pathlib import Path
from typing import Union
from datetime import datetime

def detect_git(path: Union[str, Path]) -> bool:
    """Determines whether specified path is a git folder or not.

    Args:
        path (Union[str, Path]): Accepts a string as a path or a Path variable

    Returns:
        bool: Returns true if specified path is a git repo otherwise, returns False.
    """
    try:
        Repo(path, search_parent_directories=True)
        return True
    except (InvalidGitRepositoryError, NoSuchPathError, GitCommandError, PermissionError):
        return False
    
def get_repo(path:Union[str,Path]):
    """Return a Repo object from a folder path."""
    try:
        return Repo(path)
    except Exception as e:
        raise ValueError(f"Unable to load git repo from: {path}") from e
    
def extract_all_commits(path: Union[str, Path])-> list:
    """Returns a list of commits associated with the specified git repo"""
    
    repo = get_repo(path)
    return list(repo.iter_commits()) #we can set a max_count of commits that should be returned (if necessary)

def extract_commit_hashes(path: Union[str, Path]) -> list:
    """Returns a list of commit hashes associated with the specified git repo"""
    
    return [commit.hexsha for commit in extract_all_commits(path)]

def extract_commit_messages(path: Union[str, Path]) ->list:
    """Returns a list of the commit messages associated with the specified git repo"""
    
    return [commit.message for commit in extract_all_commits(path)]

def extract_commit_authored_datetimes(path: Union[str, Path]) ->list:
    """
    Returns a list of the authored commit dates and times associated with the specified git repo.
    The authored commit datetimes tells you when the work was initially done.
    
    """
    
    return [datetime.fromtimestamp(commit.authored_date).strftime('%Y-%m-%d %H:%M:%S') for commit in extract_all_commits(path)]

def extract_commit_datetimes(path: Union[str, Path]) ->list:
    """
    Returns a list of the commit dates and times associated with the specified git repo.
    The committed datetimes tells you when the work was formally integrated into the project's history.
    """
    
    return [datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d %H:%M:%S') for commit in extract_all_commits(path)]

def extract_commit_authors(path: Union[str, Path]) ->list:
    """Returns a list of the authors of commits associated with the specified git repo"""
    
    return [commit.author.name for commit in extract_all_commits(path)]