"""
Utility functions for managing project thumbnails.
Handles image validation, storage, and database updates.
"""
import shutil
from pathlib import Path
from typing import Optional, Dict
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from app.data.db import get_connection

# Directory to store thumbnails
THUMBNAIL_DIR = Path(__file__).parent.parent / "data" / "thumbnails"
THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)

# Allowed image formats
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}


def validate_image_file(file_path: str) -> Dict[str, str]:
    """Validate that file exists and is a supported image format."""
    p = Path(file_path)
    
    if not p.exists():
        return {"status": "error", "reason": "File does not exist"}
    if not p.is_file():
        return {"status": "error", "reason": "Path is not a file"}
    if p.suffix.lower() not in ALLOWED_EXTENSIONS:
        return {"status": "error", "reason": f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"}
    
    return {"status": "ok", "path": str(p)}


def set_project_thumbnail(project_signature: str, source_image_path: str) -> Dict[str, str]:
    """Copy image to thumbnails directory and associate with project."""
    # Validate image
    validation = validate_image_file(source_image_path)
    if validation["status"] != "ok":
        return validation
    
    source = Path(source_image_path)
    dest = THUMBNAIL_DIR / f"{project_signature}{source.suffix}"
    
    # Delete any existing thumbnails with different extensions
    for existing_file in THUMBNAIL_DIR.glob(f"{project_signature}.*"):
        try:
            existing_file.unlink()
        except Exception:
            pass  # Continue even if deletion fails
    
    # Copy new thumbnail
    try:
        shutil.copy2(source, dest)
    except Exception as e:
        return {"status": "error", "reason": f"Failed to copy file: {str(e)}"}
    
    # Update database with relative path
    relative_path = f"data/thumbnails/{dest.name}"
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE PROJECT SET thumbnail_path = ? WHERE project_signature = ?",
            (relative_path, project_signature)
        )
        
        if cursor.rowcount == 0:
            conn.close()
            dest.unlink()  # Clean up if project not found
            return {"status": "error", "reason": "Project not found"}
        
        conn.commit()
        conn.close()
        return {"status": "ok", "thumbnail_path": relative_path}
    
    except Exception as e:
        # Clean up the copied file if DB update fails
        try:
            dest.unlink()
        except Exception:
            pass
        return {"status": "error", "reason": f"Failed to update database: {str(e)}"}


def get_project_thumbnail(project_signature: str) -> Optional[str]:
    """Retrieve thumbnail path for a project."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT thumbnail_path FROM PROJECT WHERE project_signature = ?", (project_signature,))
    row = cursor.fetchone()
    conn.close()
    
    if not row or not row[0]:
        return None
    
    # Convert relative path to absolute
    relative_path = row[0]
    if relative_path.startswith("data/thumbnails/"):
        absolute_path = THUMBNAIL_DIR / relative_path.split("/")[-1]
    else:
        # Handle legacy absolute paths
        absolute_path = Path(relative_path)
    
    # Verify file still exists
    if absolute_path.exists():
        return str(absolute_path)
    return None


def remove_project_thumbnail(project_signature: str) -> Dict[str, str]:
    """Remove thumbnail association and delete file."""
    thumbnail_path = get_project_thumbnail(project_signature)
    
    if not thumbnail_path:
        return {"status": "ok", "message": "No thumbnail to remove"}
    
    # Delete file (get_project_thumbnail returns absolute path)
    try:
        Path(thumbnail_path).unlink(missing_ok=True)
    except Exception as e:
        return {"status": "error", "reason": f"Failed to delete file: {str(e)}"}
    
    # Update database
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE PROJECT SET thumbnail_path = NULL WHERE project_signature = ?", (project_signature,))
    conn.commit()
    conn.close()
    
    return {"status": "ok", "message": "Thumbnail removed successfully"}


def get_all_thumbnails() -> Dict[str, Optional[str]]:
    """Get thumbnails for all projects."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT project_signature, thumbnail_path FROM PROJECT")
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}