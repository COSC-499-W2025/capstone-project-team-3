import os
from fastapi.testclient import TestClient
from fastapi import FastAPI
import pytest
from app.api.routes.get_upload_id import router

@pytest.fixture
def app(tmp_path, monkeypatch):
    """
    Create a test FastAPI app and patch the uploads directory 
    to point to a temporary path for safe filesystem testing.
    """
    # Patch the upload directory path used in your endpoint
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()

    # Set the UPLOAD_DIR environment variable to use the temp directory
    monkeypatch.setenv("UPLOAD_DIR", str(upload_dir))

    app = FastAPI()
    app.include_router(router)
    return app


def test_resolve_upload_ok(app, tmp_path, monkeypatch):
    """Test that project uploads and resolves with an ok status."""
    client = TestClient(app)
    upload_dir = tmp_path / "uploads"

    # Create dummy zip file in the temp upload directory
    upload_file = upload_dir / "123.zip"
    upload_file.write_text("dummy")

    response = client.get("/resolve-upload/123")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "123.zip" in response.json()["path"]


def test_resolve_upload_pending(app):
    client = TestClient(app)

    response = client.get("/resolve-upload/999")
    assert response.status_code == 200
    assert response.json() == {"status": "pending"}
