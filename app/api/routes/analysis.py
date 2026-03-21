from pathlib import Path
import json
import os
from typing import Any, Dict, List, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.client.llm_client import GeminiLLMClient
from app.cli.git_code_parsing import (
    _get_preferred_author_email,
    run_git_parsing_from_files,
)
from app.utils.analysis_merger_utils import merge_analysis_results
from app.utils.code_analysis.code_analysis_utils import (
    analyze_github_project,
    analyze_parsed_project,
)
from app.utils.env_utils import check_gemini_api_key
from app.utils.non_code_analysis.non_3rd_party_analysis import analyze_project_clean
from app.utils.non_code_analysis.non_code_analysis_utils import analyze_non_code_files
from app.utils.non_code_analysis.non_code_file_checker import (
    classify_non_code_files_with_user_verification,
)
from app.utils.code_analysis.parse_code_utils import parse_code_flow
from app.utils.non_code_parsing.document_parser import parsed_input_text
from app.utils.project_extractor import (
    extract_and_list_projects,
    get_project_top_level_dirs,
)
from app.utils.scan_utils import (
    run_scan_flow,
    scan_project_files,
    extract_file_signature,
    get_project_signature,
    find_similar_project,
)
from app.utils.git_utils import detect_git
from app.utils.clean_up import cleanup_upload
from app.data.db import get_connection

router = APIRouter()


def _persist_git_history(
    project_signature: str, git_commits: List[Dict[str, Any]]
) -> None:
    """Replace stored git history only when there is valid parsed commit data."""
    if not project_signature:
        return

    valid_commits: List[Dict[str, str]] = []
    for commit in git_commits:
        commit_hash = commit.get("hash") or commit.get("commit_hash")
        commit_date = commit.get("authored_datetime") or commit.get(
            "committed_datetime"
        )
        if not commit_hash or not commit_date:
            continue
        valid_commits.append(
            {
                "commit_hash": str(commit_hash),
                "commit_date": str(commit_date),
                "author_name": str(commit.get("author_name") or ""),
                "author_email": str(commit.get("author_email") or ""),
                "message": str(
                    commit.get("message_summary") or commit.get("message") or ""
                ),
            }
        )

    if not valid_commits:
        return

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "DELETE FROM GIT_HISTORY WHERE project_id = ?", (project_signature,)
        )

        for commit in valid_commits:
            cur.execute(
                """
                INSERT INTO GIT_HISTORY (project_id, commit_hash, author_name, author_email, commit_date, message)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    project_signature,
                    commit["commit_hash"],
                    commit["author_name"],
                    commit["author_email"],
                    commit["commit_date"],
                    commit["message"],
                ),
            )

        conn.commit()
    finally:
        cur.close()
        conn.close()


class AnalyzeUploadRequest(BaseModel):
    upload_id: str = Field(..., min_length=1)
    default_analysis_type: Literal["local", "ai"] = "local"
    project_analysis_types: Dict[str, Literal["local", "ai"]] = Field(
        default_factory=dict
    )
    similarity_action: Literal["create_new", "update_existing"] = "create_new"
    project_similarity_actions: Dict[str, Literal["create_new", "update_existing"]] = (
        Field(default_factory=dict)
    )
    cleanup_zip: bool = True
    cleanup_extracted: bool = True
    scan_only: bool = False


class ProjectAnalysisResult(BaseModel):
    project_name: str
    project_path: str
    project_signature: str | None = None
    requested_analysis_type: Literal["local", "ai"]
    effective_analysis_type: Literal["local", "ai"]
    status: Literal["analyzed", "skipped", "failed"]
    reason: str | None = None


def _load_projects_from_upload(upload_id: str) -> Dict[str, Any]:
    upload_dir = os.getenv("UPLOAD_DIR", "app/uploads")
    zip_path = os.path.join(upload_dir, f"{upload_id}.zip")

    if not os.path.exists(zip_path):
        raise HTTPException(
            status_code=404, detail="Upload not found for provided upload_id"
        )

    extract_result = extract_and_list_projects(zip_path)
    if extract_result.get("status") != "ok":
        raise HTTPException(
            status_code=400,
            detail=extract_result.get("reason", "Failed to extract uploaded zip"),
        )

    project_paths = extract_result.get("projects", [])
    if not project_paths:
        raise HTTPException(status_code=400, detail="No projects found in uploaded zip")

    return {
        "upload_id": upload_id,
        "zip_path": zip_path,
        "project_paths": project_paths,
        "extracted_dir": extract_result.get("extracted_dir"),
    }


def _resolve_requested_analysis_type(
    project_path: str,
    default_analysis_type: Literal["local", "ai"],
    project_analysis_types: Dict[str, Literal["local", "ai"]],
) -> Literal["local", "ai"]:
    if project_path in project_analysis_types:
        return project_analysis_types[project_path]
    project_name = Path(project_path).name
    if project_name in project_analysis_types:
        return project_analysis_types[project_name]
    return default_analysis_type


def _resolve_requested_similarity_action(
    project_path: str,
    default_similarity_action: Literal["create_new", "update_existing"],
    project_similarity_actions: Dict[str, Literal["create_new", "update_existing"]],
) -> Literal["create_new", "update_existing"]:
    if project_path in project_similarity_actions:
        return project_similarity_actions[project_path]
    project_name = Path(project_path).name
    if project_name in project_similarity_actions:
        return project_similarity_actions[project_name]
    return default_similarity_action


@router.post("/analysis/run")
def run_analysis_for_upload(payload: AnalyzeUploadRequest) -> Dict[str, Any]:
    upload_context = _load_projects_from_upload(payload.upload_id)
    project_paths = upload_context["project_paths"]
    extracted_dir = upload_context["extracted_dir"]

    api_available, _ = check_gemini_api_key()
    api_key = os.getenv("GEMINI_API_KEY")
    llm_client = GeminiLLMClient(api_key=api_key) if api_available and api_key else None

    results: List[ProjectAnalysisResult] = []

    for project_path in project_paths:
        project_name = Path(project_path).name
        requested_analysis_type = _resolve_requested_analysis_type(
            project_path=project_path,
            default_analysis_type=payload.default_analysis_type,
            project_analysis_types=payload.project_analysis_types,
        )
        requested_similarity_action = _resolve_requested_similarity_action(
            project_path=project_path,
            default_similarity_action=payload.similarity_action,
            project_similarity_actions=payload.project_similarity_actions,
        )
        similarity_decision = requested_similarity_action == "update_existing"

        try:
            scan_result = run_scan_flow(
                project_path, similarity_decision=similarity_decision
            )
        except Exception as exc:
            results.append(
                ProjectAnalysisResult(
                    project_name=project_name,
                    project_path=project_path,
                    requested_analysis_type=requested_analysis_type,
                    effective_analysis_type="local",
                    status="failed",
                    reason=f"scan_failed: {exc}",
                )
            )
            continue

        project_signature = scan_result.get("signature")
        if scan_result.get("skip_analysis"):
            results.append(
                ProjectAnalysisResult(
                    project_name=project_name,
                    project_path=project_path,
                    project_signature=project_signature,
                    requested_analysis_type=requested_analysis_type,
                    effective_analysis_type="local",
                    status="skipped",
                    reason=scan_result.get("reason", "skipped"),
                )
            )
            continue

        if payload.scan_only:
            results.append(
                ProjectAnalysisResult(
                    project_name=project_name,
                    project_path=project_path,
                    project_signature=project_signature,
                    requested_analysis_type=requested_analysis_type,
                    effective_analysis_type="local",
                    status="analyzed",
                    reason=None,
                )
            )
            continue

        files = scan_result.get("files", [])
        top_level_dirs = get_project_top_level_dirs(project_path)

        username, email = _get_preferred_author_email()
        non_code_result = classify_non_code_files_with_user_verification(
            project_path, email, username
        )

        try:
            parsed_non_code = parsed_input_text(
                file_paths_dict={
                    "collaborative": non_code_result.get("collaborative", []),
                    "non_collaborative": non_code_result.get("non_collaborative", []),
                },
                repo_path=project_path if non_code_result.get("is_git_repo") else None,
                author=(non_code_result.get("user_identity") or {}).get("email"),
            )
        except Exception:
            parsed_non_code = {"parsed_files": []}

        is_git_repo = detect_git(project_path)
        git_commits: List[Dict[str, Any]] = []
        parsed_code_files: List[Dict[str, Any]] = []

        if is_git_repo:
            try:
                code_git_history_json = run_git_parsing_from_files(
                    file_paths=files,
                    include_merges=False,
                    max_commits=None,
                )
                parsed_history = (
                    json.loads(code_git_history_json) if code_git_history_json else []
                )
                if isinstance(parsed_history, list):
                    git_commits = parsed_history
                    try:
                        _persist_git_history(project_signature, git_commits)
                    except Exception:
                        pass
            except Exception:
                git_commits = []
        else:
            try:
                parsed_code_files = parse_code_flow(files, top_level_dirs)
            except Exception:
                parsed_code_files = []

        effective_analysis_type: Literal["local", "ai"] = requested_analysis_type
        if requested_analysis_type == "ai" and not llm_client:
            effective_analysis_type = "local"

        try:
            if effective_analysis_type == "ai":
                try:
                    non_code_analysis_results = analyze_non_code_files(
                        parsed_non_code=parsed_non_code
                    )
                except Exception:
                    non_code_analysis_results = analyze_project_clean(parsed_non_code)

                try:
                    if is_git_repo:
                        code_analysis_results = analyze_github_project(
                            git_commits, llm_client
                        )
                    else:
                        code_analysis_results = analyze_parsed_project(
                            parsed_code_files, llm_client
                        )
                except Exception:
                    if is_git_repo:
                        code_analysis_results = analyze_github_project(git_commits)
                    else:
                        code_analysis_results = analyze_parsed_project(
                            parsed_code_files
                        )
            else:
                try:
                    non_code_analysis_results = analyze_project_clean(parsed_non_code)
                except Exception:
                    non_code_analysis_results = {}

                if is_git_repo:
                    code_analysis_results = analyze_github_project(git_commits)
                else:
                    code_analysis_results = analyze_parsed_project(parsed_code_files)

            merge_analysis_results(
                non_code_analysis_results=non_code_analysis_results,
                code_analysis_results=code_analysis_results,
                project_name=project_name,
                project_signature=project_signature,
            )

            results.append(
                ProjectAnalysisResult(
                    project_name=project_name,
                    project_path=project_path,
                    project_signature=project_signature,
                    requested_analysis_type=requested_analysis_type,
                    effective_analysis_type=effective_analysis_type,
                    status="analyzed",
                    reason=None,
                )
            )
        except Exception as exc:
            results.append(
                ProjectAnalysisResult(
                    project_name=project_name,
                    project_path=project_path,
                    project_signature=project_signature,
                    requested_analysis_type=requested_analysis_type,
                    effective_analysis_type=effective_analysis_type,
                    status="failed",
                    reason=f"analysis_failed: {exc}",
                )
            )

    cleanup_result = None
    if not payload.scan_only:
        cleanup_result = cleanup_upload(
            upload_id=payload.upload_id,
            extracted_dir=extracted_dir,
            delete_extracted=True,
        )
    elif payload.cleanup_zip:
        cleanup_result = cleanup_upload(
            upload_id=payload.upload_id,
            extracted_dir=extracted_dir,
            delete_extracted=payload.cleanup_extracted,
        )

    analyzed = sum(1 for item in results if item.status == "analyzed")
    skipped = sum(1 for item in results if item.status == "skipped")
    failed = sum(1 for item in results if item.status == "failed")

    return {
        "status": "ok",
        "upload_id": payload.upload_id,
        "total_projects": len(project_paths),
        "analyzed_projects": analyzed,
        "skipped_projects": skipped,
        "failed_projects": failed,
        "results": [item.model_dump() for item in results],
        "cleanup": cleanup_result,
    }


@router.get("/analysis/uploads/{upload_id}/projects")
def list_upload_projects(upload_id: str) -> Dict[str, Any]:
    try:
        upload_context = _load_projects_from_upload(upload_id)
        project_paths: List[str] = upload_context["project_paths"]

        return {
            "status": "ok",
            "upload_id": upload_id,
            "total_projects": len(project_paths),
            "projects": [
                {
                    "name": Path(project_path).name,
                    "path": project_path,
                }
                for project_path in project_paths
            ],
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list uploaded projects: {exc}",
        )


class ScanProjectRequest(BaseModel):
    project_path: str = Field(..., min_length=1)


@router.post("/analysis/uploads/{upload_id}/scan-project")
def scan_single_project(upload_id: str, payload: ScanProjectRequest) -> Dict[str, Any]:
    """Scan a single project and return similarity info WITHOUT storing in DB."""
    try:
        project_path = payload.project_path
        project_name = Path(project_path).name

        files = scan_project_files(project_path)
        if not files:
            return {
                "status": "ok",
                "project_name": project_name,
                "project_path": project_path,
                "file_count": 0,
                "similarity": None,
                "reason": "no_files",
            }

        file_signatures = [extract_file_signature(f, project_path) for f in files]
        project_signature = get_project_signature(file_signatures)
        file_count = len(files)

        # Check if exact match (100%)
        from app.utils.scan_utils import project_signature_exists

        if project_signature_exists(project_signature):
            return {
                "status": "ok",
                "project_name": project_name,
                "project_path": project_path,
                "file_count": file_count,
                "exact_match": True,
                "similarity": {
                    "jaccard_similarity": 100.0,
                    "containment_ratio": 100.0,
                    "matched_project_name": project_name,
                    "match_reason": "Exact match (100%)",
                },
                "reason": "exact_match",
            }

        # Check for similar projects
        match_info = find_similar_project(
            current_signatures=file_signatures,
            new_project_sig=project_signature,
            file_count=file_count,
        )

        if match_info:
            return {
                "status": "ok",
                "project_name": project_name,
                "project_path": project_path,
                "file_count": file_count,
                "similarity": {
                    "jaccard_similarity": match_info["similarity_percentage"],
                    "containment_ratio": match_info["containment_percentage"],
                    "matched_project_name": match_info["project_name"],
                    "match_reason": match_info["match_reason"],
                },
            }
        else:
            return {
                "status": "ok",
                "project_name": project_name,
                "project_path": project_path,
                "file_count": file_count,
                "similarity": None,
                "reason": "no_match",
            }

    except Exception as exc:
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to scan project: {exc}",
        )
