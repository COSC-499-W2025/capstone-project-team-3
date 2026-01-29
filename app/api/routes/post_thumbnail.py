from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.data.db import get_connection

router = APIRouter()


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
    """
    # Validate image type
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")
    
    # Save image to disk or cloud (example: local storage)
    image_path = f"static/thumbnails/{project_id}_{image.filename}"
    with open(image_path, "wb") as f:
        f.write(await image.read())
    
    # Update project thumbnail in DB (base utils assumed to exist)
    update_project_thumbnail(project_id, image_path)
    
    return {"success": True, "thumbnail_path": image_path}
