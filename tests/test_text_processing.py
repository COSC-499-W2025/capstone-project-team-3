"""Tests for text processing utilities - focused and concise."""

import pytest
from app.utils.code_analysis.text_processing import (
    split_camelcase_and_filter,
    extract_meaningful_filename_keywords, 
    get_top_keywords
)

def test_split_camelcase_and_filter():
    """Test camelCase splitting and filtering."""
    # Basic camelCase - using words not in COMMON_TERMS
    result = split_camelcase_and_filter("handleUserProfile")
    assert "handle" in result
    assert "profile" in result
    
    # With underscores
    result = split_camelcase_and_filter("database_connection")
    assert "database" in result
    assert "connection" in result
    
    # Filter short words
    result = split_camelcase_and_filter("handleA", min_length=2)
    assert "handle" in result
    assert len([w for w in result if len(w) <= 2]) == 0

def test_extract_meaningful_filename_keywords():
    """Test filename keyword extraction."""
    filenames = [
        "database_service.py",
        "AuthController.js", 
        "README.md",
        "authentication_utils.py"
    ]
    
    keywords = extract_meaningful_filename_keywords(filenames)
    assert "database" in keywords
    assert "service" in keywords
    assert "auth" in keywords
    assert "controller" in keywords
    assert "authentication" in keywords
    assert "utils" in keywords
    
    # Should filter out common extensions and words
    assert "py" not in keywords
    assert "js" not in keywords
    # user is filtered out by COMMON_TERMS

def test_get_top_keywords():
    """Test keyword ranking and limiting."""
    keywords = {"python", "java", "react", "django", "flask", "node"}
    
    # Test default limit
    top = get_top_keywords(keywords)
    assert len(top) <= 15
    assert isinstance(top, list)
    
    # Test custom limit
    top = get_top_keywords(keywords, limit=3)
    assert len(top) <= 3
    
    # Test with empty set
    top = get_top_keywords(set())
    assert top == []

def test_text_processing_edge_cases():
    """Test edge cases for text processing functions."""
    # Empty inputs
    assert split_camelcase_and_filter("") == set()
    assert extract_meaningful_filename_keywords([]) == set()
    assert get_top_keywords(set()) == []
    
    # Special characters - using words not filtered
    result = split_camelcase_and_filter("handle$Database@Connection#123")
    assert "handle" in result
    assert "database" in result
    assert "connection" in result
    
    # Single character handling - function returns empty for short strings
    result = split_camelcase_and_filter("x", min_length=1)
    assert result == set()  # Function filters out short strings
    
    # Test with longer single word
    result = split_camelcase_and_filter("database", min_length=2)
    assert "database" in result
