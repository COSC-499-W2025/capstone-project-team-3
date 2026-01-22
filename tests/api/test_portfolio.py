import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch
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
                "metrics": {"total_commits": 25, "total_lines": 2000},
                "technical_skills": ["Python", "FastAPI"],
                "soft_skills": ["Problem Solving"],
                "all_skills": ["Python", "FastAPI", "Problem Solving"]
            }
        ],
        "skills_timeline": [
            {"skill": "Python", "project": "Test Project 1", "date": "2024-01-15", "source": "technical"}
        ],
        "project_type_analysis": {
            "github": {"count": 2, "stats": {"avg_score": 0.88}},
            "local": {"count": 1, "stats": {"avg_score": 0.75}}
        },
        "metadata": {
            "generated_at": "2024-01-01T10:00:00",
            "total_projects": 3,
            "filtered": True,
            "project_ids": ["proj1", "proj2", "proj3"]
        }
    }

def test_post_portfolio_generate(mock_portfolio_data):
    """Test POST /portfolio/generate endpoint."""
    with patch('app.api.routes.portfolio.build_portfolio_model') as mock_build:
        mock_build.return_value = mock_portfolio_data
        
        payload = {"project_ids": ["proj1", "proj2", "proj3"]}
        response = client.post("/api/portfolio/generate", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "user" in data
        assert "overview" in data
        assert "projects" in data
        assert "skills_timeline" in data
        assert "project_type_analysis" in data
        assert "metadata" in data
        
        # Check metadata
        assert data["metadata"]["filtered"] == True
        assert len(data["metadata"]["project_ids"]) == 3
        
        # Check headers
        assert "X-Portfolio-Projects" in response.headers
        assert "X-Portfolio-Generated" in response.headers

def test_post_portfolio_generate_empty_projects():
    """Test POST /portfolio/generate with empty project_ids - should return all projects."""
    with patch('app.api.routes.portfolio.build_portfolio_model') as mock_build:
        # Mock return for all projects (empty filter)
        mock_portfolio = {
            "user": {"name": "Test User"},
            "overview": {"total_projects": 3},
            "projects": [{"id": "proj1"}, {"id": "proj2"}, {"id": "proj3"}],
            "metadata": {"generated_at": "2025-01-01T00:00:00", "filtered": False}
        }
        mock_build.return_value = mock_portfolio
        
        payload = {"project_ids": []}
        response = client.post("/api/portfolio/generate", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["overview"]["total_projects"] == 3
        assert len(data["projects"]) == 3
        assert data["metadata"]["filtered"] == False
        # Verify mock was called with empty list (treated as None internally)
        mock_build.assert_called_once_with(project_ids=[])

def test_post_portfolio_generate_null_projects():
    """Test POST /portfolio/generate with null project_ids - should return all projects.""" 
    with patch('app.api.routes.portfolio.build_portfolio_model') as mock_build:
        mock_portfolio = {
            "user": {"name": "Test User"},
            "overview": {"total_projects": 3}, 
            "projects": [{"id": "proj1"}, {"id": "proj2"}, {"id": "proj3"}],
            "metadata": {"generated_at": "2025-01-01T00:00:00", "filtered": False}
        }
        mock_build.return_value = mock_portfolio
        
        payload = {"project_ids": None}
        response = client.post("/api/portfolio/generate", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["overview"]["total_projects"] == 3
        assert len(data["projects"]) == 3
        assert data["metadata"]["filtered"] == False
        mock_build.assert_called_once_with(project_ids=None)

def test_portfolio_generation_database_error():
    """Test portfolio generation with database error."""
    with patch('app.api.routes.portfolio.build_portfolio_model') as mock_build:
        mock_build.side_effect = Exception("Database connection failed")
        
        payload = {"project_ids": ["proj1"]}
        response = client.post("/api/portfolio/generate", json=payload)
        
        assert response.status_code == 500
        assert "Database connection failed" in response.json()["detail"]