from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from app.data.db import get_connection
from pathlib import Path
import os

router = APIRouter()

# Define thumbnails directory
THUMBNAIL_DIR = Path(__file__).parent.parent.parent / "data" / "thumbnails"
THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)


def update_project_thumbnail(project_signature: str, thumbnail_path: str) -> None:
    """Update the thumbnail_path for a project in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE PROJECT SET thumbnail_path = ? WHERE project_signature = ?",
        (thumbnail_path, project_signature)
    )
    conn.commit()
    conn.close()

@router.post("/portfolio/project/thumbnail")
async def set_project_thumbnail(
    project_id: str = Form(...),
    image: UploadFile = File(...)
):
    """
    Associate a portfolio image as thumbnail for a given project.
    Supports: JPEG, PNG, GIF, SVG, and WebP formats.
    """
    # Validate image type - now including SVG and GIF
    allowed_types = [
        "image/jpeg", "image/jpg", "image/png", 
        "image/gif", "image/svg+xml", "image/webp"
    ]
    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed: JPEG, PNG, GIF, SVG, WebP. Got: {image.content_type}"
        )
    
    # Get file extension
    file_ext = os.path.splitext(image.filename)[1].lower()
    if not file_ext:
        file_ext = ".jpg"  # Default to jpg if no extension
    
    # Save image to thumbnails directory
    filename = f"{project_id}{file_ext}"
    image_path = THUMBNAIL_DIR / filename
    
    # Remove old thumbnail if exists
    for old_file in THUMBNAIL_DIR.glob(f"{project_id}.*"):
        try:
            old_file.unlink()
        except Exception:
            pass
    
    # Write new thumbnail
    with open(image_path, "wb") as f:
        f.write(await image.read())
    
    # Update project thumbnail in DB with relative path
    relative_path = f"data/thumbnails/{filename}"
    update_project_thumbnail(project_id, relative_path)
    
    return {
        "success": True, 
        "thumbnail_path": relative_path,
        "thumbnail_url": f"/api/portfolio/project/thumbnail/{project_id}"
    }


@router.get("/portfolio/project/thumbnail/{project_id}")
async def get_project_thumbnail(project_id: str):
    """
    Retrieve the thumbnail image for a given project.
    """
    # Check database for thumbnail path
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT thumbnail_path FROM PROJECT WHERE project_signature = ?",
        (project_id,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if not row or not row[0]:
        raise HTTPException(status_code=404, detail="Thumbnail not found for this project")
    
    # Extract filename from path
    thumbnail_path = row[0]
    if thumbnail_path.startswith("data/thumbnails/"):
        filename = thumbnail_path.replace("data/thumbnails/", "")
        file_path = THUMBNAIL_DIR / filename
    else:
        file_path = Path(thumbnail_path)
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Thumbnail file not found")
    
    # Return file with no-cache headers to prevent browser caching
    return FileResponse(
        file_path,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )
