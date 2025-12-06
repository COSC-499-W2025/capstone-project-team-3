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
        # Get skills for this project
        cur.execute("SELECT skill FROM SKILL_ANALYSIS WHERE project_id=?", (signature,))
        skills = [s[0] for s in cur.fetchall()]
        
        # Get metrics for this project
        cur.execute("SELECT metric_name, metric_value FROM DASHBOARD_DATA WHERE project_id=?", (signature,))
        metrics = {}
        
        # Convert metrics to dictionary format
        for metric_row in cur.fetchall():
            metric_name, metric_value = metric_row
            metrics[metric_name] = metric_value
        print("--------------------here 3---------------")
        print(metrics)    
        # Check for specific baseline metrics and include authors
        authors = []
        if "author" in metrics:
            # If author is stored as metric
            authors = [metrics["author"]["value"]]
        else:
            # Alternative: Get authors from GIT_HISTORY
            cur.execute("SELECT DISTINCT author_name FROM GIT_HISTORY WHERE project_id=?", (signature,))
            authors = [author[0] for author in cur.fetchall()]
        
        # Add authors to metrics if found
        if authors:
            metrics["authors"] = ", ".join(authors)
        
        duration = f"{format_date(created_at)} - {format_date(last_modified)}"
        
        projects.append({
            "name": name,
            "summary": summary,
            "duration": duration,
            "skills": skills,
            "created_at": format_date(created_at),
            "rank": rank,
            "metrics": metrics
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


def get_projects_by_signatures(signatures: list):
    """
    Get project information for specific project signatures.
    
    Args:
        signatures (list): List of project signature strings
        
    Returns:
        list: List of project dictionaries with name, summary, duration, skills, created_at, rank, metrics, resume_bullets
    """
    if not signatures:
        return []
    
    # Connect to the database
    conn = get_connection()
    cur = conn.cursor()
    
    projects = []
    
    for signature in signatures:
        # Get project basic info
        cur.execute(
            "SELECT project_signature, name, rank, summary, created_at, last_modified FROM PROJECT WHERE project_signature=?", 
            (signature,)
        )
        
        project_row = cur.fetchone()
        if not project_row:
            # Skip if project not found
            continue
            
        sig, name, rank, summary, created_at, last_modified = project_row
        
        # Get skills for this project
        cur.execute("SELECT skill FROM SKILL_ANALYSIS WHERE project_id=?", (signature,))
        skills = [s[0] for s in cur.fetchall()]
        
        # Get metrics for this project
        cur.execute("SELECT metric_name, metric_value FROM DASHBOARD_DATA WHERE project_id=?", (signature,))
        metrics = {}
        
        # Convert metrics to dictionary format
        for metric_row in cur.fetchall():
            metric_name, metric_value = metric_row
            metrics[metric_name] = metric_value
        
        # Get resume bullets for this project
        cur.execute("SELECT summary_text FROM RESUME_SUMMARY WHERE project_id=?", (signature,))
        resume_bullets = [row[0] for row in cur.fetchall()]
            
        # Check for specific baseline metrics and include authors
        authors = []
        if "author" in metrics:
            # If author is stored as metric
            authors = [metrics["author"]]
        else:
            # Alternative: Get authors from GIT_HISTORY
            cur.execute("SELECT DISTINCT author_name FROM GIT_HISTORY WHERE project_id=?", (signature,))
            authors = [author[0] for author in cur.fetchall()]
        
        # Add authors to metrics if found
        if authors:
            metrics["authors"] = ", ".join(authors) 
            
        duration = f"{format_date(created_at)} - {format_date(last_modified)}"
        
        projects.append({
            "name": name,
            "summary": summary,
            "duration": duration,
            "skills": skills,
            "created_at": format_date(created_at),
            "rank": rank,
            "metrics": metrics,
            "resume_bullets": resume_bullets  # ADD THIS
        })
    
    conn.close()
    return projects