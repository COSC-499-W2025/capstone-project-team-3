"""
Tests for the user confirmation flow when similar projects are detected.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

from app.utils.scan_utils import (
    find_similar_project,
    update_existing_project,
    run_scan_flow
)
from app.cli.similarity_manager import prompt_update_confirmation


class TestFindSimilarProject:
    """Tests for find_similar_project function (find-only, no DB update)."""
    
    def test_no_similar_project_found(self):
        """Test that None is returned when no similar projects exist."""
        with patch('app.utils.scan_utils.get_connection') as mock_conn:
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = []
            mock_conn.return_value.cursor.return_value = mock_cursor
            
            result = find_similar_project(
                current_signatures=["sig1", "sig2"],
                new_project_sig="new_sig",
                threshold=50.0
            )
            
            assert result is None
    
    def test_similar_project_found_via_jaccard(self):
        """Test detection of similar project via Jaccard similarity."""
        existing_sigs = '["sig1", "sig2", "sig3"]'
        
        with patch('app.utils.scan_utils.get_connection') as mock_conn:
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = [
                ("old_sig", "TestProject", existing_sigs, "/path", 1024, "2024-01-01")
            ]
            mock_conn.return_value.cursor.return_value = mock_cursor
            
            # Upload with 2 matching files + 1 new = 50% similarity (2/4)
            result = find_similar_project(
                current_signatures=["sig1", "sig2", "sig4"],
                new_project_sig="new_sig",
                threshold=40.0
            )
            
            assert result is not None
            assert result["project_name"] == "TestProject"
            assert result["old_project_signature"] == "old_sig"
            assert result["similarity_percentage"] == 50.0
            assert result["match_reason"] == "Jaccard similarity"
    
    def test_does_not_update_database(self):
        """Test that find_similar_project does NOT modify the database."""
        existing_sigs = '["sig1", "sig2"]'
        
        with patch('app.utils.scan_utils.get_connection') as mock_conn:
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = [
                ("old_sig", "TestProject", existing_sigs, "/path", 1024, "2024-01-01")
            ]
            mock_conn.return_value.cursor.return_value = mock_cursor
            
            find_similar_project(
                current_signatures=["sig1", "sig2"],
                new_project_sig="new_sig",
                threshold=50.0
            )
            
            # Verify no DELETE or INSERT was called
            mock_cursor.execute.assert_called_once()  # Only SELECT
            assert "DELETE" not in str(mock_cursor.execute.call_args)
            assert "INSERT" not in str(mock_cursor.execute.call_args)


class TestPromptUpdateConfirmation:
    """Tests for the CLI prompt function."""
    
    def test_user_says_yes(self):
        """Test that 'yes' returns True."""
        match_info = {
            "project_name": "ExistingProject",
            "similarity_percentage": 75.0,
            "match_reason": "Jaccard similarity"
        }
        
        with patch('builtins.input', return_value="yes"):
            result = prompt_update_confirmation(match_info, "NewProject")
            assert result is True
    
    def test_user_says_no(self):
        """Test that 'no' returns False."""
        match_info = {
            "project_name": "ExistingProject",
            "similarity_percentage": 75.0,
            "match_reason": "Jaccard similarity"
        }
        
        with patch('builtins.input', return_value="no"):
            result = prompt_update_confirmation(match_info, "NewProject")
            assert result is False
    
    def test_user_says_y(self):
        """Test that 'y' is accepted as yes."""
        match_info = {
            "project_name": "ExistingProject",
            "similarity_percentage": 75.0,
            "match_reason": "Jaccard similarity"
        }
        
        with patch('builtins.input', return_value="y"):
            result = prompt_update_confirmation(match_info, "NewProject")
            assert result is True
    
    def test_invalid_then_valid_input(self):
        """Test that invalid input is rejected and user is re-prompted."""
        match_info = {
            "project_name": "ExistingProject",
            "similarity_percentage": 75.0,
            "match_reason": "Jaccard similarity"
        }
        
        # First invalid, then valid
        with patch('builtins.input', side_effect=["maybe", "yes"]):
            result = prompt_update_confirmation(match_info, "NewProject")
            assert result is True


class TestUpdateExistingProject:
    """Tests for update_existing_project function."""
    
    def test_deletes_old_and_stores_new(self):
        """Test that update deletes old project and stores new one."""
        match_info = {
            "project_name": "TestProject",
            "old_project_signature": "old_sig",
            "old_path": "/old/path",
            "old_size_bytes": 1024,
            "old_created_at": "2024-01-01 10:00:00"
        }
        
        with patch('app.utils.scan_utils.get_connection') as mock_conn, \
             patch('app.utils.scan_utils.store_project_in_db') as mock_store:
            
            mock_cursor = MagicMock()
            mock_conn.return_value.cursor.return_value = mock_cursor
            
            result = update_existing_project(
                match_info=match_info,
                new_project_sig="new_sig",
                new_file_signatures=["sig1", "sig2"],
                new_path="/new/path",
                new_size_bytes=2048
            )
            
            # Verify DELETE was called
            mock_cursor.execute.assert_called_with(
                "DELETE FROM PROJECT WHERE project_signature = ?",
                ("old_sig",)
            )
            
            # Verify store was called with correct params
            mock_store.assert_called_once()
            call_kwargs = mock_store.call_args.kwargs
            assert call_kwargs["signature"] == "new_sig"
            assert call_kwargs["name"] == "TestProject"  # Preserved
            assert call_kwargs["created_at"] == "2024-01-01 10:00:00"  # Preserved
            
            assert result == "new_sig"


class TestRunScanFlowWithConfirmation:
    """Tests for run_scan_flow with the new confirmation behavior."""
    
    def test_new_project_stored_directly(self, tmp_path):
        """Test that truly new projects are stored without prompting."""
        file1 = tmp_path / "test.py"
        file1.write_text("print('hello')")
        
        with patch('app.utils.scan_utils.project_signature_exists', return_value=False), \
             patch('app.utils.scan_utils.find_similar_project', return_value=None), \
             patch('app.utils.scan_utils.store_project_in_db') as mock_store, \
             patch('app.utils.scan_utils.prompt_update_confirmation') as mock_prompt:
            
            result = run_scan_flow(str(tmp_path))
            
            # Prompt should NOT be called for new projects
            mock_prompt.assert_not_called()
            
            # Should store as new
            mock_store.assert_called_once()
            assert result["reason"] == "new_project"
    
    def test_user_chooses_update(self, tmp_path):
        """Test that choosing 'update' updates the existing project."""
        file1 = tmp_path / "test.py"
        file1.write_text("print('hello')")
        
        match_info = {
            "project_name": "ExistingProject",
            "old_project_signature": "old_sig",
            "old_path": str(tmp_path),
            "old_size_bytes": 100,
            "old_created_at": "2024-01-01",
            "similarity_percentage": 75.0,
            "containment_percentage": 80.0,
            "match_reason": "Jaccard similarity"
        }
        
        with patch('app.utils.scan_utils.project_signature_exists', return_value=False), \
             patch('app.utils.scan_utils.find_similar_project', return_value=match_info), \
             patch('app.utils.scan_utils.prompt_update_confirmation', return_value=True), \
             patch('app.utils.scan_utils.update_existing_project', return_value="new_sig"):
            
            result = run_scan_flow(str(tmp_path))
            
            assert result["reason"] == "updated_existing"
            assert result["updated_project"] == "ExistingProject"
    
    def test_user_chooses_new(self, tmp_path):
        """Test that choosing 'no' creates a new project."""
        file1 = tmp_path / "test.py"
        file1.write_text("print('hello')")
        
        match_info = {
            "project_name": "ExistingProject",
            "old_project_signature": "old_sig",
            "old_path": str(tmp_path),
            "old_size_bytes": 100,
            "old_created_at": "2024-01-01",
            "similarity_percentage": 75.0,
            "containment_percentage": 80.0,
            "match_reason": "Jaccard similarity"
        }
        
        with patch('app.utils.scan_utils.project_signature_exists', return_value=False), \
             patch('app.utils.scan_utils.find_similar_project', return_value=match_info), \
             patch('app.utils.scan_utils.prompt_update_confirmation', return_value=False), \
             patch('app.utils.scan_utils.store_project_in_db') as mock_store:
            
            result = run_scan_flow(str(tmp_path))
            
            # Should store as new project
            mock_store.assert_called_once()
            assert result["reason"] == "new_project"