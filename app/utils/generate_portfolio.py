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
            if metric_name in ['total_lines', 'files_count', 'total_commits', 'total_files', 'functions', 'components', 'classes', 'code_files_changed', 'doc_files_changed', 'test_files_changed', 'word_count']:
                metrics[project_id][metric_name] = int(metric_value) if metric_value else 0
            elif metric_name in ['avg_complexity', 'average_function_length', 'average_comment_ratio', 'completeness_score']:
                metrics[project_id][metric_name] = float(metric_value) if metric_value else 0.0
            elif metric_name in ['languages', 'roles', 'technical_keywords', 'authors']:
                # Parse JSON arrays
                try:
                    metrics[project_id][metric_name] = json.loads(metric_value) if metric_value else []
                except (json.JSONDecodeError, TypeError):
                    metrics[project_id][metric_name] = metric_value or []
            elif metric_name in ['code_patterns', 'complexity_analysis', 'contribution_activity', 'development_patterns', 'commit_patterns']:
                # Parse complex JSON objects
                try:
                    metrics[project_id][metric_name] = json.loads(metric_value) if metric_value else {}
                except (json.JSONDecodeError, TypeError):
                    metrics[project_id][metric_name] = {}
            else:
                metrics[project_id][metric_name] = metric_value
        except (ValueError, TypeError):
            metrics[project_id][metric_name] = metric_value
    
    return metrics

def load_project_summaries(cursor: sqlite3.Cursor, project_ids: Optional[List[str]] = None) -> Dict[str, str]:
    """Load project narrative summaries from PROJECT.summary field."""
    summaries = {}
    
    if project_ids:
        placeholders = ",".join(["?"] * len(project_ids))
        cursor.execute(f"""
            SELECT project_signature, summary
            FROM PROJECT 
            WHERE project_signature IN ({placeholders})
        """, project_ids)
    else:
        cursor.execute("SELECT project_signature, summary FROM PROJECT")
    
    for project_id, summary in cursor.fetchall():
        summaries[project_id] = summary or ""
    
    return summaries

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
    
    # Average score
    if project_filter:
        cursor.execute(f"""
            SELECT AVG(CAST(score AS FLOAT)) 
            FROM PROJECT 
            {project_filter} AND score IS NOT NULL
        """, params)
    else:
        cursor.execute("""
            SELECT AVG(CAST(score AS FLOAT)) 
            FROM PROJECT 
            WHERE score IS NOT NULL
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

def get_language_distribution(cursor: sqlite3.Cursor, project_ids: Optional[List[str]] = None) -> Dict[str, int]:
    """Get distribution of programming languages across projects."""
    if project_ids:
        placeholders = ",".join(["?"] * len(project_ids))
        cursor.execute(f"""
            SELECT metric_value 
            FROM DASHBOARD_DATA 
            WHERE project_id IN ({placeholders}) AND metric_name = 'languages'
        """, project_ids)
    else:
        cursor.execute("SELECT metric_value FROM DASHBOARD_DATA WHERE metric_name = 'languages'")
    
    language_count = defaultdict(int)
    for (lang_json,) in cursor.fetchall():
        try:
            languages = json.loads(lang_json) if isinstance(lang_json, str) else lang_json
            if isinstance(languages, list):
                for lang in languages:
                    language_count[lang] += 1
        except:
            pass
    
    return dict(language_count)

def get_project_complexity_distribution(cursor: sqlite3.Cursor, project_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """Get project complexity distribution for size analysis."""
    if project_ids:
        placeholders = ",".join(["?"] * len(project_ids))
        cursor.execute(f"""
            SELECT project_id, metric_value 
            FROM DASHBOARD_DATA 
            WHERE project_id IN ({placeholders}) AND metric_name = 'total_lines'
        """, project_ids)
    else:
        cursor.execute("SELECT project_id, metric_value FROM DASHBOARD_DATA WHERE metric_name = 'total_lines'")
    
    size_distribution = {"small": 0, "medium": 0, "large": 0}
    project_sizes = []
    
    for project_id, lines_str in cursor.fetchall():
        try:
            lines = int(lines_str) if lines_str else 0
            project_sizes.append({"project_id": project_id, "lines": lines})
            
            if lines < 1000:
                size_distribution["small"] += 1
            elif lines < 3000:
                size_distribution["medium"] += 1
            else:
                size_distribution["large"] += 1
        except (ValueError, TypeError):
            size_distribution["small"] += 1
    
    return {
        "distribution": size_distribution,
        "project_sizes": project_sizes,
        "avg_size": sum(p["lines"] for p in project_sizes) / len(project_sizes) if project_sizes else 0
    }

def get_score_distribution(cursor: sqlite3.Cursor, project_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """Get project score distribution for quality analysis."""
    if project_ids:
        placeholders = ",".join(["?"] * len(project_ids))
        cursor.execute(f"""
            SELECT project_signature, score 
            FROM PROJECT 
            WHERE project_signature IN ({placeholders}) AND score IS NOT NULL
        """, project_ids)
    else:
        cursor.execute("SELECT project_signature, score FROM PROJECT WHERE score IS NOT NULL")
    
    score_ranges = {"excellent": 0, "good": 0, "fair": 0, "poor": 0}
    project_scores = []
    
    for project_id, score_str in cursor.fetchall():
        try:
            score = float(score_str)
            project_scores.append({"project_id": project_id, "score": score})
            
            if score >= 0.9:
                score_ranges["excellent"] += 1
            elif score >= 0.8:
                score_ranges["good"] += 1
            elif score >= 0.7:
                score_ranges["fair"] += 1
            else:
                score_ranges["poor"] += 1
        except (ValueError, TypeError):
            score_ranges["fair"] += 1
    
    return {
        "distribution": score_ranges,
        "project_scores": project_scores,
        "avg_score": sum(p["score"] for p in project_scores) / len(project_scores) if project_scores else 0
    }

def get_monthly_activity(cursor: sqlite3.Cursor, project_ids: Optional[List[str]] = None) -> Dict[str, int]:
    """Get monthly project activity for timeline visualization."""
    if project_ids:
        placeholders = ",".join(["?"] * len(project_ids))
        cursor.execute(f"""
            SELECT created_at, last_modified 
            FROM PROJECT 
            WHERE project_signature IN ({placeholders})
        """, project_ids)
    else:
        cursor.execute("SELECT created_at, last_modified FROM PROJECT")
    
    monthly_activity = defaultdict(int)
    
    for created_at, last_modified in cursor.fetchall():
        try:
            # Count creation month
            if created_at:
                month = datetime.fromisoformat(created_at).strftime('%Y-%m')
                monthly_activity[month] += 1
                
            # Count modification month if different
            if last_modified and last_modified != created_at:
                month = datetime.fromisoformat(last_modified).strftime('%Y-%m')
                monthly_activity[month] += 0.5  # Weight modifications less than creations
        except Exception:
            continue
    
    return dict(sorted(monthly_activity.items()))

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
    project_summaries = load_project_summaries(cursor, project_ids)
    
    # New data for enhanced graphs
    language_distribution = get_language_distribution(cursor, project_ids)
    complexity_distribution = get_project_complexity_distribution(cursor, project_ids)
    score_distribution = get_score_distribution(cursor, project_ids)
    monthly_activity = get_monthly_activity(cursor, project_ids)

    projects = []
    selected_ids = [pid for pid, *_ in projects_raw]

    for pid, name, score, created_at, last_modified in projects_raw:
        metrics = project_metrics.get(pid, {})
        project_skills = skills_map.get(pid, [])
        project_summary = project_summaries.get(pid, "")
        
        # Limit skills for display
        limited_skills = limit_skills(project_skills, max_count=10)
        
        # Determine project type based on if we have commit data
        is_github = metrics.get("total_commits", 0) > 0
        
        # Extract detailed analysis data
        complexity_analysis = metrics.get("complexity_analysis", {})
        commit_patterns = metrics.get("commit_patterns", {})
        development_patterns = metrics.get("development_patterns", {})
        code_patterns = metrics.get("code_patterns", {})
        contribution_activity = metrics.get("contribution_activity", {})
        
        projects.append({
            "id": pid,
            "title": name,
            "score": float(score) if score else 0,
            "rank": float(score) if score else 0,
            "dates": format_dates(created_at, last_modified),
            "created_at": created_at,
            "last_modified": last_modified,
            "type": "GitHub" if is_github else "Local",
            "summary": project_summary,
            "metrics": {
                # Basic metrics
                "total_lines": metrics.get("total_lines", 0),
                "total_commits": metrics.get("total_commits", 0),
                "total_files": metrics.get("total_files", 0),
                "code_files_changed": metrics.get("code_files_changed", 0),
                "doc_files_changed": metrics.get("doc_files_changed", 0),
                "test_files_changed": metrics.get("test_files_changed", 0),
                "functions": metrics.get("functions", 0),
                "components": metrics.get("components", 0),
                "classes": metrics.get("classes", 0),
                "average_function_length": metrics.get("average_function_length", 0),
                "average_comment_ratio": metrics.get("average_comment_ratio", 0),
                "completeness_score": metrics.get("completeness_score", 0),
                "word_count": metrics.get("word_count", 0),
                # Lists/Arrays
                "languages": metrics.get("languages", []),
                "roles": metrics.get("roles", []),
                "technical_keywords": metrics.get("technical_keywords", []),
                "authors": metrics.get("authors", []),
                # Complex analysis objects
                "complexity_analysis": complexity_analysis,
                "commit_patterns": commit_patterns,
                "development_patterns": development_patterns,
                "code_patterns": code_patterns,
                "contribution_activity": contribution_activity,
            },
            "skills": limited_skills,
            # Editable fields (for UI)
            "editable": {
                "rank": True,
                "summary": True,
                "dates": True
            }
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
        "graphs": {
            "language_distribution": language_distribution,
            "complexity_distribution": complexity_distribution,
            "score_distribution": score_distribution,
            "monthly_activity": monthly_activity,
            "top_skills": dict(list(defaultdict(int, {
                skill: len([p for p in projects if skill in skills_map.get(p["id"], [])])
                for skill in set(skill for project_skills in skills_map.values() for skill in project_skills)
            }).items())[:10])  # Top 10 most used skills
        },
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_projects": len(projects),
            "filtered": bool(project_ids),
            "project_ids": project_ids or []
        }
    }
