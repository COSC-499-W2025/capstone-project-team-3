from collections import defaultdict
from app.data.db import get_connection
import sqlite3
from typing import Any, DefaultDict, Dict, List, Tuple, Optional
from datetime import datetime
import json
from app.utils.generate_resume import (
    format_dates,
    load_user, 
    load_projects,
    load_skills,
    limit_skills
)

def load_project_metrics(cursor: sqlite3.Cursor) -> DefaultDict[str, Dict[str, Any]]:
    """Return mapping of project_id to metrics (lines of code, commits, etc)."""
    metrics = defaultdict(dict)
    
    # Get metrics from DASHBOARD_DATA table
    cursor.execute("""
        SELECT project_id, metric_name, metric_value
        FROM DASHBOARD_DATA
    """)
    
    for project_id, metric_name, metric_value in cursor.fetchall():
        try:
            # Convert numeric values
            if metric_name in ['total_lines', 'files_count', 'total_commits']:
                metrics[project_id][metric_name] = int(metric_value) if metric_value else 0
            elif metric_name in ['avg_complexity']:
                metrics[project_id][metric_name] = float(metric_value) if metric_value else 0.0
            else:
                metrics[project_id][metric_name] = metric_value
        except (ValueError, TypeError):
            metrics[project_id][metric_name] = metric_value
    
    return metrics

def load_skills_with_dates(cursor: sqlite3.Cursor, project_ids: Optional[List[str]] = None) -> List[Tuple[str, str]]:
    """Return skills with their first usage dates for timeline view."""
    if project_ids:
        placeholders = ",".join(["?"] * len(project_ids))
        cursor.execute(f"""
            SELECT DISTINCT sa.skill, MIN(p.created_at) as first_used
            FROM SKILL_ANALYSIS sa
            JOIN PROJECT p ON sa.project_id = p.project_signature
            WHERE sa.project_id IN ({placeholders})
            GROUP BY sa.skill
            ORDER BY first_used ASC
        """, project_ids)
    else:
        cursor.execute("""
            SELECT DISTINCT sa.skill, MIN(p.created_at) as first_used
            FROM SKILL_ANALYSIS sa
            JOIN PROJECT p ON sa.project_id = p.project_signature
            GROUP BY sa.skill
            ORDER BY first_used ASC
        """)
    return cursor.fetchall()

def get_overview_stats(cursor: sqlite3.Cursor, project_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """Calculate portfolio overview statistics."""
    
    if project_ids:
        placeholders = ",".join(["?"] * len(project_ids))
        project_filter = f"WHERE project_signature IN ({placeholders})"
        params = project_ids
    else:
        project_filter = ""
        params = []
    
    # Total projects
    cursor.execute(f"SELECT COUNT(*) FROM PROJECT {project_filter}", params)
    total_projects = cursor.fetchone()[0]
    
    # Average rank (score)
    if project_filter:
        cursor.execute(f"""
            SELECT AVG(CAST(rank AS FLOAT)) 
            FROM PROJECT 
            {project_filter} AND rank IS NOT NULL
        """, params)
    else:
        cursor.execute("""
            SELECT AVG(CAST(rank AS FLOAT)) 
            FROM PROJECT 
            WHERE rank IS NOT NULL
        """)
    avg_score = cursor.fetchone()[0] or 0
    
    # Total skills count for selected projects
    if project_ids:
        skill_placeholders = ",".join(["?"] * len(project_ids))
        cursor.execute(f"""
            SELECT COUNT(DISTINCT skill) 
            FROM SKILL_ANALYSIS 
            WHERE project_id IN ({skill_placeholders})
        """, project_ids)
    else:
        cursor.execute("SELECT COUNT(DISTINCT skill) FROM SKILL_ANALYSIS")
    total_skills = cursor.fetchone()[0]
    
    # Total languages
    if project_ids:
        cursor.execute(f"""
            SELECT metric_value 
            FROM DASHBOARD_DATA 
            WHERE project_id IN ({placeholders}) AND metric_name = 'languages'
        """, project_ids)
    else:
        cursor.execute("SELECT metric_value FROM DASHBOARD_DATA WHERE metric_name = 'languages'")
    
    all_languages = set()
    for (lang_json,) in cursor.fetchall():
        try:
            languages = json.loads(lang_json) if isinstance(lang_json, str) else lang_json
            if isinstance(languages, list):
                all_languages.update(languages)
        except: 
            pass
    
    # Total lines of code
    if project_ids:
        cursor.execute(f"""
            SELECT SUM(CAST(metric_value AS INTEGER)) 
            FROM DASHBOARD_DATA 
            WHERE project_id IN ({placeholders}) AND metric_name = 'total_lines'
        """, project_ids)
    else:
        cursor.execute("""
            SELECT SUM(CAST(metric_value AS INTEGER)) 
            FROM DASHBOARD_DATA 
            WHERE metric_name = 'total_lines'
        """)
    total_lines = cursor.fetchone()[0] or 0
    
    return {
        "total_projects": total_projects,
        "avg_score": round(avg_score, 2),
        "total_skills": total_skills,
        "total_languages": len(all_languages),
        "total_lines": total_lines
    }

def categorize_projects_by_type(cursor: sqlite3.Cursor, project_ids: List[str]) -> Dict[str, List[str]]:
    """Separate GitHub projects from local projects."""
    github_projects = []
    local_projects = []
    
    for project_id in project_ids:
        cursor.execute("""
            SELECT 1 FROM DASHBOARD_DATA 
            WHERE project_id = ? AND metric_name = 'total_commits'
        """, (project_id,))
        
        if cursor.fetchone():  # Has commits = GitHub project
            github_projects.append(project_id)
        else:  # Local project
            local_projects.append(project_id)
    
    return {
        "github": github_projects,
        "local": local_projects
    }

def categorize_projects_by_type(cursor: sqlite3.Cursor, project_ids: List[str]) -> Dict[str, List[str]]:
    """Categorize projects as GitHub or Local based on metrics."""
    github_projects = []
    local_projects = []
    
    project_metrics = load_project_metrics(cursor)
    
    for project_id in project_ids:
        metrics = project_metrics.get(project_id, {})
        if metrics.get("total_commits", 0) > 0:
            github_projects.append(project_id)
        else:
            local_projects.append(project_id)
    
    return {"github": github_projects, "local": local_projects}

def get_skills_timeline(cursor: sqlite3.Cursor, project_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Get skills organized by when they were first used."""
    skills_with_dates = load_skills_with_dates(cursor, project_ids)
    
    timeline = []
    for skill, first_used in skills_with_dates:
        try:
            year = datetime.fromisoformat(first_used).year
            timeline.append({
                "skill": skill,
                "first_used": first_used,
                "year": year
            })
        except Exception:
            continue
    
    return sorted(timeline, key=lambda x: x["year"])

def build_portfolio_model(project_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """Return assembled portfolio model built from the database.
    If project_ids are provided, include only those projects.
    """
    conn = get_connection()
    cursor = conn.cursor()

    user = load_user(cursor)
    projects_raw = load_projects(cursor, project_ids=project_ids)
    skills_map = load_skills(cursor)
    overview_stats = get_overview_stats(cursor, project_ids)
    skills_timeline = get_skills_timeline(cursor, project_ids)
    project_metrics = load_project_metrics(cursor)

    projects = []
    selected_ids = [pid for pid, *_ in projects_raw]

    for pid, name, rank, created_at, last_modified in projects_raw:
        metrics = project_metrics.get(pid, {})
        project_skills = skills_map.get(pid, [])
        
        # Limit skills for display
        limited_skills = limit_skills(project_skills, max_count=10)
        
        # Determine project type based on if we have commit data
        is_github = metrics.get("total_commits", 0) > 0
        
        projects.append({
            "id": pid,
            "title": name,
            "rank": float(rank) if rank else 0,
            "dates": format_dates(created_at, last_modified),
            "created_at": created_at,
            "last_modified": last_modified,
            "type": "GitHub" if is_github else "Local",
            "metrics": metrics,
            "skills": limited_skills,
            "lines_of_code": metrics.get("total_lines", 0),
            "files_count": metrics.get("total_files", 0),
            "total_commits": metrics.get("total_commits", 0),
            "primary_language": metrics.get("languages", "Unknown"),
            "functions": metrics.get("functions", 0),
            "classes": metrics.get("classes", 0),
            "complexity": metrics.get("complexity_analysis", "N/A")
        })

    # Calculate project type analysis if projects selected
    if selected_ids:
        project_type_analysis = categorize_projects_by_type(cursor, selected_ids)
        
        # Calculate stats for each type
        github_stats = {}
        local_stats = {}
        
        if project_type_analysis["github"]:
            github_stats = get_overview_stats(cursor, project_type_analysis["github"])
            # Add GitHub-specific metrics
            cursor.execute(f"""
                SELECT AVG(CAST(metric_value AS INTEGER))
                FROM DASHBOARD_DATA 
                WHERE project_id IN ({",".join(["?"] * len(project_type_analysis["github"]))}) 
                AND metric_name = 'total_commits'
            """, project_type_analysis["github"])
            github_stats["avg_commits"] = cursor.fetchone()[0] or 0
        
        if project_type_analysis["local"]:
            local_stats = get_overview_stats(cursor, project_type_analysis["local"])
            # Add local-specific metrics  
            cursor.execute(f"""
                SELECT AVG(CAST(metric_value AS FLOAT))
                FROM DASHBOARD_DATA 
                WHERE project_id IN ({",".join(["?"] * len(project_type_analysis["local"]))}) 
                AND metric_name = 'completeness_score'
            """, project_type_analysis["local"])
            local_stats["avg_completeness"] = cursor.fetchone()[0] or 0
    else:
        project_type_analysis = {"github": [], "local": []}
        github_stats = local_stats = {}

    conn.close()

    return {
        "user": user,
        "overview": overview_stats,
        "projects": projects,
        "skills_timeline": skills_timeline,
        "project_type_analysis": {
            "github": {
                "count": len(project_type_analysis["github"]),
                "stats": github_stats
            },
            "local": {
                "count": len(project_type_analysis["local"]),
                "stats": local_stats
            }
        },
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_projects": len(projects),
            "filtered": bool(project_ids),
            "project_ids": project_ids or []
        }
    }