import pytest
from unittest.mock import patch, MagicMock
import os
import sys


def test_main_runs_file_input_when_prompt_root_enabled():
    """Test main runs file input when PROMPT_ROOT=1."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('sys.exit'), \
         patch.dict(os.environ, {'PROMPT_ROOT': '1'}):
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_file_input.return_value = 0
        mock_user_pref.return_value.manage_preferences.return_value = None
        
        from app.main import main
        main()
        
        mock_file_input.assert_called_once()


def test_main_skips_file_input_when_prompt_root_disabled():
    """Test main skips file input when PROMPT_ROOT=0."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('sys.exit'), \
         patch.dict(os.environ, {'PROMPT_ROOT': '0'}):
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None
        
        from app.main import main
        main()
        
        mock_file_input.assert_not_called()


def test_main_exits_when_file_input_fails():
    """Test main exits when file input returns non-zero."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences'), \
         patch('sys.exit') as mock_exit, \
         patch.dict(os.environ, {'PROMPT_ROOT': '1'}):
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_file_input.return_value = 1
        
        from app.main import main
        main()
        
        mock_exit.assert_called_once_with(1)


def test_main_prompt_root_accepts_truthy_values():
    """Test PROMPT_ROOT accepts multiple truthy values (1, true, True, yes)."""
    truthy_values = ['1', 'true', 'True', 'yes']
    
    for value in truthy_values:
        with patch('app.main.init_db'), \
             patch('app.main.ConsentManager') as mock_consent, \
             patch('app.main.file_input_main') as mock_file_input, \
             patch('app.main.seed_db'), \
             patch('app.main.UserPreferences') as mock_user_pref, \
             patch('sys.exit'), \
             patch.dict(os.environ, {'PROMPT_ROOT': value}, clear=True):
            
            mock_consent.return_value.enforce_consent.return_value = True
            mock_file_input.return_value = 0
            mock_user_pref.return_value.manage_preferences.return_value = None
            mock_file_input.reset_mock()
            
            from app.main import main
            main()
            
            assert mock_file_input.called, f"file_input_main not called for PROMPT_ROOT={value}"


def test_main_prints_file_input_header(capsys):
    """Test main prints project root input header when PROMPT_ROOT=1."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('sys.exit'), \
         patch.dict(os.environ, {'PROMPT_ROOT': '1'}):
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_file_input.return_value = 0
        mock_user_pref.return_value.manage_preferences.return_value = None
        
        from app.main import main
        main()
        
        captured = capsys.readouterr()
        assert "--- Project Root Input ---" in captured.out


def test_main_prints_error_when_file_input_cancelled(capsys):
    """Test main prints error when file input is cancelled."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences'), \
         patch('sys.exit'), \
         patch.dict(os.environ, {'PROMPT_ROOT': '1'}):
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_file_input.return_value = 1
        
        from app.main import main
        main()
        
        captured = capsys.readouterr()
        assert "Root input step failed or was cancelled" in captured.out


def test_main_initializes_database():
    """Test main initializes the database at startup."""
    with patch('app.main.init_db') as mock_init_db, \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('sys.exit'), \
         patch.dict(os.environ, {'PROMPT_ROOT': '0'}):
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None
        
        from app.main import main
        main()
        
        mock_init_db.assert_called_once()


def test_main_seeds_database_after_successful_flow(capsys):
    """Test main seeds the database after consent and file input (if enabled)."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.seed_db') as mock_seed_db, \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('sys.exit'), \
         patch.dict(os.environ, {'PROMPT_ROOT': '0'}):
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None
        
        from app.main import main
        main()
        
        # seed_db is called twice in main()
        assert mock_seed_db.call_count == 2
        captured = capsys.readouterr()
        assert "Database started" in captured.out


def test_main_prints_success_message(capsys):
    """Test main prints 'App started successfully' message."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('sys.exit'), \
         patch.dict(os.environ, {'PROMPT_ROOT': '0'}):
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None
        
        from app.main import main
        main()
        
        captured = capsys.readouterr()
        assert "App started successfully" in captured.out


def test_main_execution_order_with_prompt_root():
    """Test main executes steps in correct order when PROMPT_ROOT=1."""
    call_order = []
    
    def track_init_db():
        call_order.append('init_db')
    
    def track_consent():
        call_order.append('consent')
        return True
    
    def track_file_input():
        call_order.append('file_input')
        return 0
    
    def track_seed_db():
        call_order.append('seed_db')
    
    with patch('app.main.init_db', side_effect=track_init_db), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main', side_effect=track_file_input), \
         patch('app.main.seed_db', side_effect=track_seed_db), \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('sys.exit'), \
         patch.dict(os.environ, {'PROMPT_ROOT': '1'}):
        
        mock_consent.return_value.enforce_consent.side_effect = track_consent
        mock_user_pref.return_value.manage_preferences.return_value = None
        
        from app.main import main
        main()
        
        # seed_db is called twice in main()
        assert call_order == ['init_db', 'seed_db', 'consent', 'file_input', 'seed_db']


def test_main_execution_order_without_prompt_root():
    """Test main executes steps in correct order when PROMPT_ROOT=0."""
    call_order = []
    
    def track_init_db():
        call_order.append('init_db')
    
    def track_consent():
        call_order.append('consent')
        return True
    
    def track_seed_db():
        call_order.append('seed_db')
    
    with patch('app.main.init_db', side_effect=track_init_db), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.seed_db', side_effect=track_seed_db), \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('sys.exit'), \
         patch.dict(os.environ, {'PROMPT_ROOT': '0'}):
        
        mock_consent.return_value.enforce_consent.side_effect = track_consent
        mock_user_pref.return_value.manage_preferences.return_value = None
        
        from app.main import main
        main()
        
        # seed_db is called twice in main()
        assert call_order == ['init_db', 'seed_db', 'consent', 'seed_db']


def test_main_prompt_root_default_behavior():
    """Test PROMPT_ROOT defaults to '0' when not set."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('sys.exit'), \
         patch.dict(os.environ, {}, clear=True):
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None
        
        from app.main import main
        main()
        
        mock_file_input.assert_not_called()


def test_fastapi_app_exists():
    """Test FastAPI app instance is created."""
    from app.main import app
    from fastapi import FastAPI
    
    assert isinstance(app, FastAPI)


def test_root_endpoint_returns_welcome_message():
    """Test root endpoint returns correct welcome message."""
    from app.main import read_root
    
    response = read_root()
    assert response == {"message": "Welcome to the Project Insights!!"}
    assert "message" in response
    assert isinstance(response["message"], str)