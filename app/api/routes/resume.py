from typing import Optional, List, Dict, Any
from fastapi import Query
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, Response
from app.utils.generate_resume import build_resume_model, load_saved_resume, resume_exists,save_resume_edits, create_resume, attach_projects_to_resume, list_resumes, ResumeNotFoundError, ResumeServiceError, ResumePersistenceError
from app.utils.generate_resume_tex import generate_resume_tex
from app.data.db import get_connection
from pydantic import BaseModel
import subprocess
import os
import hashlib
from fastapi.concurrency import run_in_threadpool
import uuid
import shutil


router = APIRouter()
PDF_CACHE_DIR = "/tmp/resume_pdf_cache"
os.makedirs(PDF_CACHE_DIR, exist_ok=True)

LATEX_BUILD_DIR = "/tmp/latex_build"
os.makedirs(LATEX_BUILD_DIR, exist_ok=True)
class ResumeFilter(BaseModel):
    project_ids: list[str]

def tex_hash(tex: str) -> str:
    """Creates a unique hash of the LaTex source for futurer caching """
    return hashlib.sha256(tex.encode("utf-8")).hexdigest()

def get_resume_tex(project_ids: Optional[List[str]] = None, resume_id: Optional[int] = None) -> str:
    """Helper method that builds resume model and generates resume in tex format.
    
    Args:
        project_ids: For preview mode - builds from base PROJECT table
        resume_id: For saved resumes - loads from RESUME_PROJECT table with edits
    """
    if resume_id is not None:
        # Load saved/edited resume from RESUME_PROJECT table
        resume_model = load_saved_resume(resume_id)
    else:
        # Build from base PROJECT table (preview or master resume)
        resume_model = build_resume_model(project_ids=project_ids)
    return generate_resume_tex(resume_model)

def escape_tex_for_html(tex: str) -> str:
    """Helper methods to escape tex for HTML"""
    return tex.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

@router.post("/resume")
def create_tailored_resume(filter: ResumeFilter):
    """
    Create a new resume and associate selected projects.
    """
    if not filter.project_ids:
        raise HTTPException(400, "No projects selected")
    try:
        resume_id = create_resume()
        attach_projects_to_resume(resume_id, filter.project_ids)
        return {
            "resume_id": resume_id,
            "message": "Resume created successfully"
        }
    except ResumePersistenceError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ResumeServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/resume")
def resume_page(project_ids: Optional[List[str]] = Query(None)):
    """
    GET preview endpoint.
    - No project_ids → master resume
    - project_ids provided → filtered resume
    """

    try:
        resume_model = build_resume_model(project_ids=project_ids)
        return resume_model
    except ResumeServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/resume/{resume_id}")
def get_saved_resume(resume_id: int):
    """Load saved resume"""
    try:
        return load_saved_resume(resume_id)
    except ResumeNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ResumeServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/resume_names")
def list_resumes_endpoint():
    """Return all resumes for the sidebar: id, name, is_master."""
    try:
        return {"resumes": list_resumes()}
    except ResumeServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resume/{id}/edit")
def save_edited_resume(id: int, payload: Dict[str, Any]):
    """Endpoint to save edited resume"""
    try:
        # --- Validate resume exists ---
        exists= resume_exists(id)
        if not exists:
            raise HTTPException(status_code=404, detail="Resume not found")

        # Save project overrides
        save_resume_edits(id,payload)
        return {"status": "ok", "message": "Resume edits saved"}
    except ResumeNotFoundError:
        raise HTTPException(status_code=404, detail="Resume not found")
    except ResumePersistenceError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ResumeServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/resume/export/tex")
def resume_tex_export(
    project_ids: Optional[List[str]] = Query(None),
    resume_id: Optional[int] = Query(None)
):
    """Export resume as TeX.
    
    Use resume_id for saved/edited resumes (loads from RESUME_PROJECT).
    Use project_ids for preview mode (builds from base PROJECT table).
    Use neither for master resume.
    """
    # Validate that only one parameter is provided
    if project_ids and resume_id is not None:
        raise HTTPException(
            status_code=400,
            detail="Cannot specify both project_ids and resume_id. Use resume_id for saved resumes or project_ids for preview."
        )
        
    try:
        tex = get_resume_tex(project_ids=project_ids, resume_id=resume_id)
    except ResumeServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return Response(
        content=tex,
        media_type="application/x-tex",
        headers={"Content-Disposition": "attachment; filename=resume.tex"},
    )

def compile_pdf(tex: str) -> bytes:
    """
    Compile LaTeX source to PDF using pdflatex (single pass).

    Raises HTTPException with LaTeX logs on failure.
    """
    
    build_id = uuid.uuid4().hex
    build_dir = os.path.join(LATEX_BUILD_DIR, build_id)
    os.makedirs(build_dir, exist_ok=True)

    basename = "resume"
    tex_path = os.path.join(build_dir, f"{basename}.tex")
    pdf_path = os.path.join(build_dir, f"{basename}.pdf")

    try:
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(tex)

        proc = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", f"{basename}.tex"],
            cwd=build_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
        )

        if proc.returncode != 0 and not os.path.exists(pdf_path):
            raise subprocess.CalledProcessError(
                proc.returncode,
                proc.args,
                output=proc.stdout,
                stderr=proc.stderr,
            )

        with open(pdf_path, "rb") as f:
            return f.read()

    except subprocess.TimeoutExpired:
        raise HTTPException(504, "LaTeX compilation timed out.")

    except FileNotFoundError:
        raise HTTPException(
            500,
            "pdflatex not found. Is LaTeX installed in the container?",
        )

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            422,
            {
                "error": "LaTeX compilation failed",
                "stdout": (e.output or b"").decode(errors="ignore")[-1500:],
                "stderr": (e.stderr or b"").decode(errors="ignore")[-1500:],
            },
        )
    finally:
        shutil.rmtree(build_dir, ignore_errors=True)

def get_or_compile_pdf(tex: str) -> bytes:
    """Return a cached PDF for the given LaTeX source, compiling and caching it if necessary."""
    h = tex_hash(tex)

    # Validate hash: must be 64 lowercase hex chars (sha256 hexdigest)
    if not isinstance(h, str) or len(h) != 64 or not all(c in "0123456789abcdef" for c in h):
        raise HTTPException(400, "Invalid cache key")

    # Build safe cache path and ensure it stays within the cache dir
    pdf_path = os.path.join(PDF_CACHE_DIR, f"{h}.pdf")
    base = os.path.abspath(PDF_CACHE_DIR)
    target = os.path.abspath(pdf_path)
    if os.path.commonpath([base, target]) != base:
        raise HTTPException(400, "Invalid cache path")

    # Return cached PDF if it already exists and is not a symlink
    if os.path.exists(pdf_path) and not os.path.islink(pdf_path):
        with open(pdf_path, "rb") as f:
            return f.read()

    # Compile the PDF since it is not cached
    pdf_bytes = compile_pdf(tex)

    # Atomic write to avoid partial files; avoid writing through symlinks
    tmp_path = pdf_path + ".tmp"
    with open(tmp_path, "wb") as f:
        f.write(pdf_bytes)

    # If a symlink exists at the final path, remove it before replace
    if os.path.islink(pdf_path):
        try:
            os.unlink(pdf_path)
        except OSError:
            pass

    os.replace(tmp_path, pdf_path)
    return pdf_bytes
        
@router.get("/resume/export/pdf")
# Make the endpoint async to allow awaiting background tasks
async def resume_pdf_export(
    project_ids: Optional[List[str]] = Query(None),
    resume_id: Optional[int] = Query(None)
):
    """Export resume as PDF.
    
    Use resume_id for saved/edited resumes (loads from RESUME_PROJECT).
    Use project_ids for preview mode (builds from base PROJECT table).
    Use neither for master resume.
    """
    if project_ids and resume_id is not None:
        raise HTTPException(
            status_code=400, 
            detail="Cannot specify both project_ids and resume_id. Use resume_id for saved resumes or project_ids for preview."
        )
        
    try:
        tex = get_resume_tex(project_ids=project_ids, resume_id=resume_id)
    except ResumeServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Run PDF generation in a separate thread so it doesn't block the FastAPI worker
    pdf_bytes = await run_in_threadpool(
        get_or_compile_pdf,
        tex,
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=resume.pdf"},
    )

@router.delete("/resume/{resume_id}")
def delete_saved_resume(resume_id: int):
    """
    Delete a saved/edited resume by resume_id.
    
    This deletes the resume entry from RESUME table, which will cascade delete:
    - All projects from RESUME_PROJECT table
    - All skills from RESUME_SKILLS table
    
    Does NOT delete the master resume or base project data.
    """
    if resume_id == 1:
        raise HTTPException(status_code=400, detail="Cannot delete Master Resume")
    # Check if resume exists using the utility method
    if not resume_exists(resume_id):
        raise HTTPException(404, f"Resume with ID {resume_id} not found")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Delete the resume (CASCADE will handle RESUME_PROJECT and RESUME_SKILLS)
        cursor.execute("DELETE FROM RESUME WHERE id = ?", (resume_id,))
        conn.commit()
        
        return {
            "success": True,
            "message": f"Resume {resume_id} deleted successfully",
            "deleted_resume_id": resume_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(500, f"Failed to delete resume: {str(e)}")
    finally:
        conn.close()
