"""
Cover letter API routes.

POST   /api/cover-letter/generate       – Generate + save a new cover letter
GET    /api/cover-letter                – List all saved cover letters
GET    /api/cover-letter/{id}           – Retrieve a specific cover letter
GET    /api/cover-letter/{id}/pdf       – Download as PDF
DELETE /api/cover-letter/{id}           – Delete a cover letter
"""
from __future__ import annotations

import os
import re as _re
import subprocess
import tempfile
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.utils.pdflatex_path import resolve_pdflatex_executable
from app.utils.cover_letter_utils import (
    CoverLetterNotFoundError,
    CoverLetterServiceError,
    MOTIVATION_LABELS,
    delete_cover_letter,
    generate_cover_letter,
    get_cover_letter,
    list_cover_letters,
    save_cover_letter,
    update_cover_letter_content,
)
from app.utils.generate_resume import load_user
from app.data.db import get_connection

router = APIRouter()

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


class CoverLetterUpdateRequest(BaseModel):
    content: str = Field(..., min_length=1, description="Updated cover letter text")


class CoverLetterSaveRequest(BaseModel):
    resume_id: int
    job_title: str = Field(..., min_length=1)
    company: str = Field(..., min_length=1)
    job_description: str = Field(..., min_length=10)
    motivations: List[str] = Field(default_factory=list)
    content: str = Field(..., min_length=1)
    generation_mode: str = Field("local", description="'ai' or 'local'")


class CoverLetterGenerateResponse(BaseModel):
    """Returned by /generate — letter content only, not yet persisted."""
    resume_id: int
    job_title: str
    company: str
    job_description: str
    motivations: List[str]
    content: str
    generation_mode: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_cover_letter_tex(content: str, job_title: str, company: str, name: str) -> str:
    """Wrap plain-text cover letter content in a minimal LaTeX document."""
    from app.utils.generate_resume_tex import escape_latex

    # Normalize newlines; models/JSON sometimes emit literal backslash-n instead of a line break.
    content = (
        content.replace("\r\n", "\n")
        .replace("\r", "\n")
        .replace("\\r\\n", "\n")
        .replace("\\r", "\n")
        .replace("\\n", "\n")
    )

    # ── Split into header block and letter body ────────────────────────────
    body_match = _re.search(r"Dear\s+(?:\S+\s+)?Hiring", content, _re.IGNORECASE)
    if body_match:
        header_block = content[: body_match.start()].strip()
        body_text    = content[body_match.start():].strip()
    else:
        header_block = ""
        body_text    = content.strip()
    # ── Parse contact lines from the header block ─────────────────────────
    # Expected lines: name, email, [linkedin], date, blank, application-line
    header_lines = [ln.rstrip() for ln in header_block.splitlines()]

    # Extract LinkedIn URL if present (starts with http or linkedin.com)
    linkedin_url  = ""
    linkedin_line_idx = None
    for i, ln in enumerate(header_lines):
        if ln.startswith("http") or "linkedin.com" in ln.lower():
            linkedin_url = ln.strip()
            linkedin_line_idx = i
            break

    # Remove the linkedin line so remaining lines are: name, email, date, blank, app-line
    if linkedin_line_idx is not None:
        header_lines.pop(linkedin_line_idx)

    # Remove blank lines and the "Job Title Application — Company" line
    # (we render that ourselves below)
    filtered = [
        ln for ln in header_lines
        if ln.strip() and "Application" not in ln and "—" not in ln and "---" not in ln
    ]
    # filtered[0] = name, filtered[1] = email, filtered[2] = date  (best-effort)
    tex_name  = escape_latex(filtered[0]) if len(filtered) > 0 else escape_latex(name)
    tex_email = escape_latex(filtered[1]) if len(filtered) > 1 else ""
    tex_date  = escape_latex(filtered[2]) if len(filtered) > 2 else ""

    # ── LinkedIn contact line ──────────────────────────────────────────────
    if linkedin_url
        safe_url = linkedin_url.replace("#", "\\#")
        linkedin_tex = (
            r" \textbar{} \href{" + safe_url + r"}{LinkedIn}"
        )
    else:
        linkedin_tex = ""

    # ── Escape and format the letter body ─────────────────────────────────
    # Split on paragraph boundaries, escape each paragraph, then re-join.
    # The sign-off ("Sincerely,\nName") is separated with extra vertical space.
    paragraphs = body_text.split("\n\n")
    escaped_paragraphs = []
    for para in paragraphs:
        lines = [escape_latex(line) for line in para.splitlines()]
        if len(lines) > 1 and lines[0].strip().lower().startswith("sincerely"):
            # Must be " \\\\\n" (two TeX backslashes + real newline). A fifth "\" turns \n into
            # the literal letters \\n, which TeX reads as undefined control sequence \n.
            escaped_paragraphs.append(" \\\\\n".join(lines))
        else:
            escaped_paragraphs.append(" ".join(lines))

    # Detect the sign-off paragraph (starts with "Sincerely")
    sincerely_idx = None
    for i, p in enumerate(escaped_paragraphs):
        if p.strip().lower().startswith("sincerely"):
            sincerely_idx = i
            break

    # Build the body LaTeX — join with a blank line (normal parskip spacing)
    # but insert \medskip after the greeting line and \bigskip before sign-off.
    body_parts: list[str] = []
    for i, p in enumerate(escaped_paragraphs):
        if i == sincerely_idx:
            body_parts.append(r"\bigskip" + "\n\n" + p)
        elif i == 0:
            # Greeting paragraph — add extra space after it before the body opens
            body_parts.append(p + "\n\n" + r"\medskip")
        else:
            body_parts.append(p)
    escaped_body = "\n\n".join(body_parts)

    return rf"""
\documentclass[a4paper,11pt]{{article}}
\usepackage[utf8]{{inputenc}}
\usepackage[T1]{{fontenc}}
\usepackage[left=2.5cm,right=2.5cm,top=2.5cm,bottom=2.5cm]{{geometry}}
\usepackage{{parskip}}
\usepackage{{hyperref}}
\hypersetup{{colorlinks=true,urlcolor=blue,linkcolor=black}}
\setlength{{\parskip}}{{8pt}}
\pagestyle{{empty}}
\begin{{document}}

\begin{{center}}
{{\Large \textbf{{{tex_name}}}}}\\[0.25em]
{tex_email}{linkedin_tex}
\end{{center}}

\vspace{{0.6em}}
\noindent {tex_date}

\vspace{{0.3em}}
\noindent\textbf{{Re: {escape_latex(job_title)} Application --- {escape_latex(company)}}}

\medskip

{escaped_body}

\end{{document}}
"""


def _compile_tex_to_pdf(tex_source: str) -> bytes:
    """Compile a LaTeX string to PDF bytes. Raises RuntimeError on failure."""
    pdflatex = resolve_pdflatex_executable()
    if not pdflatex:
        raise RuntimeError(
            "pdflatex is not installed on this system. "
            "Install BasicTeX (macOS) or MiKTeX (Windows), or set PDFLATEX_PATH."
        )
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = os.path.join(tmpdir, "cover_letter.tex")
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(tex_source)

        result = subprocess.run(
            [
                pdflatex,
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


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/cover-letter/generate", response_model=CoverLetterGenerateResponse)
async def generate_cover_letter_preview(request: CoverLetterRequest):
    """
    Generate a cover letter from the given inputs WITHOUT persisting it.

    The caller receives the letter content and the original request metadata
    so it can be displayed for review before the user explicitly saves it.
    Use POST /api/cover-letter/save to persist the letter.

    - **mode**: `'ai'` uses Gemini (falls back to local if no API key); `'local'` is offline.
    """
    mode = request.mode.lower()
    if mode not in VALID_MODES:
        raise HTTPException(status_code=422, detail=f"mode must be one of {sorted(VALID_MODES)}")

    cleaned_motivations = [m.strip() for m in request.motivations if m and m.strip()]

    try:
        content = await run_in_threadpool(
            generate_cover_letter,
            resume_id=request.resume_id,
            job_title=request.job_title,
            company=request.company,
            job_description=request.job_description,
            motivations=cleaned_motivations,
            mode=mode,
        )
    except CoverLetterServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return CoverLetterGenerateResponse(
        resume_id=request.resume_id,
        job_title=request.job_title,
        company=request.company,
        job_description=request.job_description,
        motivations=cleaned_motivations,
        content=content,
        generation_mode=mode,
    )


@router.post("/cover-letter/save", response_model=CoverLetterResponse)
async def save_cover_letter_route(request: CoverLetterSaveRequest):
    """
    Persist a cover letter (generated or manually edited) to the database.
    """
    mode = request.generation_mode.lower()
    if mode not in VALID_MODES:
        raise HTTPException(status_code=422, detail=f"generation_mode must be one of {sorted(VALID_MODES)}")

    cleaned_motivations = [m.strip() for m in request.motivations if m and m.strip()]

    try:
        cover_letter_id = await run_in_threadpool(
            save_cover_letter,
            resume_id=request.resume_id,
            job_title=request.job_title,
            company=request.company,
            job_description=request.job_description,
            motivations=cleaned_motivations,
            content=request.content,
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


@router.patch("/cover-letter/{cover_letter_id}", response_model=CoverLetterResponse)
async def update_one_cover_letter(cover_letter_id: int, request: CoverLetterUpdateRequest):
    """Update the editable content of a saved cover letter."""
    try:
        updated = await run_in_threadpool(
            update_cover_letter_content, cover_letter_id, request.content
        )
    except CoverLetterNotFoundError:
        raise HTTPException(status_code=404, detail=f"Cover letter {cover_letter_id} not found")
    except CoverLetterServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return CoverLetterResponse(**updated)


@router.get("/cover-letter/{cover_letter_id}/pdf")
async def download_cover_letter_pdf(cover_letter_id: int):
    """
    Compile the cover letter to PDF and return it as a download.
    PDF is compiled fresh on every request.
    """
    try:
        cl = await run_in_threadpool(get_cover_letter, cover_letter_id)
    except CoverLetterNotFoundError:
        raise HTTPException(status_code=404, detail=f"Cover letter {cover_letter_id} not found")
    except CoverLetterServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

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
        msg = str(exc)
        status = 503 if "not installed" in msg else 500
        raise HTTPException(status_code=status, detail=msg)

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
