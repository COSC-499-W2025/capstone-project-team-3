"""
Tests for the cover letter backend:
  - cover_letter_utils (unit)
  - /api/cover-letter/* routes (integration via TestClient)
"""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes.cover_letter import router
from app.utils.cover_letter_utils import (
    MOTIVATION_LABELS,
    CoverLetterNotFoundError,
    CoverLetterServiceError,
    _format_project_bullets,
    _format_skills,
    _motivation_text,
)

# ---------------------------------------------------------------------------
# Test client fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


# ---------------------------------------------------------------------------
# Mock data
# ---------------------------------------------------------------------------

FAKE_PROFILE = {
    "name": "Jane Dev",
    "email": "jane@example.com",
    "industry": "Software",
    "personal_summary": "Passionate developer.",
    "linkedin": "",
    "github_user": "janedev",
    "links": [],
}

FAKE_RESUME = {
    "name": "Jane Dev",
    "email": "jane@example.com",
    "links": [],
    "education": [],
    "skills": {"Proficient": ["Python", "FastAPI"], "Familiar": ["React"]},
    "projects": [
        {
            "title": "Portfolio App",
            "dates": "Jan 2024 – Mar 2024",
            "bullets": ["Built REST API", "Deployed to cloud"],
            "skills": ["Python", "Docker"],
        }
    ],
}

FAKE_COVER_LETTER = {
    "id": 1,
    "resume_id": 2,
    "job_title": "Backend Engineer",
    "company": "Acme Corp",
    "job_description": "Build scalable APIs.",
    "motivations": ["meaningful_work", "personal_growth"],
    "content": "Dear Hiring Manager, ...",
    "generation_mode": "local",
    "created_at": "2026-03-21 10:00:00",
}


# ===========================================================================
# Unit tests — cover_letter_utils helpers
# ===========================================================================

class TestMotivationText:
    def test_empty_returns_empty_string(self):
        assert _motivation_text([]) == ""

    def test_single_motivation(self):
        text = _motivation_text(["meaningful_work"])
        assert "meaningful" in text.lower()

    def test_multiple_motivations_joined(self):
        text = _motivation_text(["meaningful_work", "personal_growth"])
        assert "and" in text

    def test_unknown_key_passed_through(self):
        text = _motivation_text(["custom_reason"])
        assert "custom_reason" in text


class TestFormatSkills:
    def test_merges_buckets(self):
        skills = {"Proficient": ["Python", "Go"], "Familiar": ["Rust"]}
        result = _format_skills(skills)
        assert "Python" in result
        assert "Go" in result
        assert "Rust" in result

    def test_empty_skills(self):
        assert _format_skills({}) == ""


class TestFormatProjectBullets:
    def test_basic_project(self):
        projects = [
            {
                "title": "My App",
                "dates": "Jan 2025",
                "bullets": ["Did X", "Did Y"],
            }
        ]
        result = _format_project_bullets(projects)
        assert "My App" in result
        assert "Did X" in result

    def test_json_string_bullets(self):
        projects = [
            {
                "title": "Another App",
                "dates": "",
                "bullets": json.dumps(["Built backend", "Added tests"]),
            }
        ]
        result = _format_project_bullets(projects)
        assert "Built backend" in result

    def test_empty_projects(self):
        assert _format_project_bullets([]) == ""


# ===========================================================================
# Unit tests — generate_local
# ===========================================================================

class TestGenerateLocal:
    @patch("app.utils.cover_letter_utils._load_user_profile", return_value=FAKE_PROFILE)
    @patch("app.utils.cover_letter_utils._load_resume_context", return_value=FAKE_RESUME)
    def test_contains_name_and_company(self, _mock_resume, _mock_profile):
        from app.utils.cover_letter_utils import generate_local

        letter = generate_local(
            resume_id=2,
            job_title="Backend Engineer",
            company="Acme Corp",
            job_description="Build APIs.",
            motivations=["meaningful_work"],
        )
        assert "Jane Dev" in letter
        assert "Acme Corp" in letter

    @patch("app.utils.cover_letter_utils._load_user_profile", return_value=FAKE_PROFILE)
    @patch("app.utils.cover_letter_utils._load_resume_context", return_value=FAKE_RESUME)
    def test_contains_job_title(self, _mock_resume, _mock_profile):
        from app.utils.cover_letter_utils import generate_local

        letter = generate_local(
            resume_id=2,
            job_title="Backend Engineer",
            company="Acme",
            job_description="Build APIs.",
            motivations=[],
        )
        assert "Backend Engineer" in letter

    @patch("app.utils.cover_letter_utils._load_user_profile", return_value=FAKE_PROFILE)
    @patch("app.utils.cover_letter_utils._load_resume_context", return_value=FAKE_RESUME)
    def test_includes_motivation_text(self, _mock_resume, _mock_profile):
        from app.utils.cover_letter_utils import generate_local

        letter = generate_local(
            resume_id=2,
            job_title="Engineer",
            company="Corp",
            job_description="Do things.",
            motivations=["strong_company_culture"],
        )
        assert "culture" in letter.lower()

    @patch("app.utils.cover_letter_utils._load_resume_context",
           side_effect=CoverLetterServiceError("resume not found"))
    @patch("app.utils.cover_letter_utils._load_user_profile", return_value=FAKE_PROFILE)
    def test_propagates_service_error(self, _mock_profile, _mock_resume):
        from app.utils.cover_letter_utils import generate_local

        with pytest.raises(CoverLetterServiceError):
            generate_local(
                resume_id=999,
                job_title="X",
                company="Y",
                job_description="Z" * 10,
                motivations=[],
            )


# ===========================================================================
# Unit tests — generate_ai falls back when no API key
# ===========================================================================

class TestGenerateAI:
    @patch("app.utils.cover_letter_utils._load_user_profile", return_value=FAKE_PROFILE)
    @patch("app.utils.cover_letter_utils._load_resume_context", return_value=FAKE_RESUME)
    @patch.dict("os.environ", {}, clear=True)  # no GEMINI_API_KEY
    def test_falls_back_to_local_without_api_key(self, _mock_resume, _mock_profile):
        from app.utils.cover_letter_utils import generate_ai

        letter = generate_ai(
            resume_id=2,
            job_title="Engineer",
            company="Corp",
            job_description="Some description here.",
            motivations=[],
        )
        # Falls back to local template which always contains the name
        assert "Jane Dev" in letter

    @patch("app.utils.cover_letter_utils._load_user_profile", return_value=FAKE_PROFILE)
    @patch("app.utils.cover_letter_utils._load_resume_context", return_value=FAKE_RESUME)
    @patch.dict("os.environ", {"GEMINI_API_KEY": "AIzaFakeKey123"})
    def test_uses_llm_when_api_key_present(self, _mock_resume, _mock_profile):
        from app.utils.cover_letter_utils import generate_ai

        mock_client = MagicMock()
        mock_client.generate.return_value = "AI generated cover letter content."

        with patch("app.utils.cover_letter_utils.GeminiLLMClient", return_value=mock_client):
            letter = generate_ai(
                resume_id=2,
                job_title="Engineer",
                company="Corp",
                job_description="Some description.",
                motivations=["personal_growth"],
            )
        assert "AI generated" in letter
        mock_client.generate.assert_called_once()

    @patch("app.utils.cover_letter_utils._load_user_profile", return_value=FAKE_PROFILE)
    @patch("app.utils.cover_letter_utils._load_resume_context", return_value=FAKE_RESUME)
    @patch.dict("os.environ", {"GEMINI_API_KEY": "AIzaFakeKey123"})
    def test_falls_back_to_local_when_llm_errors(self, _mock_resume, _mock_profile):
        from app.utils.cover_letter_utils import generate_ai

        mock_client = MagicMock()
        mock_client.generate.return_value = "Gemini API error: something went wrong"

        with patch("app.utils.cover_letter_utils.GeminiLLMClient", return_value=mock_client):
            letter = generate_ai(
                resume_id=2,
                job_title="Engineer",
                company="Corp",
                job_description="Some description.",
                motivations=[],
            )
        assert "Jane Dev" in letter


# ===========================================================================
# Unit tests — persistence helpers
# ===========================================================================

class TestPersistence:
    @patch("app.utils.cover_letter_utils.get_connection")
    def test_save_cover_letter_returns_id(self, mock_get_conn):
        from app.utils.cover_letter_utils import save_cover_letter

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 42
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        result = save_cover_letter(
            resume_id=2,
            job_title="Engineer",
            company="Corp",
            job_description="Do things.",
            motivations=["meaningful_work"],
            content="Dear ...",
            generation_mode="local",
        )
        assert result == 42

    @patch("app.utils.cover_letter_utils.get_connection")
    def test_get_cover_letter_raises_not_found(self, mock_get_conn):
        from app.utils.cover_letter_utils import get_cover_letter

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        with pytest.raises(CoverLetterNotFoundError):
            get_cover_letter(999)

    @patch("app.utils.cover_letter_utils.get_connection")
    def test_delete_cover_letter_returns_true(self, mock_get_conn):
        from app.utils.cover_letter_utils import delete_cover_letter

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        assert delete_cover_letter(1) is True

    @patch("app.utils.cover_letter_utils.get_connection")
    def test_delete_cover_letter_returns_false_when_not_found(self, mock_get_conn):
        from app.utils.cover_letter_utils import delete_cover_letter

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 0
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        assert delete_cover_letter(999) is False


# ===========================================================================
# Integration tests — API routes
# ===========================================================================

class TestGenerateRoute:
    @patch("app.api.routes.cover_letter.save_cover_letter", return_value=1)
    @patch("app.api.routes.cover_letter.get_cover_letter", return_value=FAKE_COVER_LETTER)
    @patch("app.api.routes.cover_letter.generate_cover_letter", return_value="Dear Hiring Manager, ...")
    def test_generate_returns_201_like_response(
        self, _mock_gen, _mock_get, _mock_save, client
    ):
        response = client.post(
            "/cover-letter/generate",
            json={
                "resume_id": 2,
                "job_title": "Backend Engineer",
                "company": "Acme Corp",
                "job_description": "Build scalable APIs for our platform.",
                "motivations": ["meaningful_work"],
                "mode": "local",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["job_title"] == "Backend Engineer"
        assert data["company"] == "Acme Corp"

    @patch("app.api.routes.cover_letter.generate_cover_letter",
           side_effect=CoverLetterServiceError("resume not found"))
    def test_generate_500_on_service_error(self, _mock_gen, client):
        response = client.post(
            "/cover-letter/generate",
            json={
                "resume_id": 999,
                "job_title": "Engineer",
                "company": "Corp",
                "job_description": "Do things for our platform.",
                "motivations": [],
                "mode": "local",
            },
        )
        assert response.status_code == 500

    def test_generate_422_invalid_mode(self, client):
        response = client.post(
            "/cover-letter/generate",
            json={
                "resume_id": 2,
                "job_title": "Engineer",
                "company": "Corp",
                "job_description": "Do things for the platform.",
                "motivations": [],
                "mode": "invalid_mode",
            },
        )
        assert response.status_code == 422

    def test_generate_422_missing_required_field(self, client):
        response = client.post(
            "/cover-letter/generate",
            json={
                "job_title": "Engineer",
                "company": "Corp",
                # missing resume_id and job_description
            },
        )
        assert response.status_code == 422


class TestListRoute:
    @patch("app.api.routes.cover_letter.list_cover_letters", return_value=[FAKE_COVER_LETTER])
    def test_list_returns_summaries(self, _mock_list, client):
        response = client.get("/cover-letter")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["job_title"] == "Backend Engineer"
        # Full content should NOT appear in summary
        assert "content" not in data[0]

    @patch("app.api.routes.cover_letter.list_cover_letters", return_value=[])
    def test_list_empty(self, _mock_list, client):
        response = client.get("/cover-letter")
        assert response.status_code == 200
        assert response.json() == []


class TestGetOneRoute:
    @patch("app.api.routes.cover_letter.get_cover_letter", return_value=FAKE_COVER_LETTER)
    def test_get_returns_full_letter(self, _mock_get, client):
        response = client.get("/cover-letter/1")
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Dear Hiring Manager, ..."
        assert data["motivations"] == ["meaningful_work", "personal_growth"]

    @patch("app.api.routes.cover_letter.get_cover_letter",
           side_effect=CoverLetterNotFoundError("not found"))
    def test_get_404_when_missing(self, _mock_get, client):
        response = client.get("/cover-letter/999")
        assert response.status_code == 404


class TestDeleteRoute:
    @patch("app.api.routes.cover_letter.delete_cover_letter", return_value=True)
    def test_delete_success(self, _mock_del, client):
        response = client.delete("/cover-letter/1")
        assert response.status_code == 200
        assert response.json()["deleted_id"] == 1

    @patch("app.api.routes.cover_letter.delete_cover_letter", return_value=False)
    def test_delete_404_when_not_found(self, _mock_del, client):
        response = client.delete("/cover-letter/999")
        assert response.status_code == 404

    @patch("app.api.routes.cover_letter.delete_cover_letter",
           side_effect=CoverLetterServiceError("db error"))
    def test_delete_500_on_error(self, _mock_del, client):
        response = client.delete("/cover-letter/1")
        assert response.status_code == 500


class TestPdfRoute:
    @patch("app.api.routes.cover_letter.get_cover_letter",
           side_effect=CoverLetterNotFoundError("not found"))
    def test_pdf_404_when_missing(self, _mock_get, client):
        response = client.get("/cover-letter/999/pdf")
        assert response.status_code == 404

    @patch("app.api.routes.cover_letter._compile_tex_to_pdf", return_value=b"%PDF-fake")
    @patch("app.api.routes.cover_letter.get_cover_letter", return_value=FAKE_COVER_LETTER)
    @patch("app.api.routes.cover_letter.load_user", return_value=FAKE_PROFILE)
    @patch("app.api.routes.cover_letter.get_connection")
    def test_pdf_returns_bytes(self, mock_conn, _mock_user, _mock_get, _mock_compile, client, tmp_path):
        mock_cursor = MagicMock()
        mock_conn_instance = MagicMock()
        mock_conn_instance.cursor.return_value = mock_cursor
        mock_conn.return_value = mock_conn_instance

        # Patch PDF_CACHE_DIR to tmp_path so no stale cache hits
        import app.api.routes.cover_letter as cl_mod
        original = cl_mod.PDF_CACHE_DIR
        cl_mod.PDF_CACHE_DIR = str(tmp_path)
        try:
            response = client.get("/cover-letter/1/pdf")
        finally:
            cl_mod.PDF_CACHE_DIR = original

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
