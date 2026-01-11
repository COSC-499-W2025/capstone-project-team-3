import sqlite3
from collections import defaultdict
from app.data.db import get_connection
from datetime import datetime

def format_dates(start, end):
    try:
        s = datetime.fromisoformat(start).strftime("%b %Y")
        e = datetime.fromisoformat(end).strftime("%b %Y")
        return f"{s} – {e}"
    except Exception:
        return ""
    
def load_user(cursor):
    cursor.execute("""
        SELECT name, email, github_user, education, job_title
        FROM USER_PREFERENCES
        WHERE user_id = 1
    """)
    row = cursor.fetchone()

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

def load_projects(cursor):
    cursor.execute("""
        SELECT project_signature, name, rank, created_at, last_modified
        FROM PROJECT
        ORDER BY rank DESC
    """)
    return cursor.fetchall()

def load_resume_bullets(cursor):
    cursor.execute("""
        SELECT project_id, summary_text
        FROM RESUME_SUMMARY
    """)
    bullets = defaultdict(list)
    for pid, text in cursor.fetchall():
        bullets[pid].append(text)
    return bullets

def load_skills(cursor):
    cursor.execute("""
        SELECT skill, project_id
        FROM SKILL_ANALYSIS
    """)
    skills_by_project = defaultdict(list)

    for skill, project_id in cursor.fetchall():
        skills_by_project[project_id].append(skill)

    return skills_by_project

def limit_skills(skills, max_count=5):
    seen = set()
    limited = []

    for skill in skills:
        if skill not in seen:
            seen.add(skill)
            limited.append(skill)
        if len(limited) == max_count:
            break

    return limited

def build_resume_model():
    conn = get_connection()
    cursor = conn.cursor()

    user = load_user(cursor)
    projects_raw = load_projects(cursor)
    bullets_map = load_resume_bullets(cursor)
    skills_map = load_skills(cursor)

    projects = []

    for project_id, name, rank, created_at, last_modified in projects_raw:
        raw_skills = skills_map.get(project_id, [])
        limited_skills = limit_skills(raw_skills, max_count=5)

        projects.append({
            "title": name,
            "dates": format_dates(created_at, last_modified),
            "skills": ", ".join(limited_skills),
            "bullets": bullets_map.get(project_id, [])
        })

    all_skills = sorted({
        skill
        for skills in skills_map.values()
        for skill in skills
    })

    conn.close()

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



