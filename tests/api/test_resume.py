import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.api.routes.resume import router, compile_pdf, get_or_compile_pdf
from app.utils.generate_resume import ResumeServiceError
from app.api.routes import resume as resume_mod
import os

@pytest.fixture
def client():
    """Create a FastAPI test client with the resume router mounted."""
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@pytest.fixture
def fake_resume_model():
    """Provide a minimal valid resume model for route testing."""
    return {
        "name": "John User",
        "email": "john@example.com",
        "links": [],
        "education": {
            "school": "Test University",
            "degree": "BSc Computer Science",
            "dates": "",
            "gpa": "",
        },
        "skills": {"Skills": ["Python", "Flask"]},
        "projects": [],
    }

@patch("app.api.routes.resume.build_resume_model")
def test_resume_page(mock_model, client, fake_resume_model):
    """Verify the resume endpoint returns the resume model as JSON."""
    mock_model.return_value = fake_resume_model

    response = client.get("/resume")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John User"
    assert data["email"] == "john@example.com"
    assert "education" in data
    assert "skills" in data

@patch("app.api.routes.resume.build_resume_model")
@patch("app.api.routes.resume.generate_resume_tex")
def test_resume_download_tex(mock_tex, mock_model, client, fake_resume_model):
    """Ensure the LaTeX resume is downloadable as a .tex file."""
    mock_model.return_value = fake_resume_model
    mock_tex.return_value = "LATEX CONTENT"

    response = client.get("/resume/export/tex")

    assert response.status_code == 200
    assert response.headers["content-disposition"] == "attachment; filename=resume.tex"
    assert response.text == "LATEX CONTENT"


@patch("app.api.routes.resume.load_saved_resume")
@patch("app.api.routes.resume.generate_resume_tex")
def test_resume_download_tex_with_resume_id(mock_tex, mock_load, client, fake_resume_model):
    """Ensure GET /resume/export/tex with resume_id loads saved resume edits."""
    mock_load.return_value = fake_resume_model
    mock_tex.return_value = "LATEX EDITED CONTENT"

    response = client.get("/resume/export/tex?resume_id=5")

    assert response.status_code == 200
    assert response.headers["content-disposition"] == "attachment; filename=resume.tex"
    assert response.text == "LATEX EDITED CONTENT"
    mock_load.assert_called_once_with(5)


@patch("app.api.routes.resume.build_resume_model")
@patch("app.api.routes.resume.generate_resume_tex")
def test_resume_download_tex_with_project_ids(mock_tex, mock_model, client, fake_resume_model):
    """Ensure GET /resume/export/tex with project_ids uses build_resume_model."""
    mock_model.return_value = fake_resume_model
    mock_tex.return_value = "LATEX PREVIEW CONTENT"

    response = client.get("/resume/export/tex?project_ids=proj1&project_ids=proj2")

    assert response.status_code == 200
    assert response.headers["content-disposition"] == "attachment; filename=resume.tex"
    assert response.text == "LATEX PREVIEW CONTENT"
    mock_model.assert_called_once_with(project_ids=["proj1", "proj2"])


@patch("app.api.routes.resume.build_resume_model")
@patch("app.api.routes.resume.generate_resume_tex")
@patch("app.api.routes.resume.compile_pdf")
def test_resume_pdf_download(mock_compile, mock_tex, mock_model, client, fake_resume_model):
    """Confirm the PDF resume endpoint returns a valid PDF response."""
    mock_model.return_value = fake_resume_model
    mock_tex.return_value = "LATEX CONTENT"
    mock_compile.return_value = b"%PDF-1.4 fake pdf"

    response = client.get("/resume/export/pdf")

    assert response.status_code == 200
    assert response.headers["content-disposition"] == "attachment; filename=resume.pdf"
    assert response.content.startswith(b"%PDF")


@patch("app.api.routes.resume.load_saved_resume")
@patch("app.api.routes.resume.generate_resume_tex")
@patch("app.api.routes.resume.compile_pdf")
def test_resume_pdf_download_with_resume_id(mock_compile, mock_tex, mock_load, client, fake_resume_model):
    """Confirm GET /resume/export/pdf with resume_id loads saved resume edits."""
    mock_load.return_value = fake_resume_model
    mock_tex.return_value = "LATEX EDITED CONTENT"
    mock_compile.return_value = b"%PDF-1.4 edited pdf"

    response = client.get("/resume/export/pdf?resume_id=5")

    assert response.status_code == 200
    assert response.headers["content-disposition"] == "attachment; filename=resume.pdf"
    assert response.content.startswith(b"%PDF")
    mock_load.assert_called_once_with(5)


@patch("app.api.routes.resume.build_resume_model")
@patch("app.api.routes.resume.generate_resume_tex")
@patch("app.api.routes.resume.compile_pdf")
def test_resume_pdf_download_with_project_ids(mock_compile, mock_tex, mock_model, client, fake_resume_model):
    """Confirm GET /resume/export/pdf with project_ids uses build_resume_model."""
    mock_model.return_value = fake_resume_model
    mock_tex.return_value = "LATEX PREVIEW CONTENT"
    mock_compile.return_value = b"%PDF-1.4 preview pdf"

    response = client.get("/resume/export/pdf?project_ids=proj1&project_ids=proj2")

    assert response.status_code == 200
    assert response.headers["content-disposition"] == "attachment; filename=resume.pdf"
    assert response.content.startswith(b"%PDF")
    mock_model.assert_called_once_with(project_ids=["proj1", "proj2"])

@patch("app.api.routes.resume.build_resume_model")
@patch("app.api.routes.resume.generate_resume_tex")
def test_resume_export_tex_filtered(mock_tex, mock_model, client, fake_resume_model):
    """Ensure POST /resume/export/tex returns .tex for specified projects."""
    mock_model.return_value = fake_resume_model
    mock_tex.return_value = "LATEX FILTERED CONTENT"

    body = {"project_ids": ["sig_gamma_project/hash"]}
    response = client.post("/resume/export/tex", json=body)

    assert response.status_code == 200
    assert response.headers["content-disposition"] == "attachment; filename=resume.tex"
    assert response.text == "LATEX FILTERED CONTENT"
    mock_model.assert_called_once()


@patch("app.api.routes.resume.build_resume_model")
@patch("app.api.routes.resume.generate_resume_tex")
@patch("app.api.routes.resume.compile_pdf")
def test_resume_export_pdf_filtered(mock_compile, mock_tex, mock_model, client, fake_resume_model):
    """Confirm POST /resume/export/pdf returns a valid PDF for selected projects."""
    mock_model.return_value = fake_resume_model
    mock_tex.return_value = "LATEX FILTERED CONTENT"
    mock_compile.return_value = b"%PDF-1.4 filtered"

    body = {"project_ids": ["sig_alpha_project/hash", "sig_gamma_project/hash"]}
    response = client.post("/resume/export/pdf", json=body)

    assert response.status_code == 200
    assert response.headers["content-disposition"] == "attachment; filename=resume.pdf"
    assert response.content.startswith(b"%PDF")
    mock_model.assert_called_once()


@patch("app.api.routes.resume.subprocess.run")
@patch("app.api.routes.resume.os.path.exists")
@patch("builtins.open")
def test_compile_pdf_success(mock_open, mock_exists, mock_run):
    """Verify compile_pdf returns PDF bytes on successful LaTeX compilation."""
    mock_run.return_value = MagicMock(returncode=0, stdout=b"", stderr=b"")
    mock_exists.return_value = True
    mock_open.return_value.__enter__.return_value.read.return_value = b"PDF BYTES"

    result = compile_pdf("LATEX")

    assert result == b"PDF BYTES"


@patch("app.api.routes.resume.subprocess.run")
def test_compile_pdf_pdflatex_not_found(mock_run):
    """Ensure compile_pdf raises an error when pdflatex is not installed."""
    mock_run.side_effect = FileNotFoundError()

    with pytest.raises(HTTPException) as exc:
        compile_pdf("LATEX")

    assert exc.value.status_code == 500
    assert "pdflatex not found" in exc.value.detail


@patch("app.api.routes.resume.subprocess.run")
@patch("app.api.routes.resume.os.path.exists")
def test_compile_pdf_failure_no_pdf(mock_exists, mock_run):
    """Confirm compile_pdf fails when pdflatex errors and no PDF is produced."""
    mock_run.return_value = MagicMock(
        returncode=1,
        stdout=b"latex error",
        stderr=b"fatal error",
        args=["pdflatex"],
    )
    mock_exists.return_value = False

    with pytest.raises(HTTPException) as exc:
        compile_pdf("LATEX")

    assert exc.value.status_code == 422
    assert exc.value.detail["error"] == "LaTeX compilation failed"
    assert exc.value.detail["stdout"] == "latex error"
    assert exc.value.detail["stderr"] == "fatal error"

def test_get_or_compile_pdf_cache(tmp_path, monkeypatch):
    """Verify that get_or_compile_pdf caches PDFs and avoids recompiling the same LaTeX content."""
    tex = "LATEX CONTENT"
    cache_dir = tmp_path / "cache"
    os.makedirs(cache_dir, exist_ok=True)
    # Point the router's cache directory at the temp location
    monkeypatch.setattr(resume_mod, "PDF_CACHE_DIR", str(cache_dir))

    # Ensure no cached PDF exists before first call
    h = resume_mod.tex_hash(tex)
    cache_file = cache_dir / f"{h}.pdf"
    if cache_file.exists():
        cache_file.unlink()

    # compile_pdf should be invoked because the PDF is not yet cached
    with patch("app.api.routes.resume.compile_pdf") as mock_compile:
        mock_compile.return_value = b"%PDF-1.4"
        pdf1 = get_or_compile_pdf(tex)
        assert pdf1.startswith(b"%PDF")
        mock_compile.assert_called_once()

    # PDF should be retrieved from the cache and compile_pdf should not be called
    with patch("app.api.routes.resume.compile_pdf") as mock_compile2:
        pdf2 = get_or_compile_pdf(tex)
        assert pdf2.startswith(b"%PDF")
        mock_compile2.assert_not_called()


@patch("app.api.routes.resume.get_connection")
@patch("app.api.routes.resume.resume_exists")
def test_delete_saved_resume_success(mock_resume_exists, mock_get_connection, client):
    """Verify DELETE /resume/{resume_id} successfully deletes a saved resume."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    # Mock that resume exists
    mock_resume_exists.return_value = True
    
    response = client.delete("/resume/5")
    
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["deleted_resume_id"] == 5
    assert "Resume 5 deleted successfully" in response.json()["message"]
    
    # Verify database operations
    mock_resume_exists.assert_called_once_with(5)
    mock_cursor.execute.assert_called_once_with("DELETE FROM RESUME WHERE id = ?", (5,))
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("app.api.routes.resume.resume_exists")
def test_delete_saved_resume_not_found(mock_resume_exists, client):
    """Verify DELETE /resume/{resume_id} returns 404 when resume doesn't exist."""
    # Mock that resume doesn't exist
    mock_resume_exists.return_value = False
    
    response = client.delete("/resume/999")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
    
    # Verify resume_exists was called but no further database operations
    mock_resume_exists.assert_called_once_with(999)


@patch("app.api.routes.resume.get_connection")
@patch("app.api.routes.resume.resume_exists")
def test_delete_saved_resume_database_error(mock_resume_exists, mock_get_connection, client):
    """Verify DELETE /resume/{resume_id} handles database errors gracefully."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    # Mock that resume exists
    mock_resume_exists.return_value = True
    
    # Mock database error on delete
    mock_cursor.execute.side_effect = Exception("Database constraint violation")
    
    response = client.delete("/resume/5")
    
    assert response.status_code == 500
    assert "Failed to delete resume" in response.json()["detail"]
    
    # Verify rollback called on error
    mock_conn.rollback.assert_called_once()
    mock_conn.close.assert_called_once()
        
@patch("app.api.routes.resume.load_saved_resume")
def test_get_saved_resume(mock_load, client, fake_resume_model):
    """Test GET /resume/{resume_id} returns the saved resume model."""
    mock_load.return_value = fake_resume_model
    response = client.get("/resume/1")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == fake_resume_model["name"]
    assert data["email"] == fake_resume_model["email"]

@patch("app.api.routes.resume.save_resume_edits")
@patch("app.api.routes.resume.resume_exists")
def test_save_edited_resume_success(mock_exists, mock_save, client):
    """
    Test POST /resume/{id}/edit saves edits when resume exists.
    """
    mock_exists.return_value = True
    payload = {"projects": [{"project_id": "p1", "project_name": "Edited Project"}]}
    response = client.post("/resume/1/edit", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    mock_save.assert_called_once_with(1, payload)

@patch("app.api.routes.resume.save_resume_edits")
@patch("app.api.routes.resume.resume_exists")
def test_save_edited_resume_not_found(mock_exists, mock_save, client):
    """
    Test POST /resume/{id}/edit returns 404 if resume does not exist.
    """
    mock_exists.return_value = False
    payload = {"projects": [{"project_id": "p1", "project_name": "Edited Project"}]}
    response = client.post("/resume/999/edit", json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Resume not found"
    mock_save.assert_not_called()


@patch("app.api.routes.resume.create_resume")
@patch("app.api.routes.resume.attach_projects_to_resume")
def test_create_tailored_resume_success(mock_attach, mock_create, client):
    """
    Test POST /resume creates a resume and associates selected projects.
    """
    mock_create.return_value = 42
    mock_attach.return_value = None
    payload = {"project_ids": ["p1", "p2"]}
    response = client.post("/resume", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["resume_id"] == 42
    assert data["message"] == "Resume created successfully"
    mock_create.assert_called_once_with()
    mock_attach.assert_called_once_with(42, ["p1", "p2"])


def test_create_tailored_resume_no_projects(client):
    """
    Test POST /resume returns 400 if no projects are selected.
    """
    payload = {"project_ids": []}
    response = client.post("/resume", json=payload)
    assert response.status_code == 400
    assert "No projects selected" in response.text


@patch("app.api.routes.resume.list_resumes")
def test_list_resumes_endpoint_success(mock_list_resumes, client):
    """Test GET /resume_names returns list of resumes."""
    mock_data = [
        {"id": 1, "name": "Master Resume", "is_master": True},
        {"id": 2, "name": "Software Engineer Resume", "is_master": False},
        {"id": 3, "name": "Data Analyst Resume", "is_master": False},
    ]
    mock_list_resumes.return_value = mock_data
    
    response = client.get("/resume_names")
    
    assert response.status_code == 200
    data = response.json()
    assert "resumes" in data
    assert len(data["resumes"]) == 3
    assert data["resumes"][0]["name"] == "Master Resume"
    assert data["resumes"][0]["is_master"] is True
    mock_list_resumes.assert_called_once()


@patch("app.api.routes.resume.list_resumes")
def test_list_resumes_endpoint_service_error(mock_list_resumes, client):
    """Test GET /resume_names handles ResumeServiceError."""
    
    mock_list_resumes.side_effect = ResumeServiceError("Database connection failed")
    
    response = client.get("/resume_names")
    
    assert response.status_code == 500
    assert "Database connection failed" in response.json()["detail"]
    mock_list_resumes.assert_called_once()
