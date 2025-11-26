# Import non_code_analysis_utils & code_analysis_utils to use their functions
from app.utils.non_code_analysis.non_code_analysis_utils import run_non_code_llm_analysis, run_non_code_local_analysis
from app.utils.code_analysis.code_analysis_utils import run_code_llm_analysis, run_code_local_analysis


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

    return None

# TODO : Run code and non-code analysis based on user consent

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
    merged_results = code_results + non_code_results
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
    ranked_results = project_ranker.rank(code_results, non_code_results)
    return ranked_results

# Step 4 TODO : Store ranked Project & Results in the database
def store_results_in_db(ranked_results):
    """
    This function stores the ranked results in the database.
    
    Args:
        ranked_results (list): List of ranked results.
        
    Returns:
        None
    """
    # Database storage logic goes here
    pass

