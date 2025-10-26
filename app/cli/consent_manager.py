from pathlib import Path
import sqlite3
from .consent_text import (
    CONSENT_MESSAGE,
    DETAILED_PRIVACY_INFO,
    CONSENT_GRANTED_MESSAGE,
    CONSENT_DECLINED_MESSAGE,
    CONSENT_ALREADY_PROVIDED_MESSAGE
)

class ConsentManager:
    def __init__(self, db_path=None):
        if db_path is None:
            BASE_DIR = Path(__file__).resolve().parent.parent / "data"
            db_path = BASE_DIR / "app.sqlite3"
        self.db_path = db_path
    
    def _get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def has_consent(self):
        """Check if user has given consent (consent_given = 1)"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT consent_given FROM CONSENT ORDER BY id DESC LIMIT 1")
            result = cursor.fetchone()
            conn.close()
            # Return True only if consent_given is 1
            return result[0] == 1 if result else False
        except sqlite3.Error:
            return False
    
    def record_consent(self, accepted):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO CONSENT (consent_given) VALUES (?)", (1 if accepted else 0,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error:
            return False
    
    def prompt_for_consent(self):
        print(CONSENT_MESSAGE)
        
        while True:
            response = input().strip().lower()
            
            if response == 'more':
                print(DETAILED_PRIVACY_INFO)
                input()
                print(CONSENT_MESSAGE)
                continue
            
            if response in ['yes', 'y']:
                self.record_consent(True)
                print(CONSENT_GRANTED_MESSAGE)
                return True
            
            if response in ['no', 'n']:
                self.record_consent(False)
                print(CONSENT_DECLINED_MESSAGE)
                return False
            
            print("Invalid input. Type 'yes', 'no', or 'more'.")
    
    def enforce_consent(self):
        if self.has_consent():
            print(CONSENT_ALREADY_PROVIDED_MESSAGE)
            print("\nWould you like to revoke your consent? (yes/no): ", end='')
            response = input().strip().lower()
            if response in ['yes', 'y']:
                self.revoke_consent()
                return False  # Exit the app
            return True  # Continue with the app
        return self.prompt_for_consent()

    def revoke_consent(self):
        """Set consent_given to 0 in database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE CONSENT SET consent_given = 0 WHERE consent_given = 1")
        conn.commit()
        conn.close()
        print("\n✓ Consent revoked. Application will now exit.")
        print("  You will be asked for consent again on next startup.\n")