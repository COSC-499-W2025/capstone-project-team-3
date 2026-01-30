from typing import Optional, List, Dict
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

# Payload model for editing project details
class ProjectEdit(BaseModel):
    project_signature: str
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

class BatchEditPayload(BaseModel):
    edits: List[ProjectEdit] 

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

@router.post("/portfolio/edit")
def edit_portfolio(payload: BatchEditPayload):
    """
    POST/portfolio/edit
    Edit one to many portfolio projects in a single query.
    """
    if not payload.edits:
        raise HTTPException(status_code=400, detail="No edits provided")
    
    ALLOWED_FIELDS = {"project_name", "project_summary", "created_at", "last_modified", "rank"}
    field_map = {"project_name": "name", "project_summary": "summary", "created_at": "created_at", "last_modified": "last_modified", "rank": "rank"}
    
    conn, cur = None, None

    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Collect all project signatures
        project_sigs = [edit.project_signature for edit in payload.edits]
        
        # Build a map of which projects update which fields
        field_updates = {}  # {field_name: {project_sig: value}}
        
        for edit in payload.edits:
            data = edit.model_dump(exclude_unset=True)
            project_sig = data.pop("project_signature")
            
            if not data:
                raise HTTPException(
                    status_code=400,
                    detail=f"No fields provided for project {project_sig}"
                )
            
            for key, value in data.items():
                if key not in ALLOWED_FIELDS:
                    raise HTTPException(status_code=400, detail=f"Invalid field: {key}")
                
                column = field_map[key]
                if column not in field_updates:
                    field_updates[column] = {}
                field_updates[column][project_sig] = value
        
        # Build SQL CASE statements for each column
        set_clauses = []
        params = []
        
        for column, updates in field_updates.items():
            case_parts = []
            for project_sig, value in updates.items():
                case_parts.append("WHEN project_signature = ? THEN ?")
                params.extend([project_sig, value])
            
            case_parts.append(f"ELSE {column}")  # Keep existing value
            case_statement = f"{column} = CASE {' '.join(case_parts)} END"
            set_clauses.append(case_statement)
        
        # Build final query
        placeholders = ','.join(['?'] * len(project_sigs))
        query = f"""
            UPDATE PROJECT 
            SET {', '.join(set_clauses)}
            WHERE project_signature IN ({placeholders})
        """
        
        params.extend(project_sigs)
        cur.execute(query, tuple(params))
        
        if cur.rowcount <=0:
            raise HTTPException(status_code=404, detail="No projects found")
        
        conn.commit()
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "ok",
                "projects_updated": project_sigs,
                "count": cur.rowcount
            }
        )
        
    except HTTPException:
        if conn:
            conn.rollback()
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        logger.exception(f"Failed to edit projects : : {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to edit projects")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()