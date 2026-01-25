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
    """Save or update user preferences using UPSERT."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # UPSERT: Insert if no row exists (user_id=1), otherwise UPDATE existing row
    cursor.execute(
        """
        INSERT INTO USER_PREFERENCES (user_id, name, email, github_user, education, industry, job_title, updated_at)
        VALUES (1, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id) DO UPDATE SET
            name = excluded.name,
            email = excluded.email,
            github_user = excluded.github_user,
            education = excluded.education,
            industry = excluded.industry,
            job_title = excluded.job_title,
            updated_at = CURRENT_TIMESTAMP
        """,
        (request.name, request.email, request.github_user, request.education, request.industry, request.job_title)
    )
    conn.commit()
    conn.close()
    
    return {"status": "ok", "message": "User preferences saved successfully"}
