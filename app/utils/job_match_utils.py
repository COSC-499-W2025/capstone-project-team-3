import re
from collections import Counter
from datetime import datetime
from html import unescape
from pathlib import Path
from urllib.parse import quote_plus, urlencode
from urllib.request import Request, urlopen
import json
from typing import Any, Dict, List, Set, Tuple

from app.data.db import get_connection
from app.utils.generate_portfolio import build_portfolio_model

def _load_shared_skill_catalog() -> Set[str]:
    catalog: Set[str] = {
        "python",
        "java",
        "javascript",
        "typescript",
        "react",
        "node.js",
        "fastapi",
        "sql",
        "docker",
        "git",
        "machine learning",
    }

    shared_dir = Path(__file__).resolve().parents[1] / "shared"

    language_map_path = shared_dir / "language_mapping.json"
    if language_map_path.exists():
        try:
            language_map = json.loads(language_map_path.read_text(encoding="utf-8"))
            if isinstance(language_map, dict):
                for display_name, canonical_name in language_map.items():
                    display = str(display_name or "").strip().lower()
                    canonical = str(canonical_name or "").strip().lower()
                    if display:
                        catalog.add(display)
                    if canonical:
                        catalog.add(canonical)
        except Exception:
            pass

    library_path = shared_dir / "library.json"
    if library_path.exists():
        try:
            library_map = json.loads(library_path.read_text(encoding="utf-8"))
            if isinstance(library_map, dict):
                for language_name in library_map.keys():
                    term = str(language_name or "").strip().lower()
                    if term:
                        catalog.add(term)
        except Exception:
            pass

    return {
        term
        for term in catalog
        if term and re.search(r"[a-z0-9]", term)
    }


SKILL_CATALOG = _load_shared_skill_catalog()

ROLE_TEMPLATES = [
    {
        "title": "Backend Software Engineer",
        "skills": {"python", "fastapi", "sql", "docker", "git", "rest"},
        "keywords": {"backend", "api", "server", "microservices"},
    },
    {
        "title": "Full-Stack Developer",
        "skills": {"javascript", "typescript", "react", "node.js", "sql", "git"},
        "keywords": {"full stack", "frontend", "backend", "web"},
    },
    {
        "title": "Frontend Engineer",
        "skills": {"javascript", "typescript", "react", "html", "css", "jest"},
        "keywords": {"frontend", "ui", "ux", "web"},
    },
    {
        "title": "Data / ML Engineer",
        "skills": {"python", "pandas", "numpy", "sql", "machine learning", "tensorflow"},
        "keywords": {"data", "ml", "ai", "analytics", "model"},
    },
    {
        "title": "DevOps Engineer",
        "skills": {"docker", "kubernetes", "aws", "ci/cd", "linux", "git"},
        "keywords": {"devops", "infrastructure", "deployment", "cloud"},
    },
]

REQUIRED_MARKERS = (
    "must",
    "required",
    "requirements",
    "strong",
    "hands-on",
    "experience with",
    "proficient",
)

PREFERRED_MARKERS = (
    "nice to have",
    "preferred",
    "bonus",
    "plus",
    "good to have",
)

ALIASES = {
    "js": "javascript",
    "ts": "typescript",
    "node": "node.js",
    "postgres": "postgresql",
    "k8s": "kubernetes",
    "ml": "machine learning",
}

HTTP_TIMEOUT_SECONDS = 7
HTTP_USER_AGENT = "CapstoneJobMatchBot/1.0"

SENIORITY_SENIOR_MARKERS = ("senior", "staff", "principal", "lead", "manager")
SENIORITY_ENTRY_MARKERS = ("intern", "junior", "new grad", "graduate", "entry")

REMOTE_LOCATION_MARKERS = (
    "remote",
    "worldwide",
    "anywhere",
    "work from home",
)

COUNTRY_LOCATION_HINTS = {
    "canada": ("canada", "ca", "toronto", "vancouver", "montreal", "ottawa", "calgary", "edmonton"),
    "united states": ("united states", "usa", "us", "new york", "california", "texas", "seattle", "boston"),
    "germany": ("germany", "berlin", "munich", "hamburg", "frankfurt", "cologne", "de"),
    "united kingdom": ("united kingdom", "uk", "england", "london", "manchester", "glasgow"),
    "india": ("india", "bangalore", "bengaluru", "mumbai", "delhi", "hyderabad", "pune"),
}


def _normalize_term(value: str) -> str:
    normalized = value.strip().lower()
    return ALIASES.get(normalized, normalized)


def _term_pattern(term: str) -> re.Pattern[str]:
    escaped = re.escape(term)
    return re.compile(rf"(?<!\w){escaped}(?!\w)", re.IGNORECASE)


def _extract_terms(text: str, catalog: Set[str]) -> Set[str]:
    if not text:
        return set()
    found: Set[str] = set()
    for term in catalog:
        if _term_pattern(term).search(text):
            found.add(term)
    for alias, canonical in ALIASES.items():
        if canonical not in found and _term_pattern(alias).search(text):
            found.add(canonical)
    return found


def _extract_job_requirements(job_description: str) -> Tuple[Set[str], Set[str], Set[str]]:
    sentences = [segment.strip() for segment in re.split(r"[\n\.;]", job_description) if segment.strip()]

    required: Set[str] = set()
    preferred: Set[str] = set()
    all_detected: Set[str] = set()

    for sentence in sentences:
        detected = _extract_terms(sentence, SKILL_CATALOG)
        if not detected:
            continue

        all_detected.update(detected)
        sentence_lower = sentence.lower()

        if any(marker in sentence_lower for marker in PREFERRED_MARKERS):
            preferred.update(detected)
        elif any(marker in sentence_lower for marker in REQUIRED_MARKERS):
            required.update(detected)
        else:
            preferred.update(detected)

    if not required and all_detected:
        required = set(list(all_detected)[: min(5, len(all_detected))])
        preferred = all_detected - required

    return required, preferred, all_detected


def _collect_portfolio_signals(portfolio: Dict[str, Any]) -> Tuple[Counter, Set[str]]:
    skill_counter: Counter = Counter()
    role_keywords: Set[str] = set()

    graphs = portfolio.get("graphs") or {}
    for skill, count in (graphs.get("top_skills") or {}).items():
        normalized = _normalize_term(str(skill))
        if normalized:
            skill_counter[normalized] += int(count or 0)

    for project in portfolio.get("projects") or []:
        for skill in project.get("skills") or []:
            normalized = _normalize_term(str(skill))
            if normalized:
                skill_counter[normalized] += 1

        metrics = project.get("metrics") or {}
        for keyword in metrics.get("technical_keywords") or []:
            normalized = _normalize_term(str(keyword))
            if normalized:
                skill_counter[normalized] += 1

        for role in metrics.get("roles") or []:
            role_keywords.add(str(role).lower())

    return skill_counter, role_keywords


def _load_saved_skills() -> List[str]:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT DISTINCT TRIM(skill)
            FROM SKILL_ANALYSIS
            WHERE skill IS NOT NULL
              AND TRIM(skill) != ''
            ORDER BY LOWER(TRIM(skill)) ASC
            """
        )
        rows = cur.fetchall()
        return [str(row[0]) for row in rows if row and row[0]]
    finally:
        conn.close()


def _experience_hint(portfolio: Dict[str, Any]) -> str:
    overview = portfolio.get("overview") or {}
    total_projects = int(overview.get("total_projects") or 0)
    avg_score = float(overview.get("avg_score") or 0)

    if total_projects >= 7 and avg_score >= 0.8:
        return "mid-level"
    if total_projects >= 4:
        return "junior"
    return "intern/junior"


def _load_user_preferences_snapshot() -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT name, email, industry, job_title, education, education_details
            FROM USER_PREFERENCES
            ORDER BY updated_at DESC
            LIMIT 1
            """
        )
        row = cur.fetchone()
        if not row:
            return {
                "name": "",
                "email": "",
                "industry": "",
                "job_title": "",
                "education": "",
                "education_details": [],
            }

        parsed_details: List[Dict[str, Any]] = []
        raw_details = row[5]
        if raw_details:
            try:
                parsed = json.loads(raw_details)
                if isinstance(parsed, list):
                    parsed_details = [item for item in parsed if isinstance(item, dict)]
            except Exception:
                parsed_details = []

        return {
            "name": row[0] or "",
            "email": row[1] or "",
            "industry": row[2] or "",
            "job_title": row[3] or "",
            "education": row[4] or "",
            "education_details": parsed_details,
        }
    finally:
        cur.close()
        conn.close()


def _extract_major_and_graduation(user_prefs: Dict[str, Any]) -> Tuple[str, int | None]:
    details = user_prefs.get("education_details") or []
    majors: List[str] = []
    grad_years: List[int] = []

    for entry in details:
        degree = str(entry.get("degree") or "").strip()
        if degree:
            majors.append(degree)
        end_date = str(entry.get("end_date") or "").strip()
        if end_date:
            year_match = re.search(r"(\d{4})", end_date)
            if year_match:
                grad_years.append(int(year_match.group(1)))

    fallback_education = str(user_prefs.get("education") or "").strip()
    major = majors[0] if majors else fallback_education
    grad_year = max(grad_years) if grad_years else None
    return major, grad_year


def _infer_country_from_education(user_prefs: Dict[str, Any]) -> str:
    details = user_prefs.get("education_details") or []
    institutions = [str(entry.get("institution") or "").lower() for entry in details]
    fallback_education = str(user_prefs.get("education") or "").lower()
    blob = " ".join(institutions + [fallback_education])

    if not blob.strip():
        return "Remote"

    country_hints = {
        "canada": ("canada", "toronto", "ubc", "waterloo", "mcgill", "ubc", "york university", "university of"),
        "united states": ("usa", "united states", "california", "new york", "mit", "stanford"),
        "germany": ("germany", "berlin", "munich", "hamburg", "frankfurt"),
        "united kingdom": ("uk", "united kingdom", "england", "london", "oxford", "cambridge"),
        "india": ("india", "iit", "delhi", "mumbai", "bangalore"),
    }

    for country, hints in country_hints.items():
        if any(hint in blob for hint in hints):
            return country.title()

    if details:
        return "Canada"
    return "Remote"


def _build_profile_queries(
    user_skills: Set[str],
    prioritized_skills: List[str],
    selected_skills: List[str] | None,
    user_prefs: Dict[str, Any],
    level_hint: str,
) -> List[str]:
    queries: List[str] = []
    job_title = str(user_prefs.get("job_title") or "").strip()
    industry = str(user_prefs.get("industry") or "").strip()

    preferred_skill_inputs = [
        str(skill).strip()
        for skill in (selected_skills or [])
        if isinstance(skill, str) and str(skill).strip()
    ]

    top_skills = preferred_skill_inputs[:8] if preferred_skill_inputs else [s for s in prioritized_skills if s][:8]
    if not top_skills:
        top_skills = sorted(user_skills)[:8]

    safe_skill_terms = [
        term
        for term in top_skills
        if len(term) >= 3 and not re.fullmatch(r"[a-z]{2,4}", term)
    ]
    if safe_skill_terms:
        top_skills = safe_skill_terms

    if preferred_skill_inputs:
        selected_focus_terms = [
            term
            for term in preferred_skill_inputs[:3]
            if len(term) >= 3 and not re.fullmatch(r"[a-z]{2,4}", term.lower())
        ]
        if selected_focus_terms:
            if job_title:
                queries.append(f"{job_title} {' '.join(selected_focus_terms)}")
            if len(selected_focus_terms) >= 2:
                queries.append(f"{selected_focus_terms[0]} {selected_focus_terms[1]} engineer")
            else:
                queries.append(f"software engineer {selected_focus_terms[0]}")

    if job_title:
        queries.append(f"{job_title} {level_hint}")
    if industry:
        queries.append(f"{industry} engineer")

    if len(top_skills) >= 2:
        queries.append(f"{top_skills[0]} {top_skills[1]} engineer")
    elif len(top_skills) == 1:
        if job_title:
            queries.append(f"{job_title} {top_skills[0]}")
        else:
            queries.append(f"software engineer {top_skills[0]}")

    queries.extend(
        [
            "software engineer",
            "software developer",
            "developer",
        ]
    )

    deduped: List[str] = []
    work_mode_pattern = re.compile(r"\b(remote|hybrid|onsite|on-site)\b", re.IGNORECASE)
    for query in queries:
        normalized = work_mode_pattern.sub(" ", query)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        if normalized and normalized not in deduped:
            deduped.append(normalized)
    return deduped


def _build_linkedin_search_links(
    queries: List[str],
    country: str,
    level_hint: str,
    work_types: List[str] | None = None,
    easy_apply: bool = True,
    posted_within_days: int = 7,
) -> List[Dict[str, str]]:
    links: List[Dict[str, str]] = []
    location = country if country and country.lower() != "remote" else "Worldwide"

    level = (level_hint or "").lower()
    if "intern" in level or "junior" in level:
        experience_codes = "1,2"  # internship + entry level
    elif "mid" in level:
        experience_codes = "3,4"  # associate + mid-senior
    else:
        experience_codes = "2,3,4"

    selected_work_types = [w.lower().strip() for w in (work_types or []) if isinstance(w, str)]

    linkedin_work_type_codes = {
        "onsite": "1",
        "remote": "2",
        "hybrid": "3",
    }
    work_type_codes = [linkedin_work_type_codes[w] for w in selected_work_types if w in linkedin_work_type_codes]
    work_type_param = ",".join(work_type_codes)

    posted_days_map = {
        1: "r86400",
        7: "r604800",
        30: "r2592000",
    }
    posted_param = posted_days_map.get(int(posted_within_days), "r604800")

    for query in queries[:5]:
        params = {
            "keywords": query,
            "location": location,
            "f_E": experience_codes,
            "f_TPR": posted_param,
            "sortBy": "DD",       # most recent
        }
        if work_type_param:
            params["f_WT"] = work_type_param
        if easy_apply:
            params["f_AL"] = "true"
        url = "https://www.linkedin.com/jobs/search/?" + urlencode(params, quote_via=quote_plus)
        links.append({"label": query, "url": url})

    return links


def _rank_recommended_jobs(
    user_skills: Set[str],
    job_required: Set[str],
    job_preferred: Set[str],
    role_keywords: Set[str],
    top_k: int,
) -> List[Dict[str, Any]]:
    combined_job_terms = job_required | job_preferred
    recommendations: List[Dict[str, Any]] = []

    for template in ROLE_TEMPLATES:
        role_skills = set(template["skills"])
        role_keywords_template = set(template["keywords"])

        user_skill_overlap = user_skills & role_skills
        user_fit = len(user_skill_overlap) / max(len(role_skills), 1)

        if combined_job_terms:
            job_fit = len(combined_job_terms & role_skills) / max(len(combined_job_terms), 1)
        else:
            keyword_hit = any(k in " ".join(role_keywords) for k in role_keywords_template)
            job_fit = 0.6 if keyword_hit else 0.4

        fit_score = round((0.65 * user_fit + 0.35 * job_fit) * 100)
        missing = sorted(role_skills - user_skills)[:4]
        matched = sorted(user_skill_overlap)[:4]

        reason_parts = []
        if matched:
            reason_parts.append(f"Strong overlap in {', '.join(matched)}")
        if missing:
            reason_parts.append(f"Upskill in {', '.join(missing)}")

        recommendations.append(
            {
                "title": template["title"],
                "fit_score": fit_score,
                "why": "; ".join(reason_parts) if reason_parts else "Solid baseline fit",
                "missing_skills": missing,
            }
        )

    recommendations.sort(key=lambda item: item["fit_score"], reverse=True)
    return recommendations[: max(1, top_k)]


def _http_get_json(url: str) -> Dict[str, Any]:
    req = Request(url, headers={"User-Agent": HTTP_USER_AGENT})
    with urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as response:
        body = response.read().decode("utf-8", errors="ignore")
    parsed = json.loads(body)
    return parsed if isinstance(parsed, dict) else {}


def _clean_text(value: str) -> str:
    text = unescape(value or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _extract_posting_skills(posting_text: str) -> Set[str]:
    return _extract_terms(_clean_text(posting_text), SKILL_CATALOG)


def _score_real_posting(
    posting_skills: Set[str],
    user_skills: Set[str],
    job_terms: Set[str],
    posting_title: str = "",
    posting_location: str = "",
    preferred_country: str = "",
    level_hint: str = "",
    major_terms: Set[str] | None = None,
    grad_year: int | None = None,
) -> int:
    if not posting_skills:
        return 0

    user_overlap = len(posting_skills & user_skills) / max(len(posting_skills), 1)
    if job_terms:
        job_overlap = len(posting_skills & job_terms) / max(len(job_terms), 1)
    else:
        job_overlap = 0.4

    score = (0.65 * user_overlap + 0.25 * job_overlap) * 100

    title_blob = posting_title.lower()
    location_blob = posting_location.lower()
    if preferred_country and preferred_country.lower() != "remote":
        country_blob = preferred_country.lower()
        if country_blob in location_blob:
            score += 12
        elif "remote" in location_blob:
            score += 8

    if level_hint:
        hint = level_hint.lower()
        if "intern" in hint or "junior" in hint:
            if any(marker in title_blob for marker in SENIORITY_SENIOR_MARKERS):
                score -= 20
            if any(marker in title_blob for marker in SENIORITY_ENTRY_MARKERS):
                score += 10
        elif "mid" in hint and any(marker in title_blob for marker in SENIORITY_ENTRY_MARKERS):
            score -= 6

    if grad_year is not None:
        current_year = datetime.utcnow().year
        if grad_year >= current_year - 1 and any(marker in title_blob for marker in SENIORITY_ENTRY_MARKERS):
            score += 8

    major_terms = major_terms or set()
    if major_terms and any(term in title_blob for term in major_terms):
        score += 6

    return max(0, min(100, round(score)))


def _fetch_remotive_jobs(search_query: str) -> List[Dict[str, Any]]:
    url = f"https://remotive.com/api/remote-jobs?search={quote_plus(search_query)}&limit=25"
    payload = _http_get_json(url)
    jobs = payload.get("jobs") if isinstance(payload, dict) else []
    if not isinstance(jobs, list):
        return []

    postings: List[Dict[str, Any]] = []
    for job in jobs[:25]:
        if not isinstance(job, dict):
            continue
        postings.append(
            {
                "title": _clean_text(str(job.get("title") or "")),
                "company": _clean_text(str(job.get("company_name") or "Unknown")),
                "location": _clean_text(str(job.get("candidate_required_location") or "Remote")),
                "url": str(job.get("url") or "").strip(),
                "source": "Remotive",
                "description": _clean_text(str(job.get("description") or "")),
            }
        )
    return postings


def _fetch_arbeitnow_jobs(search_query: str) -> List[Dict[str, Any]]:
    url = "https://www.arbeitnow.com/api/job-board-api"
    payload = _http_get_json(url)
    jobs = payload.get("data") if isinstance(payload, dict) else []
    if not isinstance(jobs, list):
        return []

    query_words = {
        word for word in re.findall(r"[a-zA-Z0-9\+\.#/-]+", search_query.lower()) if len(word) > 2
    }
    postings: List[Dict[str, Any]] = []
    for job in jobs[:120]:
        if not isinstance(job, dict):
            continue

        title = _clean_text(str(job.get("title") or ""))
        description = _clean_text(str(job.get("description") or ""))
        haystack = f"{title} {description}".lower()

        if query_words and not any(word in haystack for word in query_words):
            continue

        postings.append(
            {
                "title": title,
                "company": _clean_text(str(job.get("company_name") or "Unknown")),
                "location": _clean_text(str(job.get("location") or "Remote / Hybrid")),
                "url": str(job.get("url") or "").strip(),
                "source": "Arbeitnow",
                "description": description,
            }
        )
    return postings


def _location_matches_country(location: str, preferred_country: str) -> bool:
    loc = (location or "").lower()
    if not loc:
        return False

    if any(marker in loc for marker in REMOTE_LOCATION_MARKERS):
        return True

    normalized_country = (preferred_country or "").strip().lower()
    if not normalized_country or normalized_country == "remote":
        return True

    hints = COUNTRY_LOCATION_HINTS.get(normalized_country)
    if hints:
        return any(hint in loc for hint in hints)

    return normalized_country in loc


def _fetch_real_job_postings(
    query_candidates: List[str],
    user_skills: Set[str],
    job_terms: Set[str],
    top_k: int,
    preferred_country: str = "",
    level_hint: str = "",
    major_terms: Set[str] | None = None,
    grad_year: int | None = None,
) -> List[Dict[str, Any]]:

    candidate_postings: List[Dict[str, Any]] = []
    for query in query_candidates:
        for fetcher in (_fetch_remotive_jobs, _fetch_arbeitnow_jobs):
            try:
                candidate_postings.extend(fetcher(query))
            except Exception:
                continue
        if len(candidate_postings) >= max(12, top_k * 4):
            break

    if preferred_country and preferred_country.lower() != "remote":
        country_filtered = [
            posting
            for posting in candidate_postings
            if _location_matches_country(str(posting.get("location") or ""), preferred_country)
        ]
        candidate_postings = country_filtered

    dedup: Dict[str, Dict[str, Any]] = {}
    for posting in candidate_postings:
        url = (posting.get("url") or "").strip()
        title = (posting.get("title") or "").strip().lower()
        company = (posting.get("company") or "").strip().lower()
        key = url or f"{title}|{company}"
        if not key:
            continue

        posting_skills = _extract_posting_skills(
            f"{posting.get('title', '')} {posting.get('description', '')}"
        )
        score = _score_real_posting(
            posting_skills,
            user_skills,
            job_terms,
            posting_title=str(posting.get("title") or ""),
            posting_location=str(posting.get("location") or ""),
            preferred_country=preferred_country,
            level_hint=level_hint,
            major_terms=major_terms,
            grad_year=grad_year,
        )
        if score <= 0:
            continue

        posting["fit_score"] = score
        posting["matched_skills"] = sorted(posting_skills & user_skills)[:5]
        posting["missing_skills"] = sorted((job_terms | posting_skills) - user_skills)[:5]

        existing = dedup.get(key)
        if not existing or score > int(existing.get("fit_score") or 0):
            dedup[key] = posting

    ranked = sorted(dedup.values(), key=lambda item: int(item.get("fit_score") or 0), reverse=True)
    if not ranked and candidate_postings:
        fallback: List[Dict[str, Any]] = []
        seen: Set[str] = set()
        for posting in candidate_postings:
            url = (posting.get("url") or "").strip()
            title = (posting.get("title") or "").strip()
            company = (posting.get("company") or "").strip()
            key = url or f"{title.lower()}|{company.lower()}"
            if not key or key in seen:
                continue
            seen.add(key)

            fallback.append(
                {
                    "title": title,
                    "company": company or "Unknown",
                    "location": (posting.get("location") or "Remote").strip(),
                    "url": url,
                    "source": (posting.get("source") or "Job Feed").strip(),
                    "fit_score": 10,
                    "matched_skills": [],
                    "missing_skills": [],
                }
            )
            if len(fallback) >= max(3, min(12, top_k * 2)):
                break
        return fallback

    for item in ranked:
        item.pop("description", None)
    return ranked[: max(3, min(12, top_k * 2))]


def simulate_job_match(job_description: str, top_k: int = 5) -> Dict[str, Any]:
    portfolio = build_portfolio_model()
    portfolio_skill_counter, role_keywords = _collect_portfolio_signals(portfolio)
    saved_skills = [
        _normalize_term(skill)
        for skill in _load_saved_skills()
        if _normalize_term(skill)
    ]

    if saved_skills:
        skill_counter = Counter(saved_skills)
        user_skills = set(saved_skills)
    else:
        skill_counter = portfolio_skill_counter
        user_skills = set(skill_counter.keys())

    user_prefs = _load_user_preferences_snapshot()

    required, preferred, extracted = _extract_job_requirements(job_description)

    matched_required = sorted(required & user_skills)
    matched_preferred = sorted(preferred & user_skills)

    missing_required = sorted(required - user_skills)
    missing_preferred = sorted(preferred - user_skills)

    required_coverage = len(matched_required) / max(len(required), 1)
    preferred_coverage = len(matched_preferred) / max(len(preferred), 1)

    projects_count = int((portfolio.get("overview") or {}).get("total_projects") or 0)
    depth_factor = min(projects_count / 6, 1.0)

    if extracted and (matched_required or matched_preferred):
        match_score = round((0.7 * required_coverage + 0.2 * preferred_coverage + 0.1 * depth_factor) * 100)
    else:
        match_score = 0

    recommendations = _rank_recommended_jobs(
        user_skills=user_skills,
        job_required=required,
        job_preferred=preferred,
        role_keywords=role_keywords,
        top_k=top_k,
    )

    level = _experience_hint(portfolio)
    for rec in recommendations:
        rec["search_query"] = f"{rec['title']} {level}"

    strengths = [skill for skill, _count in skill_counter.most_common(8)]

    return {
        "status": "ok",
        "match_score": max(0, min(100, match_score)),
        "experience_level_hint": level,
        "extracted_job_skills": sorted(extracted),
        "matched_skills": sorted(set(matched_required + matched_preferred)),
        "missing_skills": sorted(set(missing_required + missing_preferred)),
        "required_skills": sorted(required),
        "preferred_skills": sorted(preferred),
        "strengths": strengths,
        "recommended_jobs": recommendations,
        "real_job_postings": [],
    }


def recommend_jobs_from_profile(
    top_k: int = 12,
    work_types: List[str] | None = None,
    selected_skills: List[str] | None = None,
    easy_apply: bool = True,
    posted_within_days: int = 7,
) -> Dict[str, Any]:
    portfolio = build_portfolio_model()
    skill_counter, _role_keywords = _collect_portfolio_signals(portfolio)
    user_skills = set(skill_counter.keys())
    user_prefs = _load_user_preferences_snapshot()

    level = _experience_hint(portfolio)
    major, grad_year = _extract_major_and_graduation(user_prefs)
    preferred_country = _infer_country_from_education(user_prefs)
    saved_skills = _load_saved_skills()

    query_candidates = _build_profile_queries(
        user_skills=user_skills,
        prioritized_skills=[skill for skill, _count in skill_counter.most_common(12)],
        selected_skills=selected_skills,
        user_prefs=user_prefs,
        level_hint=level,
    )

    linkedin_links = _build_linkedin_search_links(
        query_candidates,
        preferred_country,
        level,
        work_types=work_types,
        easy_apply=easy_apply,
        posted_within_days=posted_within_days,
    )
    max_links = max(3, min(8, int(top_k or 5)))

    return {
        "status": "ok",
        "profile": {
            "target_level": level,
            "country": preferred_country,
            "major": major,
            "graduation_year": grad_year,
            "top_skills": [skill for skill, _count in skill_counter.most_common()],
            "saved_skills": saved_skills,
            "industry": user_prefs.get("industry") or "",
            "job_title": user_prefs.get("job_title") or "",
        },
        "real_job_postings": [],
        "linkedin_search_links": linkedin_links[:max_links],
    }
