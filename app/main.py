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
from app.api.routes.upload_page import router as upload_page_router
from app.api.routes.get_upload_id import router as upload_resolver_router 
from app.manager.llm_consent_manager import LLMConsentManager
from app.utils.analysis_merger_utils import merge_analysis_results
from app.utils.env_utils import check_gemini_api_key
from app.utils.scan_utils import run_scan_flow
from app.utils.clean_up import cleanup_upload
from app.utils.non_code_analysis.non_code_file_checker import classify_non_code_files_with_user_verification
from app.utils.non_code_parsing.document_parser import parsed_input_text
from app.utils.project_extractor import get_project_top_level_dirs 
from app.utils.code_analysis.parse_code_utils import parse_code_flow
from app.utils.git_utils import detect_git
import uvicorn
import os
import sys
import time
import threading

load_dotenv()

# Create FastAPI app
app = FastAPI(title="Project Insights")
app.include_router(upload_page_router)
app.include_router(upload_resolver_router, prefix="/api")

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
                    top_level_dirs = get_project_top_level_dirs(project_path)
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

                    # --- Parsing integration ---
                    print("📄 Parsing non-code files...")
                    try:
                        parsed_non_code = parsed_input_text(
                            file_paths_dict={
                                'collaborative': non_code_result['collaborative'],
                                'non_collaborative': non_code_result['non_collaborative']
                            },
                            repo_path=project_path if non_code_result['is_git_repo'] else None,
                            author=non_code_result['user_identity'].get('email')
                        )
                        print(f"✅ Parsed {len(parsed_non_code.get('parsed_files', []))} non-code files")
                    except Exception as e:
                        print(f"⚠️ Warning: Non-code parsing failed: {e}")
                        parsed_non_code = {'parsed_files': []}
                    # --- End parsing integration ---       

                    
                    
                    # Check if we should skip analysis
                    if scan_result["skip_analysis"]:
                        if scan_result["reason"] == "already_analyzed":
                            print(f"⏭️ Skipping analysis - {project_name} already fully analyzed")
                            project_signatures.append(scan_result["signature"])
                        elif scan_result["reason"] == "no_files":
                            print(f"⚠️ No files to analyze in {project_name}. Skipping.")
                        continue
                    else: #Perform analysis
                        
                        # --- Non-code file checker integration (per project) ---
                        print()
                        print("🔎 Running non-code file checker...")
                        non_code_result = classify_non_code_files_with_user_verification(project_path)
                        print()
                        print(f"--- Non-Code File Checker Results for {project_name} ---")
                        print(f"Is git repo: {non_code_result['is_git_repo']}")
                        print(f"User identity: {non_code_result['user_identity']}")
                        print(f"Collaborative non-code files: {len(non_code_result['collaborative'])}")
                        print(f"Non-collaborative non-code files: {len(non_code_result['non_collaborative'])}")
                        print(f"Excluded files: {len(non_code_result['excluded'])}")
                        print(f"--------------------------------------------------------")
                        # --- End non-code file checker integration ---  
                            
                        #TODO: Non Code parsing -> analysis
                                
                        #TODO: Code parsing -> analysis
                        print()
                        print(f"🔍 Analyzing code files in {project_name}... hang tight! ⚙️📁")
                        #check if git or non git 
                        # if git: call parsing for git -> analysis for git USING LLM
                        if detect_git(project_path):
                            pass #TODO: call parsing for git
                        # else call parsing for local -> analysis for local USING LLM
                        else:
                            parse_code = parse_code_flow(files, top_level_dirs)
                        
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
                                
                                print(f"✅ Starting AI analysis for {project_name}")
                                
                                # merge code and non code LLM analysis then store into db
                                merge_analysis_results(non_code_analysis_results={}, code_analysis_results={}, project_name=project_name, project_signature = scan_result["signature"])
                                
                            except Exception as e:
                                print(f"❌ Error initializing AI client: {e}")
                                print("🔄 Falling back to local analysis...")
                                analysis_type = 'local'
                    
                    # Handle local analysis (including fallbacks from AI failures)
                    if analysis_type == 'local':
                        print("📊 Running local analysis...")
                        
                        
                        print(f"✅ Starting Local analysis for {project_name}")
                        
                        # merge code and non code LOCAL analysis then store into db
                        merge_analysis_results(non_code_analysis_results={}, code_analysis_results={}, project_name=project_name, project_signatures=project_signatures)
                        
                        
                #TODO: Print all information for projects using the signatures stored in project_signatures
                #TODO: Print Chronological order of projects analyzed from the db
                #TODO: Print Chronological Skills worked on from projects 
                
                
            else:
                print("❌ No projects found to analyze")

            # Perform cleanup of uploaded artifacts (zip + extracted dir)
            if rc.get("status") == "ok" and rc.get("upload_id"):
                cu_res = cleanup_upload(
                    rc.get("upload_id"),
                    extracted_dir=rc.get("extracted_dir"),
                    delete_extracted=True,
                )
                if cu_res.get("status") != "ok":
                     print(f"⚠️ Cleanup failed: {cu_res.get('reason')}")
          
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


@app.get("/")
def read_root():
    return {"message": "Welcome to the Project Insights!!"}

if __name__ == "__main__":
    def start_server():
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="critical",
            access_log= False
        )

    # Start API server in background
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Give server a moment to start
    time.sleep(1)

    # Now run the CLI flow
    main()