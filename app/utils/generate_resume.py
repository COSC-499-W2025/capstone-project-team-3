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
    
def load_user(cursor: sqlite3.Cursor) -> Dict[str, Any]:
    """Return user info dict from USER_PREFERENCES."""
    try:
        cursor.execute(
            """
            SELECT name, email, github_user, education, job_title
            FROM USER_PREFERENCES
            ORDER BY updated_at
            DESC LIMIT 1
            """
        )
        row = cursor.fetchone()
    except sqlite3.Error as e:
        raise ResumeServiceError("Failed loading user") from e

    links = [] #Placeholder for if we want to incorporate more links like LinkedIn, Portfolio,...

    if row[2]:  # github_user
        links.append({
            "label": "GitHub",
            "url": f"https://github.com/{row[2]}"
        })
        

    return {
        "name": row[0],
        "email": row[1],
        "links": links,
        "education": row[3],
        "job_title": row[4],
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
            ORDER BY score DESC
        """
        cursor.execute(query, project_ids)
        return cursor.fetchall()
    else:
        cursor.execute(
            """
            SELECT project_signature, name, score, created_at, last_modified
            FROM PROJECT
            ORDER BY score DESC
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

def load_resume_projects(cursor: sqlite3.Cursor, resume_id:int) -> List[Tuple[int, Optional[str],Optional[str],Optional[str],Optional[str],int,str,str,str]]:
    """Get all projects associated with the given resume_id"""
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
        JOIN PROJECT p ON p.project_signature = rp.project_id
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

        row = load_edited_skills(cursor,resume_id)
        if row and row[0]:
        # skills stored as JSON
            all_skills = json.loads(row[0])
        else: #Return to original skills shown
            # Aggregate all skills from projects
            union = set()
            for pid in project_ids:
                union.update(skills_map.get(pid, []))
            all_skills = sorted(union)
            row = load_edited_skills(cursor,resume_id)
            if row and row[0]:
                # Use edited all skills
                all_skills = [s.strip() for s in row[0].split(",") if s.strip()]
            else: #Return to original skills shown
                # Aggregate all skills from projects
                union = set()
                for pid in project_ids:
                    union.update(skills_map.get(pid, []))
                all_skills = sorted(union)

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
            last_modified
        ) in rows:
            # Parse skills: override_skills if present, else fallback to skills_map
            if override_skills:
                skills = json.loads(override_skills)
            else:
                skills = skills_map.get(pid, [])
            # Limit to 5 for display
            limited_skills = skills[:5]

            projects.append({
                "title": override_name or base_name,
                "dates": format_dates(
                    start or created_at,
                    end or last_modified
                ),
                "skills": limited_skills,
                "bullets": override_bullets if override_bullets else bullets_map.get(pid, [])
            })
        
        return {
            "name": user["name"],
            "email": user["email"],
            "links": user["links"],
            "education": {
                "school": user["education"],
                "degree": user["job_title"],
                "dates": "",
                "gpa": ""
            },
            "skills": {
                "Skills": all_skills
            },
            "projects": projects
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
                "skills": ", ".join(limited_skills),
                "bullets": bullets_map.get(pid, [])
            })

        if selected_ids:
            # Union of skills for selected projects
            union = set()
            for sid in selected_ids:
                union.update(skills_map.get(sid, []))
            all_skills = sorted(union)
        else:
            all_skills = sorted({
                skill
                for skills in skills_map.values()
                for skill in skills
            })

        return {
            "name": user["name"],
            "email": user["email"],
            "links": user["links"],
            "education": {
                "school": user["education"],
                "degree": user["job_title"],
                "dates": "", #placeholder for now (could improve user pref to include grad dates)
                "gpa": "" #only if user wishes to include
            },
            "skills": {
                "Skills": all_skills
            },
            "projects": projects
        }
    except sqlite3.Error as e:
        raise ResumeServiceError("Failed building resume model") from e
    finally:
        conn.close()

def create_resume(name: str | None = None) -> int:
    """Create a Resume and if no name is provided, set a default name"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO RESUME (name) VALUES (?)",
        (name or "",)
    )

    resume_id = cursor.lastrowid
    # If no name was provided, update the name to 'Resume-id'
    if not name:
        cursor.execute(
            "UPDATE RESUME SET name = ? WHERE id = ?",
            (f"Resume-{resume_id}", resume_id)
        )
    conn.commit()
    conn.close()
    return resume_id

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

def save_resume_edits(resume_id: int, payload: dict):
    """ Save or update edits made to the resume in the DB """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Update resume-level skills (if provided)
        if "skills" in payload:
            cursor.execute("""
                INSERT INTO RESUME_SKILLS (resume_id, skills)
                VALUES (?, ?)
                ON CONFLICT(resume_id)
                DO UPDATE SET
                    skills = excluded.skills,
                    updated_at = CURRENT_TIMESTAMP
            """, (resume_id, json.dumps(payload["skills"])))

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

def attach_projects_to_resume(resume_id: int, project_ids: list[str]):
    conn = get_connection()
    cursor = conn.cursor()

    for index, project_id in enumerate(project_ids):
        cursor.execute("""
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