"""
Tests for analysis_merger_utils.py - Skill date inference functions.
"""

import pytest
from pathlib import Path
from git import Repo
from app.utils.analysis_merger_utils import _get_skill_extensions, _infer_skill_dates_from_git


class TestGetSkillExtensions:
    """Test the _get_skill_extensions function."""
    
    def test_common_languages(self):
        """Test common programming languages return correct extensions."""
        assert _get_skill_extensions("Python") == [".py", ".pyx", ".pyw"]
        assert _get_skill_extensions("Java") == [".java"]
        assert _get_skill_extensions("JavaScript") == [".js", ".mjs", ".cjs"]
        assert _get_skill_extensions("TypeScript") == [".ts"]
        assert _get_skill_extensions("C#") == [".cs"]
    
    def test_case_insensitive(self):
        """Test skill matching is case-insensitive."""
        assert _get_skill_extensions("python") == [".py", ".pyx", ".pyw"]
        assert _get_skill_extensions("JAVA") == [".java"]
    
    def test_unknown_skills(self):
        """Test that unknown skills return empty list."""
        assert _get_skill_extensions("XYZABC123NotReal") == []
        assert _get_skill_extensions("FakeSkill999") == []
        assert _get_skill_extensions("") == []

class TestInferSkillDatesFromGit:
    """Test the _infer_skill_dates_from_git function."""
    
    @pytest.fixture
    def git_repo(self, tmp_path):
        """Create a temporary git repository with test commits."""
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        repo = Repo.init(repo_path)
        
        with repo.config_writer() as config:
            config.set_value("user", "name", "Test User")
            config.set_value("user", "email", "test@example.com")
        
        # Create Python file (Day 1)
        py_file = repo_path / "main.py"
        py_file.write_text("print('Hello')")
        repo.index.add([str(py_file)])
        repo.index.commit("Add Python file", commit_date="2024-01-15 10:00:00")
        
        # Create Java file (Day 2)
        java_file = repo_path / "App.java"
        java_file.write_text("public class App {}")
        repo.index.add([str(java_file)])
        repo.index.commit("Add Java file", commit_date="2024-02-20 14:30:00")
        
        return str(repo_path)
    
    def test_non_git_directory(self, tmp_path):
        """Test that non-git directories return None for all skills."""
        non_git_path = tmp_path / "not_a_repo"
        non_git_path.mkdir()
        
        result = _infer_skill_dates_from_git(str(non_git_path), ["Python", "Java"])
        assert result == {"Python": None, "Java": None}
    
    def test_infer_dates_from_git_history(self, git_repo):
        """Test that skill dates are correctly inferred from git history."""
        result = _infer_skill_dates_from_git(git_repo, ["Python", "Java"])
        
        assert result["Python"] == "2024-01-15"
        assert result["Java"] == "2024-02-20"
    
    def test_skill_not_in_repo(self, git_repo):
        """Test that skills not present in repo return None."""
        result = _infer_skill_dates_from_git(git_repo, ["Python", "C++"])
        
        assert result["Python"] == "2024-01-15"
        assert result["C++"] is None
    
    def test_unknown_skills(self, git_repo):
        """Test that unknown skills return None."""
        result = _infer_skill_dates_from_git(git_repo, ["backend", "frontend"])
        
        assert result["backend"] is None
        assert result["frontend"] is None
