"""
ATS (Applicant Tracking System) scoring endpoint.

Accepts a job description and a resume (master or saved) and returns
an ATS compatibility score with a breakdown, matched/missing keywords,
experience months, and a LinkedIn-style High/Medium/Low match level.
"""
from __future__ import annotations

import os
import re
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.utils.generate_resume import build_resume_model, load_saved_resume
from app.utils.tech_keywords import TECH_KEYWORDS

router = APIRouter()

# ---------------------------------------------------------------------------
# Stop-words (lightweight)
# ---------------------------------------------------------------------------
_STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "up", "about", "into", "through", "during",
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "will", "would", "could", "should", "may", "might",
    "must", "shall", "can", "need", "dare", "ought", "used",
    "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us",
    "them", "my", "your", "his", "its", "our", "their", "this", "that",
    "these", "those", "who", "which", "what", "all", "both", "each",
    "few", "more", "most", "other", "some", "such", "no", "nor", "not",
    "only", "own", "same", "so", "than", "too", "very", "s", "t", "just",
    "don", "as", "if", "when", "where", "how", "work", "working", "use",
    "using", "experience", "strong", "ability", "excellent", "etc",
    "including", "also", "well", "within", "across", "ensure", "provide",
    "take", "make", "build", "create", "develop", "manage", "support",
    "help", "ability", "required", "preferred", "years", "year", "role",
    "team", "company", "environment", "understanding", "knowledge",
    "responsibilities", "qualifications", "position", "candidate", "job",
    "looking", "seeking", "opportunity", "applications", "new", "good",
    "great", "plus", "type", "based", "various",
}


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class ATSScoreRequest(BaseModel):
    job_description: str = Field(..., min_length=10)
    resume_id: Optional[int] = Field(
        None,
        description="ID of a saved resume. Omit or pass null to use the master resume.",
    )


class ATSScoreResponse(BaseModel):
    score: int = Field(..., ge=0, le=100)
    match_level: str = Field(..., description="High | Medium | Low")
    experience_months: int = Field(..., ge=0)
    breakdown: Dict[str, int]
    matched_keywords: List[str]
    missing_keywords: List[str]
    matched_skills: List[str]
    missing_skills: List[str]
    tips: List[str]


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> List[str]:
    """Lower-case, split on non-alphanumeric, remove stop-words and short tokens."""
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9+#./]*", text.lower())
    return [t for t in tokens if t not in _STOP_WORDS and len(t) > 2]


def _extract_jd_keywords_fallback(jd: str) -> List[str]:
    """Fallback tokeniser-based JD keyword extraction."""
    tokens = _tokenize(jd)
    seen: Dict[str, int] = {}
    for t in tokens:
        seen[t] = seen.get(t, 0) + 1
    ranked = sorted(seen.items(), key=lambda x: (-x[1], x[0]))
    # Keep only words that also exist in TECH_KEYWORDS or appear 2+ times
    filtered = [
        word for word, count in ranked
        if word in TECH_KEYWORDS or count >= 2
    ]
    return filtered if filtered else [word for word, _ in ranked]


def _gemini_extract_jd_keywords(jd: str) -> List[str]:
    """
    Use Gemini to extract meaningful tech keywords from the JD.
    Returns a list of lowercase keyword strings.
    Falls back to tokeniser extraction on any error.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return _extract_jd_keywords_fallback(jd)

    try:
        import google.generativeai as genai  # type: ignore
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = (
            "You are an expert ATS keyword extractor for technical job postings.\n"
            "From the job description below, extract ONLY:\n"
            "- Programming languages, frameworks, libraries, and tools\n"
            "- Cloud platforms and infrastructure technologies\n"
            "- Databases and data technologies\n"
            "- Software engineering methodologies and practices\n"
            "- Explicit years-of-experience requirements (e.g. '5 years')\n\n"
            "DO NOT include:\n"
            "- Company-specific culture words (e.g. 'Amazonian', 'Googler')\n"
            "- Generic soft skills (e.g. 'passionate', 'collaborative')\n"
            "- Generic verbs (e.g. 'build', 'develop', 'manage')\n"
            "- Generic nouns (e.g. 'team', 'environment', 'opportunity')\n\n"
            "Return ONLY a valid JSON array of lowercase strings, nothing else.\n"
            "Example: [\"python\", \"react\", \"aws\", \"5+ years\", \"docker\"]\n\n"
            f"Job description:\n{jd}"
        )

        response = model.generate_content(prompt)
        raw = response.text.strip()

        # Strip markdown code fences if present
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        keywords = json.loads(raw)
        if isinstance(keywords, list):
            return [str(k).lower().strip() for k in keywords if k]
    except Exception:
        pass

    return _extract_jd_keywords_fallback(jd)


# ---------------------------------------------------------------------------
# Resume helpers
# ---------------------------------------------------------------------------

def _resume_full_text(resume: Any) -> str:
    """Flatten all text from a resume dict into a single string."""
    parts: List[str] = []

    for skill_list in (resume.get("skills") or {}).values():
        if isinstance(skill_list, list):
            parts.extend(skill_list)
        elif isinstance(skill_list, str):
            parts.append(skill_list)

    for proj in resume.get("projects") or []:
        parts.append(proj.get("title") or "")
        bullets = proj.get("bullets") or []
        if isinstance(bullets, str):
            try:
                bullets = json.loads(bullets)
            except Exception:
                bullets = [bullets]
        parts.extend(bullets)
        proj_skills = proj.get("skills") or []
        if isinstance(proj_skills, str):
            parts.extend(re.split(r"[,;]+", proj_skills))
        else:
            parts.extend(proj_skills)

    return " ".join(str(p) for p in parts)


def _all_resume_skills(resume: Any) -> List[str]:
    """Return a flat list of all skill tokens from the resume."""
    skills: List[str] = []
    for skill_list in (resume.get("skills") or {}).values():
        if isinstance(skill_list, list):
            for s in skill_list:
                skills.extend(_tokenize(str(s)))
        elif isinstance(skill_list, str):
            skills.extend(_tokenize(skill_list))
    for proj in resume.get("projects") or []:
        proj_skills = proj.get("skills") or []
        if isinstance(proj_skills, str):
            for part in re.split(r"[,;]+", proj_skills):
                skills.extend(_tokenize(part))
        else:
            for s in proj_skills:
                skills.extend(_tokenize(str(s)))
    return list(set(skills))


def _calc_experience_months(resume: Any) -> int:
    """
    Sum up the duration of all projects in months.
    E.g. 3 projects × 2 months each = 6 months total.
    """
    total_months = 0
    for proj in resume.get("projects") or []:
        start_str = proj.get("start_date") or ""
        end_str = proj.get("end_date") or ""
        if not start_str or not end_str:
            continue
        try:
            start_dt = datetime.fromisoformat(start_str)
            end_dt = datetime.fromisoformat(end_str)
            if end_dt > start_dt:
                diff = (end_dt.year - start_dt.year) * 12 + (end_dt.month - start_dt.month)
                total_months += max(diff, 1)
        except (ValueError, TypeError):
            continue
    return total_months


def _match_level(score: int) -> str:
    if score >= 70:
        return "High"
    if score >= 40:
        return "Medium"
    return "Low"


# ---------------------------------------------------------------------------
# Core scoring
# ---------------------------------------------------------------------------

def _score_ats(resume: Any, jd: str) -> ATSScoreResponse:
    jd_keywords = _gemini_extract_jd_keywords(jd)

    # Supplement with any TECH_KEYWORDS that appear verbatim in the JD
    jd_lower = jd.lower()
    tech_in_jd = [kw for kw in TECH_KEYWORDS if re.search(r"\b" + re.escape(kw) + r"\b", jd_lower)]
    # Merge, preserving order and uniqueness
    jd_keywords_set = set(jd_keywords)
    for kw in tech_in_jd:
        if kw not in jd_keywords_set:
            jd_keywords.append(kw)
            jd_keywords_set.add(kw)

    resume_text_tokens = set(_tokenize(_resume_full_text(resume)))
    resume_skill_tokens = set(_all_resume_skills(resume))

    # Keyword coverage: JD keywords found anywhere in resume text
    matched_kw = [kw for kw in jd_keywords if any(t in resume_text_tokens for t in _tokenize(kw) or [kw])]
    missing_kw = [kw for kw in jd_keywords if kw not in matched_kw]

    # Skill overlap: JD keywords found in resume skills specifically
    matched_sk = [kw for kw in jd_keywords if any(t in resume_skill_tokens for t in _tokenize(kw) or [kw])]
    missing_sk = [kw for kw in jd_keywords if kw not in matched_sk]

    kw_count = max(len(jd_keywords), 1)
    keyword_score = round(len(matched_kw) / kw_count * 100)
    skills_score = round(len(matched_sk) / kw_count * 100)

    bullet_count = sum(
        len(proj.get("bullets") or []) if isinstance(proj.get("bullets"), list) else 1
        for proj in (resume.get("projects") or [])
        if proj.get("bullets")
    )
    content_score = min(100, bullet_count * 8)

    overall = round(keyword_score * 0.5 + skills_score * 0.35 + content_score * 0.15)
    overall = max(0, min(100, overall))

    experience_months = _calc_experience_months(resume)

    MAX_SHOW = 20
    matched_kw_display = sorted(set(matched_kw))[:MAX_SHOW]
    missing_kw_display = sorted(set(missing_kw))[:MAX_SHOW]
    matched_sk_display = sorted(set(matched_sk))[:MAX_SHOW]
    missing_sk_display = sorted(set(missing_sk))[:MAX_SHOW]

    tips: List[str] = []
    if skills_score < 50:
        tips.append("Add more of the required skills from the job description to your resume skills section.")
    if keyword_score < 60:
        tips.append("Mirror the exact wording from the job description in your project descriptions and bullet points.")
    if content_score < 50:
        tips.append("Expand project bullet points with specific achievements and technologies to improve keyword coverage.")
    if experience_months < 12:
        tips.append("Consider adding more detailed project timelines to better reflect your total hands-on experience.")
    if not tips:
        tips.append("Great match! Review missing keywords and consider weaving them naturally into your bullet points.")

    return ATSScoreResponse(
        score=overall,
        match_level=_match_level(overall),
        experience_months=experience_months,
        breakdown={
            "keyword_coverage": keyword_score,
            "skills_match": skills_score,
            "content_richness": content_score,
        },
        matched_keywords=matched_kw_display,
        missing_keywords=missing_kw_display,
        matched_skills=matched_sk_display,
        missing_skills=missing_sk_display,
        tips=tips,
    )


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------

@router.post("/ats/score", response_model=ATSScoreResponse)
def ats_score(payload: ATSScoreRequest) -> ATSScoreResponse:
    """
    Calculate an ATS compatibility score between a resume and a job description.

    - Omit `resume_id` (or pass `null`) to use the master resume (all projects).
    - Pass a saved resume's `resume_id` to score that specific tailored resume.
    """
    try:
        if payload.resume_id is not None:
            resume = load_saved_resume(payload.resume_id)
        else:
            resume = build_resume_model()
    except Exception as exc:
        raise HTTPException(status_code=404, detail=f"Resume not found: {exc}")

    return _score_ats(resume, payload.job_description)
