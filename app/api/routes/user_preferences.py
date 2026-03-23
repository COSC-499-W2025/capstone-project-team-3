from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel, field_validator
from app.utils.canadian_institutions_api import (
    search_institutions,
    search_institutions_simple,
    get_all_institutions
)
from app.data.db import get_connection, DATA_DIR
from typing import List, Optional
import logging
import json
import re
from pathlib import Path

logger = logging.getLogger(__name__)
router = APIRouter()

# Define profile picture directories
THUMBNAIL_DIR = DATA_DIR / "thumbnails"
THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)
# Constants
PROFILE_PICTURE_FILENAME = "profile_picture"
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}
# File Size Limit
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

class EducationDetail(BaseModel):
    institution: str
    degree: str
    start_date: str  # Format: YYYY-MM-DD
    end_date: Optional[str] = None  # Format: YYYY-MM-DD or None if ongoing
    gpa: Optional[float] = None # GPA on a 4.0 scale

    
    @field_validator("start_date", "end_date", check_fields=False)
    @classmethod
    def validate_date_format(cls, value):
        """Validate date format - accepts YYYY or YYYY-MM-DD or empty string"""
        if value is None or value == "":
            return None
        
        # Check if it matches YYYY format (year only)
        if re.match(r"^\d{4}$", value):
            return value
        
        # Check if it matches YYYY-MM-DD format (full date)
        if re.match(r"^\d{4}-\d{2}-\d{2}$", value):
            return value
        
        raise ValueError("Date must be in YYYY or YYYY-MM-DD format")

class UserPreferenceRequest(BaseModel):
    name: str
    email: str
    github_user: str
    linkedin: Optional[str] = None
    education: str
    industry: str
    job_title: str
    personal_summary: Optional[str] = None
    education_details: Optional[List[EducationDetail]] = None

@router.get("/user-preferences")
def get_user_preferences():
    """Retrieve latest user preferences."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT name, email, github_user, linkedin, education, industry, job_title, education_details, profile_picture_path, personal_summary
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
        "linkedin": row[3],
        "education": row[4],
        "industry": row[5],
        "job_title": row[6],
        "education_details": row[7],
        "profile_picture_path": row[8],
        "personal_summary": row[9],
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
        INSERT INTO USER_PREFERENCES (user_id, name, email, github_user, linkedin, education, industry, job_title, personal_summary, education_details, updated_at)
        VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id) DO UPDATE SET
            name = excluded.name,
            email = excluded.email,
            github_user = excluded.github_user,
            linkedin = excluded.linkedin,
            education = excluded.education,
            industry = excluded.industry,
            job_title = excluded.job_title,
            personal_summary = excluded.personal_summary,
            education_details = excluded.education_details,
            updated_at = CURRENT_TIMESTAMP
        """,
        (request.name, request.email, request.github_user, request.linkedin, request.education, request.industry, request.job_title, request.personal_summary, education_details_json)
    )
    conn.commit()
    conn.close()
    
    return {"status": "ok", "message": "User preferences saved successfully"}

@router.get("/institutions/search")
def search_canadian_institutions(
    q: str = Query("", description="Search query for institution name"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of results"),
    simple: bool = Query(True, description="Return simple list with names and locations only")
):
    """
    Search Canadian post-secondary institutions.
    
    Query parameters:
    - q: Search term (e.g., "University of", "Toronto")
    - limit: Max results (1-200)
    - simple: If true, returns institution names with location; if false, includes programs
    
    Returns:
        List of matching institutions with details or simple name list
    """
    try:
        if simple:
            # Simple search with names and locations (for autocomplete)
            institutions = search_institutions_simple(query=q, limit=limit)
        else:
            # Full search with program details
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

@router.post("/user-preferences/profile-picture")
async def upload_profile_picture(file: UploadFile = File(...)):
    """Upload a profile picture, save to thumbnails/, store relative path in DB."""
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{file.content_type}'. Allowed: jpeg, png, webp, gif."
        )

    contents = await file.read()
    if len(contents) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 5 MB.")

    ext = ALLOWED_IMAGE_TYPES[file.content_type]
    filename = f"{PROFILE_PICTURE_FILENAME}{ext}"

    # Remove any previous profile picture files (any extension)
    for old in THUMBNAIL_DIR.glob(f"{PROFILE_PICTURE_FILENAME}.*"):
        try:
            old.unlink()
        except Exception:
            pass

    dest = THUMBNAIL_DIR / filename
    dest.write_bytes(contents)

    # Store consistent relative path (same pattern as project thumbnails)
    relative_path = f"data/thumbnails/{filename}"

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO USER_PREFERENCES (user_id, profile_picture_path)
        VALUES (1, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            profile_picture_path = excluded.profile_picture_path,
            updated_at = CURRENT_TIMESTAMP
        """,
        (relative_path,)
    )
    conn.commit()
    conn.close()

    return {"status": "ok", "message": "Profile picture saved successfully", "path": relative_path}


@router.get("/user-preferences/profile-picture")
def get_profile_picture():
    """Serve the profile picture file directly."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT profile_picture_path FROM USER_PREFERENCES WHERE user_id = 1")
    row = cursor.fetchone()
    conn.close()

    if not row or not row[0]:
        raise HTTPException(status_code=404, detail="No profile picture set")

    # Resolve absolute path from the stored relative path
    abs_path = DATA_DIR.parent / row[0]
    if not abs_path.exists():
        raise HTTPException(status_code=404, detail="Profile picture file not found")

    return FileResponse(str(abs_path))


@router.delete("/user-preferences/profile-picture")
def delete_profile_picture():
    """Remove the stored profile picture file and clear the DB entry."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT profile_picture_path FROM USER_PREFERENCES WHERE user_id = 1")
    row = cursor.fetchone()

    if row and row[0]:
        abs_path = DATA_DIR.parent / row[0]
        try:
            if abs_path.exists():
                abs_path.unlink()
        except Exception:
            pass

    cursor.execute(
        "UPDATE USER_PREFERENCES SET profile_picture_path = NULL, updated_at = CURRENT_TIMESTAMP WHERE user_id = 1"
    )
    conn.commit()
    conn.close()

    return {"status": "ok", "message": "Profile picture removed"}