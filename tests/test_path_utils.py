import zipfile
import pytest
from pathlib import Path
from app.utils.path_utils import extract_zipped_contents, is_existing_path, is_zip_file


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
        
#valid zip file
@pytest.mark.parametrize("coerce", [str, lambda p: p])  # str and Path inputs
def test_is_zip_file_valid_zip(tmp_path, coerce):
    zip_path = tmp_path / "valid.zip"
    inner = tmp_path / "file.txt"
    inner.write_text("hello")
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.write(inner, arcname="file.txt")

    assert is_zip_file(coerce(zip_path)) is True

#regular file not zip
@pytest.mark.parametrize("coerce", [str, lambda p: p])
def test_is_zip_file_non_zip_returns_false(tmp_path, coerce):
    f = tmp_path / "not_zip.txt"
    f.write_text("just text")
    assert is_zip_file(coerce(f)) is False

#corrupt file
@pytest.mark.parametrize("coerce", [str, lambda p: p])
def test_is_zip_file_corrupt_zip_returns_false(tmp_path, coerce):
    bad = tmp_path / "corrupt.zip"
    # Not a real zip file
    bad.write_text("this is not a zip")
    assert is_zip_file(coerce(bad)) is False

#provides directory
@pytest.mark.parametrize("coerce", [str, lambda p: p])
def test_is_zip_file_directory_raises_value_error(tmp_path, coerce):
    d = tmp_path / "a_directory"
    d.mkdir()
    with pytest.raises(ValueError, match="not a file"):
        is_zip_file(coerce(d))

#non existent path
@pytest.mark.parametrize("coerce", [str, lambda p: p])
def test_is_zip_file_nonexistent_raises_value_error(tmp_path, coerce):
    missing = tmp_path / "missing.zip"
    with pytest.raises(ValueError, match="does not exist"):
        is_zip_file(coerce(missing))

#none input
def test_is_zip_file_none_raises_value_error():
    with pytest.raises(ValueError, match="path must be provided"):
        is_zip_file(None)
