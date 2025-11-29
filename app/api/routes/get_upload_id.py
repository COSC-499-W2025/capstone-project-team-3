from fastapi import APIRouter
import os

router = APIRouter()

@router.get("/resolve-upload/{upload_id}")
def resolve_upload(upload_id: str):
    """Return status and path if uploaded ZIP exists."""
    # Construct absolute path to expected uploaded zip inside container
    path = f"/app/uploads/{upload_id}.zip"
    # Check if the file exists on disk
    if os.path.exists(path):
        return {"status": "ok", "path": path}
    # If not found, indicate that upload is still pending
    return {"status": "pending"}
