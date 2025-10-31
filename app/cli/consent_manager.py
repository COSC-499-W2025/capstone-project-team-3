from pathlib import Path
import sqlite3
from app.shared.text.consent_text import ConsentText
from app.utils.consent_utils import has_consent, record_consent, revoke_consent, get_connection

class ConsentManager:
    def __init__(self, db_path=None):
        if db_path is None:
            BASE_DIR = Path(__file__).resolve().parent.parent / "data"
            db_path = BASE_DIR / "app.sqlite3"
        self.db_path = db_path
    
    def _get_connection(self):
        return get_connection(self.db_path)
    
    def has_consent(self):
        return has_consent(self.db_path)
    
    def record_consent(self, accepted):
        return record_consent(self.db_path, accepted)
    
    def prompt_for_consent(self):
        print(ConsentText.CONSENT_MESSAGE)
        
        while True:
            response = input().strip().lower()
            
            if response == 'more':
                print(ConsentText.DETAILED_PRIVACY_INFO)
                input()
                print(ConsentText.CONSENT_MESSAGE)
                continue
            
            if response in ['yes', 'y']:
                record_consent(self.db_path, True)
                print(ConsentText.CONSENT_GRANTED_MESSAGE)
                return True
            
            if response in ['no', 'n']:
                record_consent(self.db_path, False)
                print(ConsentText.CONSENT_DECLINED_MESSAGE)
                return False
            
            print("Invalid input. Type 'yes', 'no', or 'more'.")
    
    def enforce_consent(self):
        if self.has_consent():
            print(ConsentText.CONSENT_ALREADY_PROVIDED_MESSAGE)
            print("\nWould you like to revoke your consent? (yes/no): ", end='')
            response = input().strip().lower()
            if response in ['yes', 'y']:
                self.revoke_consent()
                return False  # Exit the app
            return True  # Continue with the app
        return self.prompt_for_consent()

    def revoke_consent(self):
        revoke_consent(self.db_path)