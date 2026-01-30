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
    ".jpg", ".jpeg", ".gif", ".bmp", ".svg",
    ".mp4", ".mov", ".avi", ".tar", ".gz",
    ".ppt", ".pptx"
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
        author_username = getattr(commit.author, "name", None) or "unknown"
        
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
                    "author_email": set(),
                    "author_username":set(),
                    "commit_count": 0
                }
            
            # Add author and increment commit count
            file_info[file_path]["author_email"].add(author_email)
            file_info[file_path]["author_username"].add(author_username)
            file_info[file_path]["commit_count"] += 1
    
    # Convert sets to lists and add is_collaborative flag
    result = {}
    for file_path, info in file_info.items():
        result[file_path] = {
            "path": info["path"],
            "authors": sorted(list(info["author_email"])),
            "usernames": sorted(list(info["author_username"])),
            "commit_count": info["commit_count"],
            "is_collaborative": len(info["author_username"]) > 1
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
    user_email: str,
    username:str
) -> Dict[str, List[str]]:
    """
    Verify which files the user actually contributed to vs files by others only.
    
    README files and binary files (PDF, DOCX) are treated specially - they go to 
    user_solo (non-collaborative) so they get full content parsing instead of 
    git diff extraction (which doesn't work for binary files).
    
    Args:
        file_metadata: Output from collect_git_non_code_files_with_metadata()
        user_email: Email of the user to verify
    
    Returns:
        {
            "user_collaborative": [paths],    # Files with user + at least 1 other (extract git diffs)
            "user_solo": [paths],             # Files with ONLY user OR README/PDF/DOCX (parse full content)
            "others_only": [paths]            # Files WITHOUT user
        }
    """
    user_collaborative = []
    user_solo = []
    others_only = []
    
    # Binary/special extensions that can't be parsed via git diff
    non_diffable_extensions = {".pdf", ".docx", ".doc"}

    for file_path, info in file_metadata.items():
        authors = info.get("authors", [])
        usernames = info.get("usernames", [])
        path_obj = Path(info["path"])
        is_readme = path_obj.name.lower().startswith("readme")
        is_non_diffable = path_obj.suffix.lower() in non_diffable_extensions

        # README and binary files (PDF/DOCX) always go to user_solo for full content parsing
        # since git diff extraction doesn't work for these file types
        if is_readme or is_non_diffable:
            user_solo.append(info["path"])
            continue

        # Case-insensitive comparison for username and email matching
        username_lower = username.lower() if username else ""
        user_email_lower = user_email.lower() if user_email else ""
        usernames_lower = [u.lower() for u in usernames]
        authors_lower = [a.lower() for a in authors]
        
        # Check multiple matching strategies:
        # 1. Exact username match in usernames list (case-insensitive)
        # 2. Exact email match in authors (emails) list (case-insensitive)
        # 3. Username contained in GitHub noreply email (e.g., "PaintedW0lf" in "97552907+PaintedW0lf@users.noreply.github.com")
        user_is_author = False
        
        # Strategy 1: Exact username match (case-insensitive)
        if username_lower and username_lower in usernames_lower:
            user_is_author = True
        
        # Strategy 2: Exact email match (case-insensitive)
        if user_email_lower and user_email_lower in authors_lower:
            user_is_author = True
        
        # Strategy 3: Username contained in any author email (GitHub noreply format)
        if username_lower and not user_is_author:
            for author in authors_lower:
                if username_lower in author:
                    user_is_author = True
                    break
        
        if user_is_author:
            if len(authors) == 1:
                user_solo.append(info["path"])
            else:
                user_collaborative.append(info["path"])
        else:
            others_only.append(info["path"])

    return {
        "user_collaborative": user_collaborative,
        "user_solo": user_solo,
        "others_only": others_only
    }

def get_classified_non_code_file_paths(
    directory: Union[str, Path],
    user_email: str = None
) -> Dict[str, List[str]]:
    """
    Classify non-code files and return separate lists for different parsing strategies.
    
    Args:
        directory: Path to directory/repository
        user_email: Email of user (if None, gets from git config for git repos)
    
    Returns:
        Dictionary with:
        {
            "collaborative": [paths],      # Files to parse author-only content from git
            "non_collaborative": [paths]   # Files to parse full content
        }
    """
    classification = classify_non_code_files_with_user_verification(directory, user_email)
    return {
        "collaborative": classification["collaborative"],
        "non_collaborative": classification["non_collaborative"]
    }


def classify_non_code_files_with_user_verification(
    directory: Union[str, Path],
    user_email: str = None,
    username:str=None
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
        if user_email is None or username is None:
            user_identity = get_git_user_identity(directory)
            user_email = user_identity.get("email", "")
            username = user_identity.get("name","")
        else:
            user_identity = {"name": username, "email": user_email}
        
        if not username or not user_email:
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
        verified = verify_user_in_files(metadata, user_email, username)
        
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
