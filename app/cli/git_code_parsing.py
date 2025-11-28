"""
CLI to analyze Git history for a project, given a list of file paths.

Flow:
1. Accept an array of file paths belonging to a single project.
2. Use detect_git() on one of the files to determine if the project is a Git repo.
3. Look up the user's GitHub username 
4. If both conditions are satisfied, call extract_code_commit_content_by_author()
   to pull commit-level data for that author across the repo.
5. Print the JSON output (later can be stored into GIT_HISTORY, etc.).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List, Optional

from app.utils.git_utils import detect_git, extract_code_commit_content_by_author
from app.utils.user_preference_utils import UserPreferenceStore


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


def get_latest_github_user() -> Optional[str]:
    """
    For a single-user desktop app:
    Return the most recently saved github_user from USER_PREFERENCES,
    or None if not set.
    """
    store = UserPreferenceStore()
    try:
        cur = store.conn.cursor()
        cur.execute(
            """
            SELECT github_user
            FROM USER_PREFERENCES
            ORDER BY updated_at DESC
            LIMIT 1
            """
        )
        row = cur.fetchone()
    finally:
        # Always close the connection
        store.close()

    if not row:
        return None

    github_user = row[0] or ""
    github_user = github_user.strip()
    return github_user or None

