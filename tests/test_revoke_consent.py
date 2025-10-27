
import unittest
import tempfile
import sqlite3
from pathlib import Path
from app.cli.consent_manager import ConsentManager


class TestRevokeConsent(unittest.TestCase):
    """Essential test cases for consent revocation"""
    
    def setUp(self):
        """Set up test database before each test"""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()
        
        # Create CONSENT table
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS CONSENT (
                id INTEGER PRIMARY KEY,
                policy_version TEXT,
                consent_given INTEGER DEFAULT 0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
        
        self.manager = ConsentManager(db_path=self.db_path)
    
    def tearDown(self):
        """Clean up test database after each test"""
        Path(self.db_path).unlink(missing_ok=True)
    
    def test_revoke_removes_consent(self):
        """Revoking consent removes it"""
        self.manager.record_consent(True)
        self.manager.revoke_consent()
        self.assertFalse(self.manager.has_consent())
    
    def test_revoke_with_no_consent(self):
        """Revoking when no consent exists"""
        self.manager.revoke_consent()
        self.assertFalse(self.manager.has_consent())
    
    def test_grant_revoke_regrant(self):
        """Grant, revoke, then grant again"""
        self.manager.record_consent(True)
        self.manager.revoke_consent()
        self.manager.record_consent(True)
        self.assertTrue(self.manager.has_consent())


if __name__ == "__main__":
    unittest.main()
