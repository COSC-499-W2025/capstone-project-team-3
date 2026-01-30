from typing import Optional, List
from fastapi import Query, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.utils.generate_portfolio import build_portfolio_model
from pydantic import BaseModel, field_validator
from app.data.db import get_connection
from datetime import datetime
import logging
logger = logging.getLogger(__name__)


router = APIRouter()

class PortfolioFilter(BaseModel):
    project_ids: Optional[List[str]] = None

class EditPayload(BaseModel):
    project_name: Optional[str] = None # TBD Project Name length limit 
    project_summary: Optional[str] = None # TBD Project Summary length limit
    created_at: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    rank: Optional[float] = None

    # Validate rank is between 0.0 and 1.0 if provided
    @field_validator("rank")
    @classmethod
    def validate_rank(cls, value):
        if value is None:
            return value
        if not 0.0 <= value <= 1.0:
            raise ValueError("rank must be between 0.0 and 1.0")
        return value



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
    * This API call is more like a PATCH since only provided fields are updated.
    --> i.e; This endpoint is an update, not a creation.
    Body example:
    {
      "project_name": "Edited Project Name",
      "project_summary": "Edited summary",
      "created_at": "2024-01-01",
      "last_modified": "2024-02-02",
      "rank" : 0.95 # TODO replace rank with score percentage once DB is updated
    }
    """
    # Map payload fields to DB columns
    field_map = {
    "project_name": "name",
    "project_summary": "summary",
    "created_at": "created_at",
    "last_modified": "last_modified",
    "rank": "rank",
    }

    # Initialization
    fields, values = [], []
    conn, cur = None, None

    data = payload.model_dump(exclude_unset=True)

    # Validate at least one field is provided
    if not data:
        raise HTTPException(status_code=400, detail="At least one field must be provided for update")
                
    # Append fields and values to be updated
    for key, value in data.items():
        column = field_map[key]
        if not column:
            continue
        fields.append(f"{column} = ?")
        values.append(value)

    try:
            # Open DB connection
        conn = get_connection() 
        cur = conn.cursor()

        # Ensure project exists
        cur.execute("SELECT 1 FROM PROJECT WHERE project_signature = ?", (project_signature,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Project not found")
    
        # Apply Updates to project fields provided
        query = f"UPDATE PROJECT SET {', '.join(fields)} WHERE project_signature = ?"
        values.append(project_signature)
        cur.execute(query, tuple(values))

        # Commit changes
        conn.commit()
        return JSONResponse(status_code=200, content={"status": "ok", "project_updated": project_signature})
    except HTTPException: # Re-raise known HTTP exceptions
        if conn:
            conn.rollback()
        raise
    except Exception: # Handle unexpected errors
        if conn:
            conn.rollback()
        logger.exception(f"Failed to edit project: {project_signature}")
        raise HTTPException(status_code=500, detail="Failed to edit project")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# TODO Batch Edit endpoint functionality for edit of multiple projects at once 
