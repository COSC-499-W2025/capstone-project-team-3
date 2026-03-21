"""
Cover letter generation utilities.

Supports two modes:
  - 'local'  : template-based, no LLM required
  - 'ai'     : Gemini-backed generation
"""
from __future__ import annotations

import json
import logging
import os
import sqlite3
from typing import Any, Dict, List, Optional

from app.data.db import get_connection
from app.utils.generate_resume import load_user, load_saved_resume, build_resume_model
from app.client.llm_client import GeminiLLMClient

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Motivation label map
# ---------------------------------------------------------------------------
MOTIVATION_LABELS: Dict[str, str] = {
    "strong_company_culture": "strong company culture",
    "personal_growth": "personal growth and career advancement",
    "meaningful_work": "meaningful and impactful work",
    "reputation_stability": "the company's reputation and stability",
}


# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------
class CoverLetterServiceError(Exception):
    pass


class CoverLetterNotFoundError(CoverLetterServiceError):
    pass


# ---------------------------------------------------------------------------
# Profile helpers
# ---------------------------------------------------------------------------

def _load_user_profile() -> Dict[str, Any]:
    """Return user profile dict from USER_PREFERENCES."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        return load_user(cursor)
    finally:
        conn.close()


def _load_resume_context(resume_id: int) -> Dict[str, Any]:
    """Return the resume model dict for the given resume_id."""
    try:
        return load_saved_resume(resume_id)
    except Exception as exc:
        raise CoverLetterServiceError(f"Could not load resume {resume_id}: {exc}") from exc


def _format_project_bullets(projects: List[Dict[str, Any]]) -> str:
    """Return a plain-text summary of projects for use in prompts / templates."""
    lines: List[str] = []
    for p in projects:
        title = p.get("title", p.get("project_name", "Unnamed Project"))
        dates = p.get("dates", "")
        raw_bullets = p.get("bullets", [])

        # Normalise bullets to list[str]
        if isinstance(raw_bullets, str):
            try:
                raw_bullets = json.loads(raw_bullets)
            except Exception:
                raw_bullets = [raw_bullets]
        if not isinstance(raw_bullets, list):
            raw_bullets = [str(raw_bullets)]

        bullet_text = "; ".join(str(b).strip() for b in raw_bullets if b)
        lines.append(f"- {title} ({dates}): {bullet_text}")
    return "\n".join(lines)


def _format_skills(skills: Dict[str, List[str]]) -> str:
    """Return a comma-separated skills string."""
    all_skills: List[str] = []
    for items in skills.values():
        all_skills.extend(items)
    return ", ".join(all_skills)


def _motivation_text(motivations: List[str]) -> str:
    """Convert motivation keys to a readable sentence fragment."""
    labels = [MOTIVATION_LABELS.get(m, m) for m in motivations if m]
    if not labels:
        return ""
    if len(labels) == 1:
        return labels[0]
    return ", ".join(labels[:-1]) + f", and {labels[-1]}"


# ---------------------------------------------------------------------------
# Local (template-based) generation
# ---------------------------------------------------------------------------

_LOCAL_TEMPLATE = """\
{name}
{email}

{job_title} Application — {company}

Dear Hiring Manager,

I am writing to express my strong interest in the {role} position at {company}. \
With a background in {industry} and hands-on experience across a range of technical \
projects, I am confident in my ability to contribute meaningfully to your team.

{motivation_paragraph}

Throughout my career I have worked on projects that demonstrate both technical depth \
and collaborative problem-solving:

{project_summary}

My core technical skills include {skills}.

{personal_paragraph}

I am excited about the opportunity to bring my experience to {company} and would \
welcome the chance to discuss how I can contribute to your goals. Thank you for your \
time and consideration.

Sincerely,
{name}
"""

_MOTIVATION_PARAGRAPH_TEMPLATE = (
    "I am particularly drawn to {company} because of {motivation_text}. "
    "This aligns closely with my own values and professional aspirations."
)

_PERSONAL_PARAGRAPH_TEMPLATE = (
    "{personal_summary}"
)


def generate_local(
    *,
    resume_id: int,
    job_title: str,
    company: str,
    job_description: str,
    motivations: List[str],
) -> str:
    """
    Generate a cover letter from a fixed template without an LLM.
    Returns the cover letter as a plain-text string.
    """
    profile = _load_user_profile()
    resume = _load_resume_context(resume_id)

    name = profile.get("name") or "Applicant"
    email = profile.get("email") or ""
    industry = profile.get("industry") or "technology"
    personal_summary = profile.get("personal_summary") or (
        f"I bring a passion for {industry} and a commitment to delivering high-quality work."
    )

    projects_text = _format_project_bullets(resume.get("projects", []))
    skills_text = _format_skills(resume.get("skills", {}))

    motivation_text = _motivation_text(motivations)
    motivation_paragraph = (
        _MOTIVATION_PARAGRAPH_TEMPLATE.format(
            company=company, motivation_text=motivation_text
        )
        if motivation_text
        else f"I am enthusiastic about the opportunity to join {company}."
    )

    personal_paragraph = _PERSONAL_PARAGRAPH_TEMPLATE.format(
        personal_summary=personal_summary
    )

    letter = _LOCAL_TEMPLATE.format(
        name=name,
        email=email,
        job_title=job_title,
        role=job_title,
        company=company,
        industry=industry,
        motivation_paragraph=motivation_paragraph,
        project_summary=projects_text if projects_text else "various software projects",
        skills=skills_text if skills_text else "a broad technical skill set",
        personal_paragraph=personal_paragraph,
    )
    return letter.strip()


# ---------------------------------------------------------------------------
# AI generation
# ---------------------------------------------------------------------------

def generate_ai(
    *,
    resume_id: int,
    job_title: str,
    company: str,
    job_description: str,
    motivations: List[str],
) -> str:
    """
    Generate a cover letter using the Gemini LLM.
    Falls back to local generation if no API key is configured.
    Returns the cover letter as a plain-text string.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY not set – falling back to local cover letter generation.")
        return generate_local(
            resume_id=resume_id,
            job_title=job_title,
            company=company,
            job_description=job_description,
            motivations=motivations,
        )

    profile = _load_user_profile()
    resume = _load_resume_context(resume_id)

    name = profile.get("name") or "Applicant"
    email = profile.get("email") or ""
    industry = profile.get("industry") or "technology"
    personal_summary = profile.get("personal_summary") or ""
    linkedin = profile.get("linkedin") or ""

    projects_text = _format_project_bullets(resume.get("projects", []))
    skills_text = _format_skills(resume.get("skills", {}))
    motivation_text = _motivation_text(motivations)

    prompt = f"""
    You are a professional cover letter writer. Write a tailored, compelling cover letter for the following candidate.

Candidate profile:
- Name: {name}
- Email: {email}
- Industry: {industry}
- Personal summary: {personal_summary}

Target role:
- Job title: {job_title}
- Company: {company}
- Job description:
{job_description}

Candidate motivations for applying: {motivation_text if motivation_text else "general professional interest"}

Relevant project experience:
{projects_text if projects_text else "N/A"}

Technical skills: {skills_text if skills_text else "N/A"}

Instructions:
- Write a professional, concise cover letter (3-4 paragraphs).
- Open with a strong, personalised first paragraph referencing the role and company.
- Highlight 2-3 specific projects or achievements that are most relevant to the job description.
- Weave in the candidate's motivations naturally — do NOT list them mechanically.
- Close with a confident call to action.
- Do NOT include placeholders like [Your Name] or [Date] — use the real values provided.
- Return ONLY the cover letter text, no explanatory commentary.
"""

    try:
        client = GeminiLLMClient(api_key=api_key)
        result = client.generate(prompt)
        if not result or result.startswith("Gemini API error"):
            logger.warning("Gemini returned an error, falling back to local generation.")
            return generate_local(
                resume_id=resume_id,
                job_title=job_title,
                company=company,
                job_description=job_description,
                motivations=motivations,
            )
        return result.strip()
    except Exception as exc:
        logger.error(f"AI cover letter generation failed: {exc}")
        return generate_local(
            resume_id=resume_id,
            job_title=job_title,
            company=company,
            job_description=job_description,
            motivations=motivations,
        )


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

def generate_cover_letter(
    *,
    resume_id: int,
    job_title: str,
    company: str,
    job_description: str,
    motivations: List[str],
    mode: str,
) -> str:
    """
    Generate a cover letter in the requested mode ('ai' or 'local').
    Returns the letter as a plain-text string.
    """
    if mode == "ai":
        return generate_ai(
            resume_id=resume_id,
            job_title=job_title,
            company=company,
            job_description=job_description,
            motivations=motivations,
        )
    return generate_local(
        resume_id=resume_id,
        job_title=job_title,
        company=company,
        job_description=job_description,
        motivations=motivations,
    )


# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------

def save_cover_letter(
    *,
    resume_id: int,
    job_title: str,
    company: str,
    job_description: str,
    motivations: List[str],
    content: str,
    generation_mode: str,
) -> int:
    """Insert a cover letter into the DB and return its new id."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO COVER_LETTER
                (resume_id, job_title, company, job_description, motivations, content, generation_mode)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                resume_id,
                job_title,
                company,
                job_description,
                json.dumps(motivations),
                content,
                generation_mode,
            ),
        )
        conn.commit()
        return cursor.lastrowid  # type: ignore[return-value]
    except sqlite3.Error as exc:
        raise CoverLetterServiceError("Failed to save cover letter") from exc
    finally:
        conn.close()


def get_cover_letter(cover_letter_id: int) -> Dict[str, Any]:
    """Return a single cover letter row as a dict. Raises CoverLetterNotFoundError if missing."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, resume_id, job_title, company, job_description,
                   motivations, content, generation_mode, created_at
            FROM COVER_LETTER
            WHERE id = ?
            """,
            (cover_letter_id,),
        )
        row = cursor.fetchone()
    finally:
        conn.close()

    if row is None:
        raise CoverLetterNotFoundError(f"Cover letter {cover_letter_id} not found")

    return _row_to_dict(row)


def list_cover_letters() -> List[Dict[str, Any]]:
    """Return all saved cover letters ordered by most recent first."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, resume_id, job_title, company, job_description,
                   motivations, content, generation_mode, created_at
            FROM COVER_LETTER
            ORDER BY created_at DESC
            """
        )
        rows = cursor.fetchall()
    finally:
        conn.close()

    return [_row_to_dict(r) for r in rows]


def delete_cover_letter(cover_letter_id: int) -> bool:
    """Delete a cover letter by id. Returns True if a row was deleted."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM COVER_LETTER WHERE id = ?", (cover_letter_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as exc:
        raise CoverLetterServiceError("Failed to delete cover letter") from exc
    finally:
        conn.close()


def _row_to_dict(row: tuple) -> Dict[str, Any]:
    (cl_id, resume_id, job_title, company, job_description,
     motivations_json, content, generation_mode, created_at) = row

    motivations: List[str] = []
    if motivations_json:
        try:
            motivations = json.loads(motivations_json)
        except Exception:
            motivations = []

    return {
        "id": cl_id,
        "resume_id": resume_id,
        "job_title": job_title,
        "company": company,
        "job_description": job_description,
        "motivations": motivations,
        "content": content,
        "generation_mode": generation_mode,
        "created_at": created_at,
    }
