from git import InvalidGitRepositoryError, NoSuchPathError, Repo, GitCommandError
from pathlib import Path
from typing import Tuple, Union, Dict
from datetime import datetime
import os, json, re, requests
from typing import Optional


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
    Assumes that only code/text files are provided - there will be different function that checks for code files only.
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
                #  # Skip binary files - only process code/text files
                # if not is_code_file(d): 
                #     continue
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
        # TODO: Consider informing the user about errors via logging or return value
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

_ALLOWED_EXTS_FOR_README = {"", ".md", ".rst", ".txt", ".markdown", ".adoc", ".org"}

def extract_all_readmes(path: Union[str, Path]) -> Dict[str, str]:
    """
    Finds files that start with readme anywhere in repo, skips binary-looking blobs,
    caps read size, and decodes as UTF-8 (replace on errors).
    """
    readmes: Dict[str, str] = {}
    max_bytes = 2_000_000  # 2MB limit

    try:
        repo = get_repo(path)
        if not repo.head.is_valid():
            return readmes

        for item in repo.head.commit.tree.traverse():
            if item.type != "blob":
                continue

            name_lower = item.name.lower()
            if not name_lower.startswith("readme"):
                continue

            # Proper extension check
            ext = Path(name_lower).suffix  # "" if no extension
            if ext not in _ALLOWED_EXTS_FOR_README:
                continue

            try:
                stream = item.data_stream
                head = stream.read(4096)
                if _is_binary_heuristic(head):  
                    continue

                # Clamp to avoid over-read if head already exceeded max_bytes
                remaining_budget = max(0, max_bytes - len(head))
                rest = stream.read(remaining_budget)
                data = head + rest

                text = data.decode("utf-8", errors="replace")
                readmes[item.path] = text  # repo-relative path
            except Exception:
                continue

        return readmes

    except Exception:
        return readmes
    
def _is_binary_heuristic(sample: bytes) -> bool:
    """
    Heuristically detects if a file is binary.

    The check follows two simple rules:
      1. If the sample contains any NUL byte (`b'\\x00'`), it's considered binary.
      2. Otherwise, count printable ASCII and whitespace characters 
         (tab, newline, carriage return). If fewer than ~85% of bytes are printable, 
         it's likely binary.

    This lightweight heuristic reliably filters out images, PDFs, and other 
    non-text blobs while keeping normal text and Markdown files.
    """
    if not sample:
        return False
    if b"\x00" in sample:
        return True
    textish = sum(c in (9, 10, 13) or 32 <= c <= 126 for c in sample)
    ratio = textish / len(sample)
    return ratio < 0.85

GITHUB_API_URL = "https://api.github.com"

# --- Helper to parse remote URL (NEW) ---
def _parse_remote_url(repo) -> Optional[Tuple[str, str]]:
    """
    Parses the repository owner and name from the 'origin' remote URL.
    Returns (owner, repo_name) or None if parsing fails or not a GitHub repo.
    """
    try:
        # Get the URL for the 'origin' remote
        url = repo.remotes.origin.url
    except AttributeError:
        # No 'origin' remote found
        return None

    # Regex to capture owner and repo name from common GitHub URL formats (HTTPS or SSH)
    match = re.search(r'(?:github\.com[/:])([a-zA-Z0-9_-]+)/([a-zA-Z0-9_.-]+?)(\.git)?$', url)

    if match:
        owner, repo_name = match.groups()[0], match.groups()[1]
        return owner, repo_name
    
    return None

# --- Helper for API calls (NEW) ---
def _make_github_api_request(url: str, token: str) -> Optional[dict]:
    """Handles GitHub API GET requests with authentication and basic error checking."""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"GitHub API Error for {url}: {e}")
        return None
    
def _fetch_all_search_results(url: str, token: str) -> int:
    """
    Fetches the total_count from the GitHub Search API, handling pagination 
    up to a reasonable limit if needed, but primarily relying on total_count.
    The GitHub Search API returns the total_count directly, making this efficient.
    """
    # GitHub Search API total_count is often accurate, we rely on it.
    data = _make_github_api_request(url, token)
    return data.get('total_count', 0) if data else 0

def extract_pull_request_metrics(
    path: Union[str, Path], 
    author: str, 
    github_token: str
) -> Dict[str, int]:
    """
    Calculates the number of Pull Requests merged and reviewed by an author 
    by querying the GitHub Search API for maximum efficiency.
    """
    # 1. Setup and Remote Info Retrieval
    # Assumes 'get_repo' is available in the scope
    repo = get_repo(path) 
    remote_info = _parse_remote_url(repo)
    
    if not remote_info:
        # print("Could not parse remote URL or repository is not hosted on GitHub.")
        return {"prs_merged": 0, "prs_reviewed": 0}
        
    owner, repo_name = remote_info
    
    # --- PRs Merged (Authored Contributions) ---
    # Metric 1: Count of PRs authored by user that were merged.
    # Uses the single, efficient Search API call.
    merged_search_query = f"repo:{owner}/{repo_name} is:pr is:merged author:{author}"
    merged_url = f"{GITHUB_API_URL}/search/issues?q={merged_search_query}"
    
    prs_merged = _fetch_all_search_results(merged_url, github_token)

    # --- PRs Reviewed (Collaborative Contributions) ---
    # Metric 2: Count of unique PRs reviewed by the user.
    # GitHub's 'reviewed-by' operator automatically handles uniqueness and review status.
    reviewed_search_query = f"repo:{owner}/{repo_name} is:pr reviewed-by:{author}"
    reviewed_url = f"{GITHUB_API_URL}/search/issues?q={reviewed_search_query}"
    
    prs_reviewed = _fetch_all_search_results(reviewed_url, github_token)
            
    return {
        "prs_merged": prs_merged, 
        "prs_reviewed": prs_reviewed
    }