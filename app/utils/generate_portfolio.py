from collections import defaultdict
from pathlib import Path
from app.data.db import get_connection
import sqlite3
from typing import Any, DefaultDict, Dict, List, Tuple, Optional, Set
from datetime import datetime
import json
import os
from app.utils.generate_resume import (
    format_dates,
    load_user, 
    load_skills,
    limit_skills
)

def load_projects_with_override(cursor: sqlite3.Cursor, project_ids: Optional[List[str]] = None) -> List[Tuple[str, str, float, str, str, int, Optional[float], Optional[str]]]:
    """Return projects with signature, name, score, created_at, last_modified, score_overridden, score_overridden_value, score_override_exclusions.
    If project_ids are provided, return only those projects.
    """
    if project_ids:
        # Build a dynamic IN clause safely
        placeholders = ",".join(["?"] * len(project_ids))
        try:
            query = f"""
                SELECT project_signature, name, score, created_at, last_modified, score_overridden, score_overridden_value, score_override_exclusions
                FROM PROJECT
                WHERE project_signature IN ({placeholders})
                ORDER BY score DESC
            """
            cursor.execute(query, project_ids)
            return cursor.fetchall()
        except sqlite3.OperationalError:
            query = f"""
                SELECT project_signature, name, score, created_at, last_modified, score_overridden, score_overridden_value
                FROM PROJECT
                WHERE project_signature IN ({placeholders})
                ORDER BY score DESC
            """
            cursor.execute(query, project_ids)
            return [(*row, None) for row in cursor.fetchall()]
    else:
        try:
            cursor.execute(
                """
                SELECT project_signature, name, score, created_at, last_modified, score_overridden, score_overridden_value, score_override_exclusions
                FROM PROJECT
                ORDER BY score DESC
                """
            )
            return cursor.fetchall()
        except sqlite3.OperationalError:
            cursor.execute(
                """
                SELECT project_signature, name, score, created_at, last_modified, score_overridden, score_overridden_value
                FROM PROJECT
                ORDER BY score DESC
                """
            )
            return [(*row, None) for row in cursor.fetchall()]

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
            elif metric_name in ['languages', 'roles', 'technical_keywords', 'authors', 'collaborators']:
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
    
    # Average score (considering overrides)
    if project_filter:
        cursor.execute(f"""
            SELECT AVG(
                CASE 
                    WHEN score_overridden = 1 AND score_overridden_value IS NOT NULL 
                    THEN CAST(score_overridden_value AS FLOAT)
                    ELSE CAST(score AS FLOAT)
                END
            )
            FROM PROJECT 
            {project_filter} AND (score IS NOT NULL OR (score_overridden = 1 AND score_overridden_value IS NOT NULL))
        """, params)
    else:
        cursor.execute("""
            SELECT AVG(
                CASE 
                    WHEN score_overridden = 1 AND score_overridden_value IS NOT NULL 
                    THEN CAST(score_overridden_value AS FLOAT)
                    ELSE CAST(score AS FLOAT)
                END
            )
            FROM PROJECT 
            WHERE (score IS NOT NULL OR (score_overridden = 1 AND score_overridden_value IS NOT NULL))
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
            SELECT project_signature, 
                   CASE 
                       WHEN score_overridden = 1 AND score_overridden_value IS NOT NULL 
                       THEN score_overridden_value
                       ELSE score
                   END as effective_score
            FROM PROJECT 
            WHERE project_signature IN ({placeholders}) AND 
                  (score IS NOT NULL OR (score_overridden = 1 AND score_overridden_value IS NOT NULL))
        """, project_ids)
    else:
        cursor.execute("""
            SELECT project_signature, 
                   CASE 
                       WHEN score_overridden = 1 AND score_overridden_value IS NOT NULL 
                       THEN score_overridden_value
                       ELSE score
                   END as effective_score
            FROM PROJECT 
            WHERE (score IS NOT NULL OR (score_overridden = 1 AND score_overridden_value IS NOT NULL))
        """)
    
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


def _parse_iso_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        normalized = value.strip().replace("Z", "+00:00")
        return datetime.fromisoformat(normalized)
    except Exception:
        return None


def get_daily_activity(
    cursor: sqlite3.Cursor,
    projects_raw: List[Tuple[str, str, float, str, str, int, Optional[float], Optional[str]]],
    project_metrics: DefaultDict[str, Dict[str, Any]],
) -> Dict[str, float]:
    """Get daily activity timeline.

    - GitHub projects: exact daily counts from GIT_HISTORY.commit_date
    - Local projects: fallback signal from created/last_modified dates
    - GitHub projects without GIT_HISTORY: fallback to created/last_modified
    """
    daily_activity: DefaultDict[str, float] = defaultdict(float)
    if not projects_raw:
        return {}

    project_ids = [pid for pid, *_ in projects_raw]
    github_project_ids = [
        pid for pid in project_ids if (project_metrics.get(pid, {}).get("total_commits", 0) or 0) > 0
    ]

    github_days_with_activity = set()

    if github_project_ids:
        placeholders = ",".join(["?"] * len(github_project_ids))
        cursor.execute(
            f"""
            SELECT project_id, commit_date
            FROM GIT_HISTORY
            WHERE project_id IN ({placeholders})
            """,
            github_project_ids,
        )

        for project_id, commit_date in cursor.fetchall():
            dt = _parse_iso_datetime(commit_date)
            if not dt:
                continue
            day_key = dt.strftime("%Y-%m-%d")
            daily_activity[day_key] += 1.0
            github_days_with_activity.add(project_id)

    for pid, _name, _score, created_at, last_modified, *_ in projects_raw:
        is_github = (project_metrics.get(pid, {}).get("total_commits", 0) or 0) > 0
        if is_github and pid in github_days_with_activity:
            continue

        created_dt = _parse_iso_datetime(created_at)
        modified_dt = _parse_iso_datetime(last_modified)

        if created_dt:
            daily_activity[created_dt.strftime("%Y-%m-%d")] += 1.0

        if modified_dt and created_dt:
            if modified_dt.date() != created_dt.date():
                daily_activity[modified_dt.strftime("%Y-%m-%d")] += 0.5
        elif modified_dt:
            daily_activity[modified_dt.strftime("%Y-%m-%d")] += 0.5

    return dict(sorted(daily_activity.items()))


def _extract_collaborators_from_git_history(
    cursor: sqlite3.Cursor,
    project_id: str,
    user: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Fallback: derive collaborator list from GIT_HISTORY table.

    GIT_HISTORY stores per-commit author data.  When the `collaborators`
    DASHBOARD_DATA metric is missing (e.g. project was analysed before the
    feature was added), we can still recover contributor information from
    the commit history that *is* stored.
    """
    cursor.execute(
        "SELECT author_name, author_email, COUNT(*) FROM GIT_HISTORY "
        "WHERE project_id = ? GROUP BY author_name, author_email",
        (project_id,),
    )
    rows = cursor.fetchall()
    if not rows:
        return []

    primary_aliases: Set[str] = set()
    for key in ("name", "github_user", "email"):
        val = (user.get(key) or "").strip()
        if val:
            primary_aliases.add(val.casefold())

    contributors: List[Dict[str, Any]] = []
    for author_name, author_email, commit_count in rows:
        name = (author_name or "").strip()
        email = (author_email or "").strip()
        is_primary = (
            name.casefold() in primary_aliases
            or email.casefold() in primary_aliases
        ) if (name or email) else False
        contributors.append({
            "name": name or email or "Unknown",
            "email": email,
            "commits": commit_count,
            "is_primary": is_primary,
        })
    return contributors


def _try_live_extraction(
    project_path: str,
    user: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Try to extract collaborators directly from a git repo on disk."""
    try:
        if not project_path or not os.path.isdir(project_path):
            return []
        from app.utils.git_utils import detect_git, extract_all_contributors
        if not detect_git(project_path):
            return []
        aliases: List[str] = []
        for key in ("github_user", "email", "name"):
            val = (user.get(key) or "").strip()
            if val:
                aliases.append(val)
        contributors = extract_all_contributors(project_path, aliases or None)
        return contributors
    except Exception:
        return []


def _build_collaboration_network(
    projects: List[Dict[str, Any]],
    user: Dict[str, Any],
    cursor: Optional[sqlite3.Cursor] = None,
) -> Dict[str, Any]:
    """Build a collaboration network graph from per-project collaborator data.

    Falls back to extracting collaborators from the git repo (if still on
    disk) or from GIT_HISTORY when the ``collaborators`` DASHBOARD_DATA
    metric is missing.

    Returns:
        {
            "nodes": [{"id": str, "name": str, "commits": int, "is_primary": bool, "projects": [str]}],
            "edges": [{"source": str, "target": str, "projects": [str], "weight": int}]
        }
    """
    # Aggregate contributors across projects
    # node_key -> {name, commits, is_primary, projects set}
    node_map: Dict[str, Dict[str, Any]] = {}
    # (source_key, target_key) -> {projects set}  — primary ↔ collaborator
    edge_map: Dict[tuple, set] = {}
    # (source_key, target_key) -> {projects set}  — peer ↔ peer
    peer_edge_map: Dict[tuple, set] = {}

    primary_key = user.get("name") or user.get("github_user") or "You"

    for project in projects:
        collaborators = project.get("metrics", {}).get("collaborators", [])
        if not collaborators or not isinstance(collaborators, list):
            # ---- Fallback 1: live extraction from git repo on disk ----
            project_path = project.get("path", "")
            collaborators = _try_live_extraction(project_path, user)

            # ---- Fallback 2: derive from GIT_HISTORY table ----
            if (not collaborators) and cursor:
                collaborators = _extract_collaborators_from_git_history(
                    cursor, project.get("id", ""), user,
                )

        if not collaborators or not isinstance(collaborators, list):
            continue

        project_title = project.get("title", "Unknown")

        # Collect keys for everyone in this project
        project_keys: List[str] = []
        for collab in collaborators:
            if not isinstance(collab, dict):
                continue
            name = collab.get("name", "").strip()
            if not name:
                continue

            is_primary = collab.get("is_primary", False)
            key = primary_key if is_primary else name

            if key not in node_map:
                node_map[key] = {
                    "name": key,
                    "commits": 0,
                    "is_primary": is_primary,
                    "projects": set(),
                }
            node_map[key]["commits"] += collab.get("commits", 0)
            node_map[key]["projects"].add(project_title)
            if is_primary:
                node_map[key]["is_primary"] = True
            project_keys.append(key)

        # Create edges between the primary user and each collaborator in this project
        for key in project_keys:
            if key == primary_key:
                continue
            edge_key = tuple(sorted([primary_key, key]))
            if edge_key not in edge_map:
                edge_map[edge_key] = set()
            edge_map[edge_key].add(project_title)

        # Create peer edges between non-primary collaborators who share this project
        # Cap to top collaborators by commit count to avoid O(n²) blowup on large repos
        MAX_PEER_COLLABORATORS = 50
        non_primary_keys = [k for k in project_keys if k != primary_key]
        if len(non_primary_keys) > MAX_PEER_COLLABORATORS:
            non_primary_keys = sorted(
                non_primary_keys, key=lambda k: node_map[k]["commits"], reverse=True
            )[:MAX_PEER_COLLABORATORS]
        for ii in range(len(non_primary_keys)):
            for jj in range(ii + 1, len(non_primary_keys)):
                peer_edge_key = tuple(sorted([non_primary_keys[ii], non_primary_keys[jj]]))
                if peer_edge_key not in peer_edge_map:
                    peer_edge_map[peer_edge_key] = set()
                peer_edge_map[peer_edge_key].add(project_title)

    # Build output
    nodes = []
    for key, data in node_map.items():
        nodes.append({
            "id": key,
            "name": data["name"],
            "commits": data["commits"],
            "is_primary": data["is_primary"],
            "projects": sorted(data["projects"]),
        })

    edges = []
    for (source, target), proj_set in edge_map.items():
        edges.append({
            "source": source,
            "target": target,
            "projects": sorted(proj_set),
            "weight": len(proj_set),
            "is_peer": False,
        })
    for (source, target), proj_set in peer_edge_map.items():
        edges.append({
            "source": source,
            "target": target,
            "projects": sorted(proj_set),
            "weight": len(proj_set),
            "is_peer": True,
        })

    # Sort nodes: primary first, then by commits descending
    nodes.sort(key=lambda n: (not n["is_primary"], -n["commits"]))

    return {"nodes": nodes, "edges": edges}


def build_portfolio_model(project_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """Return assembled portfolio model built from the database.
    If project_ids are provided, include only those projects.
    """
    conn = get_connection()
    cursor = conn.cursor()

    user = load_user(cursor)
    projects_raw = load_projects_with_override(cursor, project_ids=project_ids)
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
    daily_activity = get_daily_activity(cursor, projects_raw, project_metrics)

    projects = []
    selected_ids = [pid for pid, *_ in projects_raw]

    for pid, name, score, created_at, last_modified, score_overridden, score_overridden_value, score_override_exclusions in projects_raw:
        metrics = project_metrics.get(pid, {})
        project_skills = skills_map.get(pid, [])
        project_summary = project_summaries.get(pid, "")

        # Fetch stored path for live git fallback
        cursor.execute("SELECT path FROM PROJECT WHERE project_signature = ?", (pid,))
        _path_row = cursor.fetchone()
        project_disk_path = (_path_row[0] if _path_row else "") or ""

        try:
            parsed_exclusions = json.loads(score_override_exclusions) if score_override_exclusions else []
            if not isinstance(parsed_exclusions, list):
                parsed_exclusions = []
        except (json.JSONDecodeError, TypeError):
            parsed_exclusions = []
        
        # Limit skills for display
        limited_skills = limit_skills(project_skills, max_count=10)
        
        # Determine project type based on if we have commit data
        is_github = metrics.get("total_commits", 0) > 0
        
        # Check for thumbnail
        thumbnail_url = None
        cursor.execute("SELECT thumbnail_path FROM PROJECT WHERE project_signature = ?", (pid,))
        thumbnail_row = cursor.fetchone()
        if thumbnail_row and thumbnail_row[0]:
            thumbnail_url = f"/api/portfolio/project/thumbnail/{pid}"
        
        # Extract detailed analysis data
        complexity_analysis = metrics.get("complexity_analysis", {})
        commit_patterns = metrics.get("commit_patterns", {})
        development_patterns = metrics.get("development_patterns", {})
        code_patterns = metrics.get("code_patterns", {})
        contribution_activity = metrics.get("contribution_activity", {})
        
        projects.append({
            "id": pid,
            "title": name,
            "path": project_disk_path,
            "score": float(score) if score else 0,
            "rank": float(score) if score else 0,
            "score_overridden": bool(score_overridden),
            "score_overridden_value": float(score_overridden_value) if score_overridden_value is not None else None,
            "score_override_exclusions": [m for m in parsed_exclusions if isinstance(m, str) and m.strip()],
            "dates": format_dates(created_at, last_modified),
            "created_at": created_at,
            "last_modified": last_modified,
            "type": "GitHub" if is_github else "Local",
            "summary": project_summary,
            "thumbnail_url": thumbnail_url,
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
                "collaborators": metrics.get("collaborators", []),
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

    # Build collaboration network from per-project collaborator data
    # (before closing conn so cursor is still usable for fallback queries)
    collaboration_network = _build_collaboration_network(projects, user, cursor)

    conn.close()

    return {
        "user": user,
        "overview": overview_stats,
        "projects": projects,
        "skills_timeline": skills_timeline,
        "collaboration_network": collaboration_network,
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
            "daily_activity": daily_activity,
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
