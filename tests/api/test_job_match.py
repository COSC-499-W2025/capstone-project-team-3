from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes.job_match import router

app = FastAPI()
app.include_router(router, prefix="/api")
client = TestClient(app)


def _mock_portfolio_payload():
    return {
        "overview": {
            "total_projects": 4,
            "avg_score": 0.82,
        },
        "graphs": {
            "top_skills": {
                "Python": 5,
                "FastAPI": 3,
                "Docker": 2,
                "SQL": 2,
                "React": 2,
            }
        },
        "projects": [
            {
                "skills": ["Python", "FastAPI", "REST", "Git"],
                "metrics": {
                    "technical_keywords": ["API", "testing"],
                    "roles": ["Backend Developer"],
                },
            },
            {
                "skills": ["React", "TypeScript", "Jest"],
                "metrics": {
                    "technical_keywords": ["frontend"],
                    "roles": ["Frontend Engineer"],
                },
            },
        ],
    }


@patch("app.utils.job_match_utils.build_portfolio_model")
def test_job_match_simulation_success(mock_build):
    mock_build.return_value = _mock_portfolio_payload()

    response = client.post(
        "/api/job-match/simulate",
        json={
            "job_description": "We are looking for a backend engineer with strong Python, FastAPI, SQL and Docker experience. React is a plus.",
            "top_k": 3,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert isinstance(data["match_score"], int)
    assert len(data["recommended_jobs"]) >= 1
    assert any(item["title"] for item in data["recommended_jobs"])


@patch("app.utils.job_match_utils.build_portfolio_model")
def test_job_match_validation_error_for_short_description(mock_build):
    mock_build.return_value = _mock_portfolio_payload()

    response = client.post(
        "/api/job-match/simulate",
        json={"job_description": "too short", "top_k": 3},
    )

    assert response.status_code == 422


@patch("app.utils.job_match_utils.build_portfolio_model")
def test_job_match_includes_search_query_recommendations(mock_build):
    mock_build.return_value = _mock_portfolio_payload()

    response = client.post(
        "/api/job-match/simulate",
        json={
            "job_description": "Build APIs, maintain Dockerized services, and collaborate on CI/CD pipelines.",
            "top_k": 5,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["recommended_jobs"]
    assert all("search_query" in job for job in data["recommended_jobs"])
