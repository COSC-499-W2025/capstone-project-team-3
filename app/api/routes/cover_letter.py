"""
Cover letter API routes.

POST   /api/cover-letter/generate       – Generate + save a new cover letter
GET    /api/cover-letter                – List all saved cover letters
GET    /api/cover-letter/{id}           – Retrieve a specific cover letter
GET    /api/cover-letter/{id}/pdf       – Download as PDF
DELETE /api/cover-letter/{id}           – Delete a cover letter
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import tempfile
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.utils.cover_letter_utils import (
    CoverLetterNotFoundError,
    CoverLetterServiceError,
    MOTIVATION_LABELS,
    delete_cover_letter,
    generate_cover_letter,
    get_cover_letter,
    list_cover_letters,
    save_cover_letter,
)
from app.utils.generate_resume import load_user
from app.data.db import get_connection

router = APIRouter()

PDF_CACHE_DIR = os.getenv("PDF_CACHE_DIR", "app/data/resume_pdf_cache")
os.makedirs(PDF_CACHE_DIR, exist_ok=True)

LATEX_BUILD_DIR = os.getenv("LATEX_BUILD_DIR", "app/data/latex_build")
os.makedirs(LATEX_BUILD_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

VALID_MODES = {"ai", "local"}
VALID_MOTIVATIONS = set(MOTIVATION_LABELS.keys())


class CoverLetterRequest(BaseModel):
    resume_id: int = Field(..., description="ID of the saved resume to base the letter on")
    job_title: str = Field(..., min_length=1)
    company: str = Field(..., min_length=1)
    job_description: str = Field(..., min_length=10)
    motivations: List[str] = Field(default_factory=list)
    mode: str = Field("local", description="'ai' or 'local'")


class CoverLetterResponse(BaseModel):
    id: int
    resume_id: int
    job_title: str
    company: str
    job_description: str
    motivations: List[str]
    content: str
    generation_mode: str
    created_at: str


class CoverLetterSummary(BaseModel):
    id: int
    resume_id: int
    job_title: str
    company: str
    generation_mode: str
    created_at: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_cover_letter_tex(content: str, job_title: str, company: str, name: str) -> str:
    """Wrap plain-text cover letter content in a minimal LaTeX document."""
    from app.utils.generate_resume_tex import escape_latex

    escaped_content = escape_latex(content)
    # Preserve paragraph breaks
    escaped_content = escaped_content.replace("\n\n", "\n\n\\medskip\n\n")
    escaped_content = escaped_content.replace("\n", " \\\\\n")

    return rf"""
\documentclass[a4paper,11pt]{{article}}
\usepackage[utf8]{{inputenc}}
\usepackage[T1]{{fontenc}}
\usepackage[left=2.5cm,right=2.5cm,top=2.5cm,bottom=2.5cm]{{geometry}}
\usepackage{{parskip}}
\pagestyle{{empty}}
\begin{{document}}

\begin{{center}}
{{\Large \textbf{{{escape_latex(name)}}}}}
\end{{center}}

\vspace{{1em}}

\textbf{{{escape_latex(job_title)}}} --- {escape_latex(company)}

\vspace{{1em}}

{escaped_content}

\end{{document}}
"""


def _compile_tex_to_pdf(tex_source: str) -> bytes:
    """Compile a LaTeX string to PDF bytes. Raises RuntimeError on failure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = os.path.join(tmpdir, "cover_letter.tex")
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(tex_source)

        result = subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-output-directory", tmpdir,
                tex_path,
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            raise RuntimeError(f"pdflatex failed:\n{result.stdout}\n{result.stderr}")

        pdf_path = os.path.join(tmpdir, "cover_letter.pdf")
        with open(pdf_path, "rb") as f:
            return f.read()


def _cached_pdf_path(content_hash: str) -> str:
    return os.path.join(PDF_CACHE_DIR, f"cover_letter_{content_hash}.pdf")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/cover-letter/generate", response_model=CoverLetterResponse)
async def generate_and_save_cover_letter(request: CoverLetterRequest):
    """
    Generate a cover letter from the given inputs and persist it to the database.

    - **resume_id**: must reference an existing saved resume (not master resume id 1 only
      when used as a base — master resume IS allowed here for context).
    - **mode**: `'ai'` uses Gemini (falls back to local if no API key); `'local'` is offline.
    - **motivations**: array of motivation keys from
      `['strong_company_culture', 'personal_growth', 'meaningful_work', 'reputation_stability']`.
    """
    mode = request.mode.lower()
    if mode not in VALID_MODES:
        raise HTTPException(status_code=422, detail=f"mode must be one of {sorted(VALID_MODES)}")

    # Filter out any unrecognised motivation keys
    valid_motivations = [m for m in request.motivations if m in VALID_MOTIVATIONS]

    try:
        content = await run_in_threadpool(
            generate_cover_letter,
            resume_id=request.resume_id,
            job_title=request.job_title,
            company=request.company,
            job_description=request.job_description,
            motivations=valid_motivations,
            mode=mode,
        )
    except CoverLetterServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    try:
        cover_letter_id = await run_in_threadpool(
            save_cover_letter,
            resume_id=request.resume_id,
            job_title=request.job_title,
            company=request.company,
            job_description=request.job_description,
            motivations=valid_motivations,
            content=content,
            generation_mode=mode,
        )
    except CoverLetterServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    try:
        saved = await run_in_threadpool(get_cover_letter, cover_letter_id)
    except CoverLetterNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return CoverLetterResponse(**saved)


@router.get("/cover-letter", response_model=List[CoverLetterSummary])
async def get_all_cover_letters():
    """List all saved cover letters (summary only — no full content)."""
    letters = await run_in_threadpool(list_cover_letters)
    return [
        CoverLetterSummary(
            id=cl["id"],
            resume_id=cl["resume_id"],
            job_title=cl["job_title"],
            company=cl["company"],
            generation_mode=cl["generation_mode"],
            created_at=cl["created_at"],
        )
        for cl in letters
    ]


@router.get("/cover-letter/{cover_letter_id}", response_model=CoverLetterResponse)
async def get_one_cover_letter(cover_letter_id: int):
    """Retrieve a full cover letter by id."""
    try:
        cl = await run_in_threadpool(get_cover_letter, cover_letter_id)
    except CoverLetterNotFoundError:
        raise HTTPException(status_code=404, detail=f"Cover letter {cover_letter_id} not found")
    except CoverLetterServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return CoverLetterResponse(**cl)


@router.get("/cover-letter/{cover_letter_id}/pdf")
async def download_cover_letter_pdf(cover_letter_id: int):
    """
    Compile the cover letter to PDF and return it as a download.
    Results are cached by content hash.
    """
    try:
        cl = await run_in_threadpool(get_cover_letter, cover_letter_id)
    except CoverLetterNotFoundError:
        raise HTTPException(status_code=404, detail=f"Cover letter {cover_letter_id} not found")
    except CoverLetterServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    content_hash = hashlib.sha256(cl["content"].encode("utf-8")).hexdigest()[:16]
    cached_path = _cached_pdf_path(content_hash)

    if os.path.exists(cached_path):
        with open(cached_path, "rb") as f:
            pdf_bytes = f.read()
    else:
        # Load user name for the LaTeX header
        try:
            conn = get_connection()
            try:
                user = load_user(conn.cursor())
            finally:
                conn.close()
            name = user.get("name") or "Applicant"
        except Exception:
            name = "Applicant"

        tex = _build_cover_letter_tex(
            content=cl["content"],
            job_title=cl["job_title"],
            company=cl["company"],
            name=name,
        )
        try:
            pdf_bytes = await run_in_threadpool(_compile_tex_to_pdf, tex)
        except RuntimeError as exc:
            raise HTTPException(
                status_code=500,
                detail=f"PDF compilation failed. Ensure pdflatex is installed. Details: {exc}",
            )

        with open(cached_path, "wb") as f:
            f.write(pdf_bytes)

    filename = f"cover_letter_{cl['company'].replace(' ', '_')}_{cl['job_title'].replace(' ', '_')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.delete("/cover-letter/{cover_letter_id}")
async def remove_cover_letter(cover_letter_id: int):
    """Delete a saved cover letter by id."""
    try:
        deleted = await run_in_threadpool(delete_cover_letter, cover_letter_id)
    except CoverLetterServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    if not deleted:
        raise HTTPException(status_code=404, detail=f"Cover letter {cover_letter_id} not found")

    return {"success": True, "deleted_id": cover_letter_id}
