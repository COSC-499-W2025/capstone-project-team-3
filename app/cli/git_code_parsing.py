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
from pathlib import Path
from typing import List, Optional
from app.utils.git_utils import extract_code_commit_content_by_author, is_collaborative
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

def _get_preferred_author_email() -> Optional[str]:
    """
    Fetch the most recent user email from USER_PREFERENCES.

    We use this email to match commit authors:
    - commit.author.email == this email
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT email
            FROM USER_PREFERENCES
            ORDER BY updated_at DESC
            LIMIT 1
            """
        )
        row = cur.fetchone()
    finally:
        conn.close()

    if not row:
        return None

    email = (row[0] or "").strip()
    return email or None

def run_git_parsing_from_files(
    file_paths: List[str],
    include_merges: bool = False,
    max_commits: Optional[int] = None,
) -> str:
    """
    Core function to call from main.py for Git-based analysis.

    Args:
        file_paths: List of file paths inside the project.
        include_merges: Whether to include merge commits when extracting history.
        max_commits: Optional cap on number of commits to return.

    Returns:
        JSON string produced by extract_code_commit_content_by_author()
    """

    # 1) Pick one representative path inside the project.
    project_file = _get_first_existing_path(file_paths)
    repo_root = project_file.parent

    # 2) Fetch the preferred author email from the DB
    author_email = _get_preferred_author_email()
    print(f"[git-analysis] Using author email from USER_PREFERENCES: '{author_email}'")

    if not author_email:
        print(
            "[git-analysis] No user email found in USER_PREFERENCES. "
            "Skipping Git analysis."
        )
        return "[]"

    # 3) Check if repository is collaborative (for logging only)
    try:
        collaborative = is_collaborative(project_file)
        if collaborative:
            print("[git-analysis] This is a COLLABORATIVE project (multiple authors detected).")
        else:
            print("[git-analysis] This is a SOLO project (only one author detected).")
    except Exception as e:
        print(f"[git-analysis] Could not determine collaboration status: {e}")

    # 4) Call commit extraction filtered by this author
    json_output = extract_code_commit_content_by_author(
        path=project_file,
        author=author_email,          \
        include_merges=include_merges,
        max_commits=max_commits,
    )

    return json_output