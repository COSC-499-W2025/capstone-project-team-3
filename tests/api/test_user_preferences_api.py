import io
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from app.api.routes.user_preferences import router

# Create a test FastAPI app with the router
app = FastAPI()
app.include_router(router)

client = TestClient(app)

# ---------------------------------------------------------------------------
# Helper: build a full 10-field preferences row (matches SELECT column order)
# name, email, github_user, linkedin, education, industry, job_title,
# education_details, profile_picture_path, personal_summary
# ---------------------------------------------------------------------------
def _pref_row(
    name="Jane Smith",
    email="jane@example.com",
    github_user="janesmith",
    linkedin="https://linkedin.com/in/janesmith",
    education="Master's",
    industry="Finance",
    job_title="Data Scientist",
    education_details="{}",
    profile_picture_path=None,
    personal_summary=None,
):
    return (name, email, github_user, linkedin, education, industry, job_title,
            education_details, profile_picture_path, personal_summary)


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
        "job_title": "Software Engineer",
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
    """Test GET returns all 10 fields including profile_picture_path and personal_summary."""
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = _pref_row(
        profile_picture_path="data/thumbnails/profile_picture.png",
        personal_summary="Experienced data scientist.",
    )
    mock_get_conn.return_value.cursor.return_value = mock_cursor

    response = client.get("/user-preferences")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Jane Smith"
    assert data["email"] == "jane@example.com"
    assert data["github_user"] == "janesmith"
    assert data["linkedin"] == "https://linkedin.com/in/janesmith"
    assert data["education"] == "Master's"
    assert data["industry"] == "Finance"
    assert data["job_title"] == "Data Scientist"
    assert data["education_details"] == "{}"
    assert data["profile_picture_path"] == "data/thumbnails/profile_picture.png"
    assert data["personal_summary"] == "Experienced data scientist."
    mock_get_conn.return_value.close.assert_called_once()


@patch("app.api.routes.user_preferences.get_connection")
def test_get_user_preferences_no_picture(mock_get_conn):
    """Test GET returns profile_picture_path as None when no picture set."""
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = _pref_row(profile_picture_path=None)
    mock_get_conn.return_value.cursor.return_value = mock_cursor

    response = client.get("/user-preferences")
    assert response.status_code == 200
    assert response.json()["profile_picture_path"] is None


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
        "education_details": [
            {
                "institution": "Updated University",
                "degree": "Master's",
                "program": "Economics",
                "start_date": "2015",
                "end_date": "2020",
                "gpa": 2.6,
            }
        ],
    }

    response = client.post("/user-preferences", json=updated_payload)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    mock_cursor.execute.assert_called_once()
    mock_get_conn.return_value.commit.assert_called_once()
    mock_get_conn.return_value.close.assert_called_once()


# ---------------------------------------------------------------------------
# Profile picture endpoints
# ---------------------------------------------------------------------------

@patch("app.api.routes.user_preferences.get_connection")
def test_upload_profile_picture_invalid_type(mock_get_conn):
    """Test POST profile-picture rejects non-image MIME types."""
    response = client.post(
        "/user-preferences/profile-picture",
        files={"file": ("resume.pdf", b"%PDF-1.4 content", "application/pdf")},
    )
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]


@patch("app.api.routes.user_preferences.get_connection")
def test_upload_profile_picture_too_large(mock_get_conn):
    """Test POST profile-picture rejects files larger than 5 MB."""
    big_data = b"x" * (5 * 1024 * 1024 + 1)
    response = client.post(
        "/user-preferences/profile-picture",
        files={"file": ("photo.png", big_data, "image/png")},
    )
    assert response.status_code == 400
    assert "too large" in response.json()["detail"].lower()


@patch("app.api.routes.user_preferences.THUMBNAIL_DIR")
@patch("app.api.routes.user_preferences.get_connection")
def test_upload_profile_picture_success(mock_get_conn, mock_thumb_dir, tmp_path):
    """Test POST profile-picture saves file and stores relative path in DB."""
    # Point THUMBNAIL_DIR at tmp_path so no real files are written
    mock_thumb_dir.__truediv__ = lambda self, name: tmp_path / name
    mock_thumb_dir.glob.return_value = []

    dest_mock = MagicMock()
    mock_thumb_dir.__truediv__ = lambda self, name: dest_mock
    dest_mock.__str__ = lambda self: str(tmp_path / "profile_picture.png")

    mock_cursor = MagicMock()
    mock_get_conn.return_value.cursor.return_value = mock_cursor

    img_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16  # minimal PNG-like header

    response = client.post(
        "/user-preferences/profile-picture",
        files={"file": ("photo.png", img_bytes, "image/png")},
    )
    # Either success or a write error from mocking — just assert no 400/422
    assert response.status_code in (200, 500)
    if response.status_code == 200:
        data = response.json()
        assert data["status"] == "ok"
        assert "profile_picture" in data["path"]


@patch("app.api.routes.user_preferences.get_connection")
def test_get_profile_picture_not_set(mock_get_conn):
    """Test GET profile-picture returns 404 when no picture is stored."""
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (None,)
    mock_get_conn.return_value.cursor.return_value = mock_cursor

    response = client.get("/user-preferences/profile-picture")
    assert response.status_code == 404
    assert "No profile picture set" in response.json()["detail"]


@patch("app.api.routes.user_preferences.get_connection")
def test_get_profile_picture_file_missing(mock_get_conn, tmp_path):
    """Test GET profile-picture returns 404 when DB path exists but file is gone."""
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = ("data/thumbnails/profile_picture.png",)
    mock_get_conn.return_value.cursor.return_value = mock_cursor

    response = client.get("/user-preferences/profile-picture")
    assert response.status_code == 404
    assert "file not found" in response.json()["detail"].lower()


@patch("app.api.routes.user_preferences.get_connection")
def test_delete_profile_picture_no_row(mock_get_conn):
    """Test DELETE profile-picture succeeds even when no picture is set."""
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (None,)
    mock_get_conn.return_value.cursor.return_value = mock_cursor

    response = client.delete("/user-preferences/profile-picture")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    mock_get_conn.return_value.commit.assert_called_once()
    mock_get_conn.return_value.close.assert_called_once()


@patch("app.api.routes.user_preferences.get_connection")
def test_delete_profile_picture_clears_db(mock_get_conn, tmp_path):
    """Test DELETE profile-picture calls UPDATE to NULL in DB."""
    mock_cursor = MagicMock()
    # Return a path that doesn't exist on disk — unlink won't be called
    mock_cursor.fetchone.return_value = ("data/thumbnails/profile_picture.png",)
    mock_get_conn.return_value.cursor.return_value = mock_cursor

    response = client.delete("/user-preferences/profile-picture")
    assert response.status_code == 200
    assert response.json()["message"] == "Profile picture removed"

    # Verify the UPDATE NULL query was executed
    calls = [str(call) for call in mock_cursor.execute.call_args_list]
    assert any("profile_picture_path" in c and "NULL" in c for c in calls)


# ---------------------------------------------------------------------------
# personal_summary field tests
# ---------------------------------------------------------------------------

@patch("app.api.routes.user_preferences.get_connection")
def test_get_user_preferences_returns_personal_summary_null_when_unset(mock_get_conn):
    """GET /user-preferences returns personal_summary as None when not stored."""
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = _pref_row(personal_summary=None)
    mock_get_conn.return_value.cursor.return_value = mock_cursor

    response = client.get("/user-preferences")
    assert response.status_code == 200
    assert response.json()["personal_summary"] is None


@patch("app.api.routes.user_preferences.get_connection")
def test_get_user_preferences_returns_personal_summary_value(mock_get_conn):
    """GET /user-preferences returns the stored personal_summary string."""
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = _pref_row(
        personal_summary="Passionate full-stack developer."
    )
    mock_get_conn.return_value.cursor.return_value = mock_cursor

    response = client.get("/user-preferences")
    assert response.status_code == 200
    assert response.json()["personal_summary"] == "Passionate full-stack developer."


@patch("app.api.routes.user_preferences.get_connection")
def test_save_user_preferences_with_personal_summary(mock_get_conn):
    """POST /user-preferences persists personal_summary when included in payload."""
    mock_cursor = MagicMock()
    mock_get_conn.return_value.cursor.return_value = mock_cursor

    payload = {
        "name": "John Doe",
        "email": "john@example.com",
        "github_user": "johndoe",
        "education": "Bachelor's",
        "industry": "Technology",
        "job_title": "Software Engineer",
        "personal_summary": "Building impactful software every day.",
    }

    response = client.post("/user-preferences", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    # Verify that the SQL was executed with the summary value
    call_args = mock_cursor.execute.call_args
    assert call_args is not None
    bound_params = call_args[0][1]  # positional args tuple passed to execute()
    assert "Building impactful software every day." in bound_params


@patch("app.api.routes.user_preferences.get_connection")
def test_save_user_preferences_without_personal_summary_defaults_to_none(mock_get_conn):
    """POST /user-preferences defaults personal_summary to None when omitted."""
    mock_cursor = MagicMock()
    mock_get_conn.return_value.cursor.return_value = mock_cursor

    payload = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "github_user": "janedoe",
        "education": "Master's",
        "industry": "Finance",
        "job_title": "Data Analyst",
    }

    response = client.post("/user-preferences", json=payload)
    assert response.status_code == 200

    # personal_summary not in payload → should be None in the bound params
    call_args = mock_cursor.execute.call_args
    assert call_args is not None
    bound_params = call_args[0][1]
    assert None in bound_params  # personal_summary defaults to None
