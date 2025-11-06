
from cmd import PROMPT

parsed_file_structure = {
"path": str(file_path),
"type": "pdf",  # Example values; one of ["pdf", "docx", "pptx", "txt"]
"name": "capstone_project_proposal_v3.pdf",
"file_size": 245760,  # bytes; used for size filtering
"content":"Project Overview: This proposal outlines goals, milestones, stakeholders, and risks for the Team 3 capstone...",
"success": False,
"error": ""
}


llm1_summary = {
"key_topics": ["project planning", "requirements analysis", "system architecture"],
"summary" : "This document proposes an event-driven architecture, defines scope, milestones (M1-M4), risks (data latency, OCR quality), and roles for Team 3."
}

aggregated_project = {
"project_title": "Team 3 Event-Driven Analytics Platform",
"Summary_union": [
  "Ingest non-code artifacts to derive resume-ready highlights",
  "Map extracted content to skills and contributions",
  "Summarize deliverables across milestones"
],
"key_topics_union": [
  "project planning", "requirements analysis", "system architecture"
],

}

llm2_metrics = {   
"Resume_Points" :  [
  "Led requirements workshops to define MVP scope and success criteria",
  "Designed event-driven ingestion pipeline leveraging queue-based decoupling"
],
"Skill_Analysis" : [
  "Python (document parsing, text pre-processing)",
  "Prompt engineering (structured prompts, token budgeting)",
  "System design (event-driven architecture, observability)"
],
"Project_Contributions" : [
  "Implemented non-code parsing and summarization pipeline (LLM1 integration)",
  "Authored architecture proposal and milestone plans"
] #*Project_Contribution section is TBD will leave this attribute here for now
}

Final_Result = {
"Project_Signature" : "Team 3 • Event-Driven Analytics Platform • 2025",
"Resume_data" : "Led requirements and designed event-driven ingestion; built LLM summarization pipeline.",
"Extracted_Skills" : "Requirement Gathering; Prompt Engineering; System Design; Built Data Pipelines",
"Contributions " : "Parsing pipeline; LLM1 integration; Architecture proposal"
}

#Step 1: Parse non-code files
# Done through parsing_utils.py
#TODO:Check user name matches with the author name in the metadata,
# Only analyze file if user name from DB matches with the author name in the metadata


#Step 2: Send non code parsed content to LLM (using TextRank Local Pre-processing)
#  *This necessary step may modifiy our consent management class in terms of privacy

def pre_process_non_code_files(parsed_files):
    """
    This function pre-processes parsed project data and generates a concise file summary and list of key topics 
    for the second LLM to use to generate metrics.
    Files that exceed a certain size should not be processed. 
    returns llm1_summary
    """
    pass


#Step 3: Aggregate non code summaries into a single analyzable project
def aggregate_non_code_summaries(llm1_summary):
    """
    This function aggregates the preprocssed llm1 summary of non-code files into one single project for
    the second LLM to analyze.
    Returns aggregated_project.
    """
    pass


# Step 4: Generate prompt for second LLM
def create_non_code_analysis_prompt(aggregated_project, llm2_metrics):
    """
    Create a structured prompt for AI agent analysis using the aggregated llm1 summaries.
    Returns formatted prompt string that follows the structure of llm2_metrics.
    """
    pass

# Step 4: Analyze summries using the second LLM
def generate_non_code_insights(PROMPT):
    """
    Generates llm2_metrics by calling LLM2 with the formatted prompt.
    Returns Final_Result
    """
    pass

   

# Step 5: Store results
def store_non_code_analysis_results(final_result):
    """
    Store analysis results in RESUME table and SKILLS table in database.
    """
    pass


def analyze_non_code_files(parsed_files):
    """
    Entry & Main Flow: pre-process files (LLM1), aggregate summaries, generate prompt,
    call LLM2, store analysis results.
    """
    # 1. Pre-Process files (Use LLM1)
    pre_process_non_code_files(parsed_files)

    # 2. Aggregate summaries 
    aggregate_non_code_summaries(llm1_summary)
    
    # 3. Generate Analysis Prompt
    create_non_code_analysis_prompt(aggregated_project)
    
    # 4. Call LLM2 for Analysis
    generate_non_code_insights(PROMPT)

    # 5. Store Data
    store_non_code_analysis_results(Final_Result)