from datetime import datetime
import json
from app.data.db import get_connection


def _normalize_authors(value):
    if value is None:
        return []
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [str(a) for a in parsed if a is not None and str(a).strip()]
        except (json.JSONDecodeError, TypeError):
            pass
        return [value] if value.strip() else []
    if isinstance(value, (list, tuple, set)):
        return [str(a) for a in value if a is not None and str(a).strip()]
    return [str(value)]


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
        # Check for specific baseline metrics and include authors
        authors = []
        if "authors" in metrics:
            # If author is stored as metric
            authors = _normalize_authors(metrics["authors"])
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

    # Top ranked projects (by rank, Handle None, limit to top 5)
    def _rank_key(proj):
        r = proj.get("rank")
        try:
            return float(r)
        except (TypeError, ValueError):
            return 0.0
    top_projects = sorted(projects, key=_rank_key, reverse=True)[:5]

    # Chronological list (by created_at limit to 10)
    chronological = sorted(projects, key=lambda x: (x["created_at"]), reverse=True)[:10]

    # Extract Resume bullets WITH project names - FIXED
    cur.execute("""
        SELECT p.name, r.summary_text 
        FROM RESUME_SUMMARY r
        JOIN PROJECT p ON r.project_id = p.project_signature
        WHERE r.summary_text IS NOT NULL
        ORDER BY p.created_at DESC
    """)
    
    resume_bullets = []
    for row in cur.fetchall():
        project_name, summary_text = row
        
        try:
            parsed = json.loads(summary_text)
            if isinstance(parsed, list):
                bullets = [b.strip() for b in parsed if isinstance(b, str) and b.strip()]
            else:
                bullets = [summary_text]
        except (json.JSONDecodeError, TypeError, ValueError):
            bullets = [summary_text]

        for b in bullets:
            resume_bullets.append({
                "project_name": project_name or "Unknown Project",
                "bullet": b
            })
    conn.close()
    
    # Return structured portfolio object and resume object
    return {
        "projects": projects, 
        "top_projects": top_projects,
        "chronological": chronological
    }, {
        "bullets": resume_bullets
    }
    
def format_date(dt_str):
    """Format datetime string to YYYY-MM-DD for easy chronological sorting."""
    if not dt_str:
        return ""
    
    try:
        from datetime import datetime
        
        # Handle ISO format with microseconds
        if 'T' in dt_str:
            # Remove microseconds if present: "2025-12-06T19:29:04.639249" -> "2025-12-06T19:29:04"
            if '.' in dt_str:
                dt_str = dt_str.split('.')[0]
            dt = datetime.fromisoformat(dt_str.replace('T', ' '))
        else:
            # Handle space-separated format
            dt = datetime.strptime(dt_str.split(' ')[0], '%Y-%m-%d')
        
        # Return YYYY-MM-DD format for easy chronological sorting
        return dt.strftime('%Y-%m-%d')  # "2025-12-06"
        
    except (ValueError, AttributeError):
        # Fallback: extract just date part
        if 'T' in str(dt_str):
            return str(dt_str).split('T')[0]
        else:
            return str(dt_str).split(' ')[0]


def get_projects_by_signatures(signatures: list):
    """
    Get project information for specific project signatures.
    Accepts either a single signature (str) or a list of signatures.
    If a single signature is supplied, returns a single project dict (or None).
    If a list is supplied, returns a list of project dicts.
    
    Args:
        signatures (list): List of project signature strings
        
    Returns:
        list: List of project dictionaries with name, summary, duration, skills, created_at, rank, metrics, resume_bullets
        dict: Single project dictionary if single signature provided
    """
    if not signatures:
        return [] if isinstance(signatures, (list, tuple)) else None
    
    single_input = False
    if isinstance(signatures, str):
        single_input = True
        signatures = [signatures]
    
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
            # Try to deserialize JSON values stored as text (lists/dicts/numeric strings)
            parsed_value = metric_value
            if isinstance(metric_value, str):
                try:
                    parsed_value = json.loads(metric_value)
                except (json.JSONDecodeError, TypeError, ValueError):
                    # keep original string if not JSON
                    parsed_value = metric_value
            metrics[metric_name] = parsed_value
        

        # Get resume bullets for this project - FIXED
        cur.execute("SELECT summary_text FROM RESUME_SUMMARY WHERE project_id=?", (signature,))
        resume_rows = cur.fetchall()

        resume_bullets = []
        for row in resume_rows:
            summary_text = row[0]
            try:
                # Try to parse as JSON first (for arrays)
                parsed = json.loads(summary_text)
                if isinstance(parsed, list):
                    resume_bullets.extend(parsed)
                else:
                    resume_bullets.append(summary_text)
            except (json.JSONDecodeError, TypeError):
                # If not JSON, treat as individual bullet
                resume_bullets.append(summary_text)

        # Filter out empty bullets
        resume_bullets = [bullet for bullet in resume_bullets if bullet and bullet.strip()]
            
        # Check for specific baseline metrics and include authors
        authors = []
        if "authors" in metrics:
            # If author is stored as metric
            authors = _normalize_authors(metrics["authors"])
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
            "resume_bullets": resume_bullets
        })
    
    conn.close()

    if single_input:
        return projects[0] if projects else None

    return projects
