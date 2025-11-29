from pathlib import Path
from unittest.mock import patch, MagicMock
from app.cli.file_input import main
import zipfile

def test_main_with_directory_rejected(tmp_path, capsys):
    """Test main rejects directory paths (ZIP-only enforcement)."""
    test_dir = tmp_path / "test_project"
    test_dir.mkdir()

    # Simulate resolved upload to the directory path (invalid)
    with patch('builtins.input', side_effect=['abc']), \
         patch('requests.get') as mock_get, \
         patch('app.cli.file_input.validate_read_access') as mock_validate:
        mock_get.return_value.json.return_value = {'status': 'ok', 'path': str(test_dir)}
        # validate_read_access will detect directory and return error like original behavior
        mock_validate.return_value = {"status": "error", "reason": "Only ZIP files are accepted"}

        result = main([])

    assert result['status'] == 'error'
    assert 'Only ZIP files are accepted' in result['reason']


def test_main_with_invalid_path(capsys):
    """Test main with non-existent path."""
    with patch('builtins.input', side_effect=['abc']), \
         patch('requests.get') as mock_get, \
         patch('app.cli.file_input.validate_read_access') as mock_validate:
        mock_get.return_value.json.return_value = {'status': 'ok', 'path': '/nonexistent/path'}
        mock_validate.return_value = {"status": "error", "reason": "file does not exist"}

        result = main([])

    assert result['status'] == 'error'
    assert 'does not exist' in result['reason']

def create_valid_zip(zip_path):
    with zipfile.ZipFile(str(zip_path), 'w') as zf:
        # Add a marker file in a subdirectory
        zf.writestr("project1/setup.py", "# setup")
        # Optionally add more files
        zf.writestr("project1/README.md", "Readme content")

def test_main_with_invalid_zip(tmp_path, capsys):
    """Test main with invalid ZIP file."""
    bad_zip = tmp_path / "bad.zip"
    bad_zip.write_text("not a zip")

    with patch('builtins.input', side_effect=['abc']), \
         patch('requests.get') as mock_get, \
         patch('app.cli.file_input.validate_read_access') as mock_validate, \
         patch('app.cli.file_input.extract_and_list_projects') as mock_extract:
        mock_get.return_value.json.return_value = {'status': 'ok', 'path': str(bad_zip)}
        mock_validate.return_value = {'status': 'ok', 'path': str(bad_zip)}
        mock_extract.return_value = {'status': 'error', 'reason': 'file is not a valid ZIP archive'}

        result = main([])

    assert result['status'] == 'error'


def test_main_with_empty_zip(tmp_path, capsys):
    """Test main with ZIP containing no identifiable projects."""

    content_dir = tmp_path / "content"
    content_dir.mkdir()
    (content_dir / "random.txt").write_text("hello")

    zip_path = tmp_path / "empty.zip"
    with zipfile.ZipFile(str(zip_path), 'w') as zf:
        zf.write(content_dir / "random.txt", "random.txt")

    with patch('builtins.input', side_effect=['abc']), \
         patch('requests.get') as mock_get, \
         patch('app.cli.file_input.validate_read_access') as mock_validate, \
         patch('app.cli.file_input.extract_and_list_projects') as mock_extract:
        mock_get.return_value.json.return_value = {'status': 'ok', 'path': str(zip_path)}
        mock_validate.return_value = {'status': 'ok', 'path': str(zip_path)}
        mock_extract.return_value = {'status': 'ok', 'projects': [], 'extracted_dir': '/tmp/e', 'count': 0}

        result = main([])

    assert result['status'] == 'error'
    assert 'No projects found' in result['reason']


def test_main_with_user_exit():
    """Test main handles user exit from prompt."""
    with patch('builtins.input', side_effect=['exit']):
        result = main([])
    assert result['status'] == 'error'
    assert result['reason'] == 'user_exit'


def test_main_with_none_path_raises_valueerror(capsys):
    """Test main handles None path gracefully."""
    with patch('builtins.input', side_effect=['abc']), \
         patch('requests.get') as mock_get, \
         patch('app.cli.file_input.validate_read_access') as mock_validate:
        mock_get.return_value.json.return_value = {'status': 'ok', 'path': None}
        mock_validate.return_value = {"status": "error", "reason": "path must be provided"}

        result = main([])

    assert result['status'] == 'error'
    assert 'path must be provided' in result['reason']

def test_main_rejects_non_zip_extension(tmp_path):
    """Test main rejects files without .zip extension."""
    tar_file = tmp_path / "archive.tar"
    tar_file.write_text("fake tar content")

    with patch('builtins.input', side_effect=['abc']), \
         patch('requests.get') as mock_get, \
         patch('app.cli.file_input.validate_read_access') as mock_validate:
        mock_get.return_value.json.return_value = {'status': 'ok', 'path': str(tar_file)}
        mock_validate.return_value = {"status": "error", "reason": "Only ZIP files are accepted"}

        result = main([])

    assert result['status'] == 'error'
    assert 'Only ZIP files are accepted' in result['reason']