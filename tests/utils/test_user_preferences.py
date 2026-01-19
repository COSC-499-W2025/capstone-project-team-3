"""
Tests for the user preferences utilities module.
"""
import pytest
from unittest.mock import patch, MagicMock
from app.utils.code_analysis.user_preferences import (
    load_user_preferences,
    get_preference_weighted_keywords,
    enhance_resume_bullets_with_preferences,
    prioritize_patterns_by_preferences
)


def test_load_user_preferences_no_email():
    """Test that load_user_preferences returns None when no email provided."""
    result = load_user_preferences(None)
    assert result is None


def test_load_user_preferences_with_email():
    """Test that load_user_preferences calls UserPreferences when email provided."""
    mock_prefs = {
        'industry': 'Technology',
        'job_title': 'Software Engineer',
        'name': 'Test User'
    }
    
    with patch('app.cli.user_preference_cli.UserPreferences') as mock_class:
        mock_instance = MagicMock()
        mock_instance.get_latest_preferences.return_value = mock_prefs
        mock_class.return_value = mock_instance
        
        result = load_user_preferences('test@example.com')
        
        assert result == mock_prefs
        mock_class.assert_called_once()
        mock_instance.get_latest_preferences.assert_called_once_with('test@example.com')


def test_load_user_preferences_import_error():
    """Test that load_user_preferences handles ImportError gracefully."""
    # Mock the import to raise ImportError
    import builtins
    real_import = builtins.__import__
    
    def mock_import(name, *args):
        if 'user_preference_cli' in name:
            raise ImportError("Mocked import error")
        return real_import(name, *args)
    
    with patch('builtins.__import__', side_effect=mock_import):
        result = load_user_preferences('test@example.com')
        assert result is None


def test_get_preference_weighted_keywords_no_prefs():
    """Test keyword weighting when no preferences provided."""
    keywords = ['python', 'javascript', 'react']
    result = get_preference_weighted_keywords(keywords, None)
    assert result == keywords


def test_get_preference_weighted_keywords_no_keywords():
    """Test keyword weighting when no keywords provided."""
    prefs = {'industry': 'Technology', 'job_title': 'Engineer'}
    result = get_preference_weighted_keywords([], prefs)
    assert result == []


def test_get_preference_weighted_keywords_with_prefs():
    """Test keyword weighting with valid preferences."""
    keywords = ['python', 'javascript', 'react', 'html']
    prefs = {
        'industry': 'Software Engineering',
        'job_title': 'Frontend Developer'
    }
    
    result = get_preference_weighted_keywords(keywords, prefs)
    
    # Should return all keywords, potentially reordered
    assert len(result) == len(keywords)
    assert all(keyword in result for keyword in keywords)


def test_enhance_resume_bullets_with_preferences_no_prefs():
    """Test resume bullet enhancement when no preferences provided."""
    bullets = ['Created a web application', 'Worked on database design']
    result = enhance_resume_bullets_with_preferences(bullets, None, {})
    assert result == bullets


def test_enhance_resume_bullets_with_preferences_no_bullets():
    """Test resume bullet enhancement when no bullets provided."""
    prefs = {'industry': 'Technology', 'job_title': 'Engineer'}
    result = enhance_resume_bullets_with_preferences([], prefs, {})
    assert result == []


def test_enhance_resume_bullets_with_preferences_valid():
    """Test resume bullet enhancement with valid preferences."""
    bullets = ['Created a web application', 'Worked on database design']
    prefs = {
        'industry': 'software engineering',
        'job_title': 'backend developer'
    }
    metrics = {}
    
    result = enhance_resume_bullets_with_preferences(bullets, prefs, metrics)
    
    # Should return same number of bullets, potentially enhanced
    assert len(result) == len(bullets)


def test_prioritize_patterns_by_preferences_no_prefs():
    """Test pattern prioritization when no preferences provided."""
    patterns = {
        'design_patterns': ['MVC', 'Singleton'],
        'architectural_patterns': ['Microservices', 'REST']
    }
    result = prioritize_patterns_by_preferences(patterns, None)
    assert result == patterns


def test_prioritize_patterns_by_preferences_valid():
    """Test pattern prioritization with valid preferences."""
    patterns = {
        'design_patterns': ['MVC', 'Singleton'],
        'architectural_patterns': ['Microservices', 'REST'],
        'frameworks_detected': ['React', 'Django']
    }
    prefs = {
        'industry': 'web development',
        'job_title': 'full stack developer'
    }
    
    result = prioritize_patterns_by_preferences(patterns, prefs)
    
    # Should return patterns, potentially reordered
    assert len(result) == len(patterns)
    assert all(key in result for key in patterns.keys())