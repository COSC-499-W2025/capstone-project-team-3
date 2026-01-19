from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from app.api.routes.projects import router, get_projects

# Create a test FastAPI app with the router
app = FastAPI()
app.include_router(router)


@patch("app.api.routes.projects.get_connection")
@patch("app.api.routes.projects.load_projects")
@patch("app.api.routes.projects.load_skills")
def test_get_projects_returns_expected_structure(mock_load_skills, mock_load_projects, mock_get_conn):
    """Ensure /projects returns projects with id, name, and top skills."""
    # Mock DB cursor
    mock_cursor = MagicMock()
    mock_get_conn.return_value.cursor.return_value = mock_cursor

    # Mock projects data
    mock_load_projects.return_value = [
        ("p1", "Project One", 1, "2020-01-01", "2020-02-01"),
        ("p2", "Project Two", 2, "2021-01-01", "2021-02-01")
    ]
    # Mock skills mapping
    mock_load_skills.return_value = {
        "p1": ["Python", "FastAPI", "Docker"],
        "p2": ["JavaScript", "React", "Node"]
    }

    client = TestClient(app)
    response = client.get("/projects")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2

    assert data[0]["id"] == "p1"
    assert data[0]["name"] == "Project One"
    assert data[0]["skills"] == ["Python", "FastAPI", "Docker"]

    assert data[1]["id"] == "p2"
    assert data[1]["name"] == "Project Two"
    assert data[1]["skills"] == ["JavaScript", "React", "Node"]

    # Ensure DB connection is closed
    mock_get_conn.return_value.close.assert_called_once()


@patch("app.api.routes.projects.get_connection")
@patch("app.api.routes.projects.load_projects", return_value=[])
@patch("app.api.routes.projects.load_skills", return_value={})
def test_get_projects_empty(mock_load_skills, mock_load_projects, mock_get_conn):
    """Ensure /projects returns empty list if no projects exist."""
    client = TestClient(app)
    response = client.get("/projects")
    assert response.status_code == 200
    assert response.json() == []
    mock_get_conn.return_value.close.assert_called_once()


@patch("app.api.routes.projects.get_connection")
@patch("app.api.routes.projects.load_projects")
@patch("app.api.routes.projects.load_skills")
def test_get_projects_skills_limited_to_five(mock_load_skills, mock_load_projects, mock_get_conn):
    """Ensure only top 5 skills are returned per project."""
    mock_cursor = MagicMock()
    mock_get_conn.return_value.cursor.return_value = mock_cursor

    mock_load_projects.return_value = [("p1", "Project One", 1, "2020-01-01", "2020-02-01")]
    mock_load_skills.return_value = {"p1": ["s1", "s2", "s3", "s4", "s5", "s6", "s7"]}

    client = TestClient(app)
    response = client.get("/projects")
    data = response.json()
    assert data[0]["skills"] == ["s1", "s2", "s3", "s4", "s5"]
    mock_get_conn.return_value.close.assert_called_once()
