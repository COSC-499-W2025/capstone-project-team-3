from unittest.mock import patch, MagicMock
from app.cli.git_code_parsing import run_git_parsing_from_files


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

    project_file = tmp_path / "dummy.py"
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
    with patch("app.cli.git_code_parsing.is_collaborative", return_value=True) as mock_collab, \
         patch("app.cli.git_code_parsing.extract_code_commit_content_by_author") as mock_extract:

        # Fake JSON returned by extract_code_commit_content_by_author
        mock_extract.return_value = '{"ok": true}'

        result = run_git_parsing_from_files(
            file_paths=[str(project_file)],
            include_merges=False,
            max_commits=10,
        )

        # We return exactly what the extractor returns
        assert result == '{"ok": true}'

        # is_collaborative called with the project file path
        mock_collab.assert_called_once_with(project_file)

        # extract_code_commit_content_by_author called with the correct args
        mock_extract.assert_called_once_with(
            path=project_file,
            author="testuser",
            include_merges=False,
            max_commits=10,
        )