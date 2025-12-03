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

import argparse
import json
from pathlib import Path
from typing import List, Optional

from app.utils.git_utils import extract_code_commit_content_by_author
from app.utils.non_code_analysis.non_code_file_checker import get_git_user_identity


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


def run_git_analysis_from_files(
    file_paths: List[str],
    include_merges: bool = False,
    max_commits: Optional[int] = None,
) -> str:
    """
    Core function you can call from main.py 

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

    # 2) Retrieve Git user identity (email from .git/config)
    user_identity = get_git_user_identity(repo_root)
    git_email = user_identity.get("email", "").strip()
    
    print(f"[git-analysis] Using git author email: '{git_email}'")
    
    if not git_email:
        print("[git-analysis] Could not determine git user email. Skipping Git analysis.")
        return "[]"

    print(f"[git-analysis] Using git author email: '{git_email}'")


    # 3) Call the existing git_utils function to extract commit data.
    json_output = extract_code_commit_content_by_author(
        path=project_file,
        author=git_email,
        include_merges=include_merges,
        max_commits=max_commits,
    )

    return json_output
