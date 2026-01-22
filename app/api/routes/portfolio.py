from typing import Optional, List
from fastapi import Query, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.utils.generate_portfolio import build_portfolio_model
from pydantic import BaseModel

router = APIRouter()

class PortfolioFilter(BaseModel):
    project_ids: Optional[List[str]] = None

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
        print(f"[DEBUG] Portfolio API called with project_ids: {filter.project_ids}")
        portfolio_model = build_portfolio_model(project_ids=filter.project_ids)
        print(f"[DEBUG] Portfolio generated with {len(portfolio_model.get('projects', []))} projects")
        print(f"[DEBUG] Overview: {portfolio_model.get('overview', {})}")
        
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