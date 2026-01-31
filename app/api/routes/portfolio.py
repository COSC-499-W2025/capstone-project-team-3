from typing import Optional, List
from fastapi import Query, APIRouter, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, Response
from app.utils.generate_portfolio import build_portfolio_model
import os

router = APIRouter()

@router.get("/portfolio")
def get_portfolio(project_ids: Optional[str] = Query(None, description="Comma-separated list of project IDs to include")):
    """
    GET /portfolio endpoint.
    Returns comprehensive portfolio dashboard data with all visualizations.
    
    Query parameters:
    - project_ids: Optional comma-separated list of project IDs (default: all projects)
    
    Returns rich portfolio data perfect for creating sophisticated graphs:
    - Overview statistics (projects, scores, skills, languages, lines of code)
    - Individual project details with metrics
    - Skills timeline for development progression
    - Language distribution for pie charts
    - Project complexity distribution for bar charts
    - Score distribution for quality analysis
    - Monthly activity timeline
    - Project type analysis (GitHub vs Local)
    - Top skills usage
    """
    try:
        # Parse project_ids if provided
        parsed_project_ids = None
        if project_ids:
            parsed_project_ids = [pid.strip() for pid in project_ids.split(",") if pid.strip()]
        
        portfolio_model = build_portfolio_model(project_ids=parsed_project_ids)
        
        return JSONResponse(
            content=portfolio_model,
            headers={
                "Content-Type": "application/json",
                "X-Portfolio-Projects": str(portfolio_model["metadata"]["total_projects"]),
                "X-Portfolio-Generated": portfolio_model["metadata"]["generated_at"],
                "X-Portfolio-Filtered": str(portfolio_model["metadata"]["filtered"])
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error generating portfolio: {str(e)}"
        )

@router.get("/portfolio-dashboard", response_class=HTMLResponse)
def portfolio_dashboard():
    """
    Serve the Portfolio Dashboard UI
    """
    # Get the path to the static HTML file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, "..", "..", "static", "portfolio.html")
    
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    else:
        return HTMLResponse(
            content="<h1>Portfolio Dashboard not found</h1>", 
            status_code=404
        )

@router.get("/static/portfolio.js")
def portfolio_js():
    """
    Serve the Portfolio Dashboard JavaScript file
    """
    # Get the path to the static JS file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    js_path = os.path.join(current_dir, "..", "..", "static", "portfolio.js")
    
    if os.path.exists(js_path):
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        return Response(content=js_content, media_type="application/javascript")
    else:
        raise HTTPException(status_code=404, detail="JavaScript file not found")