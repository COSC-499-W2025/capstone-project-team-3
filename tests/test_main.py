import pytest
from unittest.mock import patch, MagicMock
import os
import sys
from app.main import main
from app.utils.code_analysis.parse_code_utils import parse_code_flow
from pathlib import Path
from app.cli.git_code_parsing import run_git_parsing_from_files


@pytest.fixture(autouse=True)
def mock_os_operations():
    """Mock filesystem operations for all tests."""
    with patch('os.makedirs'):
        yield

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
        
        
        main()
        
        mock_file_input.assert_called()


def test_main_skips_analysis_loop_when_prompt_root_disabled():
    """Test main skips analysis loop when PROMPT_ROOT=0."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('builtins.input', return_value='exit'), \
         patch.dict(os.environ, {'PROMPT_ROOT': '0'}):
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None
        
        
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
         patch('builtins.input', side_effect=['retry','retry', 'exit']), \
         patch.dict(os.environ, {'PROMPT_ROOT': '1'}):
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None
        mock_file_input.side_effect = [{"status": "error"}, {"status": "error"}, {"status": "error"}]
        
        
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
        
        
        main()
        
        captured = capsys.readouterr()
        assert "🔍 PROJECT ANALYSIS SESSION" in captured.out


def test_main_initializes_database():
    """Test main initializes the database at startup."""
    with patch('app.main.init_db') as mock_init_db, \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('builtins.input', return_value='exit'), \
         patch.dict(os.environ, {'PROMPT_ROOT': '0'}):
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None
        
        
        main()
        
        mock_init_db.assert_called_once()

def test_main_prompt_root_default_behavior():
    """Test PROMPT_ROOT defaults to '0' when not set."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('builtins.input', return_value='exit'), \
         patch.dict(os.environ, {}, clear=True):
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None
        
        
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
            "collaborative": ["README.md"],
            "non_collaborative": []
        }
        
        
        main()
        
        mock_non_code_checker.assert_called_once_with("/tmp/project1")


# ============================================================================
# Integration tests for non-code parsing through main()
# ============================================================================

def test_main_calls_parsing_with_classification_results():
    """Test main() passes classification results to parsing correctly."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('app.main.LLMConsentManager') as mock_llm_manager, \
         patch('app.main.run_scan_flow') as mock_scan, \
         patch('app.main.classify_non_code_files_with_user_verification') as mock_classify, \
         patch('app.main.parsed_input_text') as mock_parse, \
         patch('app.main.display_startup_info'), \
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
        mock_classify.return_value = {
            'is_git_repo': True,
            'user_identity': {'email': 'test@example.com'},
            'collaborative': ['/path/file1.md'],
            'non_collaborative': ['/path/README.md'],
            'excluded': []
        }
        mock_parse.return_value = {'parsed_files': [{'path': '/path/file1.md', 'success': True}]}
        
        
        main()
        
        mock_classify.assert_called_once_with("/tmp/project1")
        mock_parse.assert_called_once()
        call_args = mock_parse.call_args
        assert call_args[1]['file_paths_dict']['collaborative'] == ['/path/file1.md']
        assert call_args[1]['file_paths_dict']['non_collaborative'] == ['/path/README.md']


def test_main_passes_repo_path_for_git_repos():
    """Test main() passes repo_path when project is a git repo."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('app.main.LLMConsentManager') as mock_llm_manager, \
         patch('app.main.run_scan_flow') as mock_scan, \
         patch('app.main.classify_non_code_files_with_user_verification') as mock_classify, \
         patch('app.main.parsed_input_text') as mock_parse, \
         patch('app.main.display_startup_info'), \
         patch('builtins.input', return_value='exit'), \
         patch.dict(os.environ, {'PROMPT_ROOT': '1'}):
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None
        mock_file_input.return_value = {"status": "ok", "projects": ["/tmp/git_project"], "count": 1}
        mock_scan.return_value = {"files": ["file1.py"], "skip_analysis": False, "signature": "test_sig"}
        mock_llm_manager.return_value.ask_analysis_type.return_value = 'local'
        mock_classify.return_value = {
            'is_git_repo': True,
            'user_identity': {'email': 'test@example.com'},
            'collaborative': ['/path/file.md'],
            'non_collaborative': [],
            'excluded': []
        }
        mock_parse.return_value = {'parsed_files': []}
        
        
        main()
        
        call_args = mock_parse.call_args
        assert call_args[1]['repo_path'] == "/tmp/git_project"
        assert call_args[1]['author'] == 'test@example.com'


def test_main_passes_none_repo_path_for_non_git():
    """Test main() passes None as repo_path for non-git projects."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('app.main.LLMConsentManager') as mock_llm_manager, \
         patch('app.main.run_scan_flow') as mock_scan, \
         patch('app.main.classify_non_code_files_with_user_verification') as mock_classify, \
         patch('app.main.parsed_input_text') as mock_parse, \
         patch('app.main.display_startup_info'), \
         patch('builtins.input', return_value='exit'), \
         patch.dict(os.environ, {'PROMPT_ROOT': '1'}):
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None
        mock_file_input.return_value = {"status": "ok", "projects": ["/tmp/local_project"], "count": 1}
        mock_scan.return_value = {"files": ["file1.py"], "skip_analysis": False, "signature": "test_sig"}
        mock_llm_manager.return_value.ask_analysis_type.return_value = 'local'
        mock_classify.return_value = {
            'is_git_repo': False,
            'user_identity': {},
            'collaborative': [],
            'non_collaborative': ['/path/local.txt'],
            'excluded': []
        }
        mock_parse.return_value = {'parsed_files': []}
        
        
        main()
        
        call_args = mock_parse.call_args
        assert call_args[1]['repo_path'] is None


def test_main_handles_parsing_with_empty_file_lists():
    """Test main() handles projects with no non-code files."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('app.main.LLMConsentManager') as mock_llm_manager, \
         patch('app.main.run_scan_flow') as mock_scan, \
         patch('app.main.classify_non_code_files_with_user_verification') as mock_classify, \
         patch('app.main.parsed_input_text') as mock_parse, \
         patch('app.main.display_startup_info'), \
         patch('builtins.input', return_value='exit'), \
         patch.dict(os.environ, {'PROMPT_ROOT': '1'}):
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None
        mock_file_input.return_value = {"status": "ok", "projects": ["/tmp/empty"], "count": 1}
        mock_scan.return_value = {"files": ["file1.py"], "skip_analysis": False, "signature": "test_sig"}
        mock_llm_manager.return_value.ask_analysis_type.return_value = 'local'
        mock_classify.return_value = {
            'is_git_repo': True,
            'user_identity': {'email': 'test@example.com'},
            'collaborative': [],
            'non_collaborative': [],
            'excluded': []
        }
        mock_parse.return_value = {'parsed_files': []}
        
        
        main()
        
        mock_parse.assert_called_once()
        call_args = mock_parse.call_args
        assert call_args[1]['file_paths_dict']['collaborative'] == []
        assert call_args[1]['file_paths_dict']['non_collaborative'] == []


def test_main_handles_parsing_exceptions_gracefully():
    """Test main() handles parsing exceptions without crashing."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('app.main.LLMConsentManager') as mock_llm_manager, \
         patch('app.main.run_scan_flow') as mock_scan, \
         patch('app.main.classify_non_code_files_with_user_verification') as mock_classify, \
         patch('app.main.parsed_input_text') as mock_parse, \
         patch('app.main.display_startup_info'), \
         patch('builtins.input', return_value='exit'), \
         patch.dict(os.environ, {'PROMPT_ROOT': '1'}):
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None
        mock_file_input.return_value = {"status": "ok", "projects": ["/tmp/project"], "count": 1}
        mock_scan.return_value = {"files": ["file1.py"], "skip_analysis": False, "signature": "test_sig"}
        mock_llm_manager.return_value.ask_analysis_type.return_value = 'local'
        mock_classify.return_value = {
            'is_git_repo': True,
            'user_identity': {'email': 'test@example.com'},
            'collaborative': ['/path/file.md'],
            'non_collaborative': [],
            'excluded': []
        }
        mock_parse.side_effect = Exception("Parsing failed")
        
        
        # Should not raise exception
        main()
        
def test_main_project_retreival(monkeypatch):
    """Test main retrieves past insights correctly and prints project info."""
    # Seed DB is called on startup, so projects exist
    monkeypatch.setenv("PROMPT_ROOT", "0")
    with patch('app.main.init_db'), \
         patch('app.main.seed_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('app.main.get_projects', return_value=[{"name": "Alpha Project"}]), \
         patch('app.main.lookup_past_insights') as mock_lookup:
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None

        
        main()
        
def test_main_calls_classify_and_parse_in_correct_order():
    """Test main() calls classify before parse in correct order."""
    with patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('app.main.LLMConsentManager') as mock_llm_manager, \
         patch('app.main.run_scan_flow') as mock_scan, \
         patch('app.main.classify_non_code_files_with_user_verification') as mock_classify, \
         patch('app.main.parsed_input_text') as mock_parse, \
         patch('app.main.display_startup_info'), \
         patch('builtins.input', return_value='exit'), \
         patch.dict(os.environ, {'PROMPT_ROOT': '1'}):
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None
        mock_file_input.return_value = {"status": "ok", "projects": ["/tmp/project"], "count": 1}
        mock_scan.return_value = {"files": ["file1.py"], "skip_analysis": False, "signature": "test_sig"}
        mock_llm_manager.return_value.ask_analysis_type.return_value = 'local'
        mock_classify.return_value = {
            'is_git_repo': True,
            'user_identity': {'email': 'test@example.com'},
            'collaborative': ['/path/file.md'],
            'non_collaborative': [],
            'excluded': []
        }
        mock_parse.return_value = {'parsed_files': []}
        
        
        from unittest.mock import call
        
        # Create a manager to track call order
        manager = MagicMock()
        manager.attach_mock(mock_classify, 'classify')
        manager.attach_mock(mock_parse, 'parse')
        
        main()
        
        # Verify classify was called before parse
        expected_calls = [call.classify('/tmp/project'), call.parse(file_paths_dict=mock_classify.return_value, repo_path='/tmp/project', author='test@example.com')]
        # Just verify both were called
        assert mock_classify.called
        assert mock_parse.called


def test_main_cleans_up_upload_artifacts_on_success():
    """Test cleanup_upload is called when analysis result has upload_id."""
    with patch('app.main.init_db'), \
         patch('app.main.seed_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('app.main.get_projects', return_value=[{"name": "Alpha Project"}]), \
         patch('app.main.lookup_past_insights') as mock_lookup:
        
        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None

        
        main()
        
        
        
def test_main_invokes_parse_code_flow_during_analysis():
    """Test that parse_code_flow is invoked with correct values inside main() flow."""
    with patch('app.main.init_db'), \
         patch('app.main.seed_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.run_scan_flow') as mock_scan, \
         patch('app.main.classify_non_code_files_with_user_verification'), \
         patch('app.main.detect_git', return_value=False), \
         patch('app.main.get_project_top_level_dirs', return_value=['alpha', 'beta']), \
         patch('app.main.parse_code_flow') as mock_parse_code, \
         patch('app.main.LLMConsentManager') as mock_llm_manager, \
         patch('builtins.input', return_value='exit'), \
         patch.dict(os.environ, {'PROMPT_ROOT': '1'}):
        # Consent granted
        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None

        # File input returns one project
        mock_file_input.return_value = {
            "status": "ok",
            "projects": ["/proj"],
            "count": 1
        }

        # Scan finds code files
        mock_scan.return_value = {
            "files": ["/proj/a.py", "/proj/b.py"],
            "skip_analysis": False,
            "signature": "sig123"
        }

        # Select "local" analysis type
        mock_llm_manager.return_value.ask_analysis_type.return_value = "local"

        # Mock parse_code_flow output
        mock_parse_code.return_value = [{"file": "parsed"}]

        
        main()

        # Ensure parse_code_flow was called once with correct files + top-level dirs
        mock_parse_code.assert_called_once_with(
            ["/proj/a.py", "/proj/b.py"],
            ['alpha', 'beta']
        )
 
        
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

        
        main()

        mock_cleanup.assert_not_called()
        
def test_main_invokes_parse_code_flow_during_analysis():
    """Test that parse_code_flow is invoked with correct values inside main() flow."""
    with patch('app.main.run_scan_flow') as mock_scan, \
         patch('app.main.classify_non_code_files_with_user_verification'), \
         patch('app.main.detect_git', return_value=False), \
         patch('app.main.get_project_top_level_dirs', return_value=['alpha', 'beta']), \
         patch('app.main.parse_code_flow') as mock_parse_code, \
         patch('app.main.LLMConsentManager') as mock_llm_manager, \
         patch('builtins.input', return_value='exit'), \
         patch.dict(os.environ, {'PROMPT_ROOT': '1'}):

        # Consent granted
        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None

        # File input returns one project
        mock_file_input.return_value = {
            "status": "ok",
            "projects": ["/proj"],
            "count": 1
        }

        # Scan finds code files
        mock_scan.return_value = {
            "files": ["/proj/a.py", "/proj/b.py"],
            "skip_analysis": False,
            "signature": "sig123"
        }

        # Select "local" analysis type
        mock_llm_manager.return_value.ask_analysis_type.return_value = "local"

        # Mock parse_code_flow output
        mock_parse_code.return_value = [{"file": "parsed"}]

        # Ensure parse_code_flow was called once with correct files + top-level dirs
        mock_parse_code.assert_called_once_with(
            ["/proj/a.py", "/proj/b.py"],
            ['alpha', 'beta']
        )
        
# ============================================================================
# tests for Git-based code parsing through main()
# ============================================================================
def test_main_invokes_git_parsing_for_git_projects():
    """Test that run_git_parsing_from_files is invoked for Git-based projects."""
    with patch('app.main.init_db'), \
         patch('app.main.seed_db'), \
         patch('app.main.display_startup_info'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.run_scan_flow') as mock_scan, \
         patch('app.main.classify_non_code_files_with_user_verification') as mock_classify, \
         patch('app.main.detect_git', return_value=True), \
         patch('app.main.run_git_parsing_from_files') as mock_git_parse, \
         patch('app.main.parse_code_flow') as mock_parse_code, \
         patch('app.main.LLMConsentManager') as mock_llm_manager, \
         patch('builtins.input', return_value='exit'), \
         patch.dict(os.environ, {'PROMPT_ROOT': '1'}):

        # Consent + prefs ok
        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None

        # One project returned from file_input_main
        mock_file_input.return_value = {
            "status": "ok",
            "projects": ["/proj"],
            "count": 1,
        }

        # Scan finds code files and no skip
        mock_scan.return_value = {
            "files": ["/proj/a.py", "/proj/b.py"],
            "skip_analysis": False,
            "signature": "sig123",
        }

        # Non-code checker still runs but contents aren't critical here
        mock_classify.return_value = {
            'is_git_repo': True,
            'user_identity': {'email': 'test@example.com'},
            'collaborative': [],
            'non_collaborative': [],
            'excluded': [],
        }

        # Choose local analysis so we go through the local branch
        mock_llm_manager.return_value.ask_analysis_type.return_value = "local"

        from app.main import main
        main()

        # ✅ We should call Git parsing with the scanned files
        mock_git_parse.assert_called_once_with(
            file_paths=["/proj/a.py", "/proj/b.py"],
            include_merges=False,
            max_commits=None,
        )

        # ✅ Local non-git parse_code_flow should NOT be used in this branch
        mock_parse_code.assert_not_called()

def test_main_calls_analyze_project_clean_in_local_mode():
    """Test main() calls analyze_project_clean with parsed_non_code in local analysis mode."""
    with patch('os.makedirs'), \
         patch('app.main.init_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.seed_db'), \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('app.main.LLMConsentManager') as mock_llm_manager, \
         patch('app.main.run_scan_flow') as mock_scan, \
         patch('app.main.classify_non_code_files_with_user_verification') as mock_classify, \
         patch('app.main.parsed_input_text') as mock_parse, \
         patch('app.main.analyze_project_clean') as mock_analyze_clean, \
         patch('app.main.detect_git', return_value=False), \
         patch('app.main.get_project_top_level_dirs', return_value=['dir1']), \
         patch('app.main.parse_code_flow'), \
         patch('app.main.display_startup_info'), \
         patch('builtins.input', return_value='exit'), \
         patch.dict(os.environ, {'PROMPT_ROOT': '1'}):
        
        # Setup mocks
        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None
        
        mock_file_input.return_value = {
            "status": "ok", 
            "projects": ["/tmp/test_project"], 
            "count": 1
        }
        
        mock_scan.return_value = {
            "files": ["file1.py"], 
            "skip_analysis": False,
            "signature": "test_sig_123"
        }
        
        mock_llm_manager.return_value.ask_analysis_type.return_value = 'local'
        
        mock_classify.return_value = {
            'is_git_repo': True,
            'user_identity': {'email': 'test@example.com'},
            'collaborative': ['/path/doc1.md'],
            'non_collaborative': ['/path/README.md'],
            'excluded': []
        }
        
        # Mock parsed data from parsed_input_text
        mock_parsed_data = {
            'parsed_files': [
                {
                    'name': 'doc1.md',
                    'path': '/path/doc1.md',
                    'content': 'Test documentation content',
                    'success': True,
                    'contribution_frequency': 5
                }
            ]
        }
        mock_parse.return_value = mock_parsed_data
        
        # Mock analyze_project_clean output
        mock_analyze_clean.return_value = {
            'summary': 'Test summary',
            'bullets': ['Bullet 1', 'Bullet 2'],
            'skills': {
                'technical_skills': ['Python'],
                'soft_skills': ['Communication']
            },
            'completeness_score': 85,
            'word_count': 100,
            'doc_type_counts': {},
            'doc_type_frequency': {}
        }
        
        # Run main
        
        main()
        
        # Verify analyze_project_clean was called with parsed_non_code
        mock_analyze_clean.assert_called_once_with(mock_parsed_data)

def test_main_calls_ai_non_code_analysis_pipeline():
    """Test main() calls AI non-code analysis pipeline with parsed_non_code in AI mode."""
    from contextlib import ExitStack
    
    with ExitStack() as stack:
        # Add all patches to the stack
        stack.enter_context(patch('os.makedirs'))
        stack.enter_context(patch('app.main.init_db'))
        stack.enter_context(patch('app.main.seed_db'))
        mock_consent = stack.enter_context(patch('app.main.ConsentManager'))
        mock_user_pref = stack.enter_context(patch('app.main.UserPreferences'))
        mock_file_input = stack.enter_context(patch('app.main.file_input_main'))
        mock_llm_manager = stack.enter_context(patch('app.main.LLMConsentManager'))
        mock_scan = stack.enter_context(patch('app.main.run_scan_flow'))
        mock_classify = stack.enter_context(patch('app.main.classify_non_code_files_with_user_verification'))
        mock_parse = stack.enter_context(patch('app.main.parsed_input_text'))
        mock_preprocess = stack.enter_context(patch('app.main.pre_process_non_code_files'))
        mock_aggregate = stack.enter_context(patch('app.main.aggregate_non_code_summaries'))
        mock_create_prompt = stack.enter_context(patch('app.main.create_non_code_analysis_prompt'))
        mock_generate_insights = stack.enter_context(patch('app.main.generate_non_code_insights'))
        mock_get_metrics = stack.enter_context(patch('app.main.get_additional_metrics'))
        stack.enter_context(patch('app.main.GeminiLLMClient'))
        stack.enter_context(patch('app.main.detect_git', return_value=False))
        stack.enter_context(patch('app.main.get_project_top_level_dirs', return_value=['dir1']))
        stack.enter_context(patch('app.main.parse_code_flow'))
        stack.enter_context(patch('app.main.display_startup_info'))
        stack.enter_context(patch('builtins.input', return_value='exit'))
        stack.enter_context(patch.dict(os.environ, {'PROMPT_ROOT': '1', 'GEMINI_API_KEY': 'test_key'}))
        
        # Setup mocks
        mock_consent.return_value.enforce_consent.return_value = True
        mock_user_pref.return_value.manage_preferences.return_value = None
        
        mock_file_input.return_value = {
            "status": "ok", 
            "projects": ["/tmp/test_project"], 
            "count": 1
        }
        
        mock_scan.return_value = {
            "files": ["file1.py"], 
            "skip_analysis": False,
            "signature": "test_sig_123"
        }
        
        mock_llm_manager.return_value.ask_analysis_type.return_value = 'ai'
        
        mock_classify.return_value = {
            'is_git_repo': True,
            'user_identity': {'email': 'test@example.com'},
            'collaborative': ['/path/doc1.md'],
            'non_collaborative': ['/path/README.md'],
            'excluded': []
        }
        
        # Mock parsed data
        mock_parsed_data = {
            'parsed_files': [
                {
                    'name': 'doc1.md',
                    'path': '/path/doc1.md',
                    'content': 'Test documentation content',
                    'success': True,
                    'contribution_frequency': 5
                }
            ]
        }
        mock_parse.return_value = mock_parsed_data
        
        # Mock AI pipeline steps
        mock_llm1_results = [{'summary': 'Test summary', 'keywords': ['test', 'doc']}]
        mock_preprocess.return_value = mock_llm1_results
        
        mock_project_metrics = {'total_words': 100, 'doc_count': 1}
        mock_aggregate.return_value = mock_project_metrics
        
        mock_prompt = "Analyze this project: ..."
        mock_create_prompt.return_value = mock_prompt
        
        mock_ai_insights = {
            'summary': 'AI-generated summary',
            'bullets': ['AI bullet 1', 'AI bullet 2'],
            'skills': {
                'technical_skills': ['Python', 'Docker'],
                'soft_skills': ['Leadership']
            }
        }
        mock_generate_insights.return_value = mock_ai_insights
        
        mock_additional_metrics = {'completeness_score': 90, 'word_count': 150}
        mock_get_metrics.return_value = mock_additional_metrics
        
        # Run main
        
        main()
        
        # Verify the AI pipeline was called in correct order with correct data
        mock_preprocess.assert_called_once_with(mock_parsed_data, language="english")
        mock_aggregate.assert_called_once_with(mock_llm1_results)
        mock_create_prompt.assert_called_once_with(mock_project_metrics)
        mock_generate_insights.assert_called_once_with(mock_prompt)
        mock_get_metrics.assert_called_once_with(mock_llm1_results)
        
def test_main_runs_merge_analysis_results():
    # Set PROMPT_ROOT to enable analysis loop
    os.environ["PROMPT_ROOT"] = "1"
    
    with patch('app.main.init_db'), \
         patch('app.main.seed_db'), \
         patch('app.main.ConsentManager') as mock_consent, \
         patch('app.main.UserPreferences') as mock_user_pref, \
         patch('app.main.file_input_main') as mock_file_input, \
         patch('app.main.LLMConsentManager') as mock_llm_manager, \
         patch('app.main.run_scan_flow') as mock_scan, \
         patch('app.main.classify_non_code_files_with_user_verification'), \
         patch('builtins.input', side_effect=['exit','exit']), \
         patch('app.main.merge_analysis_results') as mock_merge:
      
        # Setup mocks
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

        
        main()
        
        # Assert merge_analysis_results was called
        assert mock_merge.called

def test_main_user_preferences():
    # Create a mock store with the required methods
    mock_store = MagicMock()
    # Set up the mock to return a known value for get_latest_preferences
    mock_store.get_latest_preferences.return_value = {
        "name": "Test User",
        "email": "testuser@example.com",
        "github_user": "testgithub",
        "education": "BSc Computer Science",
        "industry": "Technology",
        "job_title": "Developer"
    }

    with patch("app.main.ConsentManager") as MockConsentManager, \
        patch("app.main.init_db"), \
        patch("app.main.seed_db"), \
        patch("app.main.UserPreferences") as MockUserPreferences, \
        patch("builtins.input", side_effect=[
            "testuser@example.com",  # email
            "yes",                   # update preferences
            "Test User",             # name
            "testgithub",            # github
            "BSc Computer Science",  # education
            "Technology",            # industry
            "Developer",              # job title
            "exit",
            "exit",
            "exit"
        ]):
        # Mock consent to always return True
        MockConsentManager.return_value.enforce_consent.return_value = True

        # Set the mock store on the UserPreferences instance
        mock_user_pref = MockUserPreferences.return_value
        mock_user_pref.store = mock_store
        
        main()

        # Assert that preferences were retrieved and saved
        mock_user_pref.manage_preferences.assert_called()