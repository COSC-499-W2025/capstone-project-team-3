# Import non_code_analysis_utils & code_analysis_utils to use their functions
from app.utils.non_code_analysis.non_code_analysis_utils import analyze_non_code_files
from app.utils.non_code_analysis.non_3rd_party_analysis import analyze_project_clean 
from app.utils.code_analysis.code_analysis_utils import analyze_parsed_project,analyze_github_project
from app.data.db import get_connection


# TODO : Check if user has given consent for LLM analysis or not
def check_user_consent():  
    """
    This function checks if the user has given consent for LLM analysis.
    
    If user has given consent for LLM analysis
    
    non_code_analysis_results = LLM non-code analysis
    code_analysis_results = LLM code analysis
    
    Else 
    
    non_code_analysis_results = Non-AI non-code analysis
    code_analysis_results = Non-AI code analysis
    
    Returns:
        Two lists: code_analysis_results, non_code_analysis_results
    """
    if True:  # Replace with actual consent check logic
        return True # User has given consent
    else:
        return False # User has not given consent

# TODO : Run code and non-code analysis based on user consent
def run_analyses():
    
    user_LLM_consent = check_user_consent()
    
    if user_LLM_consent:
        non_code_analysis_results = analyze_non_code_files()
        code_analysis_results = analyze_parsed_project(llm_client=True)
        code_analysis_results += analyze_github_project(llm_client=True)
    else:
        non_code_analysis_results = analyze_project_clean()
        code_analysis_results = analyze_parsed_project(llm_client=False)
        code_analysis_results += analyze_github_project(llm_client=False)

    return non_code_analysis_results, code_analysis_results

# TODO : Merge results from code and non-code analysis
def merge_analysis_results(code_results, non_code_results):
    """
    This function merges the results from code analysis and non-code analysis.
    
    Args:
        code_results (list): List of results from code analysis.
        non_code_results (list): List of results from non-code analysis.
        
    Returns:
        merged_results (list): Merged list of results.
    """
    merged_results = code_results + non_code_results # TODO: Implement a more sophisticated merging strategy if needed
    return merged_results

# TODO : # Send Metrics to project Ranker in order to rank results
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
    non_code_metrics = [result['metrics'] for result in non_code_results]
    code_metrics = [result['metrics'] for result in code_results]
    project_ranker = ProjectRanker()

    project_score = project_ranker.rank(code_metrics, non_code_metrics)

    return project_score

# Step 4 TODO : Store ranked Project & Results in the database
def store_results_in_db(ranked_results):
    """
    This function stores the ranked results in the database.
    
    Args:
        ranked_results (list): List of ranked results.
        
    Returns:
        None
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    #insert ranked results into the database

    for result in ranked_results:
        cursor.execute(
            "INSERT INTO PROJECT (project_id, rank) VALUES (%s, %s)",
            (result['project_id'], result['rank'])
        )
        
    # insert analysis results into the database
    for result in ranked_results:
        cursor.execute(
            "INSERT INTO RESUME_SUMMARY (project_id, analysis_data) VALUES (%s, %s)",
            (result['project_id'], result['analysis_data'])
        )
        cursor.execute(
            "INSERT INTO SKILL_ANALYSIS (project_id, analysis_data) VALUES (%s, %s)",
            (result['project_id'], result['analysis_data'])
        )
        cursor.execute(
            "INSERT INTO DASHBOARD_DATA (project_id, analysis_data) VALUES (%s, %s)",
            (result['project_id'], result['analysis_data'])
        )

    conn.commit()
    cursor.close()
    conn.close()
    
    pass

