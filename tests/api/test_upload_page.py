import os
from fastapi.testclient import TestClient
from fastapi import FastAPI
import app.api.routes.upload_page as upload_module
from app.api.routes.upload_page import router


def test_upload_page_renders():
    app = FastAPI()
    app.include_router(router)

    client = TestClient(app)

    resp = client.get("/upload-file")
    assert resp.status_code == 200
    assert "<h2>Upload Your ZIP File</h2>" in resp.text
    assert "form" in resp.text


def test_upload_file_success(tmp_path, monkeypatch):
    """
    Test a valid ZIP upload and verify that:
    - the API returns status ok
    - the file is physically written to disk
    """

    # Point UPLOAD_DIR to a temp directory
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    monkeypatch.setattr(upload_module, "UPLOAD_DIR", str(upload_dir))

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    # Create fake file-like ZIP data
    files = {
        "file": ("test.zip", b"dummy zip contents", "application/zip")
    }

    resp = client.post("/upload-file", files=files)
    assert resp.status_code == 200

    data = resp.json()
    assert data["status"] == "ok"
    assert "upload_id" in data

    # Check file exists physically
    upload_id = data["upload_id"]
    saved_path = upload_dir / f"{upload_id}.zip"
    assert saved_path.exists()
    assert saved_path.read_bytes() == b"dummy zip contents"


def test_upload_file_invalid_extension(tmp_path, monkeypatch):
    """
    Test that uploading a non-ZIP file returns a 400 + alert script.
    """

    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    monkeypatch.setattr(upload_module, "UPLOAD_DIR", str(upload_dir))

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    files = {
        "file": ("notzip.txt", b"nope", "text/plain")
    }

    resp = client.post("/upload-file", files=files)

    assert resp.status_code == 400
    # Should return an HTML alert + redirect script
    assert "alert('Please upload a ZIP file" in resp.text
    assert "window.location.href = '/upload-file'" in resp.text


def test_upload_file_missing_file():
    """
    Test calling POST with no file at all.
    """

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    resp = client.post("/upload-file", files={})

    assert resp.status_code == 400
    assert "Please upload a ZIP file" in resp.text
