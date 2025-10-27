from app.utils.git_utils import (detect_git,
    get_repo,
    extract_all_commits,
    extract_commit_hashes,
    extract_commit_messages,
    extract_commit_authored_datetimes,
    extract_commit_datetimes,
    extract_commit_authors,
    is_repo_empty,
    extract_files_changed,
    extract_line_changes,
    extract_contribution_by_filetype,
    extract_branches_for_author)
from git import Repo
from pathlib import Path
import time
import pytest


def test_detect_git_with_git_repo(tmp_path):
    """
    Test for when a git folder path is specified
    """
    Repo.init(tmp_path)
    assert detect_git(tmp_path) is True
    
def test_detect_git_with_folder(tmp_path):
    """
    Test for when a plain folder without git is specified
    """
    assert detect_git(tmp_path) is False
    
def create_test_repo(tmp_path: Path) -> Repo:
    """
    Helper to initialize a repo and make a couple of dummy commits.
    """
    repo = Repo.init(tmp_path)
    file_path = tmp_path / "test_file.txt"

    # Configure user (necessary for commits)
    repo.config_writer().set_value("user", "name", "Test User").release()
    repo.config_writer().set_value("user", "email", "test@example.com").release()

    # First commit
    file_path.write_text("First commit content")
    repo.index.add([str(file_path)])
    repo.index.commit("Initial commit")

    time.sleep(1)

    # Second commit
    file_path.write_text("Second commit content")
    repo.index.add([str(file_path)])
    repo.index.commit("Second commit")

    return repo

def create_test_repo_with_branches(tmp_path: Path) -> Repo:
    """
    Helper to initialize a repo, make a couple of commits, and create multiple branches.
    """
    repo = Repo.init(tmp_path)
    file_path = tmp_path / "test_file.txt"

    # Configure user (necessary for commits)
    repo.config_writer().set_value("user", "name", "Test User").release()
    repo.config_writer().set_value("user", "email", "test@example.com").release()

    # Commit 1 on main
    file_path.write_text("First commit content")
    repo.index.add([str(file_path)])
    repo.index.commit("Initial commit")

    time.sleep(1)

    # Commit 2 on main
    file_path.write_text("Second commit content\n") # overwrites counts as deletion
    repo.index.add([str(file_path)])
    repo.index.commit("Second commit")

    # Create and switch to a new branch
    new_branch = repo.create_head("feature-branch")
    repo.head.reference = new_branch
    repo.head.reset(index=True, working_tree=True)

    # Commit 3 on feature branch
    file_path.write_text("Third commit content")
    repo.index.add([str(file_path)])
    repo.index.commit("Feature commit")
    
    return repo

def test_get_repo_valid_repo(tmp_path):
    """
    Ensures get_repo successfully returns a Repo object when given a valid Git repository path.
    """
    create_test_repo(tmp_path)
    loaded_repo = get_repo(tmp_path)
    assert isinstance(loaded_repo, Repo)
    
def test_get_repo_invalid_repo(tmp_path):
    """
    Ensures get_repo successfully returns an error when given an invalid Git repository path.
    """
    with pytest.raises(ValueError, match=r"Unable to load git repo from:"):
        get_repo(tmp_path)

def test_extract_all_commits(tmp_path):
    """
    Verifies that extract_all_commits returns a complete list of commits in the repo.
    Asserts the number and order of the commits (latest first).
    """
    create_test_repo(tmp_path)
    commits = extract_all_commits(tmp_path)
    assert len(commits) == 2
    assert commits[0].message.strip() == "Second commit"
    assert commits[1].message.strip() == "Initial commit"

def test_extract_commit_hashes(tmp_path):
    """
    Ensures that extract_commit_hash returns a list of commit hashes in string format.
    """
    create_test_repo(tmp_path)
    hashes = extract_commit_hashes(tmp_path)
    assert len(hashes) == 2
    assert all(isinstance(h, str) for h in hashes)

def test_extract_commit_messages(tmp_path):
    """
    Verifies that extract_commit_message returns all commit messages in order.
    """
    create_test_repo(tmp_path)
    messages = extract_commit_messages(tmp_path)
    assert messages[0].strip() == "Second commit"
    assert messages[1].strip() == "Initial commit"

def test_extract_commit_authored_datetimes(tmp_path):
    """
    Ensures that extract_commit_authored_datetime returns commit authored timestamps
    in the expected string format: 'YYYY-MM-DD HH:MM:SS'.
    """
    create_test_repo(tmp_path)
    datetimes = extract_commit_authored_datetimes(tmp_path)
    assert len(datetimes) == 2
    assert all(isinstance(dt, str) for dt in datetimes)
    assert all(len(dt) == 19 for dt in datetimes)

def test_extract_commit_datetimes(tmp_path):
    """
    Ensures that extract_commit_datetime returns committed timestamps
    in the expected string format: 'YYYY-MM-DD HH:MM:SS'.
    """
    create_test_repo(tmp_path)
    datetimes = extract_commit_datetimes(tmp_path)
    assert len(datetimes) == 2
    assert all(isinstance(dt, str) for dt in datetimes)
    assert all(len(dt) == 19 for dt in datetimes)

def test_extract_commit_authors(tmp_path):
    """
    Verifies that extract_commit_author returns a list of author names for each commit.
    """
    create_test_repo(tmp_path)
    authors = extract_commit_authors(tmp_path)
    assert len(authors) == 2
    assert all(author == "Test User" for author in authors)
    
def test_extract_files_changed(tmp_path):
    """Verifies that extract_files_changed returns the total number of files changed by an author"""
    create_test_repo_with_branches(tmp_path)
    assert extract_files_changed(tmp_path, "Test User") == 3


def test_extract_line_changes(tmp_path):
    """Verifies that extract_line_changes returns the number of added and deleted lines by an author"""
    create_test_repo_with_branches(tmp_path)
    changes = extract_line_changes(tmp_path, "Test User")
    assert "added" in changes and "deleted" in changes
    assert changes["added"] > 0
    assert changes["deleted"] >= 0 


def test_extract_contribution_by_filetype(tmp_path):
    """Verifies that extract_contribution_by_filetype returns the number of lines added and deleted for specific filetypes by an author"""
    create_test_repo_with_branches(tmp_path)
    contributions = extract_contribution_by_filetype(tmp_path, "Test User")
    
    # Should have at least .txt in contributions
    assert ".txt" in contributions
    txt_stats = contributions[".txt"]
    assert txt_stats["files_changed"] == 3
    assert txt_stats["added"] > 0
    assert txt_stats["deleted"] >= 0


def test_extract_branches_for_author(tmp_path):
    """Verifies that branches containing commits by the author are returned"""
    create_test_repo_with_branches(tmp_path)
    branches = extract_branches_for_author(tmp_path, "Test User")
    
    # Should include both main and feature-branch
    assert "master" in branches or "main" in branches  # branch name differs depending on Git version
    assert "feature-branch" in branches 
    
def test_is_repo_empty_with_no_commits(tmp_path):
    """
    Ensures is_repo_empty returns True for a newly initialized repo (no commits).
    """
    Repo.init(tmp_path)
    assert is_repo_empty(tmp_path) is True
    
def test_is_repo_empty_with_commits(tmp_path):
    """
    Ensures is_repo_empty returns False for a repo with existing commits.
    """
    create_test_repo(tmp_path)
    assert is_repo_empty(tmp_path) is False
    
def test_is_repo_empty_with_non_repo_path(tmp_path):
    """
    Ensures is_repo_empty returns True for a path that is not a git repo 
    (handling the ValueError raised by get_repo).
    """
    # tmp_path is just a plain directory here
    assert is_repo_empty(tmp_path) is True