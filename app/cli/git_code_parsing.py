"""
CLI helper to analyze Git history for a project, given a list of file paths.

Flow:
1. Accept an array of file paths belonging to a single project.
2. Pick one file and use it to locate the repo.
3. Look up the Git user email from .git config.
4. Call extract_code_commit_content_by_author()
   to pull commit-level data for that author across the repo.
5. Return the JSON output (later can be stored into GIT_HISTORY, etc.).
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from app.utils.git_utils import extract_code_commit_content_by_author, get_repo, is_collaborative
from app.data.db import get_connection

def _get_first_existing_path(file_paths: List[str]) -> Path:
    """
    Return the first existing file path from the list, as a Path.
    Raises ValueError if none of the given paths exist.
    """

    for p in file_paths:
        candidate = Path(p).expanduser().resolve()
        if candidate.exists():
            return candidate
    raise ValueError("None of the provided file paths exist on disk.")

def _get_preferred_author_email() -> Tuple[Optional[str], Optional[str]]:
    #TODO: rename function to _get_preferred_github_user_and_email
    # implement when touching main to ensure function call sites are updated
    """
    Fetch the most recent GitHub username and email from USER_PREFERENCES.

    Used to match commit authors:
    - commit.author.email == email
    - commit.author.name / username == github_user
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT github_user, email
            FROM USER_PREFERENCES
            ORDER BY updated_at DESC
            LIMIT 1
            """
        )
        row = cur.fetchone()
    finally:
        conn.close()

    if not row:
        return None, None

    github_user = (row[0] or "").strip() or None
    email = (row[1] or "").strip() or None
    return github_user, email

def _group_paths_by_repo(file_paths: List[str]) -> Dict[Path, List[Path]]:
    """
    Group existing file paths by their Git repository root.
    Non-repo paths are skipped.
    """
    repo_map: Dict[Path, List[Path]] = {}
    for p in file_paths:
        candidate = Path(p).expanduser().resolve()
        if not candidate.exists():
            continue
        try:
            repo = get_repo(candidate)
        except ValueError:
            continue
        repo_root = Path(repo.working_tree_dir).resolve()
        repo_map.setdefault(repo_root, []).append(candidate)
    return repo_map

def run_git_parsing_from_files(
    file_paths: List[str],
    include_merges: bool = False,
    max_commits: Optional[int] = None,
) -> str:
    """
    Core function to call from main.py for Git-based parsing.

    Args:
        file_paths: List of file paths inside the project.
        include_merges: Whether to include merge commits when extracting history.
        max_commits: Optional cap on number of commits to return.

    Returns:
        JSON string produced by extract_code_commit_content_by_author()
    """

    # 1) Fetch the preferred github_user and author email from the DB
    github_user, author_email = _get_preferred_author_email()
    if not author_email and not github_user:
        print(
            "[git-analysis] No user email or username found in USER_PREFERENCES. "
            "Skipping Git analysis."
        )
        return "[]"
    
    author_identifiers = []
    for ident in (author_email, github_user):
        if ident and ident not in author_identifiers:
            author_identifiers.append(ident)

    selected_identifiers = author_identifiers
    
    if author_identifiers:
        print(
            "[git-analysis] Using author identifiers: "
            f"{', '.join(author_identifiers)}"
        )

    # 2) Group files by repo root to support nested repositories
    repo_map = _group_paths_by_repo(file_paths)
    if not repo_map:
        print("[git-analysis] No Git repositories detected in provided paths.")
        return "[]"

    all_commits: List[Dict] = []
    for repo_root in sorted(repo_map.keys()):
        # 3) Check if repository is collaborative (for logging only)
        try:
            collaborative = is_collaborative(repo_root, author_aliases=selected_identifiers)
            if collaborative:
                print(f"[git-analysis] COLLABORATIVE repo detected: {repo_root}")
            else:
                print(f"[git-analysis] SOLO repo detected: {repo_root}")
        except Exception as e:
            print(f"[git-analysis] Could not determine collaboration status for {repo_root}: {e}")

        # 4) Call commit extraction filtered by this author
        repo_json = extract_code_commit_content_by_author(
            path=repo_root,
            author=selected_identifiers,
            include_merges=include_merges,
            max_commits=max_commits,
        )
        try:
            repo_commits = json.loads(repo_json)
        except json.JSONDecodeError:
            repo_commits = []
        if isinstance(repo_commits, list):
            all_commits.extend(repo_commits)

    return json.dumps(all_commits, indent=2)
