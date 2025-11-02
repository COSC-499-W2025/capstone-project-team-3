from git import NULL_TREE, InvalidGitRepositoryError, NoSuchPathError, Repo, GitCommandError
from pathlib import Path
from typing import Union
from datetime import datetime
import os, json
from typing import Optional

BINARY_EXTENSIONS = {
    # Images
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp", ".svg", ".ico",
    # Audio
    ".mp3", ".wav", ".ogg", ".flac", ".aac",
    # Video
    ".mp4", ".mov", ".avi", ".mkv", ".webm",
    # Documents
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".odt",
    # Archives
    ".zip", ".gz", ".tar", ".rar", ".7z",
    # Compiled/Binary
    ".exe", ".dll", ".so", ".o", ".a", ".jar", ".pyc", ".class", ".swf",
    # Other
    ".db", ".sqlite", ".dat", ".bin", ".lock", ".DS_Store"
}

# --- Vendor/build folders to skip entirely ---
SKIP_DIRS = ("node_modules/", "dist/", "build/", "out/", "__pycache__/", ".git/")

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
    
def is_collaborative(path: Union[str, Path]) -> bool:
    """
    Determines if a Git repository is a collaborative project.
    A repository is considered collaborative if it has commits from
    more than one unique author.
    """
    try:
        # Use the existing helper function to get all author names
        authors = extract_commit_authors(path)
        
        # Convert the list of authors to a set to find unique authors
        unique_authors = set(authors)
        
        # If the number of unique authors is greater than 1, it's collaborative
        return len(unique_authors) > 1
    
    except (ValueError, GitCommandError, PermissionError):
        # extract_commit_authors -> get_repo will raise a ValueError
        # if the path is not a valid git repository.
        # A non-repo is not a collaborative project.
        return False
    except Exception:
        return False

def extract_code_commit_content_by_author(
    path: Union[str, Path],
    author: str,
    include_merges: bool = False,
    max_commits: Optional[int] = None,
    ) -> str:
    """
    Extract detailed, per-file commit data (metadata + diff) 
    for all commits by `author` across all branches.
    Returns a JSON string.

    Notes:
    - Data is granular, with a list of files for each commit.
    - Binary files (images, PDFs, videos, etc.) are automatically skipped
    - Merge commits are skipped by default.
    - Use max_commits to cap output size on large repos.
    """
    try:
        repo = get_repo(path)  # uses existing helper to get Repo object
    except Exception:
        return json.dumps([], indent =2)  # on error, return empty list
    seen = set()
    out = []
    errors = []

    # Iterate over all commits in the repo
    for commit in repo.iter_commits(rev="--all"):
        
        #if we've already processed this commit, skip it
        if commit.hexsha in seen:
            continue
        seen.add(commit.hexsha)

        #only process commits by the specified author
        if not author_matches(commit, author):  
            continue
        #prevents double counting merges unless specified
        is_merge = len(commit.parents) > 1
        if is_merge and not include_merges:
            continue


        # --- START NEW PER-FILE LOGIC ---
        try:
            parent = commit.parents[0] if commit.parents else NULL_TREE
            diffs = commit.diff(parent, create_patch=True) 
            
            files_changed_data = []
            for d in diffs:
                 # Skip binary files - only process code/text files
                if not is_code_file(d): 
                    continue
                status = "A" if d.new_file else "D" if d.deleted_file else "R" if d.renamed_file else "M"

                patch_text = getattr(d, "diff", b"")
                try:
                    patch = patch_text.decode("utf-8", errors="replace")
                except Exception:
                    patch = "/* Could not decode patch text */"

                files_changed_data.append({
                    "status": status,
                    "path_before": d.a_path,
                    "path_after": d.b_path,
                    "patch": patch, 
                    "size_after": getattr(getattr(d, 'b_blob', None), 'size', None),
                })
            # --- END NEW PER-FILE LOGIC ---
        # Handle potential Git command errors by adding to dictionary
        except GitCommandError as e:
            errors.append({
                "commit_hash": commit.hexsha,
                "author_name": getattr(commit.author, "name", "") or "",
                "author_email": getattr(commit.author, "email", "") or "",
                "committed_datetime": commit.committed_datetime.isoformat(),
                "message_summary": commit.summary,
                "error": str(e)
            })
            continue
        if not files_changed_data:
            continue

        out.append({
            "hash": commit.hexsha,
            "author_name": getattr(commit.author, "name", "") or "",
            "author_email": getattr(commit.author, "email", "") or "",
            "authored_datetime": commit.authored_datetime.isoformat(),
            "committed_datetime": commit.committed_datetime.isoformat(),
            "message_summary": commit.summary,
            "message_full": commit.message,
            "is_merge": is_merge,
            "files": files_changed_data 
        })
        
        # --- CRITICAL LIMITING LOGIC ---
        if max_commits is not None and len(out) >= max_commits:
            break

    return json.dumps(out, indent=2)

def is_code_file(diff_object) -> bool:
    """
    Determines if a diff object represents a code/text file.
    Returns False for binary, vendor, or very large files.
    
    Args:
        diff_object: A GitPython diff object
        
    Returns:
        bool: True if the file is a code/text file, False if binary or non-code
    """
    # --- 1. Get file path ---
    path_str = diff_object.b_path or diff_object.a_path
    if not path_str:
        return False  # No valid path
    
    # Normalize slashes for cross-platform consistency
    norm_path = path_str.replace("\\", "/")

    # --- 2. Skip vendor/build/system folders early ---
    if any(skip in norm_path for skip in SKIP_DIRS):
        return False

    # --- 3. Check file extension blacklist ---
    _, extension = os.path.splitext(path_str)
    if extension.lower() in BINARY_EXTENSIONS:
        return False

    # --- 4. Size-based skip ---
    blob = diff_object.b_blob or diff_object.a_blob
    if blob and getattr(blob, "size", 0) > 2_000_000:  # 2 MB size limit
        return False  # Too large to be meaningful source code

    # --- 5. Optional NUL-byte sniff for unknown extensions ---
    if not extension or extension.lower() not in BINARY_EXTENSIONS:
        try:
            if blob:
                # Read only first 2 KB for efficiency
                data = blob.data_stream.read(2048)
                if b"\x00" in data:  # NUL byte → binary
                    return False
        except Exception:
            return False  # Safe fallback

    return True