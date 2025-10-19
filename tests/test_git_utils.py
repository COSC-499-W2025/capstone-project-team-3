from app.utils.git_utils import (detect_git,
    get_repo,
    extract_all_commits,
    extract_commit_hash,
    extract_commit_message,
    extract_commit_authored_datetime,
    extract_commit_datetime,
    extract_commit_author)
from git import Repo
from pathlib import Path
import time


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

def test_get_repo_valid_repo(tmp_path):
    """
    Ensures get_repo successfully returns a Repo object when given a valid Git repository path.
    """
    create_test_repo(tmp_path)
    loaded_repo = get_repo(tmp_path)
    assert isinstance(loaded_repo, Repo)

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

def test_extract_commit_hash(tmp_path):
    """
    Ensures that extract_commit_hash returns a list of commit hashes in string format.
    """
    create_test_repo(tmp_path)
    hashes = extract_commit_hash(tmp_path)
    assert len(hashes) == 2
    assert all(isinstance(h, str) for h in hashes)

def test_extract_commit_message(tmp_path):
    """
    Verifies that extract_commit_message returns all commit messages in order.
    """
    create_test_repo(tmp_path)
    messages = extract_commit_message(tmp_path)
    assert messages[0].strip() == "Second commit"
    assert messages[1].strip() == "Initial commit"

def test_extract_commit_authored_datetime(tmp_path):
    """
    Ensures that extract_commit_authored_datetime returns commit authored timestamps
    in the expected string format: 'YYYY-MM-DD HH:MM:SS'.
    """
    create_test_repo(tmp_path)
    datetimes = extract_commit_authored_datetime(tmp_path)
    assert len(datetimes) == 2
    assert all(isinstance(dt, str) for dt in datetimes)
    assert all(len(dt) == 19 for dt in datetimes)

def test_extract_commit_datetime(tmp_path):
    """
    Ensures that extract_commit_datetime returns committed timestamps
    in the expected string format: 'YYYY-MM-DD HH:MM:SS'.
    """
    create_test_repo(tmp_path)
    datetimes = extract_commit_datetime(tmp_path)
    assert len(datetimes) == 2
    assert all(isinstance(dt, str) for dt in datetimes)
    assert all(len(dt) == 19 for dt in datetimes)

def test_extract_commit_author(tmp_path):
    """
    Verifies that extract_commit_author returns a list of author names for each commit.
    """
    create_test_repo(tmp_path)
    authors = extract_commit_author(tmp_path)
    assert len(authors) == 2
    assert all(author == "Test User" for author in authors)
