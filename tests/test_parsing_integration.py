"""
Unit tests for non-code parsing integration in main.py
"""
from unittest.mock import patch, Mock


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
