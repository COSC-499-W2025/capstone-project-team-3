from typing import Optional, List
from fastapi import Query, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.utils.generate_portfolio import build_portfolio_model
from pydantic import BaseModel
from pydantic import BaseModel
from app.data.db import get_connection
import datetime

router = APIRouter()

class PortfolioFilter(BaseModel):
    project_ids: Optional[List[str]] = None

class EditPayload(BaseModel):
    project_signature: str
    project_summary: Optional[str] = None
    created_at: Optional[str] = None
    last_modified: Optional[str] = None
    skills: Optional[List[Union[str, dict]]] = None
    rank: Optional[List[str]] = None

@router.post("/portfolio/generate")
def generate_portfolio(filter: PortfolioFilter):
    """
    POST /portfolio/generate endpoint.
    Generate portfolio data for selected projects.
    
    Example request body:
    {
        "project_ids": ["project_sig_1", "project_sig_2", "project_sig_3"]
    }
    
    Returns comprehensive portfolio data including overview, projects, skills timeline, etc.
    """
    try:
        portfolio_model = build_portfolio_model(project_ids=filter.project_ids)
        
        return JSONResponse(
            content=portfolio_model,
            headers={
                "Content-Type": "application/json",
                "X-Portfolio-Projects": str(len(filter.project_ids) if filter.project_ids else 0),
                "X-Portfolio-Generated": portfolio_model["metadata"]["generated_at"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error generating portfolio for projects {filter.project_ids}: {str(e)}"
        )

@router.post("/portfolio/{project_signature}/edit")
def edit_portfolio(project_signature: str, payload: EditPayload):
    """
    POST /portfolio/{id}/edit
    Edit portfolio project details such as the summary, skills, and duration of a project.

    Body example:
    {
      "project_signature": "sig_alpha_project/hash",
      "project_summary": "Overwritten summary...",
      "created_at": "2024-01-01 00:00:00",
      "last_modified": "2024-02-02 00:00:00",
      "skills": ["Python", {"skill":"Flask","source":"code"}],
    }
    """
    conn = get_connection()
    cur = conn.cursor()

    # Ensure project exists
    cur.execute("SELECT 1 FROM PROJECTS WHERE project_signature = ?", (project_signature,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Project not found")
    
    try: # Apply Updates
        if payload.project_summary is not None: # Update summary
            cur.execute(
                "UPDATE PROJECT SET summary = ? WHERE project_signature = ?",
                (payload.project_summary, payload.project_signature)
            )

        if payload.created_at is not None: # Update created_at
            cur.execute(
                "UPDATE PROJECT SET created_at = ? WHERE project_signature = ?",
                (payload.created_at, payload.project_signature)
            )

        if payload.last_modified is not None: # Update last_modified
            cur.execute(
                "UPDATE PROJECT SET last_modified = ? WHERE project_signature = ?",
                (payload.last_modified, payload.project_signature)
            )
        
        if payload.rank is not None: # Update rank
            cur.execute(
                "UPDATE PROJECT SET rank = ? WHERE project_signature = ?",
                (payload.rank, project_signature)
            )
        
        # Replace skills (delete old, insert new)
        if payload.skills is not None:
            cur.execute("DELETE FROM SKILL_ANALYSIS WHERE project_id = ?", (project_signature,))
            for s in payload.skills:
                if isinstance(s, dict):
                    skill_name = s.get("skill")
                    source = "USER"

                if skill_name:
                    cur.execute(
                        "INSERT INTO SKILL_ANALYSIS (project_id, skill, source) VALUES (?, ?, ?)",
                        (project_signature, skill_name, source)
                    )
        
        conn.commit()
        return JSONResponse(status_code=200, content={"status": "ok", "project_signature": project_signature})
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to edit project {project_signature}: {str(e)}")
    finally:
        conn.close()