import shutil
from pathlib import Path
import pytest
import app.utils.clean_up
from app.utils.clean_up import cleanup_upload


def test_cleanup_upload_requires_upload_id():
    """Ensure function errors when upload_id is missing."""
    assert cleanup_upload("") == {
        "status": "error",
        "reason": "upload_id required"
    }


def test_cleanup_upload_deletes_zip(tmp_path, monkeypatch):
    """Ensure the ZIP file is deleted when present."""
    # Arrange
    uploads = tmp_path / "uploads"
    uploads.mkdir()

    # Override the DEFAULT_UPLOADS_DIR
    monkeypatch.setattr(app.utils.clean_up, "DEFAULT_UPLOADS_DIR", str(uploads))

    # Create a dummy ZIP file to delete
    upload_id = "abc123"
    zip_path = uploads / f"{upload_id}.zip"
    zip_path.write_bytes(b"dummy zip")

    # Act
    result = cleanup_upload(upload_id)

    # Assert
    assert result["status"] == "ok"
    assert result["zip_deleted"] is True
    assert result["extracted_deleted"] is False
    assert not zip_path.exists()

def test_cleanup_upload_deletes_extracted_dir(tmp_path, monkeypatch):
    """Ensure extracted directory is deleted when requested."""
    uploads = tmp_path / "uploads"
    uploads.mkdir()

    monkeypatch.setattr(app.utils.clean_up, "DEFAULT_UPLOADS_DIR", str(uploads))

    upload_id = "xyz"
    extracted_dir = tmp_path / "extracted"
    extracted_dir.mkdir()

    result = cleanup_upload(
        upload_id,
        extracted_dir=str(extracted_dir),
        delete_extracted=True
    )

    assert result["status"] == "ok"
    assert result["zip_deleted"] is False
    assert result["extracted_deleted"] is True
    assert not extracted_dir.exists()


def test_cleanup_upload_stray_dir_deleted_if_exists(tmp_path, monkeypatch):
    """Ensure stray directory inside uploads is removed."""
    uploads = tmp_path / "uploads"
    uploads.mkdir()

    monkeypatch.setattr(app.utils.clean_up, "DEFAULT_UPLOADS_DIR", str(uploads))

    upload_id = "stray"

    # create stray dir inside uploads
    stray_dir = uploads / upload_id
    stray_dir.mkdir()

    # run cleanup
    result = cleanup_upload(upload_id)

    assert result["status"] == "ok"
    assert stray_dir.exists() is False   # deleted
    assert result["zip_deleted"] is False
    assert result["extracted_deleted"] is False


def test_cleanup_upload_extracted_dir_error(tmp_path, monkeypatch):
    """Ensure an error is returned when extracted dir deletion fails."""
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    monkeypatch.setattr(app.utils.clean_up, "DEFAULT_UPLOADS_DIR", str(uploads))

    upload_id = "err"
    ed = tmp_path / "bad_dir"
    ed.mkdir()

    # Make deletion fail by turning directory into a file-like obstruction:
    protected_file = ed / "protected"
    protected_file.write_text("cannot remove while open")

    # Patch rmtree to simulate failure
    def fake_rmtree(path, ignore_errors=False):
        raise OSError("cannot delete")

    monkeypatch.setattr(shutil, "rmtree", fake_rmtree)

    result = cleanup_upload(upload_id, extracted_dir=str(ed), delete_extracted=True)

    assert result["status"] == "error"
    assert "failed to delete extracted dir" in result["reason"]
