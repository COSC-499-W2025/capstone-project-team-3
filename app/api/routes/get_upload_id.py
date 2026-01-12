from fastapi import APIRouter
import os

router = APIRouter()

@router.get("/resolve-upload/{upload_id}")
def resolve_upload(upload_id: str):
    """Return status and path if uploaded ZIP exists."""
    # Use relative path for uploads directory, or fall back to environment variable
    upload_dir = os.getenv("UPLOAD_DIR", "app/uploads")
    path = f"{upload_dir}/{upload_id}.zip"
    # Check if the file exists on disk
    if os.path.exists(path):
        return {"status": "ok", "path": path}
    # If not found, indicate that upload is still pending
    return {"status": "pending"}
