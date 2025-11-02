"""
Minimal Python entry point.
"""
from fastapi import FastAPI
from app.data.db import init_db, seed_db
from app.cli.consent_manager import ConsentManager
from app.cli.file_input import main as file_input_main  
import uvicorn
import os
import sys

# Database Entry Point#
def main():
    init_db()  # creates the SQLite DB + tables
    # Check for the consent
    consent_manager = ConsentManager()
    if not consent_manager.enforce_consent():
        print("\n Cannot start application without consent. Please provide consent to proceed.")
        sys.exit(1)

    # Check if PROMPT_ROOT is enabled
    prompt_root = os.environ.get("PROMPT_ROOT", "0")
    if prompt_root in ("1", "true", "True", "yes"):
        print("\n--- Project Root Input ---")
        rc = file_input_main()
        if rc != 0:
            print("Root input step failed or was cancelled. Exiting.")
            sys.exit(rc)
    
    print("App started successfully")
    seed_db()  # automatically populate test data
    print("Database started")

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Project Insights!!"}

if __name__ == "__main__":
    main()
    print("App started")
    uvicorn.run(app, host="0.0.0.0", port=8000)
