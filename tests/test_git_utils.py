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
    extract_branches_for_author
    ,is_collaborative,
    extract_code_commit_content_by_author,
    extract_all_readmes,
    extract_pull_request_metrics,
    is_code_file)
from git import Repo, Actor
from pathlib import Path
import time, json, pytest, os
from unittest.mock import MagicMock, patch

import app.utils.git_utils as git_utils


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
    
def create_collaborative_repo(tmp_path: Path) -> Repo:
    """
    Helper to initialize a repo and make commits from two different authors.
    """
    repo = Repo.init(tmp_path)
    file_path = tmp_path / "test_file.txt"

    # Define Actors
    author1 = Actor("Test User", "test@example.com")
    author2 = Actor("Collaborator", "collab@example.com")

    # Author 1's commit
    file_path.write_text("First commit content")
    repo.index.add([str(file_path)])
    repo.index.commit("Initial commit by Test User", author=author1)

    time.sleep(1) 

    # Author 2's commit
    file_path.write_text("Second commit content by Collaborator")
    repo.index.add([str(file_path)])
    repo.index.commit("Second commit by Collaborator", author=author2)

    return repo

def test_is_collaborative_with_multiple_authors(tmp_path):
    """
    Ensures is_collaborative returns True for a repo with commits from 
    more than one unique author.
    """
    create_collaborative_repo(tmp_path)
    assert is_collaborative(tmp_path) is True

def test_is_collaborative_with_single_author(tmp_path):
    """
    Ensures is_collaborative returns False for a repo with multiple commits
    from only one author.
    """
    # create_test_repo makes two commits from the *same* "Test User"
    create_test_repo(tmp_path)
    assert is_collaborative(tmp_path) is False

def test_is_collaborative_with_empty_repo(tmp_path):
    """
    Ensures is_collaborative returns False for an empty repo (no commits).
    This also tests the error handling path (ValueError/GitCommandError).
    """
    Repo.init(tmp_path)
    assert is_collaborative(tmp_path) is False

def test_is_collaborative_with_non_repo(tmp_path):
    """
    Ensures is_collaborative returns False for a path that isn't a git repo.
    This tests the error handling path (ValueError from get_repo).
    """
    # tmp_path is just an empty directory
    assert is_collaborative(tmp_path) is False
    
#test for extract_code_commit_content_by_author
    
    # Helper to make fake commits
def make_commit(hexsha, author_name, author_email, message, is_merge=False, files=None):
    commit = MagicMock()
    commit.hexsha = hexsha
    commit.author.name = author_name
    commit.author.email = author_email
    commit.authored_datetime.isoformat.return_value = "2024-10-01T00:00:00"
    commit.committed_datetime.isoformat.return_value = "2024-10-01T00:00:01"
    commit.summary = message
    commit.message = message
    commit.parents = [1, 2] if is_merge else [1]
    # simulate commit.diff
    diff_mock = MagicMock()
    diff_mock.a_path = "src/app.py"
    diff_mock.b_path = "src/app.py"
    diff_mock.b_blob.size = 100
    diff_mock.diff = b""
    diff_mock.change_type = "M"
    commit.diff.return_value = files or [diff_mock]
    return commit

@patch("app.utils.git_utils.get_repo")
def test_basic_extraction(mock_get_repo):
    # Arrange
    mock_repo = MagicMock()
    commit1 = make_commit("abc123", "Alice", "alice@example.com", "Initial commit")
    mock_repo.iter_commits.return_value = [commit1]
    mock_get_repo.return_value = mock_repo

    # Act
    result_json = extract_code_commit_content_by_author("/fake/path", "alice@example.com")

    # Assert
    data = json.loads(result_json)
    assert isinstance(data, list)
    assert data[0]["author_email"] == "alice@example.com"
    assert "files" in data[0]

@patch("app.utils.git_utils.get_repo")
def test_skips_other_authors(mock_get_repo):
    mock_repo = MagicMock()
    commit = make_commit("def456", "Bob", "bob@example.com", "Bob’s commit")
    mock_repo.iter_commits.return_value = [commit]
    mock_get_repo.return_value = mock_repo

    result_json = extract_code_commit_content_by_author("/fake", "alice@example.com")
    data = json.loads(result_json)
    assert data == []  # filtered out by author

@patch("app.utils.git_utils.get_repo")
def test_skips_merges_when_flag_false(mock_get_repo):
    mock_repo = MagicMock()
    merge_commit = make_commit("xyz789", "Alice", "alice@example.com", "Merge branch", is_merge=True)
    mock_repo.iter_commits.return_value = [merge_commit]
    mock_get_repo.return_value = mock_repo

    result_json = extract_code_commit_content_by_author("/fake", "alice@example.com", include_merges=False)
    assert json.loads(result_json) == []  # merge skipped

@patch("app.utils.git_utils.get_repo")
def test_skips_non_code_files(mock_get_repo):
    mock_repo = MagicMock()
    commit = make_commit("ghi789", "Alice", "alice@example.com", "Binary file change")
    mock_repo.iter_commits.return_value = [commit]
    mock_get_repo.return_value = mock_repo

    result_json = extract_code_commit_content_by_author("/fake", "alice@example.com")
    data = json.loads(result_json)
    assert all(not f["path_after"].endswith(".png") for c in data for f in c.get("files", []))

@patch("app.utils.git_utils.get_repo", side_effect=ValueError("Invalid repo"))
def test_invalid_repo_returns_empty_list(mock_get_repo):
    result_json = extract_code_commit_content_by_author("/invalid", "alice@example.com")
    data = json.loads(result_json)
    assert data == [] 
    

# --- Tests for extract_all_readmes() ---

def test_extracts_root_readme_md(tmp_path):
    """Should find a README.md in the repo root."""

    repo = Repo.init(tmp_path)
    readme_path = tmp_path / "README.md"

    readme_path.write_text("# Hello World\nThis is a test README.")
    repo.index.add(["README.md"])
    repo.index.commit("Add README.md")

    result = extract_all_readmes(tmp_path)
    assert "README.md" in result
    assert "Hello World" in result["README.md"]

def test_extracts_nested_readmes(tmp_path):
    """Should find READMEs in subdirectories."""

    repo = Repo.init(tmp_path)
    os.makedirs(tmp_path / "docs")
    (tmp_path / "docs" / "README.txt").write_text("Docs readme content.")
    repo.index.add(["docs/README.txt"])
    repo.index.commit("Add docs README")

    result = extract_all_readmes(tmp_path)
    assert "docs/README.txt" in result
    assert "Docs readme" in result["docs/README.txt"]

def test_ignores_non_readme_files(tmp_path):
    """Should ignore files not starting with README."""

    repo = Repo.init(tmp_path)
    (tmp_path / "NOT_README.md").write_text("Should not be read.")
    repo.index.add(["NOT_README.md"])
    repo.index.commit("Add non-readme")

    result = extract_all_readmes(tmp_path)
    assert result == {}  # no files found

def test_skips_binary_files(tmp_path):
    """Should skip files that look binary (contain null bytes)."""

    repo = Repo.init(tmp_path)
    binary_data = b"\x00\x01\x02Hello"

    (tmp_path / "README.md").write_bytes(binary_data)
    repo.index.add(["README.md"])
    repo.index.commit("Add binary README")

    result = extract_all_readmes(tmp_path)
    assert result == {}  # binary skipped

def test_skips_unreadable_files(tmp_path):
    """Files with NUL bytes are treated as binary and skipped."""
    from git import Repo
    repo = Repo.init(tmp_path)

    (tmp_path / "README.md").write_bytes(b"\xff\xfe\x00\x00SomeText")  # contains NULs
    repo.index.add(["README.md"])
    repo.index.commit("Add unreadable README")

    result = extract_all_readmes(tmp_path)
    assert result == {}

def test_multiple_readmes_found(tmp_path):
    """Should handle multiple READMEs across the repo."""

    repo = Repo.init(tmp_path)
    (tmp_path / "README.md").write_text("Main readme")
    os.makedirs(tmp_path / "docs")
    (tmp_path / "docs" / "README.rst").write_text("Docs readme")
    repo.index.add(["README.md", "docs/README.rst"])
    repo.index.commit("Add multiple readmes")

    result = extract_all_readmes(tmp_path)
    assert len(result) == 2

    assert "README.md" in result
    assert "docs/README.rst" in result

def test_empty_repo_returns_empty_dict(tmp_path):
    """Should return empty dict for empty repo."""

    repo = Repo.init(tmp_path)
    result = extract_all_readmes(tmp_path)
    assert result == {}

def test_large_readme_respects_max_size(tmp_path):
    """Should cap reading at ~2MB and not crash on large files."""
    repo = Repo.init(tmp_path)

    large_text = "A" * (2_500_000)  # 2.5 MB of text
    (tmp_path / "README.md").write_text(large_text)
    repo.index.add(["README.md"])
    repo.index.commit("Add large README")

    result = extract_all_readmes(tmp_path)

    assert "README.md" in result
    content = result["README.md"]

    # Should be truncated to the configured limit (2MB)
    assert len(content.encode("utf-8")) <= 2_000_000
    # Content should look correct (still valid text, not binary)
    assert all(ch == "A" for ch in content[:1000])
    
@patch("app.utils.git_utils._fetch_all_search_results")
@patch("app.utils.git_utils._parse_remote_url")
@patch("app.utils.git_utils.get_repo")
def test_extract_pull_request_metrics_success(
    mock_get_repo, 
    mock_parse_remote_url, 
    mock_fetch_results):
    """
    Tests successful calculation by mocking the external Git and API calls.
    Verifies the final dictionary structure and the correct arguments for API calls.
    """
    # 1. Arrange the mocks
    
    # Mock GitRepo and Owner Info
    mock_get_repo.return_value = MagicMock() # Return a fake repo object
    MOCK_OWNER = "MockOrg"
    MOCK_REPO = "mock-project"
    MOCK_AUTHOR = "testuser"
    MOCK_TOKEN = "fake_pat_123"
    mock_parse_remote_url.return_value = (MOCK_OWNER, MOCK_REPO)

    # Mock API responses (The core of the test!)
    # Mock the count for merged PRs
    MOCK_MERGED_COUNT = 15
    # Mock the count for reviewed PRs
    MOCK_REVIEWED_COUNT = 42

    # Configure the mock to return different values based on the URL (merged vs reviewed)
    def side_effect_fetch_results(url, token):
        # 1. Verify the token is passed correctly
        assert token == MOCK_TOKEN
        
        # 2. Return the mocked count based on the URL query
        if "is:merged" in url:
            assert f"repo:{MOCK_OWNER}/{MOCK_REPO}" in url
            assert f"author:{MOCK_AUTHOR}" in url
            return MOCK_MERGED_COUNT
        elif "reviewed-by" in url:
            assert f"repo:{MOCK_OWNER}/{MOCK_REPO}" in url
            assert f"reviewed-by:{MOCK_AUTHOR}" in url
            return MOCK_REVIEWED_COUNT
        return 0 # Should not happen

    mock_fetch_results.side_effect = side_effect_fetch_results

    # 2. Act
    result = extract_pull_request_metrics(
        path="/fake/path",
        author=MOCK_AUTHOR,
        github_token=MOCK_TOKEN
    )

    # 3. Assert
    # Verify the final returned metrics
    assert result == {
        "prs_merged": MOCK_MERGED_COUNT,
        "prs_reviewed": MOCK_REVIEWED_COUNT
    }
    
    # Verify that the two search functions were called exactly twice (once for merged, once for reviewed)
    assert mock_fetch_results.call_count == 2
    
@patch("app.utils.git_utils._fetch_all_search_results")
@patch("app.utils.git_utils._parse_remote_url")
@patch("app.utils.git_utils.get_repo")
def test_extract_pull_request_metrics_no_remote_info(
    mock_get_repo, 
    mock_parse_remote_url, 
    mock_fetch_results):
    """
    Tests the fallback case when the remote URL cannot be parsed (e.g., not a GitHub repo 
    or no 'origin' remote).
    """
    # Arrange
    mock_get_repo.return_value = MagicMock()
    # Simulate failed parsing (no GitHub remote found)
    mock_parse_remote_url.return_value = None 

    # Act
    result = extract_pull_request_metrics(
        path="/fake/path",
        author="anyuser",
        github_token="anytoken"
    )

    # Assert
    # Should return zero counts without attempting any API call
    assert result == {"prs_merged": 0, "prs_reviewed": 0}
    assert mock_fetch_results.call_count == 0
    
@patch("app.utils.git_utils._fetch_all_search_results")
@patch("app.utils.git_utils._parse_remote_url")
@patch("app.utils.git_utils.get_repo")
def test_extract_pull_request_metrics_zero_contributions(
    mock_get_repo, 
    mock_parse_remote_url, 
    mock_fetch_results):
    """
    Tests the case where the user has no contributions (API returns 0 for both metrics).
    """
    # Arrange
    mock_get_repo.return_value = MagicMock()
    mock_parse_remote_url.return_value = ("TestOwner", "TestRepo")

    # Simulate both API calls returning 0 total_count
    mock_fetch_results.return_value = 0

    # Act
    result = extract_pull_request_metrics(
        path="/fake/path",
        author="unknownuser",
        github_token="validtoken"
    )

    # Assert
    assert result == {"prs_merged": 0, "prs_reviewed": 0}
    assert mock_fetch_results.call_count == 2
    
# --- Tests for is_code_file() ---

def make_diff_mock(
    a_path=None,
    b_path=None,
    blob_size=100,
    blob_bytes=b"print('hello')\n",
    in_vendor=False,
    binary_ext=False,
    use_b_blob=True,
    raise_on_read=False,
):
    """
    Helper to construct a diff-like mock object for is_code_file tests.
    """
    diff = MagicMock()
    diff.a_path = a_path
    diff.b_path = b_path

    # Configure blob
    blob = MagicMock()
    blob.size = blob_size

    if raise_on_read:
        blob.data_stream.read.side_effect = Exception("read error")
    else:
        blob.data_stream.read.return_value = blob_bytes

    # Attach blob either to a_blob or b_blob, or both
    if use_b_blob:
        diff.b_blob = blob
        diff.a_blob = None
    else:
        diff.a_blob = blob
        diff.b_blob = None

    return diff


def test_is_code_file_text_file_returns_true():
    """
    A normal small text/code file (.py) outside vendor/build dirs should be classified as code.
    """
    diff = make_diff_mock(
        b_path="src/app.py",
        blob_size=123,
        blob_bytes=b"def foo():\n    return 42\n",
    )

    assert is_code_file(diff) is True


def test_is_code_file_skips_binary_extension():
    """
    Files with a known binary extension (.png) should return False, regardless of content.
    """
    diff = make_diff_mock(
        b_path="images/logo.png",
        blob_size=500,
        blob_bytes=b"\x89PNG\r\n\x1a\n",  # typical PNG header
    )

    assert is_code_file(diff) is False


def test_is_code_file_skips_vendor_directories():
    """
    Files inside vendor/build/system folders (e.g., node_modules) should be skipped.
    """
    diff = make_diff_mock(
        b_path="node_modules/library/index.js",
        blob_size=200,
        blob_bytes=b"module.exports = {};",
    )

    assert is_code_file(diff) is False


def test_is_code_file_skips_large_files_by_size():
    """
    Files larger than the 2MB threshold should be treated as non-code (False),
    and the content should not need to be read.
    """
    diff = make_diff_mock(
        b_path="src/huge_file.py",
        blob_size=2_500_000,  # > 2MB
        blob_bytes=b"A" * 1024,  # should not matter
    )

    result = is_code_file(diff)
    assert result is False

    # Ensure we didn't need to inspect contents (optional but nice to assert)
    blob = diff.b_blob or diff.a_blob
    blob.data_stream.read.assert_not_called()


def test_is_code_file_detects_binary_via_nul_bytes_for_unknown_extension():
    """
    For files with non-blacklisted extensions, NUL bytes in the first chunk
    should cause classification as non-code.
    """
    diff = make_diff_mock(
        b_path="data/custom.txt",  # .txt is NOT in BINARY_EXTENSIONS
        blob_size=256,
        blob_bytes=b"hello\x00world",  # contains NUL
    )

    assert is_code_file(diff) is False


def test_is_code_file_allows_text_with_unknown_extension():
    """
    For files with non-binary extensions and no NUL bytes, we should treat them as code/text.
    """
    diff = make_diff_mock(
        b_path="data/custom.txt",
        blob_size=256,
        blob_bytes=b"just some plain text\nwith multiple lines\n",
    )

    assert is_code_file(diff) is True


def test_is_code_file_handles_missing_blob_gracefully():
    """
    If no blob is available (e.g., edge cases in diff), but the extension looks like code,
    the function should still return True (treated as text/code by extension alone).
    """
    diff = MagicMock()
    diff.a_path = None
    diff.b_path = "src/app.py"
    diff.a_blob = None
    diff.b_blob = None  # no blob

    assert is_code_file(diff) is True


def test_is_code_file_handles_read_exception_as_non_code():
    """
    If reading blob contents raises an exception, is_code_file should fail safely
    and classify the file as non-code (False).
    """
    diff = make_diff_mock(
        b_path="src/suspicious.txt",
        blob_size=100,
        raise_on_read=True,
    )

    assert is_code_file(diff) is False


def test_is_code_file_uses_a_path_when_b_path_missing():
    """
    When b_path is None (e.g., deleted file), a_path should be used to determine extension.
    """
    diff = make_diff_mock(
        a_path="src/deleted.py",
        b_path=None,
        blob_size=100,
        use_b_blob=False,  # place blob on a_blob
    )

    assert is_code_file(diff) is True


def test_is_code_file_returns_false_when_no_paths():
    """
    If both a_path and b_path are missing, the function should return False.
    """
    diff = MagicMock()
    diff.a_path = None
    diff.b_path = None
    diff.a_blob = None
    diff.b_blob = None

    assert is_code_file(diff) is False