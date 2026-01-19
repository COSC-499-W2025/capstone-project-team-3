import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.api.routes.resume import router, compile_pdf

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

    assert exc.value.status_code == 500
    assert "LaTeX compilation failed" in exc.value.detail
