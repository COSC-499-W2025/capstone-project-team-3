from git import InvalidGitRepositoryError, NoSuchPathError, Repo, GitCommandError
from pathlib import Path
from typing import Union
from datetime import datetime
import os

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
        return Repo(path,search_parent_directories=True)
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

def author_matches(commit, author: str) -> bool:
    """Return True if a commit's author matches the given author string (by name or email)."""
    a = commit.author
    return a and (a.name == author or a.email == author)

def extract_files_changed(path: Union[str, Path], author: str, branches=True) -> int:
    """Returns the total number of files changed by the author in all branches."""
    total_files_changed = 0
    repo = get_repo(path)
    seen = set()

    for commit in repo.iter_commits(branches=branches):
        if commit.hexsha in seen:
            continue
        seen.add(commit.hexsha)

        if author_matches(commit, author):
            total_files_changed += len(commit.stats.files)

    return total_files_changed
    
def extract_line_changes(path: Union[str, Path], author: str, branches=True) -> dict:
    """Return the total number of lines added and deleted by the author."""
    total_added = 0
    total_deleted = 0
    repo = get_repo(path)
    seen = set()
    
    for commit in repo.iter_commits(branches=branches):
        if commit.hexsha in seen:
            continue
        seen.add(commit.hexsha)
        
        if author_matches(commit, author):
            stats = commit.stats.total
            total_added += stats["insertions"]
            total_deleted += stats["deletions"]

    contributions = {"added":total_added,"deleted":total_deleted}
    return contributions

def init_file_stats() -> dict:
    """Initialize a contribution dictionary for a file type."""
    return {"files_changed": 0, "added": 0, "deleted": 0}

def extract_contribution_by_filetype(path: Union[str, Path], author: str, branches=True) -> dict:
    """
    Return a breakdown of contributions (files changed, lines added/deleted) by file type.
    Example format: {".py": {"files_changed": 10, "added": 310, "deleted": 80}}
    """
    repo = get_repo(path)
    contributions = {}
    seen = set()

    for commit in repo.iter_commits(branches=branches):
        if commit.hexsha in seen:
            continue
        seen.add(commit.hexsha)
        
        if not author_matches(commit, author):
            continue

        for file_path, details in commit.stats.files.items():
            ext = os.path.splitext(file_path)[1] or "[no extension]"

            if ext not in contributions:
                contributions[ext] = init_file_stats()

            contributions[ext]["files_changed"] += 1
            contributions[ext]["added"] += details["insertions"]
            contributions[ext]["deleted"] += details["deletions"]

    return contributions

def extract_branches_for_author(path: Union[str, Path], author: str) -> list[str]:
    """Return a list of branches that include at least one commit by the given author."""
    repo = get_repo(path)
    author_branches = set()

    for branch in repo.branches:
        for commit in repo.iter_commits(branch):
            if author_matches(commit, author):
                author_branches.add(branch.name)
                break  # Stop after finding first commit by that author in this branch

    return sorted(author_branches)

def is_repo_empty(path: Union[str, Path]) -> bool:
    """Check if the given path corresponds to an empty Git repository.
    A repo is considered empty if it has no commits (no HEAD reference).
    """
    try:
        repo = get_repo(path)
        # repo.head.is_valid() returns False if there are no commits
        return not repo.head.is_valid()
    except ValueError:
        # if function fails, it means it's not a valid repo
        return True
