import pytest
from unittest.mock import patch, MagicMock
import os


def test_main_runs_file_input_when_prompt_root_enabled():
    """Test main runs file input when PROMPT_ROOT=1."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.seed_db'), \
         patch.dict(os.environ, {'PROMPT_ROOT': '1'}):
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_file_input.return_value = 0
        
        from app.main import main
        main()
        
        mock_file_input.assert_called_once()


def test_main_skips_file_input_when_prompt_root_disabled():
    """Test main skips file input when PROMPT_ROOT=0."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.seed_db'), \
         patch.dict(os.environ, {'PROMPT_ROOT': '0'}):
        
        mock_consent.return_value.enforce_consent.return_value = True
        
        from app.main import main
        main()
        
        mock_file_input.assert_not_called()


def test_main_exits_when_file_input_fails():
    """Test main exits when file input returns non-zero."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
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
             patch.dict(os.environ, {'PROMPT_ROOT': value}, clear=True):
            
            mock_consent.return_value.enforce_consent.return_value = True
            mock_file_input.return_value = 0
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
         patch.dict(os.environ, {'PROMPT_ROOT': '1'}):
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_file_input.return_value = 0
        
        from app.main import main
        main()
        
        captured = capsys.readouterr()
        assert "--- Project Root Input ---" in captured.out


def test_main_prints_error_when_file_input_cancelled(capsys):
    """Test main prints error when file input is cancelled."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('sys.exit'), \
         patch.dict(os.environ, {'PROMPT_ROOT': '1'}):
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_file_input.return_value = 1
        
        from app.main import main
        main()
        
        captured = capsys.readouterr()
        assert "Root input step failed or was cancelled" in captured.out