# Import project scorer to score projects based on analysis results
# from app.utils.project_ranker import project_ranker
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from app.utils.non_code_analysis.non_code_analysis_utils import _sumy_lsa_summarize
from app.data.db import get_connection
from app.utils.project_score import compute_overall_project_contribution_score
from app.utils.git_utils import detect_git, get_repo, is_repo_empty
from app.cli.git_code_parsing import _get_preferred_author_email
MAX_SKILLS = 10 #Maximum number of skills to be stored per project (TDB: adjust based on some condition)
MAX_BULLETS = 5 #Maximum number of resume bullets to be stored per project (TBD: adjust based on some condition)
MAX_SENTENCES = 5 #Maximum number of sentences in summary (TBD: adjust based on some condition)

# Skill to file extension mapping for date inference
SKILL_TO_EXTENSIONS = {
    # Programming Languages
    "Python": [".py", ".pyx", ".pyw"],
    "Java": [".java"],
    "JavaScript": [".js", ".mjs", ".cjs"],
    "TypeScript": [".ts"],
    "C#": [".cs"],
    "C++": [".cpp", ".cc", ".cxx", ".h", ".hpp"],
    "C": [".c", ".h"],
    "Ruby": [".rb"],
    "PHP": [".php"],
    "Swift": [".swift"],
    "Kotlin": [".kt", ".kts"],
    "Go": [".go"],
    "Rust": [".rs"],
    "Scala": [".scala"],
    "Perl": [".pl", ".pm"],
    "R": [".r", ".R"],
    "Dart": [".dart"],
    "Objective-C": [".m", ".mm"],
    "Lua": [".lua"],
    "Haskell": [".hs"],
    "Elixir": [".ex", ".exs"],
    "Clojure": [".clj", ".cljs"],
    "Groovy": [".groovy"],
    "Shell": [".sh", ".bash"],
    "PowerShell": [".ps1"],
    # Web Technologies
    "HTML": [".html", ".htm"],
    "CSS": [".css"],
    "SCSS": [".scss"],
    "SASS": [".sass"],
    "Vue": [".vue"],
    "React": [".jsx", ".tsx"],
    "Angular": [".ts"],
    "Svelte": [".svelte"],
    # Frameworks/Libraries (may share extensions)
    "Django": [".py"],
    "Flask": [".py"],
    "Spring": [".java"],
    "Express": [".js", ".ts"],
    "Node.js": [".js", ".ts"],
    "ASP.NET": [".cs", ".aspx"],
    "Rails": [".rb"],
    # Data & Config
    "SQL": [".sql"],
    "JSON": [".json"],
    "YAML": [".yaml", ".yml"],
    "XML": [".xml"],
    "Markdown": [".md"],
    # Others
    "Jupyter": [".ipynb"],
    "LaTeX": [".tex"],
    "Dockerfile": ["Dockerfile"],
}

# Merge results from code and non-code analysis
def merge_analysis_results(code_analysis_results, non_code_analysis_results, project_name, project_signature):
    """
    This function merges the results from code analysis and non-code analysis.
    
    Args:
        code_results (list): List of results from code analysis.
        # Non-git related code metrics/skills extracted from code analysis
        code_results = {
            
         "resume_bullets": [resume_bullets],
         "Metrics": {
            "languages": metrics["languages"],
            "total_files": metrics["total_files"],
            "total_lines": metrics["total_lines"],
            "functions": metrics["functions"],
            "components": metrics["components"],
            "classes": metrics["classes"],
            "roles": metrics["roles"],
            "average_function_length": metrics["average_function_length"],
            "average_comment_ratio": metrics["average_comment_ratio"],
            "code_files_changed": metrics["code_files_changed"],
            "doc_files_changed": metrics["doc_files_changed"],
            "test_files_changed": metrics["test_files_changed"],
            "technical_keywords": technical_keywords,
            "code_patterns": code_patterns,
            "complexity_analysis": complexity_analysis
        }
        }
        
        #git related code metrics/skills extracted from code analysis
        code_results = {
            
         "resume_bullets": [resume_bullets],
         "Metrics": {
            "authors": metrics["authors"],
            "total_commits": metrics["total_commits"],
            "duration_days": metrics["duration_days"],
            "files_added": metrics["files_added"],
            "files_modified": metrics["files_modified"],
            "files_deleted": metrics["files_deleted"],
            "total_files_changed": metrics["total_files_changed"],
            "code_files_changed": metrics["code_files_changed"],
            "doc_files_changed": metrics["doc_files_changed"],
            "test_files_changed": metrics["test_files_changed"],
            "roles": metrics["roles"],
            "technical_keywords": technical_keywords,
            "development_patterns": development_patterns
        }
        }

        non_code_results (dict): Results from non-code analysis.
        
        non_code_results = {
            "project_summary": "Summary of the project",
            "skills": {
                "technical_skills": [],
                "soft_skills": []
            },
            "resume_bullets": [resume_bullets],
            "Metrics": {
                "completeness_score": completeness_score,
                "word_count": word_count,
                "contribution_activity": {
                    "doc_type_counts": {"README": 1, "DESIGN_DOCUMENT": 2},
                    "doc_type_frequency": {"README": 5, "DESIGN_DOCUMENT": 10}
                }
            }
        }

        *Assuming that once Analysis is done, distinction between code/non_code skills & metrics is negligible/not necessary to store*

    Returns:
        merged_results (dict): Merged results.
        
    """
    # ------------------------------- EXTRACTION LOGIC ----------------------------------
    
    # Add validation for empty or None inputs
    if not code_analysis_results:
        print("⚠️ WARNING: code_analysis_results is empty or None")
        code_analysis_results = {"Metrics": {}, "resume_bullets": []}
    if not non_code_analysis_results:
        print("⚠️ WARNING: non_code_analysis_results is empty or None")
        non_code_analysis_results = {"Metrics": {}, "resume_bullets": [], "skills": {}, "project_summary": ""}
    
    print(f"   - Keys: {list(non_code_analysis_results.keys())}")
    print(f"   - project_summary: '{non_code_analysis_results.get('project_summary', 'KEY NOT FOUND')[:100]}'...")
    print(f"   - resume_bullets count: {len(non_code_analysis_results.get('resume_bullets', []))}")
    print(f"   - skills: {non_code_analysis_results.get('skills', {})}")
    
    # Detect git metrics (if git present, send git metrics to project scorer)
    if 'authors' in code_analysis_results.get("Metrics", {}):
        git_metrics = code_analysis_results.get("Metrics", {})
        code_metrics = None
    else:
        git_metrics = None
        code_metrics = code_analysis_results.get("Metrics", {})
       
    # Extract non-code metrics   
    non_code_metrics = non_code_analysis_results.get("Metrics", {})
    
     # Send metrics to project scorer in order to compute results
    project_score = get_project_score(code_metrics, non_code_metrics, git_metrics)

    # Re-initialize metrics for merging (git vs local does not matter for storage)
    code_metrics = code_analysis_results.get("Metrics", {})
    
    # Extract & Format code resume bullets
    # Accept either 'resume_bullets' or 'Resume_bullets' (tests/use-cases vary)
    code_resume_bullets = code_analysis_results.get("resume_bullets") or code_analysis_results.get("Resume_bullets") or []
    code_resume_bullets = [
    bullet.strip() if bullet.strip().endswith('.') else bullet.strip() + '.'
    for bullet in code_resume_bullets if bullet.strip() ]

    # Extract & Format non-code resume bullets
    non_code_resume_bullets = non_code_analysis_results.get("resume_bullets", [])
    non_code_resume_bullets = [bullet.strip() if bullet.strip().endswith('.') else bullet.strip() + '.'
    for bullet in non_code_resume_bullets if bullet.strip()]
    
    # Extract skills (use technical roles & keywords from code analysis)
    code_skills = code_analysis_results.get("Metrics", {}).get("roles", []) + code_analysis_results.get("Metrics", {}).get("languages", [])
    non_code_skills = non_code_analysis_results.get("skills", {}) if non_code_analysis_results else {}
    non_code_tech_skills = non_code_skills.get("technical_skills", [])
    non_code_soft_skills = non_code_skills.get("soft_skills", [])
    
    # Filter non-code technical skills by code languages
    code_langs = set(code_metrics.get("languages", []))
    if code_langs:
        filtered_non_code_tech_skills = [
            s for s in non_code_tech_skills
            if any(lang.lower() in s.lower() for lang in code_langs)
        ]
    else:
        filtered_non_code_tech_skills = []
    
    # Build summary based on available data from non-code summary & code resume bullets 
    # ✅ CHANGED: "summary" -> "project_summary"
    summary = build_summary(
        code_resume_bullets, 
        non_code_analysis_results.get("project_summary", ""),
        MAX_SENTENCES, 
        project_name
    )

    # -------------------------------------------- MERGING LOGIC ----------------------------------------

    # Merge Skills (Ensure a proportional representation of code and non-code skills)
    merged_tech_skills = balance_merge(code_skills, filtered_non_code_tech_skills, MAX_SKILLS)
    
    merged_skills = {
        "technical_skills": merged_tech_skills,
        "soft_skills": non_code_soft_skills
    }
    
    # Merge Resume Bullets (Ensure a proportional representation of code and non-code resume bullets)
    merged_resume_bullets = balance_merge(code_resume_bullets, non_code_resume_bullets, MAX_BULLETS)

    # Merged Metrics (Merge dictionaries since keys for each are unique)
    merged_metrics = {**code_metrics, **non_code_metrics} 
    
    # Final merged results & project score to be stored in DB
    merged_results = {
        "summary": summary,
        "skills": merged_skills,
        "resume_bullets": merged_resume_bullets,
        "metrics": merged_metrics
    }
    
    # Store scored project & results in the database
    store_results_in_db(project_name, merged_results, project_score, project_signature)
        
    return merged_results

def balance_merge(code_list, non_code_list, max_items=10):
    code_count = len(code_list)
    non_code_count = len(non_code_list)
    if code_count and non_code_count:
        half = max_items // 2
        code_take = min(half, code_count)
        non_code_take = min(half, non_code_count)
        remaining = max_items - (code_take + non_code_take)
        # Fill remaining from the larger pool
        if code_count - code_take > non_code_count - non_code_take:
            code_take += remaining
        else:
            non_code_take += remaining
        return code_list[:code_take] + non_code_list[:non_code_take]
    elif code_count:
        return code_list[:max_items]
    else:
        return non_code_list[:max_items]

def remove_past_tense_action_verb(bullet):
    """
    Removes the leading past tense action verb from a resume bullet if present.
    Example: 'Implemented RESTful endpoints...' -> 'RESTful endpoints...'
    """
    # Common past tense action verbs
    past_tense_verbs = [
        "implemented", "optimized", "refactored", "developed", "integrated", "created", "configured",
        "applied", "monitored", "collaborated", "designed", "produced", "tested", "resolved", "documented"
    ]
    pattern = r"^(" + "|".join(past_tense_verbs) + r")\b\s*"
    bullet = bullet.strip()
    bullet = bullet[:-1] if bullet.endswith('.') else bullet
    bullet = bullet[0].lower() + bullet[1:] if bullet else bullet
    bullet = re.sub(pattern, "", bullet, flags=re.IGNORECASE)
    return bullet.strip()

def build_summary(code_resume_bullets, non_code_summary,MAX_SENTENCES, project_name):
    """
    This function builds a summary based on code resume bullets and non-code summary.
    
    Args:
        code_resume_bullets (list): List of resume bullets from code analysis.
        non_code_summary (str): Summary from non-code analysis.
        
    Returns:
        summary (str): Generated summary.
    """
    print(f"   - code_resume_bullets: {len(code_resume_bullets) if code_resume_bullets else 0} items")
    print(f"   - non_code_summary: '{non_code_summary[:100] if non_code_summary else 'EMPTY'}...'")
    print(f"   - project_name: {project_name}")
    
    achievements = ", ".join(remove_past_tense_action_verb(b) for b in code_resume_bullets[:MAX_SENTENCES]) if code_resume_bullets else ""
    
    if non_code_summary and not code_resume_bullets:
        result = non_code_summary.strip()
    elif not non_code_summary and code_resume_bullets:
        result = f"Key technical achievements include : {achievements}."
    elif non_code_summary and code_resume_bullets:
        result = f"{non_code_summary.strip()} Key technical achievements include : {achievements}."
    else:
        result = f"User contributed to the production of {project_name}"
    
    print(f"   ✅ Generated summary: '{result[:100]}...'")
    return result


def get_project_score(code_metrics, non_code_metrics, git_metrics):
    """
    This function calls the project scorer, sends the code and non-code metrics/results in order to score the overall project.

    Args:
        code_metrics (list): List of metrics from code analysis.
        non_code_metrics (list): List of metrics from non-code analysis.
        project_ranker (object): An instance of the project scorer.
        
    Returns:
        Score for the project.
    """
  
    project_score = compute_overall_project_contribution_score(code_metrics,git_metrics, non_code_metrics )
    if project_score is not None:
        return project_score
    else:
        project_score = 0
    
    return project_score

def _get_skill_extensions(skill: str) -> List[str]:
    """
    Get file extensions associated with a skill.
    Case-insensitive matching.
    
    Args:
        skill: The skill name (e.g., "Python", "javascript", "C++")
    
    Returns:
        List of file extensions (e.g., [".py", ".pyx"])
    """
    # Try exact match first (case-insensitive)
    for skill_name, extensions in SKILL_TO_EXTENSIONS.items():
        if skill.lower() == skill_name.lower():
            return extensions
    
    # Try partial match (skill contains or is contained in)
    skill_lower = skill.lower()
    for skill_name, extensions in SKILL_TO_EXTENSIONS.items():
        if skill_lower in skill_name.lower() or skill_name.lower() in skill_lower:
            return extensions
    
    return []

def _infer_skill_dates_from_git(project_path: str, skills: List[str]) -> Dict[str, Optional[str]]:
    """
    Infer skill dates from Git history by finding when files with related
    extensions were first committed by the current user.
    
    Args:
        project_path: Path to the project directory
        skills: List of skill names
    
    Returns:
        Dictionary mapping skill -> date string (YYYY-MM-DD) or None
    """
    skill_dates = {}
    
    # Check if it's a Git repository
    if not detect_git(project_path):
        return {skill: None for skill in skills}
    
    try:
        repo = get_repo(project_path)
        
        # Check if repo is empty
        if is_repo_empty(project_path):
            return {skill: None for skill in skills}
        
        # Get the user's preferred author email for filtering
        _, user_email = _get_preferred_author_email()
        
        # For each skill, find the earliest commit with matching file extensions
        for skill in skills:
            extensions = _get_skill_extensions(skill)
            if not extensions:
                skill_dates[skill] = None
                continue
            
            earliest_date = None
            
            # Iterate through all commits (oldest first)
            try:
                for commit in repo.iter_commits(rev="--all", reverse=True):
                    # Filter commits by user email if available
                    if user_email and commit.author.email != user_email:
                        continue
                    # Filter commits by user email if available
                    if user_email and commit.author.email != user_email:
                        continue
                    
                    # Check if this commit touched files with relevant extensions
                    parent = commit.parents[0] if commit.parents else None
                    
                    if parent is None:
                        # Initial commit - check all files
                        for item in commit.tree.traverse():
                            if hasattr(item, 'path'):
                                file_path = item.path
                                # Check if any extension matches
                                for ext in extensions:
                                    if ext == "Dockerfile":
                                        # Special case for Dockerfile
                                        if "dockerfile" in file_path.lower():
                                            earliest_date = datetime.fromtimestamp(
                                                commit.committed_date
                                            ).strftime('%Y-%m-%d')
                                            break
                                    elif file_path.endswith(ext):
                                        earliest_date = datetime.fromtimestamp(
                                            commit.committed_date
                                        ).strftime('%Y-%m-%d')
                                        break
                                if earliest_date:
                                    break
                    else:
                        # Check diff for files with matching extensions
                        diffs = commit.diff(parent)
                        for diff_item in diffs:
                            file_path = diff_item.b_path or diff_item.a_path
                            if file_path:
                                for ext in extensions:
                                    if ext == "Dockerfile":
                                        if "dockerfile" in file_path.lower():
                                            earliest_date = datetime.fromtimestamp(
                                                commit.committed_date
                                            ).strftime('%Y-%m-%d')
                                            break
                                    elif file_path.endswith(ext):
                                        earliest_date = datetime.fromtimestamp(
                                            commit.committed_date
                                        ).strftime('%Y-%m-%d')
                                        break
                            if earliest_date:
                                break
                    
                    if earliest_date:
                        break  # Found the first commit with this skill
                
                skill_dates[skill] = earliest_date
            except Exception:
                skill_dates[skill] = None
    
    except Exception:
        return {skill: None for skill in skills}
    
    return skill_dates

def store_results_in_db(project_name, merged_results, project_score, project_signature):
    """
    This function stores the scored results in the database.
    To be stored in DASHBOARD_DATA & SKILL_ANALYSIS & RESUME_SUMMARY & PROJECT Tables
    
    Args:
        ranked_results (list): List of scored results.
        
    Returns:
        None
    """
    # Get DB connection 
    conn = get_connection()
    cur = conn.cursor()
        
    # Use project_signature to identify the project in DB
    # Ensure project exists
    cur.execute("SELECT 1 FROM PROJECT WHERE project_signature = ?", (project_signature,))
    if not cur.fetchone():
        cur.execute("""
        INSERT INTO PROJECT (project_signature, name, summary, score, score_overridden, score_overridden_value)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (project_signature, project_name, merged_results["summary"], project_score, 0, None))
    else:
        # Update summary if project already exists
        cur.execute("""
        UPDATE PROJECT
        SET name = ?,
            summary = ?,
            score = ?,
            score_overridden = 0,
            score_overridden_value = NULL
        WHERE project_signature = ?
        """, (project_name, merged_results["summary"], project_score, project_signature))
    
        # Delete existing records to avoid duplicates
        cur.execute("DELETE FROM SKILL_ANALYSIS WHERE project_id = ?", (project_signature,))
        cur.execute("DELETE FROM RESUME_SUMMARY WHERE project_id = ?", (project_signature,))
        cur.execute("DELETE FROM DASHBOARD_DATA WHERE project_id = ?", (project_signature,))

    # Store skills in SKILL_ANALYSIS table with smart date inference
    # Get project path for Git history analysis
    cur.execute("SELECT path, created_at FROM PROJECT WHERE project_signature = ?", (project_signature,))
    project_info = cur.fetchone()
    project_path = project_info[0] if project_info else None
    project_created_at = project_info[1] if project_info else None
    
    # Extract date portion (YYYY-MM-DD) from project_created_at
    fallback_date = None
    if project_created_at:
        try:
            # Handle both "YYYY-MM-DD HH:MM:SS" and "YYYY-MM-DD" formats
            fallback_date = project_created_at.split()[0] if ' ' in project_created_at else project_created_at.split('T')[0]
        except:
            fallback_date = None
    
    # Collect all skills for batch date inference
    all_skills = (
        merged_results["skills"]["soft_skills"] + 
        merged_results["skills"]["technical_skills"]
    )
    
    # Infer dates from Git history if project path is available
    skill_dates = {}
    if project_path and Path(project_path).exists():
        skill_dates = _infer_skill_dates_from_git(project_path, all_skills)
    
    # Store soft skills
    for skill in merged_results["skills"]["soft_skills"]:
        skill_date = skill_dates.get(skill) or fallback_date
        cur.execute("""
        INSERT INTO SKILL_ANALYSIS (project_id, skill, source, date) VALUES (?, ?, ?, ?)
        """, (project_signature, skill, "soft_skill", skill_date))

    # Store technical skills
    for skill in merged_results["skills"]["technical_skills"]:
        skill_date = skill_dates.get(skill) or fallback_date
        cur.execute("""
        INSERT INTO SKILL_ANALYSIS (project_id, skill, source, date) VALUES (?, ?, ?, ?)
        """, (project_signature, skill, "technical_skill", skill_date))

    # Store resume bullets in RESUME_SUMMARY table
    cur.execute("""
    INSERT INTO RESUME_SUMMARY (project_id, summary_text) VALUES (?, ?)
    """, (project_signature, json.dumps(merged_results["resume_bullets"])))

    # Store metrics in DASHBOARD_DATA table
    for key, value in merged_results["metrics"].items():
        # Flatten if value is a dictionary or list type
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        cur.execute("""
            INSERT INTO DASHBOARD_DATA (project_id, metric_name, metric_value)
        VALUES (?, ?, ?)
    """, (project_signature, key, value))

    # Commit changes to DB
    conn.commit()
    
    # Close cursor and connection
    cur.close()
    conn.close()
