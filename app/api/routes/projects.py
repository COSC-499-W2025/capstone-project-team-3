from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from app.data.db import get_connection
from app.utils.generate_resume import load_projects, load_skills

router = APIRouter()

@router.get("/projects", response_model=List[Dict[str, Any]])
def get_projects():
    """
    Return all projects with id, name, and top skills.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Load all projects (no filtering)
    projects_raw = load_projects(cursor)

    # Load skills mapping
    skills_map = load_skills(cursor)

    projects = []
    for pid, name, score, created_at, last_modified in projects_raw:
        raw_skills = skills_map.get(pid, [])
        # Optional: limit to top 5 for terminal display
        top_skills = raw_skills[:5]

        projects.append({
            "id": pid,
            "name": name,
            "score": float(rank) if rank else 0.0,
            "skills": top_skills
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
    pid, name, rank, _, _ = project_rows[0]
    raw_skills = skills_map.get(pid, [])
    top_skills = raw_skills[:5]

    conn.close()
    return {
        "id": pid,
        "name": name,
        "score": float(rank) if rank else 0.0,
        "skills": top_skills,
    }
