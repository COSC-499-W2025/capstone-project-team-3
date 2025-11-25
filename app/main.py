"""
Minimal Python entry point.
"""
from fastapi import FastAPI
from app.data.db import init_db, seed_db
from app.cli.consent_manager import ConsentManager
from app.cli.user_preference_cli import UserPreferences
from app.cli.file_input import main as file_input_main 
from app.utils.scan_utils import run_scan_flow 
import uvicorn
import os
import sys

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
        # If rc is not a dict or not a ZIP, exit
        if not isinstance(rc, dict) or rc.get("type") != "zip":
            print("❌ Only ZIP archives are accepted as input. Exiting.")
            sys.exit(1)
        if rc.get("count", 0) == 0 or "projects" not in rc:
            print("❌ No projects found in ZIP archive. Exiting.")
            sys.exit(1)
        print(f"Found {rc['count']} projects in ZIP. Scanning each...")
        for project_path in rc["projects"]:
            print(f"\nScanning project: {project_path}")
            files = run_scan_flow(project_path)
            if not files:
                print(f"No files to analyze in {project_path}. Skipping.")
            else:
                print(f"Ready to analyze {len(files)} files in {project_path}.")
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
