from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, field_validator
from app.api.routes.eduction_service import search_institutions, get_all_institutions
from app.data.db import get_connection
from typing import List, Optional
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter()

class EducationDetail(BaseModel):
    institution: str
    degree: str
    start_date: str  # Format: YYYY-MM-DD
    end_date: Optional[str] = None  # Format: YYYY-MM-DD or None if ongoing
    details: Optional[str] = None

class UserPreferenceRequest(BaseModel):
    name: str
    email: str
    github_user: str
    education: str
    industry: str
    job_title: str
    education_details: Optional[List[EducationDetail]] = None
    
    @field_validator("start_date", "end_date", check_fields=False)
    @classmethod
    def validate_date_format(cls, value):
        if value:
            # Basic date format validation
            import re
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
                raise ValueError("Date must be in YYYY-MM-DD format")
        return value

@router.get("/user-preferences")
def get_user_preferences():
    """Retrieve latest user preferences."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT name, email, github_user, education, industry, job_title, education_details
        FROM USER_PREFERENCES
        ORDER BY updated_at DESC
        LIMIT 1
        """
    )
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="No user preferences found")
    
    return {
        "name": row[0],
        "email": row[1],
        "github_user": row[2],
        "education": row[3],
        "industry": row[4],
        "job_title": row[5],
        "education_details": row[6],
    }

@router.post("/user-preferences")
def save_user_preferences(request: UserPreferenceRequest):
    """Save or update user preferences using UPSERT."""
    conn = get_connection()
    cursor = conn.cursor()

    # Convert education_details to JSON string
    education_details_json = None
    if request.education_details:
        education_details_json = json.dumps([ed.model_dump() for ed in request.education_details])
    
    # UPSERT: Insert if no row exists (user_id=1), otherwise UPDATE existing row
    cursor.execute(
        """
        INSERT INTO USER_PREFERENCES (user_id, name, email, github_user, education, industry, job_title, education_details, updated_at)
        VALUES (1, ?, ?, ?, ?, ?, ?, ? , CURRENT_TIMESTAMP)
        ON CONFLICT(user_id) DO UPDATE SET
            name = excluded.name,
            email = excluded.email,
            github_user = excluded.github_user,
            education = excluded.education,
            industry = excluded.industry,
            job_title = excluded.job_title,
            education_details = excluded.education_details,
            updated_at = CURRENT_TIMESTAMP
        """,
        (request.name, request.email, request.github_user, request.education, request.industry, request.job_title, education_details_json)
    )
    conn.commit()
    conn.close()
    
    return {"status": "ok", "message": "User preferences saved successfully"}

@router.get("/institutions/search")
def search_canadian_institutions(
    q: str = Query("", description="Search query for institution name"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of results")
):
    """
    Search Canadian post-secondary institutions.
    
    Query parameters:
    - q: Search term (e.g., "University of", "Toronto")
    - limit: Max results (1-200)
    
    Returns:
        List of matching institutions with details
    """
    try:
        institutions = search_institutions(query=q, limit=limit)
        return {
            "status": "ok",
            "count": len(institutions),
            "institutions": institutions
        }
    except Exception as e:
        logger.exception("Error searching institutions")
        raise HTTPException(status_code=500, detail="Failed to search institutions")


@router.get("/institutions/list")
def get_institutions_list():
    """
    Get a complete list of all Canadian post-secondary institution names.
    Useful for autocomplete dropdowns.
    
    Returns:
        List of institution names (sorted alphabetically)
    """
    try:
        institutions = get_all_institutions()
        return {
            "status": "ok",
            "count": len(institutions),
            "institutions": institutions
        }
    except Exception as e:
        logger.exception("Error fetching institution list")
        raise HTTPException(status_code=500, detail="Failed to fetch institutions")