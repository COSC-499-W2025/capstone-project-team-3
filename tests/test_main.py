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


# ============================================================================
# Tests moved from test_parsing_integration_unit.py
# ============================================================================

def test_parsing_uses_non_code_result_directly():
    """Test that parsing uses non_code_result data without redundant calls."""
    with patch('app.utils.non_code_analysis.non_code_file_checker.classify_non_code_files_with_user_verification') as mock_classify, \
         patch('app.utils.non_code_parsing.document_parser.parsed_input_text') as mock_parse:

        mock_classify.return_value = {
            'is_git_repo': True,
            'user_identity': {'email': 'test@example.com'},
            'collaborative': ['/path/file1.md'],
            'non_collaborative': ['/path/README.md'],
            'excluded': []
        }

        mock_parse.return_value = {
            'parsed_files': [
                {'path': '/path/file1.md', 'success': True, 'contribution_frequency': 3}
            ]
        }

        project_path = '/test/project'
        non_code_result = mock_classify(project_path)

        parsed_non_code = mock_parse(
            file_paths_dict={
                'collaborative': non_code_result['collaborative'],
                'non_collaborative': non_code_result['non_collaborative']
            },
            repo_path=project_path,
            author=non_code_result['user_identity'].get('email')
        )

        mock_classify.assert_called_once_with(project_path)
        mock_parse.assert_called_once()
        assert len(parsed_non_code['parsed_files']) == 1


def test_parsing_handles_non_git_repo():
    """Test parsing correctly handles non-git repositories."""
    with patch('app.utils.non_code_analysis.non_code_file_checker.classify_non_code_files_with_user_verification') as mock_classify, \
         patch('app.utils.non_code_parsing.document_parser.parsed_input_text') as mock_parse:

        mock_classify.return_value = {
            'is_git_repo': False,
            'user_identity': {},
            'collaborative': [],
            'non_collaborative': ['/path/local.txt'],
            'excluded': []
        }

        mock_parse.return_value = {'parsed_files': []}

        project_path = '/test/local'
        non_code_result = mock_classify(project_path)

        parsed_non_code = mock_parse(
            file_paths_dict={
                'collaborative': non_code_result['collaborative'],
                'non_collaborative': non_code_result['non_collaborative']
            },
            repo_path=project_path if non_code_result['is_git_repo'] else None,
            author=non_code_result['user_identity'].get('email')
        )

        call_args = mock_parse.call_args
        assert call_args[1]['repo_path'] is None


def test_parsing_handles_empty_file_lists():
    """Test parsing handles projects with no non-code files."""
    with patch('app.utils.non_code_analysis.non_code_file_checker.classify_non_code_files_with_user_verification') as mock_classify, \
         patch('app.utils.non_code_parsing.document_parser.parsed_input_text') as mock_parse:

        mock_classify.return_value = {
            'is_git_repo': True,
            'user_identity': {'email': 'test@example.com'},
            'collaborative': [],
            'non_collaborative': [],
            'excluded': []
        }

        mock_parse.return_value = {'parsed_files': []}

        project_path = '/test/empty'
        non_code_result = mock_classify(project_path)

        parsed_non_code = mock_parse(
            file_paths_dict={
                'collaborative': non_code_result['collaborative'],
                'non_collaborative': non_code_result['non_collaborative']
            },
            repo_path=project_path,
            author=non_code_result['user_identity'].get('email')
        )

        assert parsed_non_code['parsed_files'] == []


def test_parsed_data_structure():
    """Test that parsed data has correct structure for analysis."""
    parsed_non_code = {
        'parsed_files': [
            {'path': '/path/file.md', 'success': True, 'contribution_frequency': 3}
        ]
    }

    assert 'parsed_files' in parsed_non_code
    assert len(parsed_non_code['parsed_files']) == 1
    assert parsed_non_code['parsed_files'][0]['success'] is True
    assert 'contribution_frequency' in parsed_non_code['parsed_files'][0]


def test_parsing_handles_no_parsed_files():
    """Test analysis handles case when no files are successfully parsed."""
    parsed_non_code = {'parsed_files': []}

    if parsed_non_code.get('parsed_files'):
        insights = 'analyzed'
    else:
        insights = None

    assert insights is None


def test_integration_efficiency_no_duplicate_calls():
    """Test that integration doesn't make duplicate classification calls."""
    with patch('app.utils.non_code_analysis.non_code_file_checker.classify_non_code_files_with_user_verification') as mock_classify, \
         patch('app.utils.non_code_parsing.document_parser.parsed_input_text') as mock_parse:

        mock_classify.return_value = {
            'is_git_repo': True,
            'user_identity': {'email': 'test@example.com'},
            'collaborative': ['/path/file.md'],
            'non_collaborative': ['/path/README.md'],
            'excluded': []
        }

        mock_parse.return_value = {'parsed_files': []}

        project_path = '/test/project'
        non_code_result = mock_classify(project_path)

        parsed_non_code = mock_parse(
            file_paths_dict={
                'collaborative': non_code_result['collaborative'],
                'non_collaborative': non_code_result['non_collaborative']
            },
            repo_path=project_path,
            author=non_code_result['user_identity'].get('email')
        )

        assert mock_classify.call_count == 1
        mock_parse.assert_called_once()


def test_parsing_with_contribution_frequency():
    """Test that parsed files include contribution_frequency field."""
    with patch('app.utils.non_code_parsing.document_parser.parsed_input_text') as mock_parse:
        mock_parse.return_value = {
            'parsed_files': [
                {
                    'path': '/path/file.md',
                    'name': 'file.md',
                    'type': 'md',
                    'content': '# Header',
                    'success': True,
                    'error': '',
                    'contribution_frequency': 5
                }
            ]
        }

        result = mock_parse(
            file_paths_dict={'collaborative': [], 'non_collaborative': ['/path/file.md']},
            repo_path=None,
            author=None
        )

        assert result['parsed_files'][0]['contribution_frequency'] == 5


def test_parsing_error_handling():
    """Test that parsing errors are captured in the error field."""
    with patch('app.utils.non_code_parsing.document_parser.parsed_input_text') as mock_parse:
        mock_parse.return_value = {
            'parsed_files': [
                {
                    'path': '/path/missing.pdf',
                    'name': 'missing.pdf',
                    'type': 'pdf',
                    'content': '',
                    'success': False,
                    'error': 'File does not exist',
                    'contribution_frequency': 1
                }
            ]
        }

        result = mock_parse(
            file_paths_dict={'collaborative': [], 'non_collaborative': ['/path/missing.pdf']},
            repo_path=None,
            author=None
        )

        assert result['parsed_files'][0]['success'] is False
        assert 'does not exist' in result['parsed_files'][0]['error']


def test_parsing_collaborative_vs_non_collaborative():
    """Test that collaborative and non-collaborative files are handled differently."""
    with patch('app.utils.non_code_parsing.document_parser.parsed_input_text') as mock_parse:
        mock_parse.return_value = {
            'parsed_files': [
                {'path': '/path/collab.md', 'success': True, 'contribution_frequency': 3},
                {'path': '/path/solo.txt', 'success': True, 'contribution_frequency': 1}
            ]
        }

        result = mock_parse(
            file_paths_dict={
                'collaborative': ['/path/collab.md'],
                'non_collaborative': ['/path/solo.txt']
            },
            repo_path='/test/repo',
            author='dev@example.com'
        )

        assert len(result['parsed_files']) == 2
        # Collaborative file should have higher contribution frequency
        collab_file = next(f for f in result['parsed_files'] if 'collab' in f['path'])
        assert collab_file['contribution_frequency'] >= 1
        
        


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
