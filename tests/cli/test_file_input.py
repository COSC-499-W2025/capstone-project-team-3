import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from app.cli.file_input import prompt_for_root, main


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


def test_main_with_valid_directory(tmp_path, capsys):
    """Test main with valid directory path."""
    test_dir = tmp_path / "test_project"
    test_dir.mkdir()
    
    exit_code = main(['--root', str(test_dir)])
    
    assert exit_code == 0
    captured = capsys.readouterr()
    result = json.loads(captured.out)
    assert result['status'] == 'ok'
    assert result['type'] == 'dir'
    assert result['path'] == str(test_dir)


def test_main_with_invalid_path(capsys):
    """Test main with non-existent path."""
    exit_code = main(['--root', '/nonexistent/path'])
    
    assert exit_code == 1
    captured = capsys.readouterr()
    result = json.loads(captured.out)
    assert result['status'] == 'error'
    assert 'does not exist' in result['reason']


def test_main_with_valid_zip(tmp_path, capsys):
    """Test main with valid ZIP file containing a project."""
    import zipfile
    
    # Create a test project
    proj = tmp_path / "project1"
    proj.mkdir()
    (proj / "setup.py").write_text("# setup")
    
    # Create ZIP
    zip_path = tmp_path / "projects.zip"
    with zipfile.ZipFile(str(zip_path), 'w') as zf:
        zf.write(proj / "setup.py", "project1/setup.py")
    
    exit_code = main(['--root', str(zip_path)])
    
    assert exit_code == 0
    captured = capsys.readouterr()
    result = json.loads(captured.out)
    assert result['status'] == 'ok'
    assert result['type'] == 'zip'
    assert result['count'] == 1
    assert 'extracted_dir' in result
    assert 'projects' in result


def test_main_with_invalid_zip(tmp_path, capsys):
    """Test main with invalid ZIP file."""
    bad_zip = tmp_path / "bad.zip"
    bad_zip.write_text("not a zip")
    
    exit_code = main(['--root', str(bad_zip)])
    
    assert exit_code == 1
    captured = capsys.readouterr()
    result = json.loads(captured.out)
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
    
    exit_code = main(['--root', str(zip_path)])
    
    assert exit_code == 1
    captured = capsys.readouterr()
    result = json.loads(captured.out)
    assert result['status'] == 'error'
    assert 'project' in result['reason'].lower() or 'no' in result['reason'].lower()


def test_main_with_none_path_raises_valueerror(capsys):
    """Test main handles None path gracefully."""
    with patch('app.cli.file_input.validate_read_access') as mock_validate:
        mock_validate.side_effect = ValueError("path must be provided")
        
        exit_code = main(['--root', 'dummy'])
        
        assert exit_code == 1
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result['status'] == 'error'
        assert 'path must be provided' in result['reason']


def test_main_returns_correct_exit_codes(tmp_path):
    """Test main returns 0 for success, 1 for errors."""
    # Success case
    valid_dir = tmp_path / "valid"
    valid_dir.mkdir()
    assert main(['--root', str(valid_dir)]) == 0
    
    # Error case
    assert main(['--root', '/nonexistent']) == 1


def test_main_json_output_structure(tmp_path, capsys):
    """Test main outputs valid JSON with expected structure."""
    test_dir = tmp_path / "json_test"
    test_dir.mkdir()
    
    main(['--root', str(test_dir)])
    
    captured = capsys.readouterr()
    result = json.loads(captured.out)
    
    assert 'status' in result
    assert 'type' in result
    assert 'path' in result
    assert result['type'] in ['dir', 'zip']