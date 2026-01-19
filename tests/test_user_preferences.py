"""Tests for user preferences utilities - focused and concise."""

import pytest
from unittest.mock import patch, MagicMock
from app.utils.code_analysis.user_preferences import (
    load_user_preferences,
    get_preference_weighted_keywords,
    enhance_resume_bullets_with_preferences,
    prioritize_patterns_by_preferences
)

def test_load_user_preferences():
    """Test loading user preferences."""
    # Mock the import inside the function
    with patch('app.utils.code_analysis.user_preferences.print') as mock_print:
        with patch('app.cli.user_preference_cli.UserPreferences') as mock_prefs:
            mock_instance = MagicMock()
            mock_instance.get_latest_preferences.return_value = {
                "skills": ["python", "java"], 
                "roles": ["backend"],
                "industry": "tech",
                "job_title": "developer"
            }
            mock_prefs.return_value = mock_instance
            
            # Test with valid email
            prefs = load_user_preferences("user@test.com")
            assert prefs is not None
            assert "skills" in prefs
            assert prefs["skills"] == ["python", "java"]
            
        # Test with None email
        prefs = load_user_preferences(None)
        assert prefs is None

def test_get_preference_weighted_keywords():
    """Test keyword weighting based on preferences."""
    base_keywords = ["python", "java", "react", "django"]
    user_prefs = {
        "skills": ["python", "django"],
        "roles": ["backend"]
    }
    
    # With preferences
    weighted = get_preference_weighted_keywords(base_keywords, user_prefs)
    assert isinstance(weighted, list)
    assert len(weighted) >= len([k for k in base_keywords if k in user_prefs["skills"]])
    
    # Without preferences
    weighted = get_preference_weighted_keywords(base_keywords, None)
    assert weighted == base_keywords

def test_enhance_resume_bullets_with_preferences():
    """Test resume bullet enhancement with preferences."""
    base_bullets = [
        "Developed web applications",
        "Implemented REST APIs",
        "Worked with databases"
    ]
    user_prefs = {
        "skills": ["python", "postgresql"],
        "roles": ["backend"]
    }
    metrics = {
        "frameworks_detected": ["django", "flask"],
        "databases": ["postgresql"]
    }
    
    # With preferences
    enhanced = enhance_resume_bullets_with_preferences(base_bullets, user_prefs, metrics)
    assert isinstance(enhanced, list)
    assert len(enhanced) >= len(base_bullets)
    
    # Without preferences
    enhanced = enhance_resume_bullets_with_preferences(base_bullets, None, metrics)
    assert enhanced == base_bullets

def test_prioritize_patterns_by_preferences():
    """Test pattern prioritization based on preferences."""
    patterns = {
        "frameworks_detected": ["django", "react", "flask"],
        "design_patterns": ["mvc", "singleton"],
        "architectural_patterns": ["microservices"]
    }
    user_prefs = {
        "skills": ["django", "mvc"],
        "roles": ["backend"]
    }
    
    # With preferences
    prioritized = prioritize_patterns_by_preferences(patterns, user_prefs)
    assert isinstance(prioritized, dict)
    assert "frameworks_detected" in prioritized
    
    # Without preferences
    prioritized = prioritize_patterns_by_preferences(patterns, None)
    assert prioritized == patterns

def test_user_preferences_edge_cases():
    """Test edge cases for user preferences functions."""
    # Empty inputs
    assert get_preference_weighted_keywords([], None) == []
    assert enhance_resume_bullets_with_preferences([], None, {}) == []
    assert prioritize_patterns_by_preferences({}, None) == {}
    
    # Invalid preferences format
    invalid_prefs = {"invalid": "format"}
    base_keywords = ["python", "java"]
    
    result = get_preference_weighted_keywords(base_keywords, invalid_prefs)
    assert isinstance(result, list)
