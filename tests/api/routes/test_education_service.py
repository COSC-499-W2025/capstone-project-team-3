import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
from app.main import app

# Create client once at module level (app is already initialized)
client = TestClient(app)
class TestInstitutionList:
    """Test suite for institution list endpoint."""
    
    @patch("urllib.request.urlopen")
    def test_get_institutions_list_success(self, mock_urlopen):
        """Test getting full list of institutions."""
        # Mock response for first batch
        def mock_response_generator(*args, **kwargs):
            url = str(args[0]) if args else str(kwargs.get('url', ''))
            mock_response = MagicMock()
            
            if "offset=0" in url or "offset" not in url:
                # First batch with 3 institutions
                mock_response.read.return_value = json.dumps({
                    "success": True,
                    "result": {
                        "records": [
                            {"institution_name_e": "Acadia University"},
                            {"institution_name_e": "Algonquin College"},
                            {"institution_name_e": "University of Toronto"}
                        ]
                    }
                }).encode()
            else:
                # Subsequent batches empty
                mock_response.read.return_value = json.dumps({
                    "success": True,
                    "result": {"records": []}
                }).encode()
            
            mock_response.__enter__ = lambda s: s
            mock_response.__exit__ = MagicMock()
            return mock_response
        
        mock_urlopen.side_effect = mock_response_generator
        
        response = client.get("/api/institutions/list")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["count"] == 3
        assert len(data["institutions"]) == 3
        assert "University of Toronto" in data["institutions"]

    @patch("urllib.request.urlopen")
    def test_get_institutions_list_empty(self, mock_urlopen):
        """Test getting list when no institutions are returned."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "success": True,
            "result": {"records": []}
        }).encode()
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock()
        mock_urlopen.return_value = mock_response
        
        response = client.get("/api/institutions/list")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["count"] == 0
        assert data["institutions"] == []

class TestCanadianInstitutionsAPI:
    """Test suite for the Canadian institutions API utility functions."""
    
    @patch("urllib.request.urlopen")
    def test_search_institutions_api_success(self, mock_urlopen):
        """Test search_institutions makes correct API call and parses response."""
        from app.utils.canadian_institutions_api import search_institutions
        
        # Mock API response
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "success": True,
            "result": {
                "records": [
                    {
                        "institution_name_e": "University of Toronto",
                        "program_of_study_e": "Computer Science",
                        "academic_level_area_of_study_e": "Bachelor",
                        "program_type_e": "Regular"
                    },
                    {
                        "institution_name_e": "University of Toronto",
                        "program_of_study_e": "Engineering",
                        "academic_level_area_of_study_e": "Bachelor",
                        "program_type_e": "CO-OP"
                    }
                ]
            }
        }).encode()
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock()
        mock_urlopen.return_value = mock_response
        
        results = search_institutions(query="Toronto", limit=10)
        
        assert len(results) == 1
        assert results[0]["name"] == "University of Toronto"
        assert len(results[0]["programs"]) == 2

    @patch("urllib.request.urlopen")
    def test_search_institutions_simple_api_success(self, mock_urlopen):
        """Test search_institutions_simple returns only names."""
        from app.utils.canadian_institutions_api import search_institutions_simple
        
        # Mock API response
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "success": True,
            "result": {
                "records": [
                    {"institution_name_e": "University of Toronto"},
                    {"institution_name_e": "University of British Columbia"},
                    {"institution_name_e": "University of Toronto"}  # Duplicate
                ]
            }
        }).encode()
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock()
        mock_urlopen.return_value = mock_response
        
        results = search_institutions_simple(query="University", limit=50)
        
        assert len(results) == 2  # Duplicates removed
        assert "University of Toronto" in results
        assert "University of British Columbia" in results

    @patch("urllib.request.urlopen")
    def test_search_institutions_api_failure(self, mock_urlopen):
        """Test search_institutions handles API failure gracefully."""
        from app.utils.canadian_institutions_api import search_institutions
        
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "success": False,
            "error": "API error"
        }).encode()
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock()
        mock_urlopen.return_value = mock_response
        
        results = search_institutions(query="test", limit=10)
        
        assert results == []

    @patch("urllib.request.urlopen")
    def test_get_all_institutions_batching(self, mock_urlopen):
        """Test get_all_institutions fetches multiple batches."""
        from app.utils.canadian_institutions_api import get_all_institutions
        
        # Mock multiple API responses for batching
        def mock_response_generator(*args, **kwargs):
            url = str(args[0]) if args else str(kwargs.get('url', ''))
            mock_response = MagicMock()
            
            if "offset=0" in url or "offset" not in url:
                mock_response.read.return_value = json.dumps({
                    "success": True,
                    "result": {
                        "records": [
                            {"institution_name_e": "University A"},
                            {"institution_name_e": "University B"}
                        ]
                    }
                }).encode()
            else:
                # Return empty for subsequent calls
                mock_response.read.return_value = json.dumps({
                    "success": True,
                    "result": {"records": []}
                }).encode()
            
            mock_response.__enter__ = lambda s: s
            mock_response.__exit__ = MagicMock()
            return mock_response
        
        mock_urlopen.side_effect = mock_response_generator
        
        results = get_all_institutions()
        
        assert len(results) == 2
        assert "University A" in results
        assert "University B" in results