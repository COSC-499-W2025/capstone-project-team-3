import os
import pytest
from pathlib import Path

from app.utils.path_utils import validate_read_access, validate_directory_size

def test_validate_read_access_file(tmp_path):
    f = tmp_path / "a.txt"
    f.write_text("hello")
    res = validate_read_access(str(f))
    assert res["status"] == "ok"
    assert "path" in res

def test_validate_read_access_dir_with_flag(tmp_path):
    d = tmp_path / "d"
    d.mkdir()
    res = validate_read_access(str(d), treat_as_dir=True)
    assert res["status"] == "ok"

def test_validate_read_access_dir_without_flag(tmp_path):
    d = tmp_path / "d"
    d.mkdir()
    res = validate_read_access(str(d))
    assert res["status"] == "ok"

def test_validate_read_access_missing(tmp_path):
    p = tmp_path / "no.txt"
    res = validate_read_access(str(p))
    assert res["status"] == "error"
    assert "does not exist" in res["reason"]

def test_validate_read_access_permission_denied(tmp_path, monkeypatch):
    f = tmp_path / "a.txt"
    f.write_text("x")
    monkeypatch.setattr(os, "access", lambda path, mode: False)
    res = validate_read_access(str(f))
    assert res["status"] == "error"
    assert "permission" in res["reason"].lower()

def test_validate_read_access_none_raises():
    with pytest.raises(ValueError):
        validate_read_access(None)

def test_validate_directory_size_ok(tmp_path):
    d = tmp_path / "d"
    d.mkdir()
    f = d / "small.txt"
    f.write_text("x" * 100)
    res = validate_directory_size(str(d), max_size_mb=1)
    assert res["status"] == "ok"
    assert res["size_mb"] < 1

def test_validate_directory_size_warning(tmp_path):
    d = tmp_path / "d"
    d.mkdir()
    f = d / "large.txt"
    f.write_text("x" * (10 * 1024 * 1024))  # 10 MB
    res = validate_directory_size(str(d), max_size_mb=5)
    assert res["status"] == "warning"
    assert "exceeds" in res["reason"]

def test_validate_directory_size_none_raises():
    with pytest.raises(ValueError):
        validate_directory_size(None)