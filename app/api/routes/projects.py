from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.data.db import get_connection
from app.utils.generate_resume import load_projects, load_skills
from app.utils.score_override_utils import (
    ProjectNotFoundError,
    OverrideValidationError,
    apply_project_score_override,
    clear_project_score_override,
    compute_project_breakdown,
    get_project_score_state_map,
    preview_project_score_override,
    resolve_effective_score,
)
from app.utils.delete_insights_utils import (
    get_projects as get_all_projects,
    delete_project_by_signature,
)

router = APIRouter()


class ScoreOverrideRequest(BaseModel):
    exclude_metrics: List[str] = Field(default_factory=list)


@router.get("/projects", response_model=List[Dict[str, Any]])
def get_projects():
    """
    Return all projects with id, name, and top skills.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Load all projects (no filtering)
    projects_raw = load_projects(cursor)
    project_ids = [pid for pid, *_ in projects_raw]
    score_state_map = get_project_score_state_map(cursor, project_ids)

    # Load skills mapping
    skills_map = load_skills(cursor)

    projects = []
    for pid, name, score, created_at, last_modified in projects_raw:
        raw_skills = skills_map.get(pid, [])
        # Optional: limit to top 5 for terminal display
        top_skills = raw_skills[:5]
        score_state = score_state_map.get(
            pid,
            {"score_overridden": False, "score_overridden_value": None},
        )
        score_fields = resolve_effective_score(
            score=score,
            score_overridden=score_state.get("score_overridden"),
            score_overridden_value=score_state.get("score_overridden_value"),
        )

        projects.append({
            "id": pid,
            "name": name,
            "score": score_fields["score"],
            "score_original": score_fields["score_original"],
            "score_overridden": score_fields["score_overridden"],
            "score_overridden_value": score_fields["score_overridden_value"],
            "score_override_exclusions": score_state.get("score_override_exclusions", []),
            "skills": top_skills,
            "date_added": created_at
        })

    conn.close()
    return projects


@router.get("/projects/{signature}", response_model=Dict[str, Any])
def get_project(signature: str):
    """Return a single project by signature."""
    conn = get_connection()
    cursor = conn.cursor()

    project_rows = load_projects(cursor, project_ids=[signature])
    if not project_rows:
        conn.close()
        raise HTTPException(status_code=404, detail="Project not found")

    skills_map = load_skills(cursor)
    pid, name, score, _, _ = project_rows[0]
    score_state_map = get_project_score_state_map(cursor, [pid])
    score_state = score_state_map.get(
        pid,
        {"score_overridden": False, "score_overridden_value": None},
    )
    score_fields = resolve_effective_score(
        score=score,
        score_overridden=score_state.get("score_overridden"),
        score_overridden_value=score_state.get("score_overridden_value"),
    )
    raw_skills = skills_map.get(pid, [])
    top_skills = raw_skills[:5]

    conn.close()
    return {
        "id": pid,
        "name": name,
        "score": score_fields["score"],
        "score_original": score_fields["score_original"],
        "score_overridden": score_fields["score_overridden"],
        "score_overridden_value": score_fields["score_overridden_value"],
        "score_override_exclusions": score_state.get("score_override_exclusions", []),
        "skills": top_skills,
    }


@router.get("/projects/{signature}/score-breakdown", response_model=Dict[str, Any])
def get_project_score_breakdown(signature: str):
    """Return detailed scoring breakdown for a single project."""
    try:
        return compute_project_breakdown(signature)
    except ProjectNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")


@router.post("/projects/{signature}/score-override/preview", response_model=Dict[str, Any])
def preview_project_override(signature: str, payload: Optional[ScoreOverrideRequest] = None):
    """Preview score override without persisting changes."""
    try:
        return preview_project_score_override(
            project_signature=signature,
            exclude_metrics=(payload.exclude_metrics if payload else []),
        )
    except ProjectNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")
    except OverrideValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/projects/{signature}/score-override", response_model=Dict[str, Any])
def apply_project_override(signature: str, payload: Optional[ScoreOverrideRequest] = None):
    """Apply and persist score override for a project."""
    try:
        return apply_project_score_override(
            project_signature=signature,
            exclude_metrics=(payload.exclude_metrics if payload else []),
        )
    except ProjectNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")
    except OverrideValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/projects/{signature}/score-override/clear", response_model=Dict[str, Any])
def clear_project_override(signature: str):
    """Clear score override fields for a project."""
    try:
        return clear_project_score_override(project_signature=signature)
    except ProjectNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")


@router.delete("/projects/{signature}", response_model=Dict[str, Any])
def delete_project(signature: str):
    """
    Delete all insights for a project by its signature.

    Returns 404 if no project with that signature exists.
    """
    # Verify the project exists before attempting deletion
    all_projects = get_all_projects()
    match = next(
        (p for p in all_projects if p["project_signature"] == signature), None
    )
    if match is None:
        raise HTTPException(status_code=404, detail="Project not found")

    deleted = delete_project_by_signature(signature)
    if not deleted:
        raise HTTPException(status_code=500, detail="Deletion failed unexpectedly")

    return {
        "status": "ok",
        "message": f"Project '{match['name']}' deleted successfully",
        "project_signature": signature,
    }
