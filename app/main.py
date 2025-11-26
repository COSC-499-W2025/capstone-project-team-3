"""
Minimal Python entry point.
"""
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from app.client.llm_client import GeminiLLMClient
from app.data.db import init_db, seed_db
from app.cli.consent_manager import ConsentManager
from app.cli.user_preference_cli import UserPreferences
from app.cli.file_input import main as file_input_main 
from app.manager.llm_consent_manager import LLMConsentManager
from app.utils.scan_utils import run_scan_flow 
import uvicorn
import os
import sys

load_dotenv()

# Database Entry Point#
def main():
    init_db()  # creates the SQLite DB + tables
    seed_db()  # automatically populate test data
    print("Database started")

    # Check for the consent
    consent_manager = ConsentManager()
    if not consent_manager.enforce_consent():
        print("\n Cannot start application without consent. Please provide consent to proceed.")
        sys.exit(1)

    # Manage user preferences
    user_pref = UserPreferences()
    try:
        user_pref.manage_preferences()
    finally:
        user_pref.store.close()
        print("User preferences stored successfully.")

    # Check if PROMPT_ROOT is enabled
    prompt_root = os.environ.get("PROMPT_ROOT", "0")
    if prompt_root in ("1", "true", "True", "yes"):
        print("\n--- Project Root Input ---")
        rc = file_input_main()
        if rc != 0:
            print("Root input step failed or was cancelled. Exiting.")
            sys.exit(rc)
        # If ZIP, scan each project in the projects array
        # to test flow we need to first have values in the project attribute in rc 
        if "projects" in rc:
            print(f"Found {rc['count']} projects in ZIP. Scanning each...")
            llm_manager = LLMConsentManager()
            analysis_results = {}
            
            for project_path in rc["projects"]:
                print(f"\nScanning project: {project_path}")
                files = run_scan_flow(project_path)
                if not files:
                    print(f"No files to analyze in {project_path}. Skipping.")
                    continue
                else:
                    project_name = Path(project_path).name
                    analysis_type = llm_manager.ask_analysis_type(project_name)
                    if analysis_type == 'ai':
                        # run ai analysis
                        print("run ai analysis")
                        api_key = os.getenv("GEMINI_API_KEY")
                        llm_client = GeminiLLMClient(api_key=api_key)
                        #TODO: add non code starting point for AI analysis
                        
                        #Code analysis
                        #check if git or non git 
                        # if git: call parsing for git -> analysis for git USING LLM
                        # else call parsing for local -> analysis for local USING LLM
                        
                    elif analysis_type == 'local':
                        # run local analysis
                        #TODO: add non code starting point for local analysis
                        
                        #Code analysis
                        #check if git or non git
                        # if git: call parsing for git -> analysis for git NON LLM
                        # else call parsing for local -> analysis for local NON LLM
                    
                    
                        print("run local analysis")
                # Merge code and non code analysis into analysis_results
                # Save analysis_results into db 
                # print analysis_results  
        else:
            print("No projects to be analyzed")
    
    print("App started successfully")


    
# Create FastAPI app
app = FastAPI(title="Project Insights")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Project Insights!!",
              }

if __name__ == "__main__":
    main()
    print("App started Succesfully")
    uvicorn.run(app, host="0.0.0.0", port=8000)
