"""
Score curated learning catalog items against the master resume and profile preferences.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, MutableMapping, Optional, Set, Tuple

CATALOG_PATH = Path(__file__).resolve().parent.parent / "data" / "course_catalog.json"

# Weights: higher = stronger signal for tag overlap
WEIGHT_PROFICIENT = 3.0
WEIGHT_FAMILIAR = 2.0
WEIGHT_PROJECT_SKILL = 2.5
WEIGHT_SUMMARY = 1.0
WEIGHT_JOB_TITLE = 2.0
WEIGHT_INDUSTRY = 2.0

# Bonus when ranking advanced courses
BONUS_ADVANCED_STARTER_TAG = 1.5
BONUS_ADVANCED_TOP_USER_TAG = 1.0

DEFAULT_STARTER_LIMIT = 6
DEFAULT_ADVANCED_LIMIT = 6


def normalize_tag(raw: str) -> str:
    s = raw.strip().lower()
    s = re.sub(r"[^a-z0-9+#.]+", "-", s)
    return s.strip("-")


def _add_weight(weights: MutableMapping[str, float], tag: str, w: float) -> None:
    nt = normalize_tag(tag)
    if len(nt) < 2:
        return
    weights[nt] = max(weights.get(nt, 0.0), w)


def _tokens_from_free_text(text: str) -> Set[str]:
    if not text:
        return set()
    out: Set[str] = set()
    for m in re.finditer(r"[a-zA-Z0-9][a-zA-Z0-9+#.]*", text):
        nt = normalize_tag(m.group(0))
        if len(nt) >= 2:
            out.add(nt)
    return out


def extract_user_tag_weights(
    resume: Dict[str, Any],
    job_title: str = "",
    industry: str = "",
) -> Dict[str, float]:
    """Build tag -> weight map from master resume plus job context."""
    weights: Dict[str, float] = {}

    skills = resume.get("skills") or {}
    for s in skills.get("Proficient") or []:
        if isinstance(s, str):
            _add_weight(weights, s, WEIGHT_PROFICIENT)
    for s in skills.get("Familiar") or []:
        if isinstance(s, str):
            _add_weight(weights, s, WEIGHT_FAMILIAR)

    for proj in resume.get("projects") or []:
        sk = proj.get("skills")
        if not isinstance(sk, str):
            continue
        for part in sk.split(","):
            part = part.strip()
            if part:
                _add_weight(weights, part, WEIGHT_PROJECT_SKILL)

    summary = resume.get("personal_summary")
    if isinstance(summary, str) and summary.strip():
        for t in _tokens_from_free_text(summary):
            _add_weight(weights, t, WEIGHT_SUMMARY)

    if job_title:
        for t in _tokens_from_free_text(job_title):
            _add_weight(weights, t, WEIGHT_JOB_TITLE)

    if industry:
        _add_weight(weights, industry, WEIGHT_INDUSTRY)
        for t in _tokens_from_free_text(industry):
            _add_weight(weights, t, WEIGHT_INDUSTRY)

    return weights


def score_course_base(course_tags: List[str], user_weights: Dict[str, float]) -> float:
    normalized = [normalize_tag(t) for t in course_tags if isinstance(t, str)]
    score = 0.0
    for ct in normalized:
        if ct in user_weights:
            score += user_weights[ct]
    return score


def load_course_catalog(path: Optional[Path] = None) -> List[Dict[str, Any]]:
    p = path or CATALOG_PATH
    with open(p, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("course_catalog.json must be a JSON array")
    return data


def _course_tags_set(course: Dict[str, Any]) -> Set[str]:
    tags = course.get("tags") or []
    return {normalize_tag(t) for t in tags if isinstance(t, str) and normalize_tag(t)}


def recommend_courses(
    catalog: List[Dict[str, Any]],
    resume: Dict[str, Any],
    job_title: str = "",
    industry: str = "",
    starter_limit: int = DEFAULT_STARTER_LIMIT,
    advanced_limit: int = DEFAULT_ADVANCED_LIMIT,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Returns (based_on_resume starter courses, next_steps advanced courses), each with
    the same fields as catalog entries plus optional '_score' for debugging (stripped at API).
    """
    user_weights = extract_user_tag_weights(resume, job_title=job_title, industry=industry)

    starters: List[Tuple[float, Dict[str, Any]]] = []
    advanced: List[Dict[str, Any]] = []

    for c in catalog:
        level = (c.get("level") or "").lower()
        tags = c.get("tags") or []
        if not isinstance(tags, list):
            tags = []
        base = score_course_base(tags, user_weights)
        if level == "starter":
            starters.append((base, c))
        elif level == "advanced":
            advanced.append(c)

    starters.sort(key=lambda x: (-x[0], x[1].get("title", "")))
    positive = [c for sc, c in starters if sc > 0]
    zero = [c for sc, c in starters if sc <= 0]
    picked_starters = (positive + zero)[:starter_limit]

    starter_union_tags: Set[str] = set()
    for c in picked_starters[:3]:
        starter_union_tags |= _course_tags_set(c)

    top_user_tags = sorted(user_weights.keys(), key=lambda t: -user_weights[t])[:8]
    top_user_set = set(top_user_tags)

    def advanced_score(course: Dict[str, Any]) -> float:
        tags = course.get("tags") or []
        base = score_course_base(tags if isinstance(tags, list) else [], user_weights)
        ctags = _course_tags_set(course)
        bonus_starter = BONUS_ADVANCED_STARTER_TAG * len(ctags & starter_union_tags)
        bonus_user = BONUS_ADVANCED_TOP_USER_TAG * len(ctags & top_user_set)
        return base + bonus_starter + bonus_user

    ranked_adv = sorted(advanced, key=lambda c: (-advanced_score(c), c.get("title", "")))
    picked_advanced = ranked_adv[:advanced_limit]

    return picked_starters, picked_advanced


def serialize_course(course: Dict[str, Any]) -> Dict[str, Any]:
    """Public shape for API / UI."""
    return {
        "id": course.get("id"),
        "title": course.get("title"),
        "description": course.get("description"),
        "url": course.get("url"),
        "thumbnail_url": course.get("thumbnail_url"),
        "provider": course.get("provider"),
        "tags": course.get("tags") or [],
        "level": course.get("level"),
        "pricing": course.get("pricing"),
    }


def build_learning_payload(
    catalog: Optional[List[Dict[str, Any]]] = None,
    resume: Optional[Dict[str, Any]] = None,
    job_title: str = "",
    industry: str = "",
) -> Dict[str, List[Dict[str, Any]]]:
    cat = catalog if catalog is not None else load_course_catalog()
    res = resume if resume is not None else {}
    starters, advanced = recommend_courses(cat, res, job_title=job_title, industry=industry)
    return {
        "based_on_resume": [serialize_course(c) for c in starters],
        "next_steps": [serialize_course(c) for c in advanced],
    }
