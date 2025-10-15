"""
Middleware for consent enforcement.
"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.consent_service import check_consent
import re


# Paths that don't require consent
EXEMPT_PATHS = [
    r"^/$",  # Root path
    r"^/docs",  # API documentation
    r"^/openapi.json",  # OpenAPI schema
    r"^/consent/.*",  # All consent endpoints
]


def is_exempt_path(path: str) -> bool:
    """Check if a path is exempt from consent requirements."""
    for pattern in EXEMPT_PATHS:
        if re.match(pattern, path):
            return True
    return False


class ConsentMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce consent requirements on protected endpoints.
    
    This middleware checks if a user has provided consent before allowing
    access to protected endpoints. Certain paths (like consent endpoints
    themselves) are exempt from this check.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Check if path is exempt from consent requirements
        if is_exempt_path(request.url.path):
            return await call_next(request)
        
        # For now, we'll use a default user_id from headers or query params
        # In a real application, this would come from authentication
        user_id = request.headers.get("X-User-ID")
        if not user_id:
            user_id = request.query_params.get("user_id")
        
        # If no user_id provided, return error
        if not user_id:
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "User ID required. Provide X-User-ID header or user_id query parameter.",
                    "requires_consent": True
                }
            )
        
        try:
            user_id = int(user_id)
        except ValueError:
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid user ID format"}
            )
        
        # Check consent status
        consent = check_consent(user_id)
        
        # If no consent record exists, require consent
        if consent is None:
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "Consent required. Please accept the privacy policy to continue.",
                    "requires_consent": True,
                    "user_id": user_id
                }
            )
        
        # If consent was declined, deny access
        if not consent.has_consent:
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "Access denied. Consent is required to use this feature.",
                    "requires_consent": True,
                    "user_id": user_id,
                    "consent_status": "declined"
                }
            )
        
        # Consent is valid, proceed with request
        response = await call_next(request)
        return response
