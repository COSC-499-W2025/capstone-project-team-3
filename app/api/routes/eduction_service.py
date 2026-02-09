from fastapi import APIRouter, Query, HTTPException
from app.utils.canadian_institutions_api import (
    search_institutions, 
    get_all_institutions,
    search_institutions_simple
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/institutions/search")
def search_canadian_institutions(
    q: str = Query("", description="Search query for institution name"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of results"),
    simple: bool = Query(False, description="Return simple list of names only")
):
    """
    Search Canadian post-secondary institutions.
    
    Query parameters:
    - q: Search term (e.g., "University", "Toronto", "College")
    - limit: Max results (1-200)
    - simple: If true, returns only institution names; if false, includes programs
    
    Returns:
        List of matching institutions with details or simple name list
    
    Examples:
        GET /api/institutions/search?q=Toronto&limit=10
        GET /api/institutions/search?q=University&limit=20&simple=true
    """
    try:
        if simple:
            # Simple name-only search
            institutions = search_institutions_simple(query=q, limit=limit)
            return {
                "status": "ok",
                "count": len(institutions),
                "institutions": institutions
            }
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
        raise HTTPException(status_code=500, detail=f"Failed to search institutions: {str(e)}")


@router.get("/institutions/list")
def get_institutions_list():
    """
    Get a complete list of all Canadian post-secondary institution names.
    Useful for autocomplete dropdowns.
    
    Note: This fetches ALL institutions (may take a few seconds on first call).
    
    Returns:
        List of unique institution names (sorted alphabetically)
    
    Example:
        GET /api/institutions/list
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
        raise HTTPException(status_code=500, detail=f"Failed to fetch institutions: {str(e)}")