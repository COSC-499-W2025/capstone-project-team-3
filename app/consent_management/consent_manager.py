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
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT consent_given FROM CONSENT ORDER BY id DESC LIMIT 1")
            result = cursor.fetchone()
            conn.close()
            return bool(result[0]) if result else False
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
            
            if response in ['yes', 'y', '']:
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
            return True
        return self.prompt_for_consent()