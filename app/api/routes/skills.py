from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
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

    # Query to get all skills
    cursor.execute("""
        SELECT 
            s.skill, 
            COUNT(DISTINCT s.project_id) as frequency, 
            s.source
        FROM SKILL_ANALYSIS s
        GROUP BY s.skill, s.source
        ORDER BY s.skill ASC
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


@router.get("/skills/frequent", response_model=List[Dict[str, Any]])
def get_frequent_skills(limit: Optional[int] = Query(10, ge=1, le=50)):
    """
    Return the most frequently used skills across all projects.
    
    Args:
        limit: Number of top skills to return (default: 10, max: 50)
    
    Returns:
        List of most frequently used skills sorted by frequency
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Query to get most frequent skills
    cursor.execute("""
        SELECT 
            s.skill, 
            COUNT(DISTINCT s.project_id) as frequency, 
            s.source
        FROM SKILL_ANALYSIS s
        GROUP BY s.skill, s.source
        ORDER BY frequency DESC, s.skill ASC
        LIMIT ?
    """, (limit,))

    skills = []
    for skill, frequency, source in cursor.fetchall():
        skills.append({
            "skill": skill,
            "frequency": frequency,
            "source": source
        })

    conn.close()
    return skills
