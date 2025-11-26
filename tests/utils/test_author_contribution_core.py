"""
Tests for core author contribution parsing functionality.
Tests the 3 main functions added in this PR.
"""
import pytest
import json
from pathlib import Path
from app.utils.non_code_parsing.document_parser import parse_author_contributions
from app.utils.non_code_analysis.non_code_analysis_utils import pre_process_non_code_files


class TestParseAuthorContributions:
    """Test parse_author_contributions function from document_parser.py"""
    
    def test_returns_correct_structure(self):
        """Test that function returns expected structure even with invalid repo."""
        result = parse_author_contributions(
            repo_path="/nonexistent/path",
            author="test@example.com"
        )
        
        assert "parsed_files" in result
        assert isinstance(result["parsed_files"], list)
    
    def test_handles_invalid_repo(self):
        """Test graceful handling of invalid repository path."""
        result = parse_author_contributions(
            repo_path="/invalid/repo/path",
            author="test@example.com"
        )
        
        # Should return empty list or error, not crash
        assert "parsed_files" in result
        assert len(result["parsed_files"]) == 0


class TestPreProcessWithAuthorFlag:
    """Test is_author_filtered parameter in pre_process_non_code_files"""
    
    def test_author_flag_true(self):
        """Test that is_author_filtered=True sets is_author_only=True in output."""
        sample_data = {
            "parsed_files": [
                {
                    "path": "test.md",
                    "name": "test.md",
                    "type": "md",
                    "content": "Sample content for testing purposes with multiple sentences.",
                    "success": True,
                    "error": ""
                }
            ]
        }
        
        results = pre_process_non_code_files(
            parsed_files=sample_data,
            is_author_filtered=True
        )
        
        assert len(results) > 0
        assert results[0].get("is_author_only") is True
    
    def test_author_flag_false(self):
        """Test that is_author_filtered=False sets is_author_only=False in output."""
        sample_data = {
            "parsed_files": [
                {
                    "path": "test.md",
                    "name": "test.md",
                    "type": "md",
                    "content": "Sample content for testing purposes with multiple sentences.",
                    "success": True,
                    "error": ""
                }
            ]
        }
        
        results = pre_process_non_code_files(
            parsed_files=sample_data,
            is_author_filtered=False
        )
        
        assert len(results) > 0
        assert results[0].get("is_author_only") is False
    
    def test_default_behavior(self):
        """Test default behavior without author flag (should be False)."""
        sample_data = {
            "parsed_files": [
                {
                    "path": "test.md",
                    "name": "test.md",
                    "type": "md",
                    "content": "Sample content for testing purposes with multiple sentences.",
                    "success": True,
                    "error": ""
                }
            ]
        }
        
        results = pre_process_non_code_files(parsed_files=sample_data)
        
        assert len(results) > 0
        assert results[0].get("is_author_only") is False
    
    def test_output_structure(self):
        """Test that output contains all expected fields."""
        sample_data = {
            "parsed_files": [
                {
                    "path": "docs/test.md",
                    "name": "test.md",
                    "type": "md",
                    "content": "Test content with multiple sentences. This is for testing purposes.",
                    "success": True,
                    "error": ""
                }
            ]
        }
        
        results = pre_process_non_code_files(
            parsed_files=sample_data,
            is_author_filtered=True
        )
        
        assert len(results) > 0
        result = results[0]
        
        # Check all expected fields exist
        assert "file_name" in result
        assert "file_path" in result
        assert "file_type" in result
        assert "word_count" in result
        assert "sentence_count" in result
        assert "summary" in result
        assert "key_topics" in result
        assert "is_author_only" in result
        
        # Verify is_author_only is set correctly
        assert result["is_author_only"] is True


class TestExtractNonCodeContentByAuthor:
    """Test extract_non_code_content_by_author function from git_utils.py"""
    
    def test_returns_json_string(self):
        """Test that function returns valid JSON string."""
        from app.utils.git_utils import extract_non_code_content_by_author
        
        result = extract_non_code_content_by_author(
            path="/nonexistent/path",
            author="test@example.com"
        )
        
        # Should return valid JSON even on error
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert isinstance(parsed, list)
    
    def test_handles_invalid_repo(self):
        """Test graceful handling of invalid repository."""
        from app.utils.git_utils import extract_non_code_content_by_author
        
        result = extract_non_code_content_by_author(
            path="/invalid/repo",
            author="test@example.com"
        )
        
        parsed = json.loads(result)
        assert isinstance(parsed, list)
        assert len(parsed) == 0  # Empty list on error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
