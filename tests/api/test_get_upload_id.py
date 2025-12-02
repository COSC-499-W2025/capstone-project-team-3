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

    # Monkeypatch only within the module under test and call the real exists
    real_exists = os.path.exists

    def fake_exists(path):
        return real_exists(str(path).replace("/app/uploads", str(upload_dir)))

    monkeypatch.setattr("app.api.routes.get_upload_id.os.path.exists", fake_exists)

    app = FastAPI()
    app.include_router(router)
    return app


def test_resolve_upload_ok(app, tmp_path):
    """Test that project uploads and resolves with an ok status."""
    client = TestClient(app)

    # Create dummy zip file in the temp upload directory
    upload_file = tmp_path / "uploads" / "123.zip"
    upload_file.write_text("dummy")

    response = client.get("/resolve-upload/123")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "path": "/app/uploads/123.zip"
    }


def test_resolve_upload_pending(app):
    client = TestClient(app)

    response = client.get("/resolve-upload/999")
    assert response.status_code == 200
    assert response.json() == {"status": "pending"}
