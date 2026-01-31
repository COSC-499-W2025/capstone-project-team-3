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

from app.api.routes.privacy_consent import router as privacy_consent_router 
from app.api.routes.get_upload_id import router as upload_resolver_router 
from app.api.routes.resume import router as resume_router
from app.api.routes.user_preferences import router as user_preferences_router
from app.api.routes.skills import router as skills_router
from app.api.routes.projects import router as projects_router
from app.api.routes.portfolio import router as portfolio_router

from app.manager.llm_consent_manager import LLMConsentManager
from app.utils.analysis_merger_utils import merge_analysis_results
from app.utils.code_analysis.code_analysis_utils import analyze_github_project, analyze_parsed_project
from app.utils.env_utils import check_gemini_api_key
from app.utils.scan_utils import run_scan_flow 
from app.utils.delete_insights_utils import get_projects
from app.cli.retrieve_insights_cli import lookup_past_insights, display_specific_projects, get_portfolio_resume_insights
from app.utils.scan_utils import run_scan_flow
from app.utils.clean_up import cleanup_upload
from app.utils.non_code_analysis.non_code_file_checker import classify_non_code_files_with_user_verification
from app.utils.non_code_parsing.document_parser import parsed_input_text
from app.utils.project_extractor import get_project_top_level_dirs 
from app.utils.code_analysis.parse_code_utils import parse_code_flow
from app.utils.git_utils import detect_git
from app.cli.git_code_parsing import run_git_parsing_from_files, _get_preferred_author_email
from app.utils.non_code_analysis.non_3rd_party_analysis import analyze_project_clean
from app.utils.non_code_analysis.non_code_analysis_utils import (
    analyze_non_code_files,
)
import uvicorn
import os
import sys
import time
import threading
import json

load_dotenv()

# Create FastAPI app
app = FastAPI(title="Project Insights")
app.include_router(upload_page_router)
app.include_router(upload_resolver_router, prefix="/api")
app.include_router(privacy_consent_router, prefix="/api")
app.include_router(resume_router)
app.include_router(user_preferences_router, prefix="/api")
app.include_router(skills_router, prefix="/api")
app.include_router(projects_router, prefix="/api")
app.include_router(portfolio_router, prefix="/api")


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
    #seed_db()  # automatically populate test data
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
    try:
        existing_projects = get_projects()
    except Exception:
        existing_projects = None
    if existing_projects:
        lookup_past_insights()
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
                    top_level_dirs = get_project_top_level_dirs(project_path)
                    files = scan_result['files']
                
                    print(f"✅ Found {len(files)} files")
                   
                    
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
                        # Prefer values from UserPreferences if available, fallback to DB helper
                        try:
                            latest_prefs = UserPreferences().get_latest_preferences()
                        except Exception:
                            latest_prefs = None

                        username, email=_get_preferred_author_email()
                        non_code_result = classify_non_code_files_with_user_verification(project_path,username,email)
                        print(f"--- Non-Code File Checker Results for {project_name} ---")
                        print(f"Collaborative non-code files: {len(non_code_result['collaborative'])}")
                        print(f"Non-collaborative non-code files: {len(non_code_result['non_collaborative'])}")
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
                                
    
                        print(f"🔍 Analyzing code files in {project_name}... hang tight! ⚙️📁")
                        #check if git or non git 
                        # if git: call parsing for git -> analysis for git USING LLM
                        if detect_git(project_path):
                            print("📘 Git repository detected — running Git-based code parsing...")
                            try:
                                code_git_history_json = run_git_parsing_from_files(
                                file_paths=files,
                                include_merges=False,
                                max_commits=None,  # set a limit if needed
                                )
                                print("✅ Git code parsing completed.")
                            except Exception as e:
                                print(f"⚠️ Git code parsing failed: {e}")
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
                                # --- NON-CODE ANALYSIS (AI) ---
                                try:
                                    non_code_analysis_results=analyze_non_code_files(parsed_non_code=parsed_non_code)
                                    print(f"✅ AI Non Code Analysis completed successfully!")
                                    
                                except Exception as e:
                                    print(f"⚠️ AI non-code analysis failed: {e}")
                                    print("🔄 Falling back to local non-code analysis...")
                                    non_code_analysis_results = analyze_project_clean(parsed_non_code)
                                 # --- NON-CODE ANALYSIS (AI) ---

                                try:
                                    if detect_git(project_path):
                                        code_analysis_results = analyze_github_project(code_git_history_json, llm_client)
                                    else:
                                        code_analysis_results = analyze_parsed_project(parse_code, llm_client)
                                except Exception as e:
                                    print(f"⚠️ AI code analysis failed: {e}")
                                    print("🔄 Falling back to local non-code analysis...")
                                    code_analysis_results = analyze_parsed_project(parsed_non_code)
                                 # --- NON-CODE ANALYSIS (AI) ---
                                # merge code and non code LLM analysis then store into db
                                try:
                                    merge_analysis_results(non_code_analysis_results=non_code_analysis_results,code_analysis_results=code_analysis_results, project_name=project_name, project_signature=scan_result["signature"])
                                except Exception as e:
                                    print(f"❌ Error storing analysis results for {project_name}: {e}")
                                    
                                
                            except Exception as e:
                                print(f"❌ Error initializing AI client: {e}")
                                print("🔄 Falling back to local analysis...")
                                analysis_type = 'local'
                    
                    # Handle local analysis (including fallbacks from AI failures)
                    if analysis_type == 'local':
                        print("📊 Running local analysis...")
                        print(f"✅ Starting Local analysis for {project_name}")
                        
                        try:
                            # Run non-3rd party analysis (no LLM) using parsed_non_code with user preferences
                            non_code_local_results = analyze_project_clean(parsed_non_code)
                            print(f"✅ Non Code Analysis completed successfully!")
                        except Exception as e:
                            print(f"⚠️ Non Code Local analysis failed: {e}")
                            import traceback
                            traceback.print_exc()
                            non_code_local_results = {}
                        
                        try:
                            if detect_git(project_path):
                                code_analysis_results = analyze_github_project(json.loads(code_git_history_json))
                            else:
                                code_analysis_results = analyze_parsed_project(parse_code)
                        except Exception as e:
                            print(f"⚠️ Code Local analysis failed: {e}")
                            code_analysis_results = {}
                        # merge code and non code LOCAL analysis then store into db
                        try:
                            merge_analysis_results(non_code_analysis_results=non_code_local_results, code_analysis_results=code_analysis_results, project_name=project_name, project_signature=scan_result["signature"])
                        except Exception as e:
                            print(f"❌ Error storing analysis results for {project_name}: {e}")
       
            
                
                # 1. Print specific projects analyzed this session
                if project_signatures:
                    print(f"\n🎯 PROJECTS ANALYZED THIS SESSION ({len(project_signatures)} projects)")
                    print("="*60)
                    display_specific_projects(project_signatures)
                else:
                    print("\n⚠️ No projects were analyzed in this session.")
                
                # 2. Print chronological order and skills from ALL projects in database
                print(f"\n{'='*60}")
                print("📅 ALL PROJECTS CHRONOLOGICAL OVERVIEW")
                print("="*60)
                
                try:
                    portfolio, resume = get_portfolio_resume_insights()
                    
                    if portfolio["projects"]:
                        # Chronological order of ALL projects
                        print(f"\n🏆 Top Ranked Projects ({len(portfolio['top_projects'])} projects):")
                        for i, proj in enumerate(portfolio["top_projects"], 1):
                            skills_count = len(proj['skills'])
                            rank_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}️⃣"
                            print(f"   {rank_emoji} {proj['name']} — Score: {proj['rank']} — ({proj['duration']}) — {skills_count} skills")
                            
                            # Show summry of project
                            if proj['summary']:
                                print(f"      📝 Summary: {proj['summary']}")
                                
                            # Show a few key skills for top projects
                            if proj['skills']:
                                top_skills_preview = sorted(set(proj['skills']))[:5]
                                skills_text = ", ".join(top_skills_preview)
                                if len(proj['skills']) > 5:
                                    skills_text += f" + {len(proj['skills']) - 5} more"
                                print(f"      🛠️  Key skills: {skills_text}")
                        print(f"\n📜 All Projects in Chronological Order ({len(portfolio['chronological'])} recent):")
                        for i, proj in enumerate(portfolio["chronological"], 1):
                            skills_count = len(proj['skills'])
                            print(f"   {i:2d}. ⏳ {proj['name']} — ({proj['duration']}) — {skills_count} skills")
                        
                        # Skills timeline from all projects
                        print(f"\n🛠️ Chronological Skills Evolution:")
                        all_skills_timeline = []
                        
                        # Collect all skills with project dates
                        for proj in sorted(portfolio["projects"], key=lambda x: x["created_at"]):
                            for skill in proj['skills']:
                                all_skills_timeline.append({
                                    "skill": skill,
                                    "project": proj['name'],
                                    "date": proj['created_at']
                                })
                        
                        # Display unique skills in order they first appeared
                        seen_skills = set()
                        skills_progression = []
                        
                        for item in all_skills_timeline:
                            if item["skill"] not in seen_skills:
                                seen_skills.add(item["skill"])
                                skills_progression.append(item)
                        
                        # Show skills progression (limit to 20 for readability)
                        print(f"   📈 Skills learned over time (first {min(20, len(skills_progression))} skills):")
                        for i, skill_item in enumerate(skills_progression[:20], 1):
                            print(f"      {i:2d}. {skill_item['skill']} — (first used in '{skill_item['project']}' on {skill_item['date']})")
                        
                        if len(skills_progression) > 20:
                            print(f"      ... and {len(skills_progression) - 20} more skills")
                        
                        # Skills frequency analysis
                        from collections import Counter
                        skill_frequency = Counter(item["skill"] for item in all_skills_timeline)
                        top_skills = skill_frequency.most_common(10)
                        
                        print(f"\n🔥 Most Frequently Used Skills (across all projects):")
                        for i, (skill, count) in enumerate(top_skills, 1):
                            print(f"      {i:2d}. {skill} — used in {count} project{'s' if count > 1 else ''}")
                        
                        # ADD RESUME SECTION HERE
                        print(f"\n{'='*60}")
                        print("📄 RESUME SUMMARY")
                        print("="*60)

                        # Show resume bullets from the database
                        if resume and resume.get("bullets"):
                            print(f"\n📝 All Resume Bullets:")
    
                            # Group bullets by project
                            bullets_by_project = {}
    
                            for bullet_data in resume["bullets"]:
                                # Extract project name and bullet list
                                if isinstance(bullet_data, dict):
                                    project_name = bullet_data.get("project_name", "Unknown Project")
                                    bullet_list = bullet_data.get("bullet", [])
                                else:
                                    # If it's just a string, try to parse it
                                    project_name = "Unknown Project"
                                    bullet_list = bullet_data
        
                                # Handle if bullet_list is a JSON string
                                if isinstance(bullet_list, str):
                                    try:
                                        bullet_list = json.loads(bullet_list)
                                    except json.JSONDecodeError:
                                        # If not JSON, treat as single bullet
                                        bullet_list = [bullet_list]
        
                                # Ensure it's a list
                                if not isinstance(bullet_list, list):
                                    bullet_list = [str(bullet_list)]
        
                                # Add bullets to project group
                                if project_name not in bullets_by_project:
                                    bullets_by_project[project_name] = []
        
                                # Flatten and clean bullets
                                for bullet in bullet_list:
                                    if bullet and isinstance(bullet, str) and bullet.strip():
                                        bullets_by_project[project_name].append(bullet.strip())
    
                            # Display bullets grouped by project
                            total_bullets = sum(len(bullets) for bullets in bullets_by_project.values())
                            print(f"   Total: {total_bullets} bullets across {len(bullets_by_project)} project(s)\n")
    
                            for project_name, bullets in bullets_by_project.items():
                                print(f"   📂 {project_name} ({len(bullets)} bullets):")
                                for bullet in bullets:
                                    print(f"      • {bullet}")
                                print()  # Empty line between projects
                            
                            print("Download your resume in Latex/PDF format here:")
                            print("   → http://localhost:8000/resume")
                        else:
                            print("\n📭 No resume bullets found in database.")
                    else:
                        print("📭 No projects found in database.")
                        
                except Exception as e:
                    print(f"❌ Error retrieving project overview: {e}")
                
                print(f"\n{'='*60}")
                print("✅ SESSION ANALYSIS COMPLETE")
                print("="*60)
                
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

    