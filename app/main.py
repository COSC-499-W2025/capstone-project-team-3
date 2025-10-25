"""
Minimal Python entry point.
"""
from fastapi import FastAPI
from app.data.db import init_db
import uvicorn

# Database Entry Point#
def main():
    init_db()  # creates the SQLite DB + tables
    print("App started")

app = FastAPI()
# Ensure the parent directory is in sys.path so 'app' can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from consent_management.consent_manager import ConsentManager
from consent_management.consent_cli import ConsentCLI
from consent_management.consent_text import CONSENT_ALREADY_PROVIDED_MESSAGE, CONSENT_GRANTED_MESSAGE  
@app.get("/")
def read_root():
    return {"message": CONSENT_GRANTED_MESSAGE}

if __name__ == "__main__":
    print("App started")

    # Initialize consent management
    consent_manager = ConsentManager()
    
    # Check for consent
    if not consent_manager.has_consent():
        print("\nBefore starting the server, we need your consent.")
        
        # Create the CLI and prompt for consent
        consent_cli = ConsentCLI(consent_manager)
        consent_granted = consent_cli.prompt_for_consent()
        
        if not consent_granted:
            print("Exiting application since consent was declined.")
            sys.exit(0)
    else:
        print(CONSENT_ALREADY_PROVIDED_MESSAGE)
    
    print("Starting server...")
    # Start server AFTER consent is granted
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()