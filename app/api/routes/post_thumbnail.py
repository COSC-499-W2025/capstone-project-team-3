from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.manager.llm_consent_manager import update_project_thumbnail

router = APIRouter()

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
