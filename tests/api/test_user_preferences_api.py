import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from app.api.routes.user_preferences import router

# Create a test FastAPI app with the router
app = FastAPI()
app.include_router(router)

client = TestClient(app)

@patch("app.api.routes.user_preferences.get_connection")
def test_get_user_preferences_not_found(mock_get_conn):
    """Test GET when no preferences exist."""
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_get_conn.return_value.cursor.return_value = mock_cursor
    
    response = client.get("/user-preferences")
    assert response.status_code == 404
    assert "No user preferences found" in response.json()["detail"]
    mock_get_conn.return_value.close.assert_called_once()

@patch("app.api.routes.user_preferences.get_connection")
def test_save_user_preferences(mock_get_conn):
    """Test POST to save user preferences."""
    mock_cursor = MagicMock()
    mock_get_conn.return_value.cursor.return_value = mock_cursor
    
    payload = {
        "name": "John Doe",
        "email": "john@example.com",
        "github_user": "johndoe",
        "education": "Bachelor's",
        "industry": "Technology",
        "job_title": "Software Engineer"
    }
    
    response = client.post("/user-preferences", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "saved successfully" in response.json()["message"]
    
    mock_cursor.execute.assert_called_once()
    mock_get_conn.return_value.commit.assert_called_once()
    mock_get_conn.return_value.close.assert_called_once()

@patch("app.api.routes.user_preferences.get_connection")
def test_get_user_preferences_success(mock_get_conn):
    """Test GET after saving preferences."""
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (
        "Jane Smith",
        "jane@example.com",
        "janesmith",
        "Master's",
        "Finance",
        "Data Scientist",
        "{}"  # education_details as JSON string, can be empty for this test
    )
    mock_get_conn.return_value.cursor.return_value = mock_cursor
    
    response = client.get("/user-preferences")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Jane Smith"
    assert data["email"] == "jane@example.com"
    assert data["github_user"] == "janesmith"
    assert data["education"] == "Master's"
    assert data["industry"] == "Finance"
    assert data["job_title"] == "Data Scientist"
    assert data["education_details"] == "{}"
    mock_get_conn.return_value.close.assert_called_once()

@patch("app.api.routes.user_preferences.get_connection")
def test_update_user_preferences(mock_get_conn):
    """Test updating existing preferences."""
    mock_cursor = MagicMock()
    mock_get_conn.return_value.cursor.return_value = mock_cursor
    
    updated_payload = {
        "name": "Alice Updated",
        "email": "alice@example.com",
        "github_user": "alice",
        "education": "Master's",
        "industry": "Technology",
        "job_title": "Senior Developer",
        "education_details": [{"institution": "Updated University", "degree": "Master's","program":"Economics", "start_date": "2015", "end_date": "2020", "gpa": 2.6}]
    }
    
    response = client.post("/user-preferences", json=updated_payload)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    
    mock_cursor.execute.assert_called_once()
    mock_get_conn.return_value.commit.assert_called_once()
    mock_get_conn.return_value.close.assert_called_once()
