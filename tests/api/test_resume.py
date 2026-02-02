import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.api.routes.resume import router, compile_pdf, get_or_compile_pdf
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
@patch("app.api.routes.resume.generate_resume_tex")
def test_resume_page(mock_tex, mock_model, client, fake_resume_model):
    """Verify the resume HTML preview page renders successfully."""
    mock_model.return_value = fake_resume_model
    mock_tex.return_value = r"\documentclass{article}"

    response = client.get("/resume")

    assert response.status_code == 200
    assert "Resume Export" in response.text
    assert "\\documentclass" in response.text


@patch("app.api.routes.resume.build_resume_model")
@patch("app.api.routes.resume.generate_resume_tex")
def test_resume_preview_selected_projects(mock_tex, mock_model, client, fake_resume_model):
    """Verify POST /resume/preview renders HTML for selected project signatures."""
    mock_model.return_value = fake_resume_model
    mock_tex.return_value = r"\\documentclass{preview}"

    selected = ["sig_alpha_project/hash", "sig_gamma_project/hash"]
    response = client.post("/resume/preview", json={"project_ids": selected})

    assert response.status_code == 200
    # Title and selected projects listed
    assert "Generated Resume" in response.text
    assert "sig_alpha_project/hash" in response.text
    assert "sig_gamma_project/hash" in response.text
    # Preview contains LaTeX from generate_resume_tex
    assert "\\documentclass" in response.text

    # Ensure builder was invoked with the selected project IDs
    mock_model.assert_called_once_with(project_ids=selected)


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
def test_delete_saved_resume_success(mock_get_connection, client):
    """Verify DELETE /resume/{resume_id} successfully deletes a saved resume."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    # Mock that resume exists
    mock_cursor.fetchone.return_value = (5, "My Custom Resume")
    
    response = client.delete("/resume/5")
    
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["deleted_resume_id"] == 5
    assert "My Custom Resume" in response.json()["message"]
    
    # Verify database operations
    mock_cursor.execute.assert_any_call("SELECT id, name FROM RESUME WHERE id = ?", (5,))
    mock_cursor.execute.assert_any_call("DELETE FROM RESUME WHERE id = ?", (5,))
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("app.api.routes.resume.get_connection")
def test_delete_saved_resume_not_found(mock_get_connection, client):
    """Verify DELETE /resume/{resume_id} returns 404 when resume doesn't exist."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    # Mock that resume doesn't exist
    mock_cursor.fetchone.return_value = None
    
    response = client.delete("/resume/999")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
    
    # Verify no deletion attempted
    assert mock_cursor.execute.call_count == 1  # Only SELECT, no DELETE
    mock_conn.commit.assert_not_called()
    mock_conn.close.assert_called_once()


@patch("app.api.routes.resume.get_connection")
def test_delete_saved_resume_database_error(mock_get_connection, client):
    """Verify DELETE /resume/{resume_id} handles database errors gracefully."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    # Mock that resume exists
    mock_cursor.fetchone.return_value = (5, "My Custom Resume")
    
    # Mock database error on delete
    mock_cursor.execute.side_effect = [
        None,  # First call (SELECT) succeeds
        Exception("Database constraint violation")  # Second call (DELETE) fails
    ]
    
    response = client.delete("/resume/5")
    
    assert response.status_code == 500
    assert "Failed to delete resume" in response.json()["detail"]
    
    # Verify rollback called on error
    mock_conn.rollback.assert_called_once()
    mock_conn.close.assert_called_once()