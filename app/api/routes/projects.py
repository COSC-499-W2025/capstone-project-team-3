from fastapi import APIRouter
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
    for pid, name, rank, created_at, last_modified in projects_raw:
        raw_skills = skills_map.get(pid, [])
        # Optional: limit to top 5 for terminal display
        top_skills = raw_skills[:5]

        projects.append({
            "id": pid,
            "name": name,
            "skills": top_skills
        })

    conn.close()
    return projects
