# Import Project Ranker to rank projects based on analysis results
# from app.utils.project_ranker import project_ranker

# TODO : Merge results from code and non-code analysis
def merge_analysis_results(code_results, non_code_results, project_name, project_signature):
    """
    This function merges the results from code analysis and non-code analysis.
    
    Args:
        code_results (list): List of results from code analysis.
        
        code_results = {
            
         "Resume_bullets": [resume_bullets],
         "Metrics": {
            "authors": authors,
            "total_commits": total_commits,
            "duration_days": duration_days,
            "files_added": files_added,
            "files_modified": files_modified,
            "files_deleted": files_deleted,
            "total_files_changed": total_files_changed,
            "code_files_changed": code_files_changed,
            "doc_files_changed": doc_files_changed,
            "test_files_changed": test_files_changed,
            "roles": roles,
            "technical_keywords": technical_keywords,
            "development_patterns": development_patterns
        }
        }
        
        
        non_code_results (list): List of results from non-code analysis.
        
        non_code_results = {

        "summary":"Summary of the project",
        "skills" : {
            "technical_skills": [],
            "soft_skills": []
        },
         "Resume_bullets": [resume_bullets],
         "Metrics": {
            "word_count": word_count,
            "completeness_score": completeness_score,
            "activity_type_contribution": activity_type_contribution,
        }

        *Assuming that once Analysis is done, distinction between code/non_code skills & metrics is negligible/not necessary to store*

    Returns:
        merged_results (list): Merged list of results.
        
        analysis_results = {
            "summary":"Summary of the project",
            "skills" : {
                "technical_skills": [],
                "soft_skills": []
            },
             "Resume_bullets": [resume_bullets],
             "Metrics": {
                "authors": authors,
                "total_commits": total_commits,
                "duration_days": duration_days,
                "files_added": files_added,
                "files_modified": files_modified,
                "files_deleted": files_deleted,
                "total_files_changed": total_files_changed,
                "code_files_changed": code_files_changed,
                "doc_files_changed": doc_files_changed,
                "test_files_changed": test_files_changed,
                "roles": roles,
                "technical_keywords": technical_keywords,
                "development_patterns": development_patterns,
                "word_count": word_count,
                "completeness_score": completeness_score,
                "activity_type_contribution": activity_type_contribution,
            }
        
    """
    
    # To be stored in DASHBOARD_DATA & SKILL_ANALYSIS & RESUME_SUMMARY & PROJECT Tables
    
    code_metrics = code_results.get("Metrics", {})
    non_code_metrics = non_code_results.get("Metrics", {})

    code_resume_bullets = code_results.get("Resume_bullets", [])
    non_code_resume_bullets = non_code_results.get("Resume_bullets", [])
    
    non_code_skills = non_code_results.get("skills", {})
    code_skills = code_results.get("Metrics", {}).get("roles", {})

    summary = non_code_results.get("summary", "")
    
    # Send Metrics to project Ranker in order to rank results
    project_rank = get_project_rank(code_metrics, non_code_metrics)

    # Merge Results
    merged_skills = {
        "technical_skills": code_skills + non_code_skills.get("technical_skills", []),
        "soft_skills": non_code_skills.get("soft_skills", [])
    }
    merged_resume_bullets = code_resume_bullets + non_code_resume_bullets
    merged_metrics = {**code_metrics, **non_code_metrics} # Merge dictionaries since keys for each are unique

    merged_results = {
        "summary": summary,
        "skills": merged_skills,
        "resume_bullets": merged_resume_bullets,
        "metrics": merged_metrics
    }

    # Step 4 TODO : Store ranked Project & Results in the database
    store_results_in_db(project_name, merged_results, project_rank, project_signature)



def get_project_rank(code_results, non_code_results):
    """
    This function calls the project_ranker, sends the code and non-code metrics/results in order to rank the overall project.

    Args:
        code_results (list): List of results from code analysis.
        non_code_results (list): List of results from non-code analysis.
        project_ranker (object): An instance of the project ranker.
        
    Returns:
        Ranked Score for the Project.
    """
    ranked_results = project_ranker.rank(code_results, non_code_results)
    return ranked_results


def store_results_in_db(project_name, merged_results, project_rank, project_signature):
    """
    This function stores the ranked results in the database.
    
    Args:
        ranked_results (list): List of ranked results.
        
    Returns:
        None
    """
    
    # TODO : Use project_signature to identify the project in DB
    
    # TODO : Update PROJECT table with summary and rank
    
    # TODO : Store skills in SKILL_ANALYSIS table
    
    # TODO : Store resume bullets in RESUME_SUMMARY table
    
    # TODO : Store metrics in DASHBOARD_DATA table
    
    # TODO : Commit changes to DB

    pass

