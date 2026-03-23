from collections import defaultdict
from app.data.db import get_connection
import sqlite3
from typing import Any, DefaultDict, Dict, List, Tuple, Optional
from datetime import datetime
import json

class ResumeServiceError(Exception):
    pass

class ResumeNotFoundError(ResumeServiceError):
    pass

class ResumePersistenceError(ResumeServiceError):
    pass

def format_dates(start: str, end: str) -> str:
    """Format dates shown to months and year"""
    try:
        s = datetime.fromisoformat(start).strftime("%b %Y")
        e = datetime.fromisoformat(end).strftime("%b %Y")
        return f"{s} – {e}"
    except Exception:
        return ""

def parse_education_details(education_details_json: Optional[str], fallback_education: str = "", fallback_job_title: str = "") -> List[Dict[str, Any]]:
    """
    Parse education_details JSON and return a list of education entries.
    Falls back to legacy education/job_title fields if education_details is empty.
    """
    if education_details_json:
        try:
            details = json.loads(education_details_json)
            if isinstance(details, list) and len(details) > 0:
                # Map education_details to the expected format
                result = []
                for entry in details:
                    # Handle date formatting
                    start = entry.get("start_date", "")
                    end = entry.get("end_date", "")
                    
                    # Format dates if both are present
                    if start and end:
                        dates = format_dates(start, end)
                    elif start:
                        # Year-only format
                        try:
                            dates = f"{datetime.fromisoformat(start).strftime('%Y')} – Present"
                        except:
                            dates = f"{start} – Present"
                    else:
                        dates = ""
                    
                    result.append({
                        "school": entry.get("institution", ""),
                        "degree": entry.get("degree", ""),
                        "dates": dates,
                        "gpa": str(entry.get("gpa", "")) if entry.get("gpa") else ""
                    })
                return result
        except (json.JSONDecodeError, TypeError, KeyError):
            pass
    
    # Fallback to legacy fields if no valid education_details
    if fallback_education or fallback_job_title:
        return [{
            "school": fallback_education,
            "degree": fallback_job_title,
            "dates": "",
            "gpa": ""
        }]
    
    return []


def load_awards(cursor: sqlite3.Cursor, resume_id: int) -> List[Dict[str, Any]]:
    """Load awards/honours for a saved tailored resume."""
    cursor.execute(
        "SELECT awards FROM RESUME_AWARDS WHERE resume_id = ? LIMIT 1",
        (resume_id,),
    )
    row = cursor.fetchone()
    if not row:
        return []

    awards_raw = row[0]
    if not awards_raw:
        return []

    try:
        parsed = json.loads(awards_raw) if isinstance(awards_raw, str) else awards_raw
        if isinstance(parsed, list):
            # Keep only dict entries to avoid template renderer issues.
            return [a for a in parsed if isinstance(a, dict)]
    except (json.JSONDecodeError, TypeError):
        pass

    return []


def load_work_experience(cursor: sqlite3.Cursor, resume_id: int) -> List[Dict[str, Any]]:
    """Load work experience entries for a saved tailored resume."""
    cursor.execute(
        "SELECT work_experience FROM RESUME_WORK_EXPERIENCE WHERE resume_id = ? LIMIT 1",
        (resume_id,),
    )
    row = cursor.fetchone()
    if not row:
        return []

    work_raw = row[0]
    if not work_raw:
        return []

    try:
        parsed = json.loads(work_raw) if isinstance(work_raw, str) else work_raw
        if isinstance(parsed, list):
            # Keep only dict entries to avoid template renderer issues.
            return [e for e in parsed if isinstance(e, dict)]
    except (json.JSONDecodeError, TypeError):
        pass

    return []
    
def load_user(cursor: sqlite3.Cursor) -> Dict[str, Any]:
    """Return user info dict from USER_PREFERENCES."""
    try:
        try:
            # Extended query — includes industry, personal_summary, linkedin, profile_picture_path
            cursor.execute(
                """
                SELECT name, email, github_user, education, job_title, education_details,
                       industry, personal_summary, linkedin, profile_picture_path
                FROM USER_PREFERENCES
                ORDER BY updated_at DESC LIMIT 1
                """
            )
        except sqlite3.OperationalError:
            try:
                # Fallback: without profile_picture_path (older schema)
                cursor.execute(
                    """
                    SELECT name, email, github_user, education, job_title, education_details,
                           industry, personal_summary, linkedin
                    FROM USER_PREFERENCES
                    ORDER BY updated_at DESC LIMIT 1
                    """
                )
            except sqlite3.OperationalError:
                try:
                    # Fallback: without linkedin (older schema)
                    cursor.execute(
                        """
                        SELECT name, email, github_user, education, job_title, education_details,
                               industry, personal_summary
                        FROM USER_PREFERENCES
                        ORDER BY updated_at DESC LIMIT 1
                        """
                    )
                except sqlite3.OperationalError:
                    # Fallback for oldest DB schemas without industry/personal_summary
                    cursor.execute(
                        """
                        SELECT name, email, github_user, education, job_title, education_details
                        FROM USER_PREFERENCES
                        ORDER BY updated_at DESC LIMIT 1
                        """
                    )
        row = cursor.fetchone()
    except sqlite3.Error as e:
        raise ResumeServiceError("Failed loading user") from e

    if row is None:
        return {
            "name": "",
            "email": "",
            "links": [],
            "education": "",
            "job_title": "",
            "education_details": None,
            "github_user": None,
            "industry": None,
            "personal_summary": None,
            "profile_picture_path": None,
        }

    links = []

    if row[2]:  # github_user
        links.append({
            "label": "GitHub",
            "url": f"https://github.com/{row[2]}"
        })

    linkedin = row[8] if len(row) > 8 else None
    if linkedin:
        links.append({
            "label": "LinkedIn",
            "url": linkedin if linkedin.startswith("http") else f"https://{linkedin}"
        })

    return {
        "name": row[0],
        "email": row[1],
        "links": links,
        "education": row[3],
        "job_title": row[4],
        "education_details": row[5],  # JSON string or None
        "github_user": row[2],
        "industry": row[6] if len(row) > 6 else None,
        "personal_summary": row[7] if len(row) > 7 else None,
        "linkedin": linkedin,
        "profile_picture_path": row[9] if len(row) > 9 else None,
    }

def load_projects(cursor: sqlite3.Cursor, project_ids: Optional[List[str]] = None) -> List[Tuple[str, str, float, str, str]]:
    """Return projects with signature, name, score, created_at, last_modified.
    If project_ids are provided, return only those projects.
    """
    if project_ids:
        # Build a dynamic IN clause safely
        placeholders = ",".join(["?"] * len(project_ids))
        query = f"""
            SELECT project_signature, name, score, created_at, last_modified
            FROM PROJECT
            WHERE project_signature IN ({placeholders})
            ORDER BY last_modified DESC
        """
        cursor.execute(query, project_ids)
        return cursor.fetchall()
    else:
        cursor.execute(
            """
            SELECT project_signature, name, score, created_at, last_modified
            FROM PROJECT
            ORDER BY last_modified DESC
            """
        )
        return cursor.fetchall()

def load_resume_bullets(cursor: sqlite3.Cursor) -> DefaultDict[int, List[str]]:
    """Return mapping of project_id to resume summary bullets."""
    cursor.execute("""
        SELECT project_id, summary_text
        FROM RESUME_SUMMARY
    """)
    bullets = defaultdict(list)
    for pid, text in cursor.fetchall():
        # Parse JSON if summary_text is stored as JSON array
        try:
            parsed = json.loads(text) if isinstance(text, str) and text.startswith('[') else [text]
            bullets[pid].extend(parsed)
        except json.JSONDecodeError:
            bullets[pid].append(text)
    return bullets

def load_skills(cursor: sqlite3.Cursor) -> DefaultDict[int, List[str]]:
    """Return mapping of project_id to list of skills."""
    cursor.execute("""
        SELECT skill, project_id
        FROM SKILL_ANALYSIS
    """)
    skills_by_project = defaultdict(list)

    for skill, project_id in cursor.fetchall():
        skills_by_project[project_id].append(skill)

    return skills_by_project

def limit_skills(skills: List[str], max_count: int = 5) -> List[str]:
    """Return up to max_count unique skills preserving order."""
    seen = set()
    limited = []

    for skill in skills:
        if skill not in seen:
            seen.add(skill)
            limited.append(skill)
        if len(limited) == max_count:
            break

    return limited


def bucket_skills_for_evidence(
    cursor: sqlite3.Cursor,
    evidence_project_ids: List[str],
    allowed_skills: Optional[List[str]] = None,
) -> Dict[str, List[str]]:
    """
    Buckets evidence-based resume skills into recruiter-friendly groups.

    Bucket logic (based on distinct skill count, n):
    - if n <= 10: Proficient = all skills; Familiar = []
    - if 11 <= n <= 18: Proficient = top 7; Familiar = next up to 8
    - if n > 18: Proficient = top 8; Familiar = next up to 8
    """
    if not evidence_project_ids:
        return {"Proficient": [], "Familiar": []}

    allowed_set = set(allowed_skills) if allowed_skills is not None else None

    placeholders = ",".join(["?"] * len(evidence_project_ids))
    cursor.execute(
        f"""
        SELECT
            s.skill AS skill,
            COUNT(DISTINCT s.project_id) AS frequency,
            MAX(COALESCE(s.date, p.last_modified)) AS latest_use
        FROM SKILL_ANALYSIS s
        JOIN PROJECT p ON p.project_signature = s.project_id
        WHERE s.project_id IN ({placeholders})
        GROUP BY s.skill
        ORDER BY frequency DESC, latest_use DESC, s.skill ASC
        """,
        evidence_project_ids,
    )

    ordered_skills: List[str] = []
    for skill, _frequency, _latest_use in cursor.fetchall():
        if allowed_set is not None and skill not in allowed_set:
            continue
        ordered_skills.append(skill)

    # If legacy resume-level skills contain entries not present in the evidence set,
    # keep them (append to the end) so we don't silently drop user edits.
    if allowed_skills is not None:
        ordered_set = set(ordered_skills)
        for skill in allowed_skills:
            if skill not in ordered_set:
                ordered_skills.append(skill)

    n = len(ordered_skills)
    if n <= 10:
        return {"Proficient": ordered_skills, "Familiar": []}
    if 11 <= n <= 18:
        return {"Proficient": ordered_skills[:7], "Familiar": ordered_skills[7:15]}
    return {"Proficient": ordered_skills[:8], "Familiar": ordered_skills[8:16]}

def load_resume_projects(cursor: sqlite3.Cursor, resume_id: int) -> List[Tuple[str, Optional[str], Optional[str], Optional[str], Optional[str], int, Optional[str], Optional[str], Optional[str]]]:
    """Get all projects associated with the given resume_id. Uses LEFT JOIN so rows remain when PROJECT is deleted (snapshot)."""
    cursor.execute("""
        SELECT
            rp.project_id,
            rp.project_name,
            rp.start_date,
            rp.end_date,
            rp.skills,
            rp.bullets,
            rp.display_order,
            p.name,
            p.created_at,
            p.last_modified
        FROM RESUME_PROJECT rp
        LEFT JOIN PROJECT p ON p.project_signature = rp.project_id
        WHERE rp.resume_id = ?
        ORDER BY rp.display_order
    """, (resume_id,))
    return cursor.fetchall()

def load_edited_skills(cursor: sqlite3.Cursor, resume_id:int) -> Optional[Tuple[str]]:
    """ Get edited all skills if present """
    cursor.execute("SELECT skills FROM RESUME_SKILLS WHERE resume_id = ? LIMIT 1", (resume_id,))
    return cursor.fetchone()

def load_saved_resume(resume_id:int) ->Dict[str,Any]:
    """Loads a saved resume, merges base bullets with edited versions"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        user = load_user(cursor)
        skills_map = load_skills(cursor)

        # Get edited resume and display order
        rows = load_resume_projects(cursor, resume_id)
        
        if not rows:
            raise ResumeNotFoundError(f"Resume {resume_id} not found")
        
        project_ids = [r[0] for r in rows]
        

        # Get original bullets
        bullets_map = defaultdict(list)
        if project_ids:
            placeholders = ",".join(["?"] * len(project_ids))
            cursor.execute(f"""
                SELECT project_id, summary_text
                FROM RESUME_SUMMARY
                WHERE project_id IN ({placeholders})
            """, project_ids)

            for pid, text in cursor.fetchall():
                # Parse JSON if summary_text is stored as JSON array
                try:
                    parsed = json.loads(text) if isinstance(text, str) and text.startswith('[') else [text]
                    bullets_map[pid].extend(parsed)
                except json.JSONDecodeError:
                    bullets_map[pid].append(text)

        row = load_edited_skills(cursor, resume_id)
        if row and row[0]:
            edited = json.loads(row[0])
            # New format: persisted bucket dict.
            if isinstance(edited, dict):
                all_skills_buckets = {
                    "Proficient": list(edited.get("Proficient", []) or []),
                    "Familiar": list(edited.get("Familiar", []) or []),
                }
            # Legacy format: persisted flat list of skills.
            elif isinstance(edited, list):
                all_skills_buckets = bucket_skills_for_evidence(
                    cursor=cursor,
                    evidence_project_ids=project_ids,
                    allowed_skills=edited,
                )
            else:
                all_skills_buckets = bucket_skills_for_evidence(
                    cursor=cursor,
                    evidence_project_ids=project_ids,
                    allowed_skills=None,
                )
        else:
            # No persisted resume-level skills: bucket based on evidence.
            all_skills_buckets = bucket_skills_for_evidence(
                cursor=cursor,
                evidence_project_ids=project_ids,
                allowed_skills=None,
            )

        projects = []
        for (
            pid,
            override_name,
            start,
            end,
            override_skills,
            override_bullets,
            _order,
            base_name,
            created_at,
            last_modified,
        ) in rows:
            if override_skills:
                skills = json.loads(override_skills) if isinstance(override_skills, str) else (override_skills or [])
            else:
                skills = skills_map.get(pid, [])
            # Limit to 5 for display
            limited_skills = skills[:5]

            # Parse bullets: stored as JSON in DB, so decode if string
            if override_bullets:
                bullets_list = json.loads(override_bullets) if isinstance(override_bullets, str) else (override_bullets or [])
            else:
                bullets_list = bullets_map.get(pid, [])

            title = override_name or base_name or "(Removed project)"
            start_val = start or created_at or ""
            end_val = end or last_modified or ""
            projects.append({
                "project_id": pid,
                "title": title,
                "dates": format_dates(start_val, end_val) if start_val and end_val else "",
                "start_date": start_val,
                "end_date": end_val,
                "skills": limited_skills,
                "bullets": bullets_list,
            })
        
        # Parse education details
        education_list = parse_education_details(
            user.get("education_details"),
            fallback_education=user.get("education", ""),
            fallback_job_title=user.get("job_title", "")
        )
        
        # Parse awards/honours (tailored-resume only)
        awards_list = load_awards(cursor, resume_id)
        if resume_id == 1:
            # Master resume should never include awards.
            awards_list = []

        work_experience_list = load_work_experience(cursor, resume_id)
        if resume_id == 1:
            # Master resume should never include work experience.
            work_experience_list = []
        
        return {
            "name": user["name"],
            "email": user["email"],
            "links": user["links"],
            "education": education_list,
            "awards": awards_list,
            "work_experience": work_experience_list,
            "skills": {
                "Proficient": all_skills_buckets["Proficient"],
                "Familiar": all_skills_buckets["Familiar"],
            },
            "projects": projects,
            "personal_summary": user.get("personal_summary"),
        }
    except sqlite3.Error as e:
        raise ResumeServiceError("Failed loading saved resume") from e
    finally:
        conn.close()

    
def build_resume_model(project_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """Return assembled resume model built from the database.
    If project_ids are provided, include only those projects in the list.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        user = load_user(cursor)
        projects_raw = load_projects(cursor, project_ids=project_ids)
        bullets_map = load_resume_bullets(cursor)
        skills_map = load_skills(cursor)

        projects = []

        selected_ids = set(pid for pid, *_ in projects_raw)

        for pid, name, score, created_at, last_modified in projects_raw:
            raw_skills = skills_map.get(pid, [])
            limited_skills = limit_skills(raw_skills, max_count=5)

            projects.append({
                "title": name,
                "dates": format_dates(created_at, last_modified),
                "start_date": created_at or "",
                "end_date": last_modified or "",
                "skills": ", ".join(limited_skills),
                "bullets": bullets_map.get(pid, [])
            })

        all_skills_buckets = bucket_skills_for_evidence(
            cursor=cursor,
            evidence_project_ids=list(selected_ids),
            allowed_skills=None,
        )

        # Parse education details
        education_list = parse_education_details(
            user.get("education_details"),
            fallback_education=user.get("education", ""),
            fallback_job_title=user.get("job_title", "")
        )

        return {
            "name": user["name"],
            "email": user["email"],
            "links": user["links"],
            "education": education_list,
            # Awards are tailored-resume only; preview/master don't load them.
            "awards": [],
            "work_experience": [],
            "skills": {
                "Proficient": all_skills_buckets["Proficient"],
                "Familiar": all_skills_buckets["Familiar"],
            },
            "projects": projects,
            "personal_summary": user.get("personal_summary"),
        }
    except sqlite3.Error as e:
        raise ResumeServiceError("Failed building resume model") from e
    finally:
        conn.close()

def create_resume(name: str) -> int:
    """Create a Resume and if no name is provided, set a default name"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO RESUME (name) VALUES (?)",
        (name,)
    )

    resume_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return resume_id

def list_resumes() -> List[Dict[str, Any]]:
    """Return list of resumes for sidebar: id, name, is_master. Master is id=1."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM RESUME ORDER BY id")
        rows = cursor.fetchall()
        return [
            {"id": r[0], "name": (r[1] or f"Resume-{r[0]}").strip() or f"Resume-{r[0]}", "is_master": r[0] == 1}
            for r in rows
        ]
    except sqlite3.Error as e:
        raise ResumeServiceError("Failed listing resumes") from e
    finally:
        conn.close()

def resume_exists(resume_id: int) -> bool:
    """Method to check if specified resume ID exists (precaution)"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM RESUME WHERE id = ?", (resume_id,))
        exists = cursor.fetchone() is not None
        return exists
    except sqlite3.Error as e:
        raise ResumeServiceError("Failed checking resume existence") from e
    finally:
        conn.close()


def duplicate_resume(source_id: int) -> int:
    """Clone a resume (including master id=1) into a new row with copied projects and optional sidecar tables."""
    if not resume_exists(source_id):
        raise ResumeNotFoundError(f"Resume with ID {source_id} not found")

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name FROM RESUME WHERE id = ?", (source_id,))
        src_row = cursor.fetchone()
        if not src_row:
            raise ResumeNotFoundError(f"Resume with ID {source_id} not found")
        raw_name = (src_row[0] or "").strip()
        base = raw_name if raw_name else f"Resume-{source_id}"
        new_name = f"{base} copy"

        cursor.execute("INSERT INTO RESUME (name) VALUES (?)", (new_name,))
        new_id = cursor.lastrowid

        cursor.execute(
            """
            SELECT project_id, project_name, start_date, end_date, skills, bullets, display_order
            FROM RESUME_PROJECT
            WHERE resume_id = ?
            ORDER BY display_order
            """,
            (source_id,),
        )
        for (
            project_id,
            project_name,
            start_date,
            end_date,
            skills,
            bullets,
            display_order,
        ) in cursor.fetchall():
            cursor.execute(
                """
                INSERT INTO RESUME_PROJECT (
                    resume_id, project_id, project_name, start_date, end_date,
                    skills, bullets, display_order
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    new_id,
                    project_id,
                    project_name,
                    start_date,
                    end_date,
                    skills,
                    bullets,
                    display_order,
                ),
            )

        cursor.execute(
            "SELECT skills FROM RESUME_SKILLS WHERE resume_id = ? LIMIT 1",
            (source_id,),
        )
        sk_row = cursor.fetchone()
        if sk_row and sk_row[0]:
            cursor.execute(
                "INSERT INTO RESUME_SKILLS (resume_id, skills) VALUES (?, ?)",
                (new_id, sk_row[0]),
            )

        cursor.execute(
            "SELECT awards FROM RESUME_AWARDS WHERE resume_id = ? LIMIT 1",
            (source_id,),
        )
        aw_row = cursor.fetchone()
        if aw_row and aw_row[0]:
            cursor.execute(
                "INSERT INTO RESUME_AWARDS (resume_id, awards) VALUES (?, ?)",
                (new_id, aw_row[0]),
            )

        cursor.execute(
            "SELECT work_experience FROM RESUME_WORK_EXPERIENCE WHERE resume_id = ? LIMIT 1",
            (source_id,),
        )
        we_row = cursor.fetchone()
        if we_row and we_row[0]:
            cursor.execute(
                "INSERT INTO RESUME_WORK_EXPERIENCE (resume_id, work_experience) VALUES (?, ?)",
                (new_id, we_row[0]),
            )

        conn.commit()
        return new_id
    except sqlite3.Error as e:
        conn.rollback()
        raise ResumePersistenceError("Failed to duplicate resume") from e
    finally:
        conn.close()


def rename_resume(resume_id: int, name: str) -> None:
    """Rename a saved resume. Master resume (id=1) cannot be renamed."""
    trimmed = (name or "").strip()
    if not trimmed:
        raise ResumePersistenceError("Resume name cannot be empty")
    if resume_id == 1:
        raise ResumePersistenceError("Cannot rename the Master Resume")
    if not resume_exists(resume_id):
        raise ResumeNotFoundError(f"Resume with ID {resume_id} not found")

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE RESUME SET name = ? WHERE id = ?", (trimmed, resume_id))
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise ResumePersistenceError("Failed to rename resume") from e
    finally:
        conn.close()


def save_resume_edits(resume_id: int, payload: dict):
    """ Save or update edits made to the resume in the DB """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Update resume-level skills (if provided)
        if "skills" in payload:
            skills_payload = payload["skills"]
            if isinstance(skills_payload, dict):
                # Normalize to { Proficient: [...], Familiar: [...] }
                normalized = {
                    "Proficient": [
                        str(s).strip()
                        for s in (skills_payload.get("Proficient", []) or [])
                        if str(s).strip()
                    ],
                    "Familiar": [
                        str(s).strip()
                        for s in (skills_payload.get("Familiar", []) or [])
                        if str(s).strip()
                    ],
                }
                skills_payload = normalized
            cursor.execute("""
                INSERT INTO RESUME_SKILLS (resume_id, skills)
                VALUES (?, ?)
                ON CONFLICT(resume_id)
                DO UPDATE SET
                    skills = excluded.skills,
                    updated_at = CURRENT_TIMESTAMP
            """, (resume_id, json.dumps(skills_payload)))

        # Update tailored-resume awards (if provided)
        if "awards" in payload:
            awards_payload = payload.get("awards") or []

            normalized_awards: List[Dict[str, Any]] = []
            if isinstance(awards_payload, list):
                for a in awards_payload:
                    if not isinstance(a, dict):
                        continue
                    title = str(a.get("title", "")).strip()
                    if not title:
                        continue
                    issuer = str(a.get("issuer", "")).strip() if a.get("issuer") else ""
                    date = str(a.get("date", "")).strip() if a.get("date") else ""

                    details_raw = a.get("details", []) or []
                    details: List[str] = []
                    if isinstance(details_raw, list):
                        details = [str(d).strip() for d in details_raw if str(d).strip()]
                    elif isinstance(details_raw, str):
                        # Accept newline-separated details for robustness.
                        details = [line.strip() for line in details_raw.splitlines() if line.strip()]

                    normalized_awards.append(
                        {
                            "title": title,
                            "issuer": issuer,
                            "date": date,
                            "details": details,
                        }
                    )

            cursor.execute(
                """
                INSERT INTO RESUME_AWARDS (resume_id, awards)
                VALUES (?, ?)
                ON CONFLICT(resume_id)
                DO UPDATE SET
                    awards = excluded.awards,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (resume_id, json.dumps(normalized_awards)),
            )

        # Update tailored-resume work experience (if provided)
        if "work_experience" in payload:
            work_payload = payload.get("work_experience") or []

            normalized_work: List[Dict[str, Any]] = []
            if isinstance(work_payload, list):
                for e in work_payload:
                    if not isinstance(e, dict):
                        continue
                    role = str(e.get("role", "")).strip()
                    if not role:
                        continue

                    company = str(e.get("company", "")).strip() if e.get("company") else ""
                    start_date = str(e.get("start_date", "")).strip() if e.get("start_date") else ""
                    end_date = str(e.get("end_date", "")).strip() if e.get("end_date") else ""

                    details_raw = e.get("details", []) or []
                    details: List[str] = []
                    if isinstance(details_raw, list):
                        details = [str(d).strip() for d in details_raw if str(d).strip()]
                    elif isinstance(details_raw, str):
                        # Accept newline-separated details for robustness.
                        details = [line.strip() for line in details_raw.splitlines() if line.strip()]

                    normalized_work.append(
                        {
                            "role": role,
                            "company": company,
                            "start_date": start_date,
                            "end_date": end_date,
                            "details": details,
                        }
                    )

            cursor.execute(
                """
                INSERT INTO RESUME_WORK_EXPERIENCE (resume_id, work_experience)
                VALUES (?, ?)
                ON CONFLICT(resume_id)
                DO UPDATE SET
                    work_experience = excluded.work_experience,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (resume_id, json.dumps(normalized_work)),
            )

        for project in payload.get("projects", []):
            cursor.execute("""
                INSERT INTO RESUME_PROJECT (
                    resume_id,
                    project_id,
                    project_name,
                    start_date,
                    end_date,
                    skills,
                    bullets,
                    display_order
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(resume_id, project_id)
                DO UPDATE SET
                    project_name  = COALESCE(excluded.project_name, RESUME_PROJECT.project_name),
                    start_date    = COALESCE(excluded.start_date, RESUME_PROJECT.start_date),
                    end_date      = COALESCE(excluded.end_date, RESUME_PROJECT.end_date),
                    skills        = COALESCE(excluded.skills, RESUME_PROJECT.skills),
                    bullets       = COALESCE(excluded.bullets, RESUME_PROJECT.bullets),
                    display_order = COALESCE(excluded.display_order, RESUME_PROJECT.display_order)
            """, (
                resume_id,
                project["project_id"],
                project.get("project_name"),
                project.get("start_date"),
                project.get("end_date"),
                json.dumps(project["skills"]) if "skills" in project else None,
                json.dumps(project["bullets"]) if "bullets" in project else None,
                project.get("display_order")
            ))

        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise ResumePersistenceError("Invalid resume edit data") from e
    except sqlite3.Error as e:
        conn.rollback()
        raise ResumePersistenceError("Failed to save resume edits") from e
    finally:
        conn.close()


def save_personal_summary(summary: str) -> None:
    """Persist the personal_summary back to USER_PREFERENCES (user_id=1)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO USER_PREFERENCES (user_id, personal_summary, updated_at)
            VALUES (1, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                personal_summary = excluded.personal_summary,
                updated_at = CURRENT_TIMESTAMP
            """,
            (summary,),
        )
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise ResumePersistenceError("Failed to save personal summary") from e
    finally:
        conn.close()


def snapshot_project_into_resume_rows(cursor: sqlite3.Cursor, project_signature: str) -> None:
    """Snapshot project data into all RESUME_PROJECT rows that reference this project.
    Call this before deleting the project so tailored resumes keep the project's data.
    Only fills columns that are currently NULL, so existing user edits on the tailored
    resume are preserved."""
    cursor.execute(
        "SELECT name, created_at, last_modified FROM PROJECT WHERE project_signature = ?",
        (project_signature,),
    )
    row = cursor.fetchone()
    if not row:
        return
    name, created_at, last_modified = row
    cursor.execute("SELECT summary_text FROM RESUME_SUMMARY WHERE project_id = ?", (project_signature,))
    bullets_raw = cursor.fetchall()
    bullets_list: List[str] = []
    for (text,) in bullets_raw:
        try:
            parsed = json.loads(text) if isinstance(text, str) and text.strip().startswith("[") else [text]
            bullets_list.extend(parsed)
        except (json.JSONDecodeError, TypeError):
            if text:
                bullets_list.append(str(text))
    bullets_json = json.dumps(bullets_list) if bullets_list else None
    cursor.execute("SELECT skill FROM SKILL_ANALYSIS WHERE project_id = ?", (project_signature,))
    skills = [r[0] for r in cursor.fetchall()]
    skills_json = json.dumps(skills) if skills else None
    cursor.execute(
        """
        UPDATE RESUME_PROJECT
        SET project_name = COALESCE(project_name, ?),
            start_date = COALESCE(start_date, ?),
            end_date = COALESCE(end_date, ?),
            skills = COALESCE(skills, ?),
            bullets = COALESCE(bullets, ?)
        WHERE project_id = ?
        """,
        (name, created_at, last_modified, skills_json, bullets_json, project_signature),
    )


def attach_projects_to_resume(resume_id: int, project_ids: list[str]):
    """Attach projects to a resume with display_order set by last_modified DESC (newest first)."""
    conn = get_connection()
    cursor = conn.cursor()

    if not project_ids:
        conn.close()
        return

    # Resolve each project_id to its last_modified from PROJECT
    placeholders = ",".join(["?"] * len(project_ids))
    cursor.execute(
        f"""
        SELECT project_signature, last_modified
        FROM PROJECT
        WHERE project_signature IN ({placeholders})
        """,
        project_ids,
    )
    date_map = {row[0]: row[1] for row in cursor.fetchall()}

    # Sort by last_modified DESC (newest first). project_ids come from the app's project list, so they exist in PROJECT.
    ordered_ids = sorted(
        project_ids,
        key=lambda p: date_map.get(p) or "",
        reverse=True,
    )

    for index, project_id in enumerate(ordered_ids):
        cursor.execute(
            """
            INSERT INTO RESUME_PROJECT (
                resume_id,
                project_id,
                display_order
            )
            VALUES (?, ?, ?)
        """, (
            resume_id,
            project_id,
            index + 1  # 1-based ordering
        ))

    conn.commit()
    conn.close()


def add_projects_to_resume(resume_id: int, project_ids: list[str]) -> None:
    """Append projects to an existing resume with display_order after current max.
    Skips project_ids already on the resume (idempotent). New projects are ordered
    by last_modified DESC (newest first).
    Raises ResumeNotFoundError if the resume does not exist.
    Raises ResumePersistenceError if resume_id is the master resume (1).
    """
    if resume_id == 1:
        raise ResumePersistenceError("Cannot add projects to the Master Resume")
    if not resume_exists(resume_id):
        raise ResumeNotFoundError(f"Resume with ID {resume_id} not found")
    if not project_ids:
        return

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT project_id, display_order FROM RESUME_PROJECT WHERE resume_id = ?",
            (resume_id,),
        )
        existing = {row[0]: row[1] for row in cursor.fetchall()}
        max_order = max(existing.values(), default=0)
        new_ids = [pid for pid in project_ids if pid not in existing]
        if not new_ids:
            return

        placeholders = ",".join(["?"] * len(new_ids))
        cursor.execute(
            f"""
            SELECT project_signature, last_modified
            FROM PROJECT
            WHERE project_signature IN ({placeholders})
            """,
            new_ids,
        )
        date_map = {row[0]: row[1] for row in cursor.fetchall()}
        ordered_ids = sorted(
            new_ids,
            key=lambda p: date_map.get(p) or "",
            reverse=True,
        )

        for index, project_id in enumerate(ordered_ids):
            cursor.execute(
                """
                INSERT INTO RESUME_PROJECT (resume_id, project_id, display_order)
                VALUES (?, ?, ?)
                """,
                (resume_id, project_id, max_order + 1 + index),
            )
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise ResumePersistenceError(
            "One or more project IDs are invalid or already on this resume"
        ) from e
    except sqlite3.Error as e:
        conn.rollback()
        raise ResumeServiceError("Failed to add projects to resume") from e
    finally:
        conn.close()


def remove_project_from_resume(resume_id: int, project_id: str) -> None:
    """Remove a project from a resume (delete from RESUME_PROJECT).
    Does not delete the project from PROJECT table.
    Raises ResumeNotFoundError if the resume does not exist.
    No error if the project was not attached to this resume (idempotent).
    """
    if not resume_exists(resume_id):
        raise ResumeNotFoundError(f"Resume with ID {resume_id} not found")
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM RESUME_PROJECT WHERE resume_id = ? AND project_id = ?",
            (resume_id, project_id),
        )
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise ResumeServiceError("Failed to remove project from resume") from e
    finally:
        conn.close()