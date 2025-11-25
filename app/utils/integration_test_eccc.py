# tests/test_extract_code_commit_content_integration.py
import json
from pathlib import Path

import pytest
from git import Repo, Actor

from git_utils import extract_code_commit_content_by_author


def _create_repo_with_commits(base_dir: Path) -> Path:
    """
    Create a small Git repo with:
    - 2 commits by TARGET_AUTHOR
    - 1 commit by OTHER_AUTHOR
    Returns the repo path.
    """
    repo_path = base_dir / "test_repo"
    repo_path.mkdir(parents=True, exist_ok=True)

    repo = Repo.init(repo_path)

    target_author = Actor("Target Author", "target@example.com")
    other_author = Actor("Other Author", "other@example.com")

    # Commit 1 by target author
    file1 = repo_path / "file1.py"
    file1.write_text("print('v1')\n")
    repo.index.add([str(file1)])
    repo.index.commit("Initial commit by target", author=target_author, committer=target_author)

    # Commit 2 by other author
    file1.write_text("print('v2')\n")
    repo.index.add([str(file1)])
    repo.index.commit("Change by other author", author=other_author, committer=other_author)

    # Commit 3 by target author, new file
    file2 = repo_path / "file2.py"
    file2.write_text("x = 1\n")
    repo.index.add([str(file2)])
    repo.index.commit("Second commit by target", author=target_author, committer=target_author)

    return repo_path


@pytest.mark.integration
def test_extract_code_commit_content_by_author_filters_and_shapes_correctly(tmp_path):
    repo_path = _create_repo_with_commits(tmp_path)

    # Call your function under test
    json_output = extract_code_commit_content_by_author(
        path=repo_path,
        author="Target Author",   # this should match commit.author.name
        max_commits=None,
    )

    # 1. JSON should be valid and a list
    data = json.loads(json_output)
    assert isinstance(data, list), "Expected a list of commit records"

    # We know we created 2 commits by Target Author, so we expect 2 results.
    # (If your implementation walks all branches differently, you can relax this.)
    assert len(data) == 2, f"Expected 2 commits for Target Author, got {len(data)}"

    for commit in data:
        # 2. Author info should match Target Author (or at least include it)
        assert "author_name" in commit
        assert commit["author_name"] == "Target Author"

        # 3. Required commit fields present
        assert "hash" in commit
        assert "authored_datetime" in commit
        assert "committed_datetime" in commit
        assert "message_summary" in commit
        assert "files" in commit
        assert isinstance(commit["files"], list)
        assert commit["files"], "Each commit should report at least one changed file"

        # 4. Basic file entry checks
        for f in commit["files"]:
            assert "status" in f
            assert f["status"] in {"A", "M", "D", "R"}
            # At least one of path_before/path_after should exist
            assert f.get("path_before") is not None or f.get("path_after") is not None
            assert "patch" in f


@pytest.mark.integration
def test_extract_code_commit_content_by_author_empty_repo_returns_empty_list(tmp_path):
    # Create an empty repo (no commits)
    repo_path = tmp_path / "empty_repo"
    repo_path.mkdir()
    Repo.init(repo_path)

    json_output = extract_code_commit_content_by_author(
        path=repo_path,
        author="Someone",
        max_commits=None,
    )

    data = json.loads(json_output)
    assert data == [], "Empty repo should return an empty list"
