from datetime import datetime
from app.data.db import get_connection


def get_portfolio_resume_insights():
    
    # Connect to the database
    conn = get_connection()
    cur = conn.cursor()
    
    # Build Portfolio: Project name, summary, duration, skills
    cur.execute("SELECT project_signature, name, rank, summary, created_at, last_modified FROM PROJECT")
    projects = []
    for row in cur.fetchall():
        signature, name, rank, summary, created_at, last_modified = row
        cur.execute("SELECT skill FROM SKILL_ANALYSIS WHERE project_id=?", (signature,))
        # TODO : Initialize metric object = {}
        # TODO : Include a select amount of metrics from DASHBOARD_DATA as needed. Check for existence first.
                # Baseline Metrics to check & include : doc_type_frequency, completeness_score, author, languages etc..
        # TODO : Identify authors for collaborative projects (if metric_name == 'author' is available in DASHBOARD_DATA, then include it)

        skills = [s[0] for s in cur.fetchall()]
        duration = f"{format_date(created_at)} - {format_date(last_modified)}"
        
        projects.append({
            "name": name,
            "summary": summary,
            "duration": duration,
            "skills": skills,
            "created_at": format_date(created_at),
            "rank": rank
            # TODO: Include metric object in project to be sent to retrieve_insights_cli.py 
        })

    # Top ranked projects (by rank limit to top 5)
    top_projects = sorted(projects, key=lambda x: x["rank"], reverse=True)[:5]

    # Chronological list (by created_at limit to 10)
    chronological = sorted(projects, key=lambda x: (x["created_at"],len(x["skills"])), reverse=True)[:10]

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