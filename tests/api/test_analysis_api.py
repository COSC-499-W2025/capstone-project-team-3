from pathlib import Path

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
        "project_analysis_types": {"/tmp/extracted/proj2": "local"},
        "similarity_action": "create_new",
        "project_similarity_actions": {"/tmp/extracted/proj2": "update_existing"},
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

    first_call, second_call = mock_run_scan.call_args_list
    assert first_call.kwargs.get("similarity_decision") is False
    assert second_call.kwargs.get("similarity_decision") is True


# ---------------------------------------------------------------------------
# Extension and name-prefix exclusion tests
# ---------------------------------------------------------------------------

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
        "collaborative": ["/tmp/proj/README.md", "/tmp/proj/notes.md", "/tmp/proj/report.pdf"],
        "non_collaborative": [],
    },
)
@patch("app.api.routes.analysis._get_preferred_author_email", return_value=(None, None))
@patch("app.api.routes.analysis.detect_git", return_value=False)
@patch(
    "app.api.routes.analysis.run_scan_flow",
    return_value={
        "files": [],
        "skip_analysis": False,
        "signature": "sig-ext",
    },
)
@patch("app.api.routes.analysis.check_gemini_api_key", return_value=(False, "missing key"))
@patch(
    "app.api.routes.analysis.extract_and_list_projects",
    return_value={
        "status": "ok",
        "projects": ["/tmp/proj"],
        "extracted_dir": "/tmp",
    },
)
@patch("app.api.routes.analysis.os.path.exists", return_value=True)
def test_project_exclude_extensions_filters_non_code_files(
    mock_exists, mock_extract, mock_api_status, mock_scan, mock_git,
    mock_identity, mock_classify, mock_parse_non_code, mock_top_level,
    mock_parse_code, mock_analyze_non_code, mock_analyze_code, mock_merge,
):
    """Files with excluded extensions must not reach parsed_input_text."""
    response = client.post(
        "/api/analysis/run",
        json={
            "upload_id": "upload-ext",
            "project_exclude_extensions": {"/tmp/proj": [".md", ".pdf"]},
        },
    )
    assert response.status_code == 200
    # parsed_input_text should have been called with empty lists (all non-code files filtered out)
    call_kwargs = mock_parse_non_code.call_args.kwargs
    assert call_kwargs["file_paths_dict"]["collaborative"] == []
    assert call_kwargs["file_paths_dict"]["non_collaborative"] == []


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
        "collaborative": ["/tmp/proj/README.md", "/tmp/proj/README.txt", "/tmp/proj/CONTRIBUTING.md"],
        "non_collaborative": [],
    },
)
@patch("app.api.routes.analysis._get_preferred_author_email", return_value=(None, None))
@patch("app.api.routes.analysis.detect_git", return_value=False)
@patch(
    "app.api.routes.analysis.run_scan_flow",
    return_value={
        "files": [],
        "skip_analysis": False,
        "signature": "sig-prefix",
    },
)
@patch("app.api.routes.analysis.check_gemini_api_key", return_value=(False, "missing key"))
@patch(
    "app.api.routes.analysis.extract_and_list_projects",
    return_value={
        "status": "ok",
        "projects": ["/tmp/proj"],
        "extracted_dir": "/tmp",
    },
)
@patch("app.api.routes.analysis.os.path.exists", return_value=True)
def test_project_exclude_name_prefixes_filters_readme_files(
    mock_exists, mock_extract, mock_api_status, mock_scan, mock_git,
    mock_identity, mock_classify, mock_parse_non_code, mock_top_level,
    mock_parse_code, mock_analyze_non_code, mock_analyze_code, mock_merge,
):
    """Files whose stem starts with 'readme' must be excluded when namePrefix filter is set."""
    response = client.post(
        "/api/analysis/run",
        json={
            "upload_id": "upload-prefix",
            "project_exclude_name_prefixes": {"/tmp/proj": ["readme"]},
        },
    )
    assert response.status_code == 200
    call_kwargs = mock_parse_non_code.call_args.kwargs
    remaining = call_kwargs["file_paths_dict"]["collaborative"]
    # README.md and README.txt should be gone; CONTRIBUTING.md should remain
    assert all("readme" not in p.lower().split("/")[-1].split(".")[0] for p in remaining)
    assert any("contributing" in p.lower() for p in remaining)


# ---------------------------------------------------------------------------
# all_files_excluded skip path
# ---------------------------------------------------------------------------

@patch("app.api.routes.analysis.check_gemini_api_key", return_value=(False, "missing key"))
@patch(
    "app.api.routes.analysis.extract_and_list_projects",
    return_value={
        "status": "ok",
        "projects": ["/tmp/proj"],
        "extracted_dir": "/tmp",
    },
)
@patch("app.api.routes.analysis.os.path.exists", return_value=True)
@patch(
    "app.api.routes.analysis.run_scan_flow",
    return_value={
        "files": [Path("/tmp/proj/README.md"), Path("/tmp/proj/notes.md")],
        "skip_analysis": False,
        "signature": "sig-all-excl",
    },
)
def test_all_files_excluded_returns_skipped(mock_scan, mock_exists, mock_extract, mock_api_key):
    """When exclusions remove every file the project must be skipped with reason all_files_excluded."""
    response = client.post(
        "/api/analysis/run",
        json={
            "upload_id": "upload-all-excl",
            "project_exclude_extensions": {"/tmp/proj": [".md"]},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["analyzed_projects"] == 0
    assert data["skipped_projects"] == 1
    assert data["failed_projects"] == 0
    result = data["results"][0]
    assert result["status"] == "skipped"
    assert result["reason"] == "all_files_excluded"
