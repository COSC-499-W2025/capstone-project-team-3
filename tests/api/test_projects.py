from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from app.api.routes.projects import router, get_projects
from app.utils.score_override_utils import ProjectNotFoundError, OverrideValidationError

# Create a test FastAPI app with the router
app = FastAPI()
app.include_router(router)


@patch("app.api.routes.projects.get_connection")
@patch("app.api.routes.projects.load_projects")
@patch("app.api.routes.projects.load_skills")
def test_get_projects_returns_expected_structure(mock_load_skills, mock_load_projects, mock_get_conn):
    """Ensure /projects returns projects with score fields and top skills."""
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

    with patch(
        "app.api.routes.projects.get_project_score_state_map",
        return_value={
            "p1": {"score_overridden": False, "score_overridden_value": None},
            "p2": {"score_overridden": True, "score_overridden_value": 0.95},
        }
    ):
        client = TestClient(app)
        response = client.get("/projects")
        assert response.status_code == 200

    data = response.json()
    assert len(data) == 2

    assert data[0]["id"] == "p1"
    assert data[0]["name"] == "Project One"
    assert data[0]["skills"] == ["Python", "FastAPI", "Docker"]
    assert data[0]["score"] == 1.0
    assert data[0]["score_original"] == 1.0
    assert data[0]["score_overridden"] is False
    assert data[0]["score_overridden_value"] is None
    assert data[0]["display_score"] == 1.0

    assert data[1]["id"] == "p2"
    assert data[1]["name"] == "Project Two"
    assert data[1]["skills"] == ["JavaScript", "React", "Node"]
    assert data[1]["score"] == 0.95
    assert data[1]["score_original"] == 2.0
    assert data[1]["score_overridden"] is True
    assert data[1]["score_overridden_value"] == 0.95
    assert data[1]["display_score"] == 0.95

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

    with patch(
        "app.api.routes.projects.get_project_score_state_map",
        return_value={"p1": {"score_overridden": False, "score_overridden_value": None}},
    ):
        client = TestClient(app)
        response = client.get("/projects")
        data = response.json()
        assert data[0]["skills"] == ["s1", "s2", "s3", "s4", "s5"]
    mock_get_conn.return_value.close.assert_called_once()


@patch("app.api.routes.projects.get_connection")
@patch("app.api.routes.projects.load_projects")
@patch("app.api.routes.projects.load_skills")
def test_get_project_returns_single_project(mock_load_skills, mock_load_projects, mock_get_conn):
    """Ensure /projects/{signature} returns a single project with score fields."""
    mock_cursor = MagicMock()
    mock_get_conn.return_value.cursor.return_value = mock_cursor

    mock_load_projects.return_value = [
        ("sig-1", "Project One", 0.65, "2020-01-01", "2020-02-01")
    ]
    mock_load_skills.return_value = {"sig-1": ["Python", "FastAPI", "Docker", "SQL", "AWS", "Extra"]}

    with patch(
        "app.api.routes.projects.get_project_score_state_map",
        return_value={"sig-1": {"score_overridden": True, "score_overridden_value": 0.82}},
    ):
        client = TestClient(app)
        response = client.get("/projects/sig-1")
        assert response.status_code == 200
        data = response.json()

    assert data["id"] == "sig-1"
    assert data["name"] == "Project One"
    assert data["skills"] == ["Python", "FastAPI", "Docker", "SQL", "AWS"]
    assert data["score"] == 0.82
    assert data["score_original"] == 0.65
    assert data["score_overridden"] is True
    assert data["score_overridden_value"] == 0.82
    assert data["display_score"] == 0.82
    mock_get_conn.return_value.close.assert_called_once()


@patch("app.api.routes.projects.get_connection")
@patch("app.api.routes.projects.load_projects", return_value=[])
def test_get_project_not_found(mock_load_projects, mock_get_conn):
    """Ensure /projects/{signature} returns 404 when project is missing."""
    client = TestClient(app)
    response = client.get("/projects/unknown")
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"
    mock_get_conn.return_value.close.assert_called_once()


@patch("app.api.routes.projects.compute_project_breakdown")
def test_get_score_breakdown_endpoint(mock_breakdown):
    mock_breakdown.return_value = {
        "project_signature": "sig-1",
        "name": "Project One",
        "score": 0.8,
        "breakdown": {"final_score": 0.8},
    }

    client = TestClient(app)
    response = client.get("/projects/sig-1/score-breakdown")
    assert response.status_code == 200
    assert response.json()["breakdown"]["final_score"] == 0.8


@patch("app.api.routes.projects.compute_project_breakdown", side_effect=ProjectNotFoundError("Project not found"))
def test_get_score_breakdown_not_found(mock_breakdown):
    client = TestClient(app)
    response = client.get("/projects/missing/score-breakdown")
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


@patch("app.api.routes.projects.preview_project_score_override")
def test_preview_score_override_endpoint(mock_preview):
    mock_preview.return_value = {
        "project_signature": "sig-1",
        "current_score": 0.7,
        "preview_score": 0.9,
        "exclude_metrics": ["total_lines"],
        "breakdown": {"final_score": 0.9},
    }

    client = TestClient(app)
    response = client.post(
        "/projects/sig-1/score-override/preview",
        json={"exclude_metrics": ["total_lines"]},
    )
    assert response.status_code == 200
    assert response.json()["preview_score"] == 0.9
    mock_preview.assert_called_once_with(
        project_signature="sig-1",
        exclude_metrics=["total_lines"],
    )


@patch(
    "app.api.routes.projects.preview_project_score_override",
    side_effect=OverrideValidationError("At least one code metric must remain after exclusions"),
)
def test_preview_score_override_validation_error(mock_preview):
    client = TestClient(app)
    response = client.post(
        "/projects/sig-1/score-override/preview",
        json={"exclude_metrics": ["total_commits"]},
    )
    assert response.status_code == 400
    assert "At least one code metric must remain" in response.json()["detail"]


@patch("app.api.routes.projects.apply_project_score_override")
def test_apply_score_override_endpoint(mock_apply):
    mock_apply.return_value = {
        "project_signature": "sig-1",
        "display_score": 0.93,
        "score_overridden": True,
        "score_overridden_value": 0.93,
        "exclude_metrics": ["total_lines"],
    }

    client = TestClient(app)
    response = client.post(
        "/projects/sig-1/score-override",
        json={"exclude_metrics": ["total_lines"]},
    )
    assert response.status_code == 200
    assert response.json()["display_score"] == 0.93
    assert response.json()["score_overridden"] is True
    mock_apply.assert_called_once_with(
        project_signature="sig-1",
        exclude_metrics=["total_lines"],
    )


@patch("app.api.routes.projects.clear_project_score_override")
def test_clear_score_override_endpoint(mock_clear):
    mock_clear.return_value = {
        "project_signature": "sig-1",
        "display_score": 0.7,
        "score_overridden": False,
        "score_overridden_value": None,
    }

    client = TestClient(app)
    response = client.post("/projects/sig-1/score-override/clear")
    assert response.status_code == 200
    assert response.json()["display_score"] == 0.7
    assert response.json()["score_overridden"] is False
    mock_clear.assert_called_once_with(project_signature="sig-1")
