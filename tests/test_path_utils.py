import pytest
from pathlib import Path
from app.utils.path_utils import is_existing_path


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