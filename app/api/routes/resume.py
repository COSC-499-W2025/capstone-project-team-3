from typing import Optional, List
from fastapi import Query
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, Response
from app.utils.generate_resume import build_resume_model
from app.utils.generate_resume_tex import generate_resume_tex
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

def get_resume_tex(project_ids: Optional[List[str]]) -> str:
    """Helper method that builds resume model and generates resume in tex format"""
    resume_model = build_resume_model(project_ids=project_ids)
    return generate_resume_tex(resume_model)

def escape_tex_for_html(tex: str) -> str:
    """Helper methods to escape tex for HTML"""
    return tex.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

@router.get("/resume", response_class=HTMLResponse)
def resume_page(project_ids: Optional[List[str]] = Query(None)):
    """
    GET preview endpoint.
    - No project_ids → master resume
    - project_ids provided → filtered resume
    """

    tex = get_resume_tex(project_ids)
    preview = escape_tex_for_html(tex)

    # Build export links dynamically
    if project_ids:
        params = "&".join(f"project_ids={pid}" for pid in project_ids)
        tex_link = f"/resume/export/tex?{params}"
        pdf_link = f"/resume/export/pdf?{params}"
        title = "Resume Export (Selected Projects)"
    else:
        tex_link = "/resume/export/tex"
        pdf_link = "/resume/export/pdf"
        title = "Resume Export (All Projects)"

    return f"""
    <html>
        <body style="font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;">
            <h2>{title}</h2>
            <p>Download your LaTeX/PDF resume:</p>
            <p><a href="{tex_link}">Download resume.tex</a></p>
            <p><a href="{pdf_link}">Download resume.pdf</a></p>
            <h3>Preview (LaTeX)</h3>
            <pre style="white-space: pre-wrap; border:1px solid #ddd; padding:10px; max-height: 50vh; overflow:auto; background:#fafafa;">{preview}</pre>
        </body>
    </html>
    """
    
@router.post("/resume/preview", response_class=HTMLResponse)
def generate_resume(filter: ResumeFilter):
    """
    This is to generate a resume for selected projects 
    
    Example use-cases:
    - Allowing a user to tailor their resume for a certain job
    - Generating a resume for the top three ranked projects
    """
   
    tex = get_resume_tex(filter.project_ids)
    preview = escape_tex_for_html(tex)

    return f"""
    <html>
        <body>
            <h2>Generated Resume</h2>
            <p>Projects included: {", ".join(filter.project_ids)}</p>
            <pre style="white-space: pre-wrap;">{preview}</pre>
        </body>
    </html>
    """

@router.get("/resume/export/tex")
def resume_tex_export(project_ids: Optional[List[str]] = Query(None)):
    tex = get_resume_tex(project_ids)

    return Response(
        content=tex,
        media_type="application/x-tex",
        headers={"Content-Disposition": "attachment; filename=resume.tex"},
    )

@router.post("/resume/export/tex")
def resume_tex_filtered(filter: ResumeFilter):
    """This method downloads a resume for specified projects."""
    tex = get_resume_tex(filter.project_ids)
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

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(tex)

    try:
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

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    # Optional cleanup (recommended)
    shutil.rmtree(build_dir, ignore_errors=True)

    return pdf_bytes

def get_or_compile_pdf(tex: str) -> bytes:
    """Return a cached PDF for the given LaTeX source, compiling and caching it if necessary."""
    h = tex_hash(tex)
    pdf_path = os.path.join(PDF_CACHE_DIR, f"{h}.pdf")

    # Return cached PDF if it already exists
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            return f.read()

    # Compile the PDF since it is not cached
    pdf_bytes = compile_pdf(tex)

    # Cache the compiled PDF for future requests
    with open(pdf_path, "wb") as f:
        f.write(pdf_bytes)

    return pdf_bytes
        
@router.get("/resume/export/pdf")
# Make the endpoint async to allow awaiting background tasks
async def resume_pdf_export(project_ids: Optional[List[str]] = Query(None)):
    tex = get_resume_tex(project_ids)

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
    
@router.post("/resume/export/pdf")
async def resume_pdf_filtered(filter: ResumeFilter):
    """This method downloads a resume for specified projects."""
    tex = get_resume_tex(filter.project_ids)
    pdf_bytes = await run_in_threadpool(
        get_or_compile_pdf,
        tex,
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=resume.pdf"},
    )