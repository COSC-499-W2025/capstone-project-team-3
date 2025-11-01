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

    # Manage user preferences
    user_pref = UserPreferences()
    prefs = user_pref.get_latest_preferences()
    if not prefs:
        print("No user preferences found — let's create them.\n")
        user_pref.manage_preferences()
        prefs = user_pref.get_latest_preferences()
    else:
        print("Existing user preferences found.")
        user_pref.manage_preferences()

    
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
