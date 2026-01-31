import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, mock_open
from app.api.routes.portfolio import router

# Create a test FastAPI app with the portfolio router
app = FastAPI()
app.include_router(router, prefix="/api")
client = TestClient(app)

@pytest.fixture
def mock_portfolio_data():
    """Mock portfolio data structure."""
    return {
        "user": {
            "name": "Test User",
            "email": "test@example.com",
            "github_user": "testuser",
            "links": [{"label": "GitHub", "url": "https://github.com/testuser"}],
            "education": "Test University",
            "job_title": "Developer"
        },
        "overview": {
            "total_projects": 3,
            "avg_score": 0.85,
            "total_skills": 15,
            "total_languages": 4,
            "total_lines": 5000
        },
        "projects": [
            {
                "id": "proj1",
                "title": "Test Project 1",
                "rank": 0.9,
                "summary": "A test project",
                "dates": "Jan 2024 – Mar 2024",
                "type": "GitHub",
                "metrics": {
                    "total_commits": 25, 
                    "total_lines": 2000,
                    "technical_keywords": ["API", "testing"],
                    "languages": ["Python", "JavaScript"]
                },
                "skills": ["Python", "FastAPI", "Problem Solving"]
            }
        ],
        "skills_timeline": [
            {"skill": "Python", "first_used": "2024-01-15", "year": 2024}
        ],
        "project_type_analysis": {
            "github": {"count": 2, "stats": {"avg_score": 0.88}},
            "local": {"count": 1, "stats": {"avg_score": 0.75}}
        },
        "graphs": {
            "language_distribution": {"Python": 2, "JavaScript": 1},
            "complexity_distribution": {"distribution": {"small": 1, "medium": 2, "large": 0}},
            "score_distribution": {"distribution": {"excellent": 1, "good": 2, "fair": 0, "poor": 0}},
            "monthly_activity": {"2024-01": 2, "2024-02": 1},
            "top_skills": {"Python": 3, "FastAPI": 2}
        },
        "metadata": {
            "generated_at": "2024-01-01T10:00:00",
            "total_projects": 3,
            "filtered": True,
            "project_ids": ["proj1", "proj2", "proj3"]
        }
    }


class TestPortfolioEndpoints:
    """Test suite for portfolio API endpoints."""
    
    def test_get_portfolio_all_projects(self, mock_portfolio_data):
        """Test GET /portfolio endpoint without filters (all projects)."""
        with patch('app.api.routes.portfolio.build_portfolio_model') as mock_build:
            mock_build.return_value = mock_portfolio_data
            
            response = client.get("/api/portfolio")
            
            assert response.status_code == 200
            data = response.json()
            
            # Check required fields
            assert "user" in data
            assert "overview" in data
            assert "projects" in data
            assert "skills_timeline" in data
            assert "project_type_analysis" in data
            assert "graphs" in data
            assert "metadata" in data
            
            # Check metadata for no filtering
            assert data["metadata"]["total_projects"] == 3
            assert data["metadata"]["filtered"] == True  # Mock data has filtered=True
            
            # Check headers
            assert "X-Portfolio-Projects" in response.headers
            assert "X-Portfolio-Generated" in response.headers
            assert "X-Portfolio-Filtered" in response.headers
            
            # Verify mock was called with None (no filtering)
            mock_build.assert_called_once_with(project_ids=None)

    def test_get_portfolio_with_project_ids(self, mock_portfolio_data):
        """Test GET /portfolio endpoint with specific project IDs."""
        with patch('app.api.routes.portfolio.build_portfolio_model') as mock_build:
            mock_build.return_value = mock_portfolio_data
            
            response = client.get("/api/portfolio?project_ids=proj1,proj2,proj3")
            
            assert response.status_code == 200
            data = response.json()
            
            # Check that data is returned properly
            assert "overview" in data
            assert data["overview"]["total_projects"] == 3
            assert len(data["projects"]) == 1  # Mock data has 1 project
            
            # Verify mock was called with parsed project IDs
            mock_build.assert_called_once_with(project_ids=["proj1", "proj2", "proj3"])

    def test_get_portfolio_with_whitespace_project_ids(self):
        """Test GET /portfolio endpoint with project IDs containing whitespace."""
        with patch('app.api.routes.portfolio.build_portfolio_model') as mock_build:
            mock_build.return_value = {
                "user": {"name": "Test User"},
                "overview": {"total_projects": 2},
                "projects": [],
                "skills_timeline": [],
                "project_type_analysis": {"github": {"count": 0}, "local": {"count": 0}},
                "graphs": {},
                "metadata": {"generated_at": "2024-01-01T10:00:00", "total_projects": 2, "filtered": True}
            }
            
            response = client.get("/api/portfolio?project_ids= proj1 , proj2 ,")
            
            assert response.status_code == 200
            
            # Verify whitespace was stripped and empty strings removed
            mock_build.assert_called_once_with(project_ids=["proj1", "proj2"])

    def test_get_portfolio_empty_project_ids(self):
        """Test GET /portfolio endpoint with empty project_ids string."""
        with patch('app.api.routes.portfolio.build_portfolio_model') as mock_build:
            mock_build.return_value = {
                "user": {"name": "Test User"},
                "overview": {"total_projects": 3},
                "projects": [],
                "skills_timeline": [],
                "project_type_analysis": {"github": {"count": 0}, "local": {"count": 0}},
                "graphs": {},
                "metadata": {"generated_at": "2024-01-01T10:00:00", "total_projects": 3, "filtered": False}
            }
            
            response = client.get("/api/portfolio?project_ids=")
            
            assert response.status_code == 200
            
            # Empty string should be treated as None (no filtering)
            mock_build.assert_called_once_with(project_ids=None)

    def test_get_portfolio_database_error(self):
        """Test GET /portfolio endpoint with database error."""
        with patch('app.api.routes.portfolio.build_portfolio_model') as mock_build:
            mock_build.side_effect = Exception("Database connection failed")
            
            response = client.get("/api/portfolio")
            
            assert response.status_code == 500
            assert "Database connection failed" in response.json()["detail"]

    def test_get_portfolio_response_headers(self, mock_portfolio_data):
        """Test GET /portfolio endpoint response headers are set correctly."""
        with patch('app.api.routes.portfolio.build_portfolio_model') as mock_build:
            mock_build.return_value = mock_portfolio_data
            
            response = client.get("/api/portfolio?project_ids=proj1,proj2")
            
            assert response.status_code == 200
            
            # Check custom headers
            assert response.headers["X-Portfolio-Projects"] == "3"
            assert response.headers["X-Portfolio-Generated"] == "2024-01-01T10:00:00"
            assert response.headers["X-Portfolio-Filtered"] == "True"
            assert response.headers["Content-Type"] == "application/json"


class TestPortfolioDashboardEndpoints:
    """Test suite for portfolio dashboard UI endpoints."""
    
    def test_portfolio_dashboard_success(self):
        """Test GET /portfolio-dashboard endpoint returns HTML when file exists."""
        mock_html_content = "<html><head><title>Portfolio Dashboard</title></head><body>Dashboard Content</body></html>"
        
        with patch('os.path.exists') as mock_exists, \
             patch('builtins.open', mock_open(read_data=mock_html_content)):
            mock_exists.return_value = True
            
            response = client.get("/api/portfolio-dashboard")
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/html; charset=utf-8"
            assert "Portfolio Dashboard" in response.text
            assert "Dashboard Content" in response.text

    def test_portfolio_dashboard_file_not_found(self):
        """Test GET /portfolio-dashboard endpoint when HTML file doesn't exist."""
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = False
            
            response = client.get("/api/portfolio-dashboard")
            
            assert response.status_code == 404
            assert "Portfolio Dashboard not found" in response.text

    def test_portfolio_js_success(self):
        """Test GET /static/portfolio.js endpoint returns JavaScript when file exists."""
        mock_js_content = "// Portfolio Dashboard JavaScript\nclass PortfolioDashboard { constructor() {} }"
        
        with patch('os.path.exists') as mock_exists, \
             patch('builtins.open', mock_open(read_data=mock_js_content)):
            mock_exists.return_value = True
            
            response = client.get("/api/static/portfolio.js")
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/javascript"
            assert "PortfolioDashboard" in response.text
            assert "constructor" in response.text

    def test_portfolio_js_file_not_found(self):
        """Test GET /static/portfolio.js endpoint when JS file doesn't exist."""
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = False
            
            response = client.get("/api/static/portfolio.js")
            
            assert response.status_code == 404
            assert "JavaScript file not found" in response.json()["detail"]


class TestPortfolioDataStructure:
    """Test suite for portfolio data structure validation."""
    
    def test_portfolio_data_structure_validation(self, mock_portfolio_data):
        """Test that portfolio response contains all required data structures."""
        with patch('app.api.routes.portfolio.build_portfolio_model') as mock_build:
            mock_build.return_value = mock_portfolio_data
            
            response = client.get("/api/portfolio")
            data = response.json()
            
            # Test user structure
            user = data["user"]
            assert "name" in user
            assert "email" in user
            
            # Test overview structure
            overview = data["overview"]
            assert "total_projects" in overview
            assert "avg_score" in overview
            assert "total_skills" in overview
            assert "total_languages" in overview
            assert "total_lines" in overview
            
            # Test projects structure
            projects = data["projects"]
            assert len(projects) > 0
            project = projects[0]
            assert "id" in project
            assert "title" in project
            assert "rank" in project
            assert "metrics" in project
            assert "skills" in project
            
            # Test graphs structure
            graphs = data["graphs"]
            assert "language_distribution" in graphs
            assert "complexity_distribution" in graphs
            assert "score_distribution" in graphs
            assert "monthly_activity" in graphs
            assert "top_skills" in graphs
            
            # Test metadata structure
            metadata = data["metadata"]
            assert "generated_at" in metadata
            assert "total_projects" in metadata
            assert "filtered" in metadata

def test_edit_portfolio_batch_success():
    with patch("app.api.routes.portfolio.get_connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_db = mock_conn.return_value
        mock_db.cursor.return_value = mock_cursor

        # Simulate successful update
        mock_cursor.rowcount = 2

        payload = {
            "edits": [
                {
                    "project_signature": "sig1",
                    "project_name": "Batch Name 1",
                    "rank": 0.8
                },
                {
                    "project_signature": "sig2",
                    "project_summary": "Batch summary 2",
                    "rank": 0.7
                }
            ]
        }

        response = client.post("/api/portfolio/edit", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert set(data["projects_updated"]) == {"sig1", "sig2"}
        assert data["count"] == 2

        mock_db.commit.assert_called_once()
        mock_cursor.execute.assert_called_once()

def test_edit_portfolio_batch_not_found():
    with patch("app.api.routes.portfolio.get_connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_db = mock_conn.return_value
        mock_db.cursor.return_value = mock_cursor

        # Simulate no rows updated
        mock_cursor.rowcount = 0

        payload = {
            "edits": [
                {
                    "project_signature": "missing_sig",
                    "project_name": "Should not update"
                }
            ]
        }

        response = client.post("/api/portfolio/edit", json=payload)
        assert response.status_code == 404
        assert response.json()["detail"] == "No projects found"
        mock_db.commit.assert_not_called()

def test_edit_portfolio_batch_partial_fields():
    with patch("app.api.routes.portfolio.get_connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_db = mock_conn.return_value
        mock_db.cursor.return_value = mock_cursor

        mock_cursor.rowcount = 1

        payload = {
            "edits": [
                {
                    "project_signature": "sig1",
                    "project_name": "Only Name"
                }
            ]
        }

        response = client.post("/api/portfolio/edit", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["projects_updated"] == ["sig1"]
        assert data["count"] == 1

        mock_db.commit.assert_called_once()
        mock_cursor.execute.assert_called_once()

def test_edit_portfolio_batch_db_error():
    with patch("app.api.routes.portfolio.get_connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_db = mock_conn.return_value
        mock_db.cursor.return_value = mock_cursor

        mock_cursor.execute.side_effect = Exception("DB write failed")

        payload = {
            "edits": [
                {
                    "project_signature": "sig1",
                    "project_name": "Crash Me"
                }
            ]
        }

        response = client.post("/api/portfolio/edit", json=payload)
        assert response.status_code == 500
        assert "Failed to edit projects" in response.json()["detail"]
        mock_db.rollback.assert_called_once()

def test_edit_portfolio_batch_no_fields():
    with patch("app.api.routes.portfolio.get_connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_db = mock_conn.return_value
        mock_db.cursor.return_value = mock_cursor

        # No fields provided to edit
        payload = {
            "edits": [
                {
                    "project_signature": "sig1"
                }
            ]
        }

        response = client.post("/api/portfolio/edit", json=payload)
        assert response.status_code == 400
        assert "No fields provided for project" in response.json()["detail"]
        mock_db.commit.assert_not_called()
