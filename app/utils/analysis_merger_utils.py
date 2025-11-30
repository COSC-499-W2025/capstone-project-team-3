# Import Project Ranker to rank projects based on analysis results
# from app.utils.project_ranker import project_ranker
import json
from app.shared.test_data.analysis_results_text import code_analysis_results, non_code_analysis_result, git_code_analysis_results, project_name, project_signature
from app.utils.non_code_analysis.non_code_analysis_utils import _sumy_lsa_summarize
# Merge results from code and non-code analysis
def merge_analysis_results(code_analysis_results, non_code_analysis_results, project_name, project_signature):
    """
    This function merges the results from code analysis and non-code analysis.
    
    Args:
        code_results (list): List of results from code analysis.
        # Non-git related code metrics/skills extracted from code analysis
        code_results = {
            
         "Resume_bullets": [resume_bullets],
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
        
        #git related non-code metrics/skills extracted from non-code analysis
        code_results = {
            
         "Resume_bullets": [resume_bullets],
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
        
    """
    
    # Extract metrics 
    code_metrics = code_analysis_results.get("Metrics", {})
    non_code_metrics = non_code_analysis_results.get("Metrics", {})

    # Extract & Format resume bullets
    code_resume_bullets = code_analysis_results.get("resume_bullets", [])
    code_resume_bullets = [f"{bullet.strip()}." for bullet in code_resume_bullets if bullet.strip()]

    non_code_resume_bullets = non_code_analysis_results.get("resume_bullets", [])
    non_code_resume_bullets = [f"{bullet.strip()}." for bullet in non_code_resume_bullets if bullet.strip()]
    
    # Extract skills (use technical keywords from code analysis)
    code_skills = code_analysis_results.get("Metrics", {}).get("technical_keywords", [])
    non_code_skills = non_code_analysis_results.get("skills", {})

    # Extract project summary from non-code summary & code resume bullets
    # use NLP summarization to generate concise summary
    #Make resume bullets into sentences for summarization
    summary = _sumy_lsa_summarize(non_code_analysis_results.get("summary", "") + " " + " ".join(code_resume_bullets),5)

    
    # Send Metrics to project Ranker in order to rank results
    project_rank = get_project_rank(code_metrics, non_code_metrics)

    # Merge Skills
    merged_skills = {
        "technical_skills": code_skills + non_code_skills.get("technical_skills", []),
        "soft_skills": non_code_skills.get("soft_skills", [])
    }
    
    # Merge Resume Bullets
    merged_resume_bullets = code_resume_bullets + non_code_resume_bullets
    
    # Merge Metrics
    merged_metrics = {**code_metrics, **non_code_metrics} # Merge dictionaries since keys for each are unique
    
    # Final Merged Results to be stored in DB
    merged_results = {
        "summary": summary,
        "skills": merged_skills,
        "resume_bullets": merged_resume_bullets,
        "metrics": merged_metrics
    }
    
    print("Merged Results:\n", json.dumps(merged_results, indent=4))
    
    store_results_in_db(project_name, merged_results, project_rank, project_signature)
    
    return merged_results

    # TO DO: Store ranked Project & Results in the database
    


def get_project_rank(code_metrics, non_code_metrics):
    """
    This function calls the project_ranker, sends the code and non-code metrics/results in order to rank the overall project.

    Args:
        code_metrics (list): List of metrics from code analysis.
        non_code_metrics (list): List of metrics from non-code analysis.
        project_ranker (object): An instance of the project ranker.
        
    Returns:
        Ranked Score for the Project.
    """
    # TODO : Call project ranker
    # project_score = project_ranker.rank(code_metrics, non_code_metrics)
    project_score = None  # Placeholder for actual project ranking logic
    if project_score is not None:
        return project_score
    else:
        project_score = 0
    
    return project_score


def store_results_in_db(project_name, merged_results, project_rank, project_signature):
    """
    This function stores the ranked results in the database.
    
    Args:
        ranked_results (list): List of ranked results.
        
    Returns:
        None
    """
     # To be stored in DASHBOARD_DATA & SKILL_ANALYSIS & RESUME_SUMMARY & PROJECT Tables
    
    # TODO : Use project_signature to identify the project in DB
    
    # TODO : Update PROJECT table with summary and rank
    
    # TODO : Store skills in SKILL_ANALYSIS table
    
    # TODO : Store resume bullets in RESUME_SUMMARY table
    
    # TODO : Store metrics in DASHBOARD_DATA table
    
    # TODO : Commit changes to DB

    pass

def main():
    # Merge analysis results for testing
    merged_results = merge_analysis_results(code_analysis_results, non_code_analysis_result, project_name, project_signature)
    
    
if __name__ == "__main__":
    main()