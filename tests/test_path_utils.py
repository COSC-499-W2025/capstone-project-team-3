import zipfile
import pytest
from pathlib import Path
from app.utils.path_utils import extract_zipped_contents, is_existing_path


def test_existing_dir(tmp_path):
    d = tmp_path / "folder"
    d.mkdir()
    assert is_existing_path(str(d)) is True
    assert is_existing_path(d) is True


def test_existing_file(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("hello")
    assert is_existing_path(str(f)) is True
    assert is_existing_path(f) is True


def test_nonexistent(tmp_path):
    p = tmp_path / "missing"
    assert is_existing_path(str(p)) is False


def test_none_raises():
    with pytest.raises(ValueError):
        is_existing_path(None)
        

def test_valid_zip_file_extracts(tmp_path):
    """
    Test for a valid zip file
    """
    zip_path = tmp_path / "test.zip"
    test_file = tmp_path / "file.txt"
    test_file.write_text("Hello")

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(test_file, arcname="file.txt")

    assert extract_zipped_contents(str(zip_path)) == True

def test_none_path_raises_value_error():
    """
    Test for when no path is passed
    """
    with pytest.raises(ValueError, match="path must be provided"):
        extract_zipped_contents(None)
    
def test_corrupt_zip_file_raises_value_error(tmp_path):
    """ 
    Test for a corrupt/invalid zip file
    """
    corrupt_zip = tmp_path / "corrupt.zip"
    corrupt_zip.write_text("this is not a zip file")

    with pytest.raises(ValueError, match="not a valid zip archive"):
        extract_zipped_contents(corrupt_zip)