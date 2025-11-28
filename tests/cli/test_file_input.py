from pathlib import Path
from unittest.mock import patch, MagicMock
from app.cli.file_input import prompt_for_root, main
import zipfile

def test_prompt_for_root_valid_input(monkeypatch):
    """Test prompt_for_root returns valid non-empty input."""
    monkeypatch.setattr('builtins.input', lambda _: '/valid/path')
    result = prompt_for_root()
    assert result == '/valid/path'


def test_prompt_for_root_rejects_empty_input(monkeypatch, capsys):
    """Test prompt_for_root loops until non-empty input provided."""
    inputs = iter(['', '   ', '/valid/path'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    
    result = prompt_for_root()
    assert result == '/valid/path'
    
    captured = capsys.readouterr()
    assert captured.out.count('❌ Path cannot be empty') == 2


def test_prompt_for_root_strips_whitespace(monkeypatch):
    """Test prompt_for_root strips leading/trailing whitespace."""
    monkeypatch.setattr('builtins.input', lambda _: '  /path/with/spaces  ')
    result = prompt_for_root()
    assert result == '/path/with/spaces'


def test_main_with_directory_rejected(tmp_path, capsys):
    """Test main rejects directory paths (ZIP-only enforcement)."""
    test_dir = tmp_path / "test_project"
    test_dir.mkdir()
    
    result = main(['--root', str(test_dir)])
    
    assert result['status'] == 'error'
    assert 'Only ZIP files are accepted' in result['reason']


def test_main_with_invalid_path(capsys):
    """Test main with non-existent path."""
    result = main(['--root', '/nonexistent/path'])
    
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
    
    result = main(['--root', str(bad_zip)])
    
    assert result['status'] == 'error'


def test_main_with_empty_zip(tmp_path, capsys):
    """Test main with ZIP containing no identifiable projects."""
    import zipfile
    
    # Create a directory with a file (no project markers)
    content_dir = tmp_path / "content"
    content_dir.mkdir()
    (content_dir / "random.txt").write_text("hello")
    
    # Create ZIP
    zip_path = tmp_path / "empty.zip"
    with zipfile.ZipFile(str(zip_path), 'w') as zf:
        zf.write(content_dir / "random.txt", "random.txt")
    
    result = main(['--root', str(zip_path)])
    
    assert result['status'] == 'error'
    assert 'no identifiable projects found' in result['reason']


def test_main_with_user_exit(monkeypatch):
    """Test main handles user exit from prompt."""
    monkeypatch.setattr('builtins.input', lambda _: 'exit')
    
    result = main([])
    
    assert result['status'] == 'error'
    assert result['reason'] == 'user_exit'


def test_main_with_none_path_raises_valueerror(capsys):
    """Test main handles None path gracefully."""
    with patch('app.cli.file_input.validate_read_access') as mock_validate:
        mock_validate.side_effect = ValueError("path must be provided")
        
        result = main(['--root', 'dummy'])
        
        assert result['status'] == 'error'
        assert 'path must be provided' in result['reason']

def test_main_rejects_non_zip_extension(tmp_path):
    """Test main rejects files without .zip extension."""
    # Create a file with .tar extension
    tar_file = tmp_path / "archive.tar"
    tar_file.write_text("fake tar content")
    
    result = main(['--root', str(tar_file)])
    
    assert result['status'] == 'error'
    assert 'Only ZIP files are accepted' in result['reason']