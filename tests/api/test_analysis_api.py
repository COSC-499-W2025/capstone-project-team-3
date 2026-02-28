from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.api.routes.analysis import router


app = FastAPI()
app.include_router(router, prefix="/api")
client = TestClient(app)


@patch("app.api.routes.analysis.extract_and_list_projects")
@patch("app.api.routes.analysis.os.path.exists", return_value=True)
def test_list_upload_projects_success(mock_exists, mock_extract):
    mock_extract.return_value = {
        "status": "ok",
        "projects": ["/tmp/extracted/untitled folder", "/tmp/extracted/untitled folder 2"],
        "extracted_dir": "/tmp/extracted",
    }

    response = client.get("/api/analysis/uploads/upload-123/projects")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["upload_id"] == "upload-123"
    assert data["total_projects"] == 2
    assert data["projects"][0]["name"] == "untitled folder"
    assert data["projects"][1]["name"] == "untitled folder 2"


@patch("app.api.routes.analysis.os.path.exists", return_value=False)
def test_list_upload_projects_not_found(mock_exists):
    response = client.get("/api/analysis/uploads/missing/projects")
    assert response.status_code == 404
    assert response.json()["detail"] == "Upload not found for provided upload_id"


@patch("app.api.routes.analysis.os.path.exists", return_value=False)
def test_run_analysis_upload_not_found(mock_exists):
    response = client.post(
        "/api/analysis/run",
        json={"upload_id": "missing-upload"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Upload not found for provided upload_id"


@patch("app.api.routes.analysis.merge_analysis_results")
@patch("app.api.routes.analysis.analyze_parsed_project", return_value={"Metrics": {}, "Resume_bullets": []})
@patch("app.api.routes.analysis.analyze_project_clean", return_value={"Metrics": {}})
@patch("app.api.routes.analysis.parse_code_flow", return_value=[])
@patch("app.api.routes.analysis.get_project_top_level_dirs", return_value=[])
@patch("app.api.routes.analysis.parsed_input_text", return_value={"parsed_files": []})
@patch(
    "app.api.routes.analysis.classify_non_code_files_with_user_verification",
    return_value={
        "is_git_repo": False,
        "user_identity": {},
        "collaborative": [],
        "non_collaborative": [],
    },
)
@patch("app.api.routes.analysis._get_preferred_author_email", return_value=(None, None))
@patch("app.api.routes.analysis.detect_git", return_value=False)
@patch(
    "app.api.routes.analysis.run_scan_flow",
    side_effect=[
        {
            "files": ["/tmp/extracted/proj1/main.py"],
            "skip_analysis": True,
            "reason": "already_analyzed",
            "signature": "sig-1",
        },
        {
            "files": ["/tmp/extracted/proj2/main.py"],
            "skip_analysis": False,
            "signature": "sig-2",
        },
    ],
)
@patch("app.api.routes.analysis.check_gemini_api_key", return_value=(False, "missing key"))
@patch(
    "app.api.routes.analysis.extract_and_list_projects",
    return_value={
        "status": "ok",
        "projects": ["/tmp/extracted/proj1", "/tmp/extracted/proj2"],
        "extracted_dir": "/tmp/extracted",
    },
)
@patch("app.api.routes.analysis.os.path.exists", return_value=True)
def test_run_analysis_non_interactive_flow(
    mock_exists,
    mock_extract,
    mock_api_status,
    mock_run_scan,
    mock_detect_git,
    mock_identity,
    mock_classify,
    mock_parse_non_code,
    mock_top_level,
    mock_parse_code,
    mock_analyze_non_code,
    mock_analyze_code,
    mock_merge,
):
    payload = {
        "upload_id": "upload-123",
        "default_analysis_type": "ai",
        "project_analysis_types": {"proj2": "local"},
        "similarity_action": "create_new",
    }

    response = client.post("/api/analysis/run", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["total_projects"] == 2
    assert data["analyzed_projects"] == 1
    assert data["skipped_projects"] == 1
    assert data["failed_projects"] == 0

    skipped = next(item for item in data["results"] if item["project_name"] == "proj1")
    analyzed = next(item for item in data["results"] if item["project_name"] == "proj2")

    assert skipped["status"] == "skipped"
    assert skipped["reason"] == "already_analyzed"

    assert analyzed["status"] == "analyzed"
    assert analyzed["requested_analysis_type"] == "local"
    assert analyzed["effective_analysis_type"] == "local"

    for call in mock_run_scan.call_args_list:
        assert call.kwargs.get("similarity_decision") is False
