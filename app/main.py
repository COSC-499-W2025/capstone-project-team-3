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

# Database Entry Point
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
        
        # Initialize LLM manager once (outside the loop)
        llm_manager = LLMConsentManager()
        
        # Main analysis loop - keeps asking for projects until user exits
        while True:
            print("\n" + "="*60)
            print("🔍 PROJECT ANALYSIS SESSION")
            print("="*60)
            
            print("\n--- Project Root Input ---")
            rc = file_input_main()
            print(rc)
            
            # Handle cancellation or error
            if not isinstance(rc, dict) or rc.get("status") != "ok":
                print("\n❌ Project input failed or was cancelled.")
                
                # Ask if user wants to try again or exit
                while True:
                    choice = input("\nWould you like to:\n  ↺ 'retry' - Try entering another project path\n  🚪 'exit'  - Exit the application\n\nChoice (retry/exit): ").lower().strip()
                    
                    if choice in ['exit', 'e', 'quit', 'q']:
                        print("👋 Exiting Project Insights. Goodbye!")
                        break
                    elif choice in ['retry', 'r', 'again', 'y', 'yes']:
                        break
                    else:
                        print("❌ Please enter 'retry' or 'exit'")
                
                if choice in ['exit', 'e', 'quit', 'q']:
                    break
                else:
                    continue  # Go back to project input
            
            # Process projects (we only expect "projects" in rc now)
            if "projects" in rc:
                print(f"Found {rc['count']} projects in ZIP. Scanning each...")
                analysis_results = {}
                
                for i, project_path in enumerate(rc["projects"], 1):
                    project_name = Path(project_path).name
                    print(f"\n{'='*50}")
                    print(f"📁 PROJECT {i}/{rc['count']}: {project_name}")
                    print(f"{'='*50}")
                    
                    print(f"🔍 Scanning project files...")
                    files = run_scan_flow(project_path)
                    
                    if not files:
                        print(f"⚠️ No files to analyze in {project_path}. Skipping.")
                        analysis_results[project_name] = {"status": "skipped", "reason": "no_files"}
                        continue
                    
                    print(f"✅ Found {len(files)} files")
                    
                    analysis_type = llm_manager.ask_analysis_type(project_name)
                    
                    if analysis_type == 'ai':
                        print("🤖 Running AI analysis...")
                        api_key = os.getenv("GEMINI_API_KEY")
                        llm_client = GeminiLLMClient(api_key=api_key)
                        
                        #TODO: add non code starting point for AI analysis
                        
                        #Code analysis
                        #check if git or non git 
                        # if git: call parsing for git -> analysis for git USING LLM
                        # else call parsing for local -> analysis for local USING LLM
                        
                        print(f"✅ starting AI analysis for {project_name}")
                        
                    elif analysis_type == 'local':
                        print("📊 Running local analysis...")
                        
                        #TODO: add non code starting point for local analysis
                        
                        #Code analysis
                        #check if git or non git
                        # if git: call parsing for git -> analysis for git NON LLM
                        # else call parsing for local -> analysis for local NON LLM
                        
                        print(f"✅ starting Local analysis for {project_name}")
                
                # Print analysis summary
                # Merge code and non code analysis into analysis_results
                # Save analysis_results into db 
                # print analysis_results
                
            else:
                print("❌ No projects found to analyze")
            
    
    print("App started successfully")

# Create FastAPI app
app = FastAPI(title="Project Insights")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Project Insights!!"}

if __name__ == "__main__":
    main()
    print("App started Successfully")
    uvicorn.run(app, host="0.0.0.0", port=8000)