from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.data.db import get_connection

router = APIRouter()

class UserPreferenceRequest(BaseModel):
    name: str
    email: str
    github_user: str
    education: str
    industry: str
    job_title: str

@router.get("/user-preferences")
def get_user_preferences():
    """Retrieve latest user preferences."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT name, email, github_user, education, industry, job_title
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
        "job_title": row[5]
    }

@router.post("/user-preferences")
def save_user_preferences(request: UserPreferenceRequest):
    """Save or update user preferences."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        INSERT OR REPLACE INTO USER_PREFERENCES (name, email, github_user, education, industry, job_title)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (request.name, request.email, request.github_user, request.education, request.industry, request.job_title)
    )
    conn.commit()
    conn.close()
    
    return {"status": "ok", "message": "User preferences saved successfully"}
