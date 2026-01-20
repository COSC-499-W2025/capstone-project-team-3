from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.data.db import get_connection

router = APIRouter()

@router.get("/skills", response_model=List[Dict[str, Any]])
def get_skills():
    """
    Return all unique skills across all projects.
    
    Returns:
        List of all skills with frequency and source information
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Query to get all skills with their frequency
    cursor.execute("""
        SELECT 
            s.skill, 
            COUNT(DISTINCT s.project_id) as frequency, 
            s.source
        FROM SKILL_ANALYSIS s
        GROUP BY s.skill, s.source
        ORDER BY frequency DESC, s.skill ASC
    """)

    skills = []
    for skill, frequency, source in cursor.fetchall():
        skills.append({
            "skill": skill,
            "frequency": frequency,
            "source": source
        })

    conn.close()
    return skills
