import pytest
from unittest.mock import patch, MagicMock
import os
import sys


VALID_ZIP_RESPONSE = {
    "type": "zip",
    "count": 1,
    "projects": ["projA"]
}


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
        mock_file_input.return_value = VALID_ZIP_RESPONSE
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
    """Test main exits when file input returns non-zip."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences'), \
         patch('sys.exit', side_effect=SystemExit) as mock_exit, \
         patch.dict(os.environ, {'PROMPT_ROOT': '1'}):

        mock_consent.return_value.enforce_consent.return_value = True
        mock_file_input.return_value = {"type": None}

        from app.main import main

        with pytest.raises(SystemExit):
            main()

        mock_exit.assert_called_once_with(1)



def test_main_prompt_root_accepts_truthy_values():
    """Test PROMPT_ROOT accepts multiple truthy values."""
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
            mock_file_input.return_value = VALID_ZIP_RESPONSE
            mock_user_pref.return_value.manage_preferences.return_value = None
            mock_file_input.reset_mock()

            from app.main import main
            main()

            assert mock_file_input.called


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
        mock_file_input.return_value = VALID_ZIP_RESPONSE
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
         patch('sys.exit', side_effect=SystemExit) as mock_exit, \
         patch.dict(os.environ, {'PROMPT_ROOT': '1'}):

        mock_consent.return_value.enforce_consent.return_value = True
        mock_file_input.return_value = {"type": None}

        from app.main import main

        with pytest.raises(SystemExit):
            main()

        captured = capsys.readouterr()
        assert "Only ZIP archives are accepted" in captured.out

        mock_exit.assert_called_once_with(1)



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
    """Test main seeds the database once at startup."""
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

        assert mock_seed_db.call_count == 1
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
    """Test execution order when PROMPT_ROOT=1."""
    call_order = []

    def track_init_db():
        call_order.append('init_db')

    def track_consent():
        call_order.append('consent')
        return True

    def track_file_input():
        call_order.append('file_input')
        return VALID_ZIP_RESPONSE

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

        assert call_order == ['init_db', 'seed_db', 'consent', 'file_input']


def test_main_execution_order_without_prompt_root():
    """Test execution order when PROMPT_ROOT=0."""
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

        assert call_order == ['init_db', 'seed_db', 'consent']


def test_fastapi_app_exists():
    """Test FastAPI app instance exists."""
    from app.main import app
    from fastapi import FastAPI

    assert isinstance(app, FastAPI)


def test_root_endpoint_returns_welcome_message():
    """Test root endpoint returns correct message."""
    from app.main import read_root

    response = read_root()
    assert response == {"message": "Welcome to the Project Insights!!"}
