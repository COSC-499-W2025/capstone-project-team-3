"""
API routes for chronological project and skill date management.

Wraps ChronologicalManager utility methods as REST endpoints so the
frontend / desktop app can read and correct project/skill dates without
going through the CLI.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
from app.utils.chronological_utils import ChronologicalManager

router = APIRouter()


# ---------------------------------------------------------------------------
# Pydantic request models
# ---------------------------------------------------------------------------

class UpdateProjectDatesRequest(BaseModel):
    created_at: str
    last_modified: str


class AddSkillRequest(BaseModel):
    skill: str
    source: str  # "code" or "non-code"
    date: str


class UpdateSkillDateRequest(BaseModel):
    date: str


class UpdateSkillNameRequest(BaseModel):
    skill: str


# ---------------------------------------------------------------------------
# Project endpoints
# ---------------------------------------------------------------------------

@router.get("/chronological/projects", response_model=List[Dict[str, Any]])
def get_chronological_projects():
    """
    Return all projects with their date information (created_at, last_modified).

    These are the raw dates stored in the PROJECT table, useful for reviewing
    and correcting project timelines.
    """
    manager = ChronologicalManager()
    try:
        return manager.get_all_projects()
    finally:
        manager.close()


@router.get("/chronological/projects/{signature}", response_model=Dict[str, Any])
def get_chronological_project(signature: str):
    """
    Return a single project's date information by its signature.

    Raises 404 if the project is not found.
    """
    manager = ChronologicalManager()
    try:
        project = manager.get_project_by_signature(signature)
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        return project
    finally:
        manager.close()


@router.patch("/chronological/projects/{signature}/dates", response_model=Dict[str, Any])
def update_project_dates(signature: str, body: UpdateProjectDatesRequest):
    """
    Update the created_at and last_modified dates of a project.

    Accepts dates in YYYY-MM-DD or YYYY-MM-DD HH:MM:SS format.
    Raises 404 if the project does not exist.
    """
    manager = ChronologicalManager()
    try:
        project = manager.get_project_by_signature(signature)
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        manager.update_project_dates(signature, body.created_at, body.last_modified)
        return manager.get_project_by_signature(signature)
    finally:
        manager.close()


# ---------------------------------------------------------------------------
# Skill endpoints (per project)
# ---------------------------------------------------------------------------

@router.get(
    "/chronological/projects/{signature}/skills",
    response_model=List[Dict[str, Any]],
)
def get_project_chronological_skills(signature: str):
    """
    Return all skills for a project ordered chronologically (date ascending).

    Each entry includes: id, skill, source, date.
    Raises 404 if the project does not exist.
    """
    manager = ChronologicalManager()
    try:
        project = manager.get_project_by_signature(signature)
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        return manager.get_chronological_skills(signature)
    finally:
        manager.close()


@router.post(
    "/chronological/projects/{signature}/skills",
    response_model=Dict[str, Any],
    status_code=201,
)
def add_skill_to_project(signature: str, body: AddSkillRequest):
    """
    Add a new skill with a date to a project.

    Request body:
    - skill: skill name
    - source: "code" or "non-code"
    - date: YYYY-MM-DD

    Raises 404 if the project does not exist.
    Raises 400 if skill name is empty or source is invalid.
    """
    if not body.skill.strip():
        raise HTTPException(status_code=400, detail="Skill name cannot be empty")
    if body.source not in ("code", "non-code"):
        raise HTTPException(
            status_code=400, detail="Source must be 'code' or 'non-code'"
        )

    manager = ChronologicalManager()
    try:
        project = manager.get_project_by_signature(signature)
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        manager.add_skill_with_date(signature, body.skill.strip(), body.source, body.date)
        return {"message": "Skill added", "skill": body.skill.strip(), "source": body.source, "date": body.date}
    finally:
        manager.close()


# ---------------------------------------------------------------------------
# Skill endpoints (by skill ID)
# ---------------------------------------------------------------------------

@router.patch("/chronological/skills/{skill_id}/date", response_model=Dict[str, Any])
def update_skill_date(skill_id: int, body: UpdateSkillDateRequest):
    """
    Update the date of a specific skill entry.

    Raises 404 if no skill with that id exists.
    """
    manager = ChronologicalManager()
    try:
        # Verify skill exists
        cur = manager.conn.cursor()
        cur.execute("SELECT id, skill, source, date FROM SKILL_ANALYSIS WHERE id = ?", (skill_id,))
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Skill not found")
        manager.update_skill_date(skill_id, body.date)
        return {"id": skill_id, "skill": row[1], "source": row[2], "date": body.date}
    finally:
        manager.close()


@router.patch("/chronological/skills/{skill_id}/name", response_model=Dict[str, Any])
def update_skill_name(skill_id: int, body: UpdateSkillNameRequest):
    """
    Rename a skill entry.

    Raises 404 if no skill with that id exists.
    Raises 400 if new skill name is empty.
    """
    if not body.skill.strip():
        raise HTTPException(status_code=400, detail="Skill name cannot be empty")

    manager = ChronologicalManager()
    try:
        cur = manager.conn.cursor()
        cur.execute("SELECT id, skill, source, date FROM SKILL_ANALYSIS WHERE id = ?", (skill_id,))
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Skill not found")
        manager.update_skill_name(skill_id, body.skill.strip())
        return {"id": skill_id, "skill": body.skill.strip(), "source": row[2], "date": row[3]}
    finally:
        manager.close()


@router.delete("/chronological/skills/{skill_id}", status_code=204)
def delete_skill(skill_id: int):
    """
    Delete a skill entry by its ID.

    Raises 404 if no skill with that id exists.
    Returns 204 No Content on success.
    """
    manager = ChronologicalManager()
    try:
        cur = manager.conn.cursor()
        cur.execute("SELECT id FROM SKILL_ANALYSIS WHERE id = ?", (skill_id,))
        if cur.fetchone() is None:
            raise HTTPException(status_code=404, detail="Skill not found")
        manager.remove_skill(skill_id)
    finally:
        manager.close()
