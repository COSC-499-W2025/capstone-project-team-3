import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from app.cli.git_code_parsing import run_git_parsing_from_files
import app.cli.git_code_parsing as git_code_parsing


def test_run_git_parsing_returns_empty_when_no_user_email(tmp_path, monkeypatch):
    """run_git_parsing_from_files should return '[]' if USER_PREFERENCES has no email."""

    # Import the real module + function from cli
    import app.cli.git_code_parsing as git_code_parsing
    from app.cli.git_code_parsing import run_git_parsing_from_files

    project_file = tmp_path / "dummy.py"
    project_file.write_text("print('hello')")

    class DummyCursor:
        def execute(self, *args, **kwargs):
            return None

        def fetchone(self):
            return None  # No email row

    class DummyConn:
        def cursor(self):
            return DummyCursor()

        def close(self):
            pass

    # Patch get_connection on the actual module object
    monkeypatch.setattr(git_code_parsing, "get_connection", lambda: DummyConn())

    result = run_git_parsing_from_files(
        file_paths=[str(project_file)],
        include_merges=False,
        max_commits=10,
    )

    assert result == "[]"


def test_run_git_parsing_uses_email_and_calls_extraction(tmp_path, monkeypatch):
    """
    When USER_PREFERENCES has an email, run_git_parsing_from_files:
    - uses that email as the author filter
    - calls extract_code_commit_content_by_author
    - returns its JSON result.
    """
    # Import the real module + function from cli
    import app.cli.git_code_parsing as git_code_parsing
    from app.cli.git_code_parsing import run_git_parsing_from_files

    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    project_file = repo_root / "dummy.py"
    project_file.write_text("print('hello')")

    # --- Mock DB to return an email row ---
    class DummyCursor:
        def __init__(self):
            self._row = ("testuser", "testuser@example.com",)

        def execute(self, *args, **kwargs):
            return None

        def fetchone(self):
            return self._row

    class DummyConn:
        def cursor(self):
            return DummyCursor()

        def close(self):
            pass

    # Patch DB connection used inside the helper
    monkeypatch.setattr(git_code_parsing, "get_connection", lambda: DummyConn())

    # --- Patch git_utils functions used in the helper ---
    monkeypatch.setattr(
        git_code_parsing, "_group_paths_by_repo", lambda paths: {repo_root: [project_file]}
    )

    with patch("app.cli.git_code_parsing.is_collaborative", return_value=True) as mock_collab, \
         patch("app.cli.git_code_parsing.extract_code_commit_content_by_author") as mock_extract:

        # Fake JSON returned by extract_code_commit_content_by_author
        mock_extract.return_value = '[{"hash": "abc"}]'

        result = run_git_parsing_from_files(
            file_paths=[str(project_file)],
            include_merges=False,
            max_commits=10,
        )

        # We return a JSON list aggregated from repos
        assert json.loads(result) == [{"hash": "abc"}]

        # is_collaborative called with the repo root path
        mock_collab.assert_called_once_with(repo_root)

        # extract_code_commit_content_by_author called with the correct args
        mock_extract.assert_called_once_with(
            path=repo_root,
            author="testuser",
            include_merges=False,
            max_commits=10,
        )
def test_run_git_parsing_no_user_prefs_skips_extraction(tmp_path, monkeypatch):
    

    project_file = tmp_path / "dummy.py"
    project_file.write_text("print('hello')")

    monkeypatch.setattr(git_code_parsing, "_get_preferred_author_email", lambda: (None, None))

    with patch("app.cli.git_code_parsing.extract_code_commit_content_by_author") as mock_extract, \
         patch("app.cli.git_code_parsing.is_collaborative") as mock_collab:
        result = run_git_parsing_from_files(
            file_paths=[str(project_file)],
            include_merges=False,
            max_commits=10,
        )

        assert result == "[]"
        mock_extract.assert_not_called()
        mock_collab.assert_not_called()


def test_run_git_parsing_uses_email_when_username_missing(tmp_path, monkeypatch, capsys):
    import app.cli.git_code_parsing as git_code_parsing
    from app.cli.git_code_parsing import run_git_parsing_from_files

    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    project_file = repo_root / "dummy.py"
    project_file.write_text("print('hello')")

    monkeypatch.setattr(git_code_parsing, "_get_preferred_author_email", lambda: (None, "testuser@example.com"))
    monkeypatch.setattr(
        git_code_parsing, "_group_paths_by_repo", lambda paths: {repo_root: [project_file]}
    )

    with patch("app.cli.git_code_parsing.is_collaborative", return_value=False) as mock_collab, \
         patch("app.cli.git_code_parsing.extract_code_commit_content_by_author") as mock_extract:
        mock_extract.return_value = '[{"hash": "abc"}]'

        result = run_git_parsing_from_files(
            file_paths=[str(project_file)],
            include_merges=False,
            max_commits=10,
        )

        assert json.loads(result) == [{"hash": "abc"}]
        mock_collab.assert_called_once_with(repo_root)
        mock_extract.assert_called_once_with(
            path=repo_root,
            author="testuser@example.com",
            include_merges=False,
            max_commits=10,
        )

        out = capsys.readouterr().out
        assert "Using author identifier (author_email): 'testuser@example.com'" in out


def test_run_git_parsing_uses_username_when_email_missing(tmp_path, monkeypatch, capsys):
    import app.cli.git_code_parsing as git_code_parsing
    from app.cli.git_code_parsing import run_git_parsing_from_files

    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    project_file = repo_root / "dummy.py"
    project_file.write_text("print('hello')")

    monkeypatch.setattr(git_code_parsing, "_get_preferred_author_email", lambda: ("testuser", None))
    monkeypatch.setattr(
        git_code_parsing, "_group_paths_by_repo", lambda paths: {repo_root: [project_file]}
    )

    with patch("app.cli.git_code_parsing.is_collaborative", return_value=False) as mock_collab, \
         patch("app.cli.git_code_parsing.extract_code_commit_content_by_author") as mock_extract:
        mock_extract.return_value = '[{"hash": "abc"}]'

        result = run_git_parsing_from_files(
            file_paths=[str(project_file)],
            include_merges=False,
            max_commits=10,
        )

        assert json.loads(result) == [{"hash": "abc"}]
        mock_collab.assert_called_once_with(repo_root)
        mock_extract.assert_called_once_with(
            path=repo_root,
            author="testuser",
            include_merges=False,
            max_commits=10,
        )

        out = capsys.readouterr().out
        assert "Using author identifier (github_user): 'testuser'" in out


def test_run_git_parsing_handles_nested_repos(tmp_path, monkeypatch):
    repo_a = tmp_path / "repo_a"
    repo_b = tmp_path / "repo_b"
    repo_a.mkdir()
    repo_b.mkdir()
    file_a = repo_a / "a.py"
    file_b = repo_b / "b.py"
    file_a.write_text("print('a')")
    file_b.write_text("print('b')")

    monkeypatch.setattr(git_code_parsing, "_get_preferred_author_email", lambda: ("testuser", None))
    monkeypatch.setattr(
        git_code_parsing,
        "_group_paths_by_repo",
        lambda paths: {repo_a: [file_a], repo_b: [file_b]},
    )

    with patch("app.cli.git_code_parsing.is_collaborative", return_value=True) as mock_collab, \
         patch("app.cli.git_code_parsing.extract_code_commit_content_by_author") as mock_extract:
        mock_extract.side_effect = ['[{"hash": "a"}]', '[{"hash": "b"}]']

        result = run_git_parsing_from_files(
            file_paths=[str(file_a), str(file_b)],
            include_merges=False,
            max_commits=10,
        )

        assert json.loads(result) == [{"hash": "a"}, {"hash": "b"}]
        assert mock_collab.call_count == 2
        assert mock_extract.call_count == 2


def test_run_git_parsing_skips_when_no_git_repos(monkeypatch):
    monkeypatch.setattr(git_code_parsing, "_get_preferred_author_email", lambda: ("testuser", None))
    monkeypatch.setattr(git_code_parsing, "_group_paths_by_repo", lambda paths: {})

    with patch("app.cli.git_code_parsing.extract_code_commit_content_by_author") as mock_extract:
        result = run_git_parsing_from_files(
            file_paths=["/nonexistent/path.py"],
            include_merges=False,
            max_commits=10,
        )

        assert result == "[]"
        mock_extract.assert_not_called()


def test_run_git_parsing_handles_invalid_extractor_json(tmp_path, monkeypatch):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    project_file = repo_root / "dummy.py"
    project_file.write_text("print('hello')")

    monkeypatch.setattr(git_code_parsing, "_get_preferred_author_email", lambda: ("testuser", None))
    monkeypatch.setattr(
        git_code_parsing, "_group_paths_by_repo", lambda paths: {repo_root: [project_file]}
    )

    with patch("app.cli.git_code_parsing.is_collaborative", return_value=False), \
         patch("app.cli.git_code_parsing.extract_code_commit_content_by_author") as mock_extract:
        mock_extract.return_value = "not-json"

        result = run_git_parsing_from_files(
            file_paths=[str(project_file)],
            include_merges=False,
            max_commits=10,
        )

        assert json.loads(result) == []


def test_run_git_parsing_skips_non_repo_then_finds_repo(tmp_path, monkeypatch):
    outside_file = tmp_path / "outside.py"
    outside_file.write_text("print('outside')")
    repo_root = tmp_path / "repo"
    nested_file = repo_root / "src" / "deep" / "file.py"
    nested_file.parent.mkdir(parents=True)
    nested_file.write_text("print('inside')")

    monkeypatch.setattr(git_code_parsing, "_get_preferred_author_email", lambda: ("testuser", None))

    class FakeRepo:
        def __init__(self, root):
            self.working_tree_dir = str(root)

    with patch("app.cli.git_code_parsing.get_repo") as mock_get_repo, \
         patch("app.cli.git_code_parsing.is_collaborative", return_value=False), \
         patch("app.cli.git_code_parsing.extract_code_commit_content_by_author") as mock_extract:
        mock_get_repo.side_effect = [ValueError("not a repo"), FakeRepo(repo_root)]
        mock_extract.return_value = '[{"hash": "abc"}]'

        result = run_git_parsing_from_files(
            file_paths=[str(outside_file), str(nested_file)],
            include_merges=False,
            max_commits=10,
        )

        assert json.loads(result) == [{"hash": "abc"}]
        assert mock_get_repo.call_count == 2
        mock_extract.assert_called_once_with(
            path=repo_root,
            author="testuser",
            include_merges=False,
            max_commits=10,
        )


def test_run_git_parsing_resolves_nested_path_to_repo_root(tmp_path, monkeypatch):
    repo_root = tmp_path / "repo"
    nested_file = repo_root / "src" / "deep" / "file.py"
    nested_file.parent.mkdir(parents=True)
    nested_file.write_text("print('nested')")

    monkeypatch.setattr(git_code_parsing, "_get_preferred_author_email", lambda: ("testuser", None))

    class FakeRepo:
        def __init__(self, root):
            self.working_tree_dir = str(root)

    with patch("app.cli.git_code_parsing.get_repo") as mock_get_repo, \
         patch("app.cli.git_code_parsing.is_collaborative", return_value=False), \
         patch("app.cli.git_code_parsing.extract_code_commit_content_by_author") as mock_extract:
        mock_get_repo.return_value = FakeRepo(repo_root)
        mock_extract.return_value = '[{"hash": "abc"}]'

        result = run_git_parsing_from_files(
            file_paths=[str(nested_file)],
            include_merges=False,
            max_commits=10,
        )

        assert json.loads(result) == [{"hash": "abc"}]
        mock_get_repo.assert_called_once_with(nested_file)
        mock_extract.assert_called_once_with(
            path=repo_root,
            author="testuser",
            include_merges=False,
            max_commits=10,
        )



def test_run_git_parsing_relative_paths_fail_without_project_root(tmp_path, monkeypatch, capsys):
    project_root = tmp_path / "extracted_project"

    (project_root / "src").mkdir(parents=True)
    (project_root / "src" / "main.py").write_text("print('hi')")


    other_cwd = tmp_path / "somewhere_else"

    other_cwd.mkdir()
    monkeypatch.chdir(other_cwd)


    assert not Path("src/main.py").exists()

    assert (project_root / "src" / "main.py").exists()

    monkeypatch.setattr(git_code_parsing, "_get_preferred_author_email", lambda: ("testuser", None))


    with patch("app.cli.git_code_parsing.extract_code_commit_content_by_author") as mock_extract:
        result = run_git_parsing_from_files(
            file_paths=["src/main.py"],  # <-- RELATIVE PATH like scan_result["files"]

            include_merges=False,
            max_commits=10,
        )
        assert result == "[]"

        mock_extract.assert_not_called()

    out = capsys.readouterr().out
    assert "No Git repositories detected in provided paths" in out