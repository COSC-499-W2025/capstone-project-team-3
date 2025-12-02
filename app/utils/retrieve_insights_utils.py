import sqlite3
from datetime import datetime

def get_portfolio_resume_insights():
    
    # Connect to the database
    conn = sqlite3.connect("app/data/app.sqlite3")
    cur = conn.cursor()
    
    # Build Portfolio: Project name, summary, duration, skills
    cur.execute("SELECT project_signature, name, rank, summary, created_at, last_modified FROM PROJECT")
    projects = []
    for row in cur.fetchall():
        signature, name, rank, summary, created_at, last_modified = row
        cur.execute("SELECT skill FROM SKILL_ANALYSIS WHERE project_id=?", (signature,))
        skills = [s[0] for s in cur.fetchall()]
        duration = f"{format_date(created_at)} - {format_date(last_modified)}"
        projects.append({
            "name": name,
            "summary": summary,
            "duration": duration,
            "skills": skills,
            "created_at": format_date(created_at),
            "rank": rank
        })

    # Top ranked projects (by rank limit to top 5)
    top_projects = sorted(projects, key=lambda x: x["rank"], reverse=True)[:5]

    # Chronological list (by created_at limit to 10)
    chronological = sorted(projects, key=lambda x: x["created_at"])[:10]

    # Extract Resume bullets
    cur.execute("SELECT summary_text FROM RESUME_SUMMARY")
    bullets = [row[0] for row in cur.fetchall()]
    conn.close()
    
    # Return structured portfolio object and resume object
    return {
        "projects": projects,
        "top_projects": top_projects,
        "chronological": chronological
    }, {
        "bullets": bullets
    }
    
def format_date(dt_str):
    # Assumes format "YYYY-MM-DD HH:MM:SS"
    return dt_str.split(" ")[0] if dt_str else ""