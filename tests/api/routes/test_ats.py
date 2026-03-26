"""Tests for the ATS scoring backend route and helper functions."""
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.routes.ats import (
    _tokenize,
    _extract_jd_keywords_fallback,
    _match_level,
    _calc_experience_months,
    _resume_full_text,
    _all_resume_skills,
    _score_ats,
)

client = TestClient(app)

LONG_JD = (
    "We are looking for a software engineer with Python and React experience. "
    "Must have 3 or more years of experience with Docker and AWS cloud infrastructure."
)

SAMPLE_RESUME = {
    "skills": {"Languages": ["Python", "JavaScript", "React"]},
    "projects": [
        {
            "title": "Backend API",
            "start_date": "2024-01-01",
            "end_date": "2024-04-01",
            "bullets": [
                "Built REST API with Python and FastAPI",
                "Deployed to AWS using Docker containers",
                "Wrote unit tests with pytest",
            ],
            "skills": ["Python", "FastAPI", "Docker"],
        }
    ],
}


# ---------------------------------------------------------------------------
# _tokenize
# ---------------------------------------------------------------------------

def test_tokenize_lowercases_input():
    tokens = _tokenize("Python React AWS")
    assert "python" in tokens
    assert "react" in tokens
    assert "aws" in tokens


def test_tokenize_removes_stop_words():
    tokens = _tokenize("the application and environment")
    assert "the" not in tokens
    assert "and" not in tokens
    assert "environment" not in tokens


def test_tokenize_removes_short_tokens():
    tokens = _tokenize("ok hi ccc dddd")
    assert "ok" not in tokens
    assert "hi" not in tokens
    assert "ccc" in tokens
    assert "dddd" in tokens


def test_tokenize_handles_special_characters():
    tokens = _tokenize("node.js c++ react")
    # Should include multi-char tokens
    assert any(len(t) > 2 for t in tokens)


def test_tokenize_empty_string():
    assert _tokenize("") == []


# ---------------------------------------------------------------------------
# _extract_jd_keywords_fallback
# ---------------------------------------------------------------------------

def test_extract_jd_keywords_fallback_returns_list():
    result = _extract_jd_keywords_fallback("We need Python and React developers. Docker Docker Docker.")
    assert isinstance(result, list)
    assert len(result) > 0


def test_extract_jd_keywords_fallback_prefers_tech_keywords():
    # "python" is in TECH_KEYWORDS, so it should be returned even if rare
    result = _extract_jd_keywords_fallback("We need python for this role.")
    assert "python" in result


def test_extract_jd_keywords_fallback_includes_high_frequency_words():
    # "distributed" appears 3 times and is a real tech word
    result = _extract_jd_keywords_fallback(
        "distributed systems distributed architecture distributed computing"
    )
    assert "distributed" in result


def test_extract_jd_keywords_fallback_non_empty_jd():
    result = _extract_jd_keywords_fallback(LONG_JD)
    assert len(result) > 0


# ---------------------------------------------------------------------------
# _match_level
# ---------------------------------------------------------------------------

def test_match_level_high_at_70():
    assert _match_level(70) == "High"


def test_match_level_high_at_100():
    assert _match_level(100) == "High"


def test_match_level_medium_at_40():
    assert _match_level(40) == "Medium"


def test_match_level_medium_at_69():
    assert _match_level(69) == "Medium"


def test_match_level_low_at_0():
    assert _match_level(0) == "Low"


def test_match_level_low_at_39():
    assert _match_level(39) == "Low"


# ---------------------------------------------------------------------------
# _calc_experience_months
# ---------------------------------------------------------------------------

def test_calc_experience_months_sums_projects():
    resume = {
        "projects": [
            {"start_date": "2024-01-01", "end_date": "2024-03-01"},  # 2 months
            {"start_date": "2024-04-01", "end_date": "2024-07-01"},  # 3 months
        ]
    }
    assert _calc_experience_months(resume) == 5


def test_calc_experience_months_skips_missing_dates():
    resume = {
        "projects": [
            {"start_date": None, "end_date": "2024-03-01"},
            {"start_date": "2024-01-01", "end_date": "2024-04-01"},  # 3 months
        ]
    }
    assert _calc_experience_months(resume) == 3


def test_calc_experience_months_skips_invalid_dates():
    resume = {
        "projects": [
            {"start_date": "not-a-date", "end_date": "2024-03-01"},
            {"start_date": "2024-01-01", "end_date": "2024-04-01"},  # 3 months
        ]
    }
    assert _calc_experience_months(resume) == 3


def test_calc_experience_months_empty_projects():
    assert _calc_experience_months({"projects": []}) == 0


def test_calc_experience_months_no_projects_key():
    assert _calc_experience_months({}) == 0


def test_calc_experience_months_skips_end_before_start():
    resume = {
        "projects": [
            {"start_date": "2024-06-01", "end_date": "2024-01-01"},  # invalid range
        ]
    }
    assert _calc_experience_months(resume) == 0


# ---------------------------------------------------------------------------
# _resume_full_text
# ---------------------------------------------------------------------------

def test_resume_full_text_includes_skills():
    resume = {"skills": {"Languages": ["Python", "JavaScript"]}, "projects": []}
    text = _resume_full_text(resume)
    assert "Python" in text
    assert "JavaScript" in text


def test_resume_full_text_includes_bullets():
    resume = {
        "projects": [
            {"title": "My App", "bullets": ["Built REST API", "Used Docker"], "skills": []}
        ]
    }
    text = _resume_full_text(resume)
    assert "Built REST API" in text
    assert "Used Docker" in text


def test_resume_full_text_includes_project_skills():
    resume = {
        "projects": [
            {"title": "X", "bullets": [], "skills": ["FastAPI", "PostgreSQL"]}
        ]
    }
    text = _resume_full_text(resume)
    assert "FastAPI" in text


def test_resume_full_text_empty_resume():
    assert _resume_full_text({}) == ""


# ---------------------------------------------------------------------------
# _all_resume_skills
# ---------------------------------------------------------------------------

def test_all_resume_skills_returns_tokens_from_skills_section():
    resume = {"skills": {"Languages": ["Python", "JavaScript"]}}
    skills = _all_resume_skills(resume)
    assert "python" in skills
    assert "javascript" in skills


def test_all_resume_skills_returns_tokens_from_project_skills():
    resume = {
        "projects": [{"skills": ["React", "Node.js"]}]
    }
    skills = _all_resume_skills(resume)
    assert "react" in skills


def test_all_resume_skills_empty_resume():
    assert _all_resume_skills({}) == []


# ---------------------------------------------------------------------------
# _score_ats (integration)
# ---------------------------------------------------------------------------

def test_score_ats_returns_valid_structure():
    with patch("app.api.routes.ats._gemini_extract_jd_keywords", return_value=["python", "docker"]):
        result = _score_ats(SAMPLE_RESUME, LONG_JD)

    assert 0 <= result.score <= 100
    assert result.match_level in ("High", "Medium", "Low")
    assert result.experience_months >= 0
    assert set(result.breakdown.keys()) == {"keyword_coverage", "skills_match", "content_richness"}
    assert isinstance(result.matched_keywords, list)
    assert isinstance(result.missing_keywords, list)
    assert isinstance(result.matched_skills, list)
    assert isinstance(result.missing_skills, list)
    assert isinstance(result.tips, list)


def test_score_ats_keyword_lists_capped_at_20():
    # 25 non-tech keywords to force the cap on the general-keywords pool
    many_kw = [f"keyword{i}" for i in range(25)]
    with patch("app.api.routes.ats._extract_jd_keywords_fallback", return_value=many_kw):
        result = _score_ats({}, "placeholder job description for testing purposes here")

    assert len(result.matched_keywords) <= 20
    assert len(result.missing_keywords) <= 20
    assert len(result.matched_skills) <= 20
    assert len(result.missing_skills) <= 20


def test_score_ats_known_keyword_in_resume_is_matched():
    resume = {
        "skills": {"Languages": ["Python"]},
        "projects": [{"title": "Test", "bullets": ["Used python for analysis"], "skills": []}],
    }
    with patch("app.api.routes.ats._extract_jd_keywords_fallback", return_value=["python"]):
        result = _score_ats(resume, "We need python for this role.")

    assert "python" in result.matched_skills
    assert "python" in result.matched_keywords


def test_score_ats_unknown_keyword_not_in_resume_is_missing():
    with patch("app.api.routes.ats._extract_jd_keywords_fallback", return_value=["kubernetes"]):
        result = _score_ats({"skills": {}, "projects": []}, "We need kubernetes experience.")

    assert "kubernetes" in result.missing_skills
    assert "kubernetes" in result.missing_keywords


def test_score_ats_content_richness_capped_at_100():
    resume = {"projects": [{"bullets": [f"Bullet {i}" for i in range(20)]}]}
    with patch("app.api.routes.ats._gemini_extract_jd_keywords", return_value=["python"]):
        result = _score_ats(resume, "We need python developers with 3 years experience.")

    assert result.breakdown["content_richness"] == 100


def test_score_ats_empty_resume_gives_zero_keyword_and_skills_score():
    # Empty resume → keywords not found → both keyword_coverage and skills_match are 0.
    with patch("app.api.routes.ats._extract_jd_keywords_fallback",
               return_value=["python", "react", "docker", "kubernetes"]):
        result = _score_ats({}, "Requires python react docker kubernetes experience now.")

    assert result.breakdown["keyword_coverage"] == 0
    assert result.breakdown["skills_match"] == 0


def test_score_ats_always_returns_at_least_one_tip():
    with patch("app.api.routes.ats._gemini_extract_jd_keywords", return_value=["python"]):
        result = _score_ats(SAMPLE_RESUME, "We need python for this role.")

    assert len(result.tips) >= 1


def test_score_ats_experience_months_matches_project_dates():
    resume = {
        "projects": [
            {"start_date": "2024-01-01", "end_date": "2024-07-01",  # 6 months
             "bullets": [], "skills": []}
        ]
    }
    with patch("app.api.routes.ats._extract_jd_keywords_fallback", return_value=["python"]):
        result = _score_ats(resume, "We need python for this role.")

    assert result.experience_months == 6


def test_tech_keywords_in_matched_skills_and_matched_keywords():
    """Tech keywords found in resume appear in both matched_skills and matched_keywords."""
    resume = {
        "projects": [{"bullets": ["Built API with python and react"], "skills": []}]
    }
    with patch("app.api.routes.ats._extract_jd_keywords_fallback",
               return_value=["python", "react"]):
        result = _score_ats(resume, "We need python and react experience.")

    assert "python" in result.matched_skills
    assert "react" in result.matched_skills
    assert "python" in result.matched_keywords
    assert "react" in result.matched_keywords


def test_skills_match_uses_only_tech_keywords():
    """skills_match denominator is only tech-keyword JD terms; keyword_coverage uses all JD terms."""
    resume = {
        "projects": [{"bullets": ["Experienced with python and agile processes"], "skills": []}]
    }
    # "python" is a tech keyword, "agile" is not
    with patch("app.api.routes.ats._extract_jd_keywords_fallback",
               return_value=["python", "agile"]):
        result = _score_ats(resume, "We need python and agile experience.")

    # keyword_coverage: 2/2 matched → 100%
    assert result.breakdown["keyword_coverage"] == 100
    # skills_match: only "python" in tech pool, found → 100%
    assert result.breakdown["skills_match"] == 100
    # "agile" is in matched_keywords (general pool) but NOT in matched_skills (tech pool)
    assert "agile" in result.matched_keywords
    assert "agile" not in result.matched_skills


def test_all_keywords_matched_gives_100():
    """When all JD keywords are found in the resume, both scores are 100."""
    resume = {
        "projects": [{"bullets": ["Works with python react docker daily"], "skills": []}]
    }
    with patch("app.api.routes.ats._extract_jd_keywords_fallback",
               return_value=["python", "react", "docker"]):
        result = _score_ats(resume, "We need python react docker experience.")

    assert result.breakdown["keyword_coverage"] == 100
    assert result.breakdown["skills_match"] == 100


def test_no_keywords_matched_gives_zero():
    """When no JD keywords appear in the resume, both scores are 0."""
    with patch("app.api.routes.ats._extract_jd_keywords_fallback",
               return_value=["kubernetes", "terraform", "ansible"]):
        result = _score_ats({}, "We need kubernetes terraform ansible experience.")

    assert result.breakdown["keyword_coverage"] == 0
    assert result.breakdown["skills_match"] == 0


def test_compound_token_expansion_matches_skills():
    """Resume text 'node.js' should match JD keyword 'node' via token expansion."""
    resume = {
        "projects": [{"bullets": ["Built REST API with Node.js and React.js on AWS"], "skills": []}]
    }
    with patch("app.api.routes.ats._extract_jd_keywords_fallback",
               return_value=["node", "react", "aws"]):
        result = _score_ats(resume, "We need node react and aws experience.")

    assert result.breakdown["skills_match"] > 0
    assert "node" in result.matched_skills or "react" in result.matched_skills


# ---------------------------------------------------------------------------
# POST /api/ats/score endpoint
# ---------------------------------------------------------------------------

def test_post_ats_score_rejects_jd_shorter_than_10_chars():
    response = client.post("/api/ats/score", json={"job_description": "short"})
    assert response.status_code == 422


def test_post_ats_score_returns_200_with_valid_payload():
    with patch("app.api.routes.ats.build_resume_model", return_value=SAMPLE_RESUME):
        response = client.post("/api/ats/score", json={"job_description": LONG_JD})

    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert "match_level" in data
    assert "breakdown" in data
    assert "matched_keywords" in data
    assert "missing_keywords" in data
    assert "matched_skills" in data
    assert "missing_skills" in data
    assert "tips" in data


def test_post_ats_score_uses_master_resume_when_no_resume_id():
    with patch("app.api.routes.ats.build_resume_model", return_value=SAMPLE_RESUME) as mock_build, \
         patch("app.api.routes.ats.load_saved_resume") as mock_load:
        response = client.post("/api/ats/score", json={"job_description": LONG_JD})

    assert response.status_code == 200
    mock_build.assert_called_once()
    mock_load.assert_not_called()


def test_post_ats_score_uses_master_resume_when_resume_id_is_null():
    with patch("app.api.routes.ats.build_resume_model", return_value=SAMPLE_RESUME) as mock_build, \
         patch("app.api.routes.ats.load_saved_resume") as mock_load:
        response = client.post(
            "/api/ats/score",
            json={"job_description": LONG_JD, "resume_id": None}
        )

    assert response.status_code == 200
    mock_build.assert_called_once()
    mock_load.assert_not_called()


def test_post_ats_score_uses_saved_resume_when_resume_id_given():
    with patch("app.api.routes.ats.load_saved_resume", return_value=SAMPLE_RESUME) as mock_load, \
         patch("app.api.routes.ats.build_resume_model") as mock_build:
        response = client.post(
            "/api/ats/score",
            json={"job_description": LONG_JD, "resume_id": 2}
        )

    assert response.status_code == 200
    mock_load.assert_called_once_with(2)
    mock_build.assert_not_called()


def test_post_ats_score_returns_404_when_resume_not_found():
    with patch("app.api.routes.ats.load_saved_resume", side_effect=Exception("Resume not found")):
        response = client.post(
            "/api/ats/score",
            json={"job_description": LONG_JD, "resume_id": 999}
        )

    assert response.status_code == 404
    assert "Resume not found" in response.json()["detail"]


def test_post_ats_score_returns_404_when_master_resume_fails_to_build():
    with patch("app.api.routes.ats.build_resume_model", side_effect=Exception("DB error")):
        response = client.post("/api/ats/score", json={"job_description": LONG_JD})

    assert response.status_code == 404


def test_post_ats_score_returns_422_when_resume_has_no_content():
    empty_resume = {"skills": {}, "projects": []}
    with patch("app.api.routes.ats.build_resume_model", return_value=empty_resume):
        response = client.post("/api/ats/score", json={"job_description": LONG_JD})

    assert response.status_code == 422
    assert response.json()["detail"] == "EMPTY_RESUME"


def test_post_ats_score_score_is_in_valid_range():
    with patch("app.api.routes.ats.build_resume_model", return_value=SAMPLE_RESUME):
        response = client.post("/api/ats/score", json={"job_description": LONG_JD})

    assert response.status_code == 200
    score = response.json()["score"]
    assert 0 <= score <= 100


def test_post_ats_score_match_level_is_valid():
    with patch("app.api.routes.ats.build_resume_model", return_value=SAMPLE_RESUME):
        response = client.post("/api/ats/score", json={"job_description": LONG_JD})

    assert response.status_code == 200
    assert response.json()["match_level"] in ("High", "Medium", "Low")


def test_post_ats_score_breakdown_has_all_keys():
    with patch("app.api.routes.ats.build_resume_model", return_value=SAMPLE_RESUME):
        response = client.post("/api/ats/score", json={"job_description": LONG_JD})

    assert response.status_code == 200
    breakdown = response.json()["breakdown"]
    assert "keyword_coverage" in breakdown
    assert "skills_match" in breakdown
    assert "content_richness" in breakdown


def test_post_ats_score_breakdown_values_in_range():
    with patch("app.api.routes.ats.build_resume_model", return_value=SAMPLE_RESUME):
        response = client.post("/api/ats/score", json={"job_description": LONG_JD})

    assert response.status_code == 200
    for val in response.json()["breakdown"].values():
        assert 0 <= val <= 100


def test_post_ats_score_response_keyword_lists_capped_at_20():
    with patch("app.api.routes.ats.build_resume_model", return_value=SAMPLE_RESUME):
        response = client.post("/api/ats/score", json={"job_description": LONG_JD})

    assert response.status_code == 200
    data = response.json()
    assert len(data["matched_keywords"]) <= 20
    assert len(data["missing_keywords"]) <= 20
    assert len(data["matched_skills"]) <= 20
    assert len(data["missing_skills"]) <= 20


# ---------------------------------------------------------------------------
# analysis_mode routing
# ---------------------------------------------------------------------------

def test_local_mode_uses_fallback_not_gemini():
    """analysis_mode=local must call _extract_jd_keywords_fallback and NOT _gemini_extract_jd_keywords."""
    with patch("app.api.routes.ats.build_resume_model", return_value=SAMPLE_RESUME), \
         patch("app.api.routes.ats._extract_jd_keywords_fallback", return_value=["python", "docker"]) as mock_local, \
         patch("app.api.routes.ats._gemini_extract_jd_keywords") as mock_gemini:
        response = client.post(
            "/api/ats/score",
            json={"job_description": LONG_JD, "analysis_mode": "local"},
        )
    assert response.status_code == 200
    mock_local.assert_called_once_with(LONG_JD)
    mock_gemini.assert_not_called()


def test_ai_mode_uses_gemini_not_fallback():
    """analysis_mode=ai must call _gemini_extract_jd_keywords and NOT _extract_jd_keywords_fallback."""
    with patch("app.api.routes.ats.build_resume_model", return_value=SAMPLE_RESUME), \
         patch("app.api.routes.ats._gemini_extract_jd_keywords", return_value=["python", "docker"]) as mock_gemini, \
         patch("app.api.routes.ats._extract_jd_keywords_fallback") as mock_local:
        response = client.post(
            "/api/ats/score",
            json={"job_description": LONG_JD, "analysis_mode": "ai"},
        )
    assert response.status_code == 200
    mock_gemini.assert_called_once_with(LONG_JD)
    mock_local.assert_not_called()


def test_default_analysis_mode_is_local():
    """Omitting analysis_mode must default to local (fallback) extraction."""
    with patch("app.api.routes.ats.build_resume_model", return_value=SAMPLE_RESUME), \
         patch("app.api.routes.ats._extract_jd_keywords_fallback", return_value=["python"]) as mock_local, \
         patch("app.api.routes.ats._gemini_extract_jd_keywords") as mock_gemini:
        response = client.post("/api/ats/score", json={"job_description": LONG_JD})
    assert response.status_code == 200
    mock_local.assert_called_once()
    mock_gemini.assert_not_called()


def test_invalid_analysis_mode_rejected():
    """An unrecognised analysis_mode value must be rejected with 422."""
    with patch("app.api.routes.ats.build_resume_model", return_value=SAMPLE_RESUME):
        response = client.post(
            "/api/ats/score",
            json={"job_description": LONG_JD, "analysis_mode": "turbo"},
        )
    assert response.status_code == 422
