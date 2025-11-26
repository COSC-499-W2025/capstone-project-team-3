"""
Non-code file checker - identifies and filters non-code files from repositories and local paths.
Reuses functions from git_utils.py for consistency.
"""
from pathlib import Path
from typing import Set, List, Union, Dict, Any
from app.utils.git_utils import (
    get_repo, 
    detect_git
)
from app.utils.scan_utils import scan_project_files

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


def collect_git_non_code_files_with_metadata(
    repo_path: Union[str, Path]
) -> Dict[str, Dict[str, Any]]:
    """
    Collect non-code files from a git repository with author and commit metadata.
    REUSES: get_repo() from git_utils.py
    
    Args:
        repo_path: Path to git repository
    
    Returns:
        Dictionary mapping file paths to metadata:
        {
            file_path: {
                "path": str,              # Absolute path to file
                "authors": [emails],      # List of author emails who committed
                "commit_count": int,      # Total number of commits
                "is_collaborative": bool  # True if >1 author
            }
        }
    """
    try:
        repo = get_repo(repo_path)  # REUSED from git_utils.py
    except Exception:
        return {}
    
    file_info: Dict[str, Dict[str, Any]] = {}
    
    # Iterate through all commits in all branches (same pattern as git_utils.py)
    for commit in repo.iter_commits(rev="--all"):
        author_email = getattr(commit.author, "email", None) or "unknown"
        
        try:
            files = commit.stats.files or {}
        except Exception:
            continue
        
        for file_path in files.keys():
            # Check if it's a non-code file
            if not is_non_code_file(file_path):
                continue
            
            # Initialize file info if first time seeing this file
            if file_path not in file_info:
                file_info[file_path] = {
                    "path": str((Path(repo_path) / file_path).resolve()),
                    "authors": set(),
                    "commit_count": 0
                }
            
            # Add author and increment commit count
            file_info[file_path]["authors"].add(author_email)
            file_info[file_path]["commit_count"] += 1
    
    # Convert sets to lists and add is_collaborative flag
    result = {}
    for file_path, info in file_info.items():
        result[file_path] = {
            "path": info["path"],
            "authors": sorted(list(info["authors"])),
            "commit_count": info["commit_count"],
            "is_collaborative": len(info["authors"]) > 1
        }
    
    return result


def filter_non_code_files_by_collaboration(
    file_metadata: Dict[str, Dict[str, Any]],
    author_threshold: int = 1
) -> Dict[str, List[str]]:
    """
    Filter non-code files into collaborative and non-collaborative categories.
    
    Args:
        file_metadata: Output from collect_git_non_code_files_with_metadata()
        author_threshold: Minimum number of authors for a file to be considered collaborative
                         Default is 1, meaning files with 2+ authors are collaborative
    
    Returns:
        Dictionary with two keys:
        {
            "collaborative": [list of file paths with >author_threshold authors],
            "non_collaborative": [list of file paths with <=author_threshold authors]
        }
    """
    collaborative = []
    non_collaborative = []
    
    for file_path, info in file_metadata.items():
        author_count = len(info.get("authors", []))
        
        if author_count > author_threshold:
            collaborative.append(info["path"])
        else:
            non_collaborative.append(info["path"])
    
    return {
        "collaborative": collaborative,
        "non_collaborative": non_collaborative
    }

def get_git_user_identity(repo_path: Union[str, Path]) -> Dict[str, str]:
    """
    Get the current git user's identity (name and email) from the repository.
    REUSES: get_repo() from git_utils.py
    
    Args:
        repo_path: Path to git repository
        
    Returns:
        Dict with 'name' and 'email' keys, or empty dict if not found
    """
    try:
        repo = get_repo(repo_path)  # REUSED from git_utils.py
        config_reader = repo.config_reader()
        
        name = config_reader.get_value("user", "name", default="")
        email = config_reader.get_value("user", "email", default="")
        
        return {
            "name": name,
            "email": email
        }
    except Exception:
        return {}
    

def verify_user_in_files(
    file_metadata: Dict[str, Dict[str, Any]],
    user_email: str
) -> Dict[str, List[str]]:
    """
    Verify which files the user actually contributed to vs files by others only.
    
    Ensures collaborative files have user + at least 1 other person.
    Ensures non-collaborative files have ONLY the user.
    
    Args:
        file_metadata: Output from collect_git_non_code_files_with_metadata()
        user_email: Email of the user to verify
    
    Returns:
        {
            "user_collaborative": [paths],    # Files with user + at least 1 other
            "user_solo": [paths],             # Files with ONLY user
            "others_only": [paths]            # Files WITHOUT user
        }
    """
    user_collaborative = []
    user_solo = []
    others_only = []
    
    for file_path, info in file_metadata.items():
        authors = info.get("authors", [])
        
        if user_email in authors:
            # User IS an author
            if len(authors) == 1:
                # ONLY user (solo work)
                user_solo.append(info["path"])
            else:
                # User + at least 1 other person (collaborative)
                user_collaborative.append(info["path"])
        else:
            # User is NOT an author (others' work)
            others_only.append(info["path"])
    
    return {
        "user_collaborative": user_collaborative,
        "user_solo": user_solo,
        "others_only": others_only
    }

def get_classified_non_code_file_paths(
    directory: Union[str, Path],
    user_email: str = None
) -> List[str]:
    """
    Classify non-code files and return file paths ready for parsing.
    Does NOT parse files - returns paths only for later parsing integration.
    
    Args:
        directory: Path to directory/repository
        user_email: Email of user (if None, gets from git config for git repos)
    
    Returns:
        List of file paths (collaborative + non_collaborative, excludes others' files)
    """
    classification = classify_non_code_files_with_user_verification(directory, user_email)
    return classification["collaborative"] + classification["non_collaborative"]


def classify_non_code_files_with_user_verification(
    directory: Union[str, Path],
    user_email: str = None
) -> Dict[str, Any]:
    """
    Classify non-code files as collaborative or non-collaborative with user verification.
    REUSES: detect_git(), get_repo() from git_utils.py
           scan_project_files() from scan_utils.py
           filter_non_code_files() from this module
    
    Classification logic:
    - COLLABORATIVE: Git repo + 2+ authors + user is one of them
    - NON-COLLABORATIVE: 
        * Git repo + only 1 author (user) 
        * OR local files (non-git)
    
    Args:
        directory: Path to directory/repository
        user_email: Email of user (if None, gets from git config for git repos)
    
    Returns:
        {
            "is_git_repo": bool,
            "user_identity": {"name": str, "email": str} or {},
            "collaborative": [paths],        # Git + 2+ authors + user is author
            "non_collaborative": [paths],    # Git + user only OR local files
            "excluded": [paths]              # Git + user NOT author
        }
    
    Example:
        # Git repo with user verification
        >>> result = classify_non_code_files_with_user_verification('/path/to/git/repo')
        >>> print(f"Collaborative (you + others): {len(result['collaborative'])}")
        >>> print(f"Non-collaborative (solo or local): {len(result['non_collaborative'])}")
        
        # Non-git directory (all files are non-collaborative)
        >>> result = classify_non_code_files_with_user_verification('/path/to/local')
        >>> print(f"All local files (non-collaborative): {len(result['non_collaborative'])}")
    """
    directory = Path(directory)
    
    # REUSED: detect_git() from git_utils.py
    if detect_git(directory):
        # Git repository - get user identity
        if user_email is None:
            user_identity = get_git_user_identity(directory)
            user_email = user_identity.get("email", "")
        else:
            user_identity = {"name": "", "email": user_email}
        
        if not user_email:
            # Can't determine user - treat as error case
            return {
                "is_git_repo": True,
                "user_identity": {},
                "collaborative": [],
                "non_collaborative": [],
                "excluded": [],
                "error": "Could not determine git user identity"
            }
        
        # Collect git metadata (uses get_repo internally)
        metadata = collect_git_non_code_files_with_metadata(directory)
        
        # Verify user in files
        verified = verify_user_in_files(metadata, user_email)
        
        return {
            "is_git_repo": True,
            "user_identity": user_identity,
            "collaborative": verified["user_collaborative"],      # Git + 2+ authors + user
            "non_collaborative": verified["user_solo"],           # Git + user only
            "excluded": verified["others_only"]                   # Git + user NOT author
        }
    else:
        # Non-git directory - REUSE scan_project_files + filter_non_code_files
        all_files = scan_project_files(str(directory))
        local_files = filter_non_code_files(all_files)
        
        return {
            "is_git_repo": False,
            "user_identity": {},
            "collaborative": [],                                  # No git = no collaboration
            "non_collaborative": local_files,                     # All local files
            "excluded": []
        }
