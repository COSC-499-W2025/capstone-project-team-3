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
from app.utils.env_utils import check_gemini_api_key
from app.utils.scan_utils import run_scan_flow 
from app.utils.delete_insights_utils import get_projects
from app.cli.retrieve_insights_cli import lookup_past_insights
from app.utils.non_code_analysis.non_code_file_checker import classify_non_code_files_with_user_verification
import uvicorn
import os
import sys

load_dotenv()

def display_startup_info():
    """Display startup information including API key status."""
    print("\n" + "="*60)
    print("🚀 PROJECT INSIGHTS - STARTUP INFO")
    print("="*60)
    
    # Check API key status
    api_available, api_status = check_gemini_api_key()
    
    print("📊 Available Analysis Types:")
    print("   📍 Local Analysis: ✅ Always available")
    
    if api_available:
        print("   🤖 AI Analysis: ✅ Ready (Gemini API key detected)")
    else:
        print("   🤖 AI Analysis: ❌ Requires Gemini API key")
        print("      💡 Get your key at: https://aistudio.google.com/app/apikey")
    
    print("="*60)

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

    # Display startup info including API status
    display_startup_info()
    
    # Check if existing local Project Insights data is present
    existing_projects = get_projects()
    if existing_projects:
        lookup_past_insights(existing_projects)
    else:
        pass  # No existing projects found

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
                
                # will be used once analysis on each project is done to be able to fetch individual project analysis to display
                project_signatures = []
                
                for i, project_path in enumerate(rc["projects"], 1):
                    project_name = Path(project_path).name
                    print(f"\n{'='*50}")
                    print(f"📁 PROJECT {i}/{rc['count']}: {project_name}")
                    print(f"{'='*50}")
                    
                    print(f"🔍 Scanning project files...")
                    scan_result = run_scan_flow(project_path)
                    files = scan_result['files']
                
                    print(f"✅ Found {len(files)} files")

                    # --- Non-code file checker integration (per project) ---
                    print("🔎 Running non-code file checker...")
                    non_code_result = classify_non_code_files_with_user_verification(project_path)
                    print(f"--- Non-Code File Checker Results for {project_name} ---")
                    print(f"Is git repo: {non_code_result['is_git_repo']}")
                    print(f"User identity: {non_code_result['user_identity']}")
                    print(f"Collaborative non-code files: {len(non_code_result['collaborative'])}")
                    print(f"Non-collaborative non-code files: {len(non_code_result['non_collaborative'])}")
                    print(f"Excluded files: {len(non_code_result['excluded'])}")
                    print(f"--------------------------------------------------------")
                    # --- End non-code file checker integration ---       
                    
                    # Check if we should skip analysis
                    if scan_result["skip_analysis"]:
                        if scan_result["reason"] == "already_analyzed":
                            print(f"⏭️ Skipping analysis - {project_name} already fully analyzed")
                            project_signatures.append(scan_result["signature"])
                        elif scan_result["reason"] == "no_files":
                            print(f"⚠️ No files to analyze in {project_name}. Skipping.")
                        continue
                        
                    project_signatures.append(scan_result["signature"])
                    analysis_type = llm_manager.ask_analysis_type(project_name)
                    
                    # analysis flow with LLM
                    if analysis_type == 'ai':
                        print("🤖 Running AI analysis...")
                        
                        # Double-check API key (safety check)
                        api_key = os.getenv("GEMINI_API_KEY")
                        if not api_key:
                            print("❌ Error: Gemini API key not available. Falling back to local analysis.")
                            analysis_type = 'local'
                        else:
                            try:
                                llm_client = GeminiLLMClient(api_key=api_key)
                                
                                #TODO: Non Code parsing -> analysis
                                
                                #TODO: Code parsing -> analysis
                                #check if git or non git 
                                # if git: call parsing for git -> analysis for git USING LLM
                                # else call parsing for local -> analysis for local USING LLM
                                
                                print(f"✅ Starting AI analysis for {project_name}")
                                
                                #TODO: merge code and non code LLM analysis then store into db
                                
                            except Exception as e:
                                print(f"❌ Error initializing AI client: {e}")
                                print("🔄 Falling back to local analysis...")
                                analysis_type = 'local'
                    
                    # Handle local analysis (including fallbacks from AI failures)
                    if analysis_type == 'local':
                        print("📊 Running local analysis...")
                        
                        #TODO: Non Code parsing -> analysis
                        
                        #TODO: Code parsing -> analysis
                        #check if git or non git
                        # if git: call parsing for git -> analysis for git NON LLM
                        # else call parsing for local -> analysis for local NON LLM
                        
                        print(f"✅ Starting Local analysis for {project_name}")
                        
                        #TODO: merge code and non code LOCAL analysis then store into db
                
                #TODO: Print all information for projects using the signatures stored in project_signatures
                #TODO: Print Chronological order of projects analyzed from the db
                #TODO: Print Chronological Skills worked on from projects 
                
                
            else:
                print("❌ No projects found to analyze")
          
            # ADD THE MISSING SECTION HERE!
            print(f"\n{'='*60}")
            print("🔄 CONTINUE OR EXIT?")
            print(f"{'='*60}")
            
            while True:
                choice = input("\nWould you like to:\n  🔄 'continue' - Analyze another project\n  🚪 'exit'     - Exit the application\n\nChoice (continue/exit): ").lower().strip()
                
                if choice in ['exit', 'e', 'quit', 'q', 'done', 'finish']:
                    print("👋 Exiting Project Insights. Thank you for using our service!")
                    break
                elif choice in ['continue', 'c', 'again', 'y', 'yes', 'more']:
                    print("🔄 Starting new analysis session...")
                    break
                else:
                    print("❌ Please enter 'continue' or 'exit'")
            
            # Break out of the main while loop if user chose exit
            if choice in ['exit', 'e', 'quit', 'q', 'done', 'finish']:
                break
    
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