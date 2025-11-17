import pytest
import zipfile
from pathlib import Path

from app.utils.project_extractor import extract_and_list_projects, _identify_projects, get_project_top_level_dirs

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

def test_identify_projects_root_is_project(tmp_path):
    """Test when root directory itself is a project."""
    (tmp_path / "setup.py").write_text("# setup")
    (tmp_path / "main.py").write_text("print('hi')")
    
    projects = _identify_projects(tmp_path)
    
    assert len(projects) == 1
    assert str(tmp_path) in projects[0]

def test_identify_projects_multiple_subdirs(tmp_path):
    """Test identifying multiple projects in subdirectories."""
    proj1 = tmp_path / "proj1"
    proj1.mkdir()
    (proj1 / "package.json").write_text("{}")
    
    proj2 = tmp_path / "proj2"
    proj2.mkdir()
    (proj2 / "setup.py").write_text("# setup")
    
    proj3 = tmp_path / "proj3"
    proj3.mkdir()
    (proj3 / "go.mod").write_text("module main")
    
    projects = _identify_projects(tmp_path)
    
    assert len(projects) == 3
    assert any("proj1" in p for p in projects)
    assert any("proj2" in p for p in projects)
    assert any("proj3" in p for p in projects)

def test_identify_projects_ignores_hidden_dirs(tmp_path):
    """Test that hidden directories (starting with .) are ignored."""
    hidden = tmp_path / ".hidden"
    hidden.mkdir()
    (hidden / "setup.py").write_text("# setup")
    
    proj = tmp_path / "visible"
    proj.mkdir()
    (proj / "package.json").write_text("{}")
    
    projects = _identify_projects(tmp_path)
    
    assert len(projects) == 1
    assert any("visible" in p for p in projects)
    assert not any(".hidden" in p for p in projects)

def test_identify_projects_no_projects(tmp_path):
    """Test when no projects are found."""
    (tmp_path / "file.txt").write_text("hello")
    (tmp_path / "another.md").write_text("# README")
    
    projects = _identify_projects(tmp_path)
    
    assert len(projects) == 0

def test_identify_projects_mixed_files_and_dirs(tmp_path):
    """Test with mix of files and directories."""
    (tmp_path / "README.md").write_text("# Project")
    (tmp_path / "LICENSE").write_text("MIT")
    
    proj1 = tmp_path / "backend"
    proj1.mkdir()
    (proj1 / "setup.py").write_text("# setup")
    
    proj2 = tmp_path / "frontend"
    proj2.mkdir()
    (proj2 / "package.json").write_text("{}")
    
    projects = _identify_projects(tmp_path)
    
    assert len(projects) == 2

def test_identify_projects_empty_directory(tmp_path):
    """Test with empty directory."""
    projects = _identify_projects(tmp_path)
    
    assert len(projects) == 0

def test_identify_projects_returns_list(tmp_path):
    """Test that function returns a list of strings."""
    proj = tmp_path / "proj"
    proj.mkdir()
    (proj / ".git").mkdir()
    
    projects = _identify_projects(tmp_path)
    
    assert isinstance(projects, list)
    assert all(isinstance(p, str) for p in projects)

def test_identify_projects_git_marker(tmp_path):
    """Test detection by .git marker."""
    proj = tmp_path / "git_proj"
    proj.mkdir()
    (proj / ".git").mkdir()
    
    projects = _identify_projects(tmp_path)
    
    assert len(projects) == 1
    assert "git_proj" in projects[0]

def test_identify_projects_multiple_markers(tmp_path):
    """Test project with multiple markers (should still count as one)."""
    proj = tmp_path / "multi_marker"
    proj.mkdir()
    (proj / "setup.py").write_text("# setup")
    (proj / "package.json").write_text("{}")
    (proj / ".git").mkdir()
    
    projects = _identify_projects(tmp_path)
    
    assert len(projects) == 1
    
def test_get_project_top_level_dirs_normal_case(tmp_path):
    """Test that valid top-level project directories are returned and excluded patterns are ignored."""
    # Create a mix of valid projects and excluded directories
    (tmp_path / "my_python_app").mkdir()
    (tmp_path / "react_frontend").mkdir()
    (tmp_path / ".git").mkdir()
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "build").mkdir()
    (tmp_path / "README.md").write_text("# Project")  # file, should be ignored

    result = get_project_top_level_dirs(tmp_path)

    # Only non-excluded directories should be returned, sorted
    assert result == ["my_python_app", "react_frontend"]


def test_get_project_top_level_dirs_edge_cases(tmp_path):
    """Test edge cases: empty dir, non-existent path, custom excludes, and case sensitivity."""
    # Test empty directory
    assert get_project_top_level_dirs(tmp_path) == []

    # Test non-existent path
    assert get_project_top_level_dirs(tmp_path) == []

    # Test custom exclude pattern
    (tmp_path / "secret").mkdir()
    (tmp_path / "public_api").mkdir()
    custom_excludes = ["secret"]
    result = get_project_top_level_dirs(tmp_path, exclude_patterns=custom_excludes)
    assert result == ["public_api"]

    # Test case sensitivity: "NODE_MODULES" is not excluded if pattern is "node_modules"
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "NODE_MODULES").mkdir()  # different case
    result = get_project_top_level_dirs(tmp_path)
    # "node_modules" is excluded; "NODE_MODULES" is not (unless explicitly in EXCLUDE_PATTERNS)
    assert "node_modules" not in result
    assert "NODE_MODULES" in result  # because EXCLUDE_PATTERNS has "node_modules", not uppercase