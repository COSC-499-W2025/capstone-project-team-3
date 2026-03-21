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
from datetime import date as _date
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
    "innovation": "a culture of innovation and cutting-edge technology",
    "work_life_balance": "a healthy work-life balance and employee well-being",
    "social_impact": "the company's positive social impact and mission",
    "compensation": "competitive compensation and benefits",
    "team_collaboration": "a collaborative and supportive team environment",
    "learning_opportunities": "strong learning and development opportunities",
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
    """Return a plain-text project section, one project per paragraph."""
    blocks: List[str] = []
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

        # Keep the three most meaningful bullets to avoid congestion
        meaningful = [str(b).strip() for b in raw_bullets if b][:3]
        bullet_lines = "\n".join(f"  • {b}" for b in meaningful)

        header = f"{title}"
        if dates:
            header += f"  ({dates})"
        blocks.append(f"{header}\n{bullet_lines}")

    return "\n\n".join(blocks)


def _format_skills(skills: Dict[str, List[str]]) -> str:
    """Return a comma-separated skills string."""
    all_skills: List[str] = []
    for items in skills.values():
        all_skills.extend(items)
    return ", ".join(all_skills)


def _collect_project_skills(projects: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """Return a mapping of project title → list of skill tokens found in its bullets."""
    result: Dict[str, List[str]] = {}
    for p in projects:
        title = p.get("title", p.get("project_name", "Unnamed Project"))
        raw_bullets = p.get("bullets", [])
        if isinstance(raw_bullets, str):
            try:
                raw_bullets = json.loads(raw_bullets)
            except Exception:
                raw_bullets = [raw_bullets]
        if not isinstance(raw_bullets, list):
            raw_bullets = [str(raw_bullets)]
        tokens: List[str] = []
        for b in raw_bullets:
            tokens.extend(str(b).lower().split())
        result[title] = tokens
    return result


def _match_skills_to_jd(
    resume_skills: Dict[str, List[str]],
    projects: List[Dict[str, Any]],
    job_description: str,
) -> Dict[str, Any]:
    """
    Cross-reference the candidate's skills and project bullet keywords against the
    job description.  Returns a dict with:
      - matched_skills: skills from the resume found in the JD
      - best_projects:  up to 2 project titles whose bullets share the most keywords with the JD
    """
    jd_words = set(job_description.lower().split())

    # --- Matched resume skills -------------------------------------------------
    all_skills: List[str] = []
    for items in resume_skills.values():
        all_skills.extend(items)

    matched_skills = [
        s for s in all_skills
        if any(word in jd_words for word in s.lower().split())
    ]
    # Deduplicate while preserving order
    seen: set = set()
    unique_matched: List[str] = []
    for s in matched_skills:
        key = s.lower()
        if key not in seen:
            seen.add(key)
            unique_matched.append(s)

    # --- Best-matching & scoring projects ------------------------------------------------
    project_skill_map = _collect_project_skills(projects)
    project_scores: List[tuple] = []
    for title, tokens in project_skill_map.items():
        score = sum(1 for t in tokens if t in jd_words)
        project_scores.append((score, title))
    project_scores.sort(key=lambda x: x[0], reverse=True)
    best_projects = [title for score, title in project_scores if score > 0][:2]

    return {
        "matched_skills": unique_matched,
        "best_projects": best_projects,
    }


def _motivation_text(motivations: List[str]) -> str:
    """Convert motivation keys (or free-text custom values) to a readable sentence fragment."""
    labels = []
    for m in motivations:
        if not m:
            continue
        labels.append(MOTIVATION_LABELS.get(m, m))
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
{email}{linkedin_line}
{date}

{job_title} Application — {company}

Dear {company} Hiring Team,

I am writing to express my strong interest in the {role} position at {company}. {education_line} with a background in {industry} and hands-on experience across a range of technical projects, I am confident in my ability to contribute meaningfully to your team.

{motivation_paragraph}

{personal_paragraph}

{skills_paragraph}

{closing_paragraph}

Thank you for your time and consideration.

Sincerely,
{name}
"""

_MOTIVATION_PARAGRAPH_TEMPLATE = (
    "I am particularly drawn to {company} because of {motivation_text}. "
    "This aligns closely with my own professional aspirations and is what initially drew me to the role."
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
    linkedin = profile.get("linkedin") or ""
    industry = profile.get("industry") or "technology"
    personal_summary = profile.get("personal_summary") or (
        f"I bring a passion for {industry} and a commitment to delivering high-quality work."
    )

    projects = resume.get("projects", [])
    resume_skills = resume.get("skills", {})
    education_list = resume.get("education", [])

    projects_text = _format_project_bullets(projects)
    skills_text = _format_skills(resume_skills)

    today = _date.today().strftime("%B %d, %Y")

    # ── Education line ─────────────────────────────────────────────────────
    education_line = ""
    if education_list:
        first = education_list[0]
        degree = first.get("degree", "").strip()
        school = first.get("school", "").strip()
        if degree and school:
            education_line = f"As a {degree} graduate from {school}"
        elif degree:
            education_line = f"As a {degree} graduate"
        elif school:
            education_line = f"As a graduate from {school} "

    # ── JD skill-matching ──────────────────────────────────────────────────
    match = _match_skills_to_jd(resume_skills, projects, job_description)
    matched_skills = match["matched_skills"]
    best_projects = match["best_projects"]

    # Skills paragraph — highlight matched skills + attribute to specific projects
    if matched_skills:
        top_matched = ", ".join(matched_skills[:6])
        remaining = [s for s in (skills_text.split(", ") if skills_text else [])
                     if s not in matched_skills]
        additional = (", ".join(remaining[:4]) + "," if remaining else "")
        if best_projects:
            project_attr = " and ".join(f'"{t}"' for t in best_projects)
            skills_paragraph = (
                f"My technical skill set spans {additional} among others. "
                f"Particularly relevant to this role, I have hands-on experience with "
                f"{top_matched} — skills I developed through projects including {project_attr}, "
                f"which directly align with the requirements outlined in the job description."
            )
        else:
            skills_paragraph = (
                f"My technical skill set spans {additional} among others. "
                f"Particularly relevant to this role, I have hands-on experience with "
                f"{top_matched} — skills that directly align with the requirements outlined "
                f"in the job description."
            )
    else:
        skills_paragraph = (
            f"My core technical skills include {skills_text if skills_text else 'a broad technical skill set'}."
        )


    # ── Motivation & personal paragraphs ──────────────────────────────────
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

    # Closing paragraph
    closing_paragraph = (
        f"I am excited about the opportunity to bring my skills and experience to {company} "
        f"and would welcome the chance to discuss how I can contribute to your team's goals. "
        f"Please feel free to reach out at any time — my contact information is listed above."
    )

    # ── Assemble ───────────────────────────────────────────────────────────
    # LinkedIn line: only include if present
    linkedin_line = f"\n{linkedin}" if linkedin else ""

    letter = _LOCAL_TEMPLATE.format(
        name=name,
        email=email,
        linkedin_line=linkedin_line,
        date=today,
        job_title=job_title,
        role=job_title,
        company=company,
        industry=industry,
        education_line=education_line,
        motivation_paragraph=motivation_paragraph,
        personal_paragraph=personal_paragraph,
        skills_paragraph=skills_paragraph,
        closing_paragraph=closing_paragraph,
    )
    return letter.strip()


# ---------------------------------------------------------------------------
# AI output post-processor
# ---------------------------------------------------------------------------

import re as _re


def _postprocess_ai_body(raw: str, *, name: str, company: str) -> str:
    """
    Extract just the letter body from raw LLM output and ensure the
    candidate's name follows "Sincerely,".

    Finds "Dear Hiring Manager," (start) and "Sincerely," (end), keeps only
    that slice, replaces the generic greeting with "Dear {company} Hiring Team,",
    strips any name the LLM may have appended after "Sincerely,",
    then appends the real name from the user's profile.  If either boundary
    is missing the raw text is returned stripped so generation still succeeds.
    """
    text = raw.strip()

    start_match = _re.search(r"Dear Hiring Manager,", text, _re.IGNORECASE)
    end_match   = _re.search(r"Sincerely,", text, _re.IGNORECASE)

    if start_match and end_match and end_match.start() > start_match.start():
        text = text[start_match.start(): end_match.end()].strip()

    # Replace generic greeting with company-specific one
    text = _re.sub(
        r"Dear Hiring Manager,",
        f"Dear {company} Hiring Team,",
        text,
        flags=_re.IGNORECASE,
    )

    # Always close with the real name — remove whatever the LLM put there
    text = _re.sub(r"(Sincerely,)[\s\S]*$", r"\1", text, flags=_re.IGNORECASE).strip()
    text = f"{text}\n{name}"

    return text


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

    The header (name / email / linkedin / date / job title line) is always
    assembled from the user's stored profile data.  The LLM only writes the
    body paragraphs (greeting through sign-off), which are then slotted into
    the same structural envelope used by the local template.

    Falls back to local generation if no API key is configured.
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

    # ── Header data (never sent to the LLM) ───────────────────────────────
    name     = profile.get("name") or "Applicant"
    email    = profile.get("email") or ""
    linkedin = profile.get("linkedin") or ""
    today    = _date.today().strftime("%B %d, %Y")
    linkedin_line = f"\n{linkedin}" if linkedin else ""

    # ── Context for the prompt ────────────────────────────────────────────
    projects = resume.get("projects", [])
    resume_skills = resume.get("skills", {})

    projects_text = _format_project_bullets(projects)
    skills_text   = _format_skills(resume_skills)
    motivation_text = _motivation_text(motivations)

    # JD matching — used only to tell the LLM which projects to emphasise
    match = _match_skills_to_jd(resume_skills, projects, job_description)
    best_projects = match["best_projects"]
    emphasis = (
        f"Please emphasise the following projects as they are the most relevant to the role: "
        + ", ".join(f'"{t}"' for t in best_projects)
        if best_projects else ""
    )

    prompt = f"""You are a professional cover letter writer.

Based on the context provided, write ONLY the body of a cover letter — starting from "Dear Hiring Manager," 
and ending with "Sincerely,"). Do NOT include any header, date, address, or name block.

Target role:
- Job title: {job_title}
- Company: {company}
- Job description:
{job_description}

Relevant project experience:
{projects_text if projects_text else "N/A"}

Technical skills: {skills_text if skills_text else "N/A"}

Candidate motivations for applying: {motivation_text if motivation_text else "general professional interest"}

{emphasis}

Instructions:
- Write 3–4 tight paragraphs, maximum 350 words.
- Open with a strong, personalised first paragraph referencing the role and company.
- Highlight 1–3 specific projects or achievements that are most relevant to the job description.
- Weave in the candidate's motivations naturally — do NOT list them mechanically.
- Close with a confident call to action.
- Do NOT include any date, name, email, address, or placeholders like [Your Name] or [Date].
- Return ONLY the body of the letter as plain-text.
"""

    try:
        client = GeminiLLMClient(api_key=api_key)
        raw = client.generate(prompt)
        if not raw or raw.startswith("Gemini API error"):
            logger.warning("Gemini returned an error, falling back to local generation.")
            return generate_local(
                resume_id=resume_id,
                job_title=job_title,
                company=company,
                job_description=job_description,
                motivations=motivations,
            )

        body = _postprocess_ai_body(raw, name=name, company=company)

        # ── Assemble: pre-built header + AI body ──────────────────────────
        header = (
            f"{name}\n"
            f"{email}{linkedin_line}\n"
            f"{today}\n\n"
            f"{job_title} Application — {company}"
        )
        return f"{header}\n\n{body}".strip()

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


def update_cover_letter_content(cover_letter_id: int, content: str) -> Dict[str, Any]:
    """Update the content of an existing cover letter. Returns the updated row."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE COVER_LETTER SET content = ? WHERE id = ?",
            (content, cover_letter_id),
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise CoverLetterNotFoundError(f"Cover letter {cover_letter_id} not found")
    except sqlite3.Error as exc:
        raise CoverLetterServiceError("Failed to update cover letter") from exc
    finally:
        conn.close()
    return get_cover_letter(cover_letter_id)


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
