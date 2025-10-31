"""
Minimal Python entry point.
"""
from fastapi import FastAPI
from app.data.db import init_db, seed_db
from app.cli.consent_manager import ConsentManager
from app.cli.user_preference_cli import UserPreferences
import uvicorn
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
    
    print("App started successfully")
    
    #Allow first time and returning users to manage preferences
    user_preference_manager = UserPreferences()

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Project Insights!!"}

if __name__ == "__main__":
    main()
    print("App started")
    uvicorn.run(app, host="0.0.0.0", port=8000)
