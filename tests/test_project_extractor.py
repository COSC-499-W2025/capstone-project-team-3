import pytest
import zipfile
from pathlib import Path

from app.utils.project_extractor import extract_and_list_projects

def test_extract_and_list_projects_single_project(tmp_path):
    """Test extracting a ZIP with one project."""
    proj = tmp_path / "project1"
    proj.mkdir()
    (proj / "setup.py").write_text("# setup")
    (proj / "main.py").write_text("print('hi')")
    
    zip_path = tmp_path / "projects.zip"
    with zipfile.ZipFile(str(zip_path), 'w') as zf:
        zf.write(proj / "setup.py", "project1/setup.py")
        zf.write(proj / "main.py", "project1/main.py")
    
    res = extract_and_list_projects(str(zip_path))
    
    assert res["status"] == "ok"
    assert res["count"] == 1
    assert len(res["projects"]) == 1
    assert res["extracted_dir"] is not None

def test_extract_and_list_projects_multiple_projects(tmp_path):
    """Test extracting a ZIP with multiple projects."""
    proj1 = tmp_path / "proj1"
    proj1.mkdir()
    (proj1 / "package.json").write_text("{}")
    
    proj2 = tmp_path / "proj2"
    proj2.mkdir()
    (proj2 / "setup.py").write_text("# setup")
    
    zip_path = tmp_path / "projects.zip"
    with zipfile.ZipFile(str(zip_path), 'w') as zf:
        zf.write(proj1 / "package.json", "proj1/package.json")
        zf.write(proj2 / "setup.py", "proj2/setup.py")
    
    res = extract_and_list_projects(str(zip_path))
    
    assert res["status"] == "ok"
    assert res["count"] == 2
    assert len(res["projects"]) == 2

def test_extract_and_list_projects_invalid_zip(tmp_path):
    """Test with an invalid ZIP file."""
    bad_zip = tmp_path / "bad.zip"
    bad_zip.write_text("not a zip")
    
    res = extract_and_list_projects(str(bad_zip))
    
    assert res["status"] == "error"
    assert "valid ZIP" in res["reason"]

def test_extract_and_list_projects_nonexistent_path(tmp_path):
    """Test with a non-existent ZIP file."""
    missing_zip = tmp_path / "missing.zip"
    
    res = extract_and_list_projects(str(missing_zip))
    
    assert res["status"] == "error"
    assert "does not exist" in res["reason"]

def test_extract_and_list_projects_none_raises():
    """Test that None input raises ValueError."""
    with pytest.raises(ValueError):
        extract_and_list_projects(None)

def test_extract_and_list_projects_returns_correct_structure(tmp_path):
    """Test that the function returns the correct dict structure."""
    proj = tmp_path / "proj"
    proj.mkdir()
    (proj / "setup.py").write_text("# setup")
    
    zip_path = tmp_path / "test.zip"
    with zipfile.ZipFile(str(zip_path), 'w') as zf:
        zf.write(proj / "setup.py", "proj/setup.py")
    
    res = extract_and_list_projects(str(zip_path))
    
    assert "status" in res
    assert "count" in res
    assert "projects" in res
    assert "extracted_dir" in res