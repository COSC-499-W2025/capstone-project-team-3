import pytest
from unittest.mock import patch, MagicMock
import os
import sys


def test_main_runs_analysis_loop_when_prompt_root_enabled():
    """Test main runs analysis loop when PROMPT_ROOT=1."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('app.main.LLMConsentManager'), \
         patch('app.main.run_scan_flow') as mock_scan, \
         patch('builtins.input') as mock_input, \
         patch.dict(os.environ, {'PROMPT_ROOT': '1'}):
        
        # Set up all the mocks
        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None
        mock_file_input.return_value = {"status": "ok", "projects": ["/tmp/project1"], "count": 1}
        mock_scan.return_value = {
            "files": ["file1.py"], 
            "skip_analysis": True, 
            "reason": "already_analyzed",
            "signature": "test_sig"
        }
        
        # CRITICAL: Handle multiple input calls in sequence
        # First call might be for error handling, second for continue/exit
        mock_input.side_effect = ['exit', 'exit', 'exit']  # Cover all possible input calls
        
        from app.main import main
        main()
        
        mock_file_input.assert_called()


def test_main_skips_analysis_loop_when_prompt_root_disabled():
    """Test main skips analysis loop when PROMPT_ROOT=0."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch.dict(os.environ, {'PROMPT_ROOT': '0'}):
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None
        
        from app.main import main
        main()
        
        mock_file_input.assert_not_called()


def test_main_handles_file_input_failure_with_retry():
    """Test main handles file input failure and allows retry."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('app.main.LLMConsentManager'), \
         patch('builtins.input', side_effect=['retry', 'exit']), \
         patch.dict(os.environ, {'PROMPT_ROOT': '1'}):
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None
        mock_file_input.side_effect = [{"status": "error"}, {"status": "error"}]
        
        from app.main import main
        main()
        
        assert mock_file_input.call_count >= 2


def test_main_handles_file_input_failure_with_exit():
    """Test main exits when user chooses exit after file input failure."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('app.main.LLMConsentManager'), \
         patch('builtins.input', return_value='exit'), \
         patch.dict(os.environ, {'PROMPT_ROOT': '1'}):
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None
        mock_file_input.return_value = {"status": "error"}
        
        from app.main import main
        main()
        
        mock_file_input.assert_called_once()


def test_main_processes_projects_from_zip():
    """Test main processes projects from ZIP file."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('app.main.LLMConsentManager') as mock_llm_manager, \
         patch('app.main.run_scan_flow') as mock_scan, \
         patch('app.main.GeminiLLMClient'), \
         patch('builtins.input', return_value='exit'), \
         patch.dict(os.environ, {'PROMPT_ROOT': '1', 'GEMINI_API_KEY': 'test_key'}):
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None
        mock_file_input.return_value = {
            "status": "ok", 
            "projects": ["/tmp/project1", "/tmp/project2"], 
            "count": 2
        }
        mock_scan.return_value = {
            "files": ["file1.py"], 
            "skip_analysis": False,
            "signature": "test_sig"
        }
        mock_llm_manager.return_value.ask_analysis_type.return_value = 'ai'
        
        from app.main import main
        main()
        
        assert mock_scan.call_count == 2
        mock_llm_manager.return_value.ask_analysis_type.assert_called()


def test_main_skips_already_analyzed_projects():
    """Test main skips projects that are already analyzed."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('app.main.LLMConsentManager') as mock_llm_manager, \
         patch('app.main.run_scan_flow') as mock_scan, \
         patch('builtins.input', return_value='exit'), \
         patch.dict(os.environ, {'PROMPT_ROOT': '1'}):
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None
        mock_file_input.return_value = {
            "status": "ok", 
            "projects": ["/tmp/project1"], 
            "count": 1
        }
        mock_scan.return_value = {
            "files": ["file1.py"], 
            "skip_analysis": True,
            "reason": "already_analyzed",
            "signature": "test_sig"
        }
        
        from app.main import main
        main()
        
        # Should not call ask_analysis_type for already analyzed projects
        mock_llm_manager.return_value.ask_analysis_type.assert_not_called()


def test_main_handles_projects_with_no_files():
    """Test main handles projects with no files correctly."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('app.main.LLMConsentManager') as mock_llm_manager, \
         patch('app.main.run_scan_flow') as mock_scan, \
         patch('builtins.input', return_value='exit'), \
         patch.dict(os.environ, {'PROMPT_ROOT': '1'}):
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None
        mock_file_input.return_value = {
            "status": "ok", 
            "projects": ["/tmp/empty_project"], 
            "count": 1
        }
        mock_scan.return_value = {
            "files": [], 
            "skip_analysis": True,
            "reason": "no_files",
            "signature": None
        }
        
        from app.main import main
        main()
        
        mock_llm_manager.return_value.ask_analysis_type.assert_not_called()


def test_main_runs_ai_analysis():
    """Test main runs AI analysis when selected."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('app.main.LLMConsentManager') as mock_llm_manager, \
         patch('app.main.run_scan_flow') as mock_scan, \
         patch('app.main.GeminiLLMClient') as mock_llm_client, \
         patch('builtins.input', return_value='exit'), \
         patch.dict(os.environ, {'PROMPT_ROOT': '1', 'GEMINI_API_KEY': 'test_key'}):
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None
        mock_file_input.return_value = {
            "status": "ok", 
            "projects": ["/tmp/project1"], 
            "count": 1
        }
        mock_scan.return_value = {
            "files": ["file1.py"], 
            "skip_analysis": False,
            "signature": "test_sig"
        }
        mock_llm_manager.return_value.ask_analysis_type.return_value = 'ai'
        
        from app.main import main
        main()
        
        mock_llm_client.assert_called_once_with(api_key='test_key')


def test_main_runs_local_analysis():
    """Test main runs local analysis when selected."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('app.main.LLMConsentManager') as mock_llm_manager, \
         patch('app.main.run_scan_flow') as mock_scan, \
         patch('builtins.input', return_value='exit'), \
         patch.dict(os.environ, {'PROMPT_ROOT': '1'}):
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None
        mock_file_input.return_value = {
            "status": "ok", 
            "projects": ["/tmp/project1"], 
            "count": 1
        }
        mock_scan.return_value = {
            "files": ["file1.py"], 
            "skip_analysis": False,
            "signature": "test_sig"
        }
        mock_llm_manager.return_value.ask_analysis_type.return_value = 'local'
        
        from app.main import main
        main()
        
        mock_llm_manager.return_value.ask_analysis_type.assert_called_once()


def test_main_handles_no_projects_found():
    """Test main handles case when no projects are found."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('app.main.LLMConsentManager'), \
         patch('builtins.input', return_value='exit'), \
         patch.dict(os.environ, {'PROMPT_ROOT': '1'}):
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None
        mock_file_input.return_value = {"status": "ok"}  # No "projects" key
        
        from app.main import main
        main()
        
        mock_file_input.assert_called()


def test_main_prompt_root_accepts_truthy_values():
    """Test PROMPT_ROOT accepts multiple truthy values (1, true, True, yes)."""
    truthy_values = ['1', 'true', 'True', 'yes']
    
    for value in truthy_values:
        with patch('app.main.init_db'), \
             patch('app.main.ConsentManager') as mock_consent, \
             patch('app.main.file_input_main') as mock_file_input, \
             patch('app.main.seed_db'), \
             patch('app.main.UserPreferences') as mock_user_pref, \
             patch('app.main.LLMConsentManager'), \
             patch('builtins.input', return_value='exit'), \
             patch.dict(os.environ, {'PROMPT_ROOT': value}, clear=True):
            
            mock_consent.return_value.enforce_consent.return_value = True
            mock_file_input.return_value = {"status": "error"}
            mock_user_pref.return_value.manage_preferences.return_value = None
            mock_file_input.reset_mock()
            
            from app.main import main
            main()
            
            assert mock_file_input.called, f"file_input_main not called for PROMPT_ROOT={value}"


def test_main_prints_analysis_session_header(capsys):
    """Test main prints analysis session header when PROMPT_ROOT=1."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('app.main.LLMConsentManager'), \
         patch('builtins.input', return_value='exit'), \
         patch.dict(os.environ, {'PROMPT_ROOT': '1'}):
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_file_input.return_value = {"status": "error"}
        mock_user_pref.return_value.manage_preferences.return_value = None
        
        from app.main import main
        main()
        
        captured = capsys.readouterr()
        assert "🔍 PROJECT ANALYSIS SESSION" in captured.out


def test_main_initializes_database():
    """Test main initializes the database at startup."""
    with patch('app.main.init_db') as mock_init_db, \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch.dict(os.environ, {'PROMPT_ROOT': '0'}):
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None
        
        from app.main import main
        main()
        
        mock_init_db.assert_called_once()

def test_main_prompt_root_default_behavior():
    """Test PROMPT_ROOT defaults to '0' when not set."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences') as mock_user_pref, \
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

def test_main_integrates_non_code_file_checker():
    """Test main integrates non-code file checker and prints results per project."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('app.main.LLMConsentManager') as mock_llm_manager, \
         patch('app.main.run_scan_flow') as mock_scan, \
         patch('app.main.classify_non_code_files_with_user_verification') as mock_non_code_checker, \
         patch('builtins.input', return_value='exit'), \
         patch.dict(os.environ, {'PROMPT_ROOT': '1'}):
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None
        mock_file_input.return_value = {
            "status": "ok", 
            "projects": ["/tmp/project1"], 
            "count": 1
        }
        mock_scan.return_value = {
            "files": ["file1.py", "README.md"], 
            "skip_analysis": False,
            "signature": "test_sig"
        }
        mock_llm_manager.return_value.ask_analysis_type.return_value = 'local'
        mock_non_code_checker.return_value = {
            "is_git_repo": True,
            "user_identity": {"name": "Test User"},
            "collaborative": ["README.md"],
            "non_collaborative": [],
            "excluded": []
        }
        
        from app.main import main
        main()
        
        mock_non_code_checker.assert_called_once_with("/tmp/project1")
        


def test_main_cleans_up_upload_artifacts_on_success():
    """Test cleanup_upload is called when analysis result has upload_id."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('app.main.LLMConsentManager'), \
         patch('app.main.run_scan_flow') as mock_scan, \
         patch('app.main.cleanup_upload') as mock_cleanup, \
         patch('builtins.input', return_value='exit'), \
         patch.dict(os.environ, {'PROMPT_ROOT': '1'}):

        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None
        mock_file_input.return_value = {
            "status": "ok",
            "projects": [],
            "count": 0,
            "upload_id": "abc123",
            "extracted_dir": "/tmp/extracted",
        }
        mock_scan.return_value = {"files": [], "skip_analysis": True, "reason": "no_files", "signature": None}

        from app.main import main
        main()

        mock_cleanup.assert_called_once_with(
            "abc123",
            extracted_dir="/tmp/extracted",
            delete_extracted=True,
        )


def test_main_skips_cleanup_when_no_upload_id():
    """Test cleanup_upload is not called when upload_id is missing."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('app.main.LLMConsentManager'), \
         patch('app.main.run_scan_flow') as mock_scan, \
         patch('app.main.cleanup_upload') as mock_cleanup, \
         patch('builtins.input', return_value='exit'), \
         patch.dict(os.environ, {'PROMPT_ROOT': '1'}):

        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None
        mock_file_input.return_value = {
            "status": "ok",
            "projects": [],
            "count": 0,
            # no upload_id
        }
        mock_scan.return_value = {"files": [], "skip_analysis": True, "reason": "no_files", "signature": None}

        from app.main import main
        main()

        mock_cleanup.assert_not_called()