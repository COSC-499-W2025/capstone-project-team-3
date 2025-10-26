from app.cli.consent_manager import ConsentManager
import unittest
import unittest.mock
import sqlite3
import tempfile
import os

CONSENT_SCHEMA = """
CREATE TABLE IF NOT EXISTS CONSENT (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    consent_given INTEGER DEFAULT 0
);
"""

class ConsentManagerTempFile(ConsentManager):
    def __init__(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        super().__init__(db_path=self.temp_db.name)
        self._init_schema()
    def _init_schema(self):
        conn = self._get_connection()
        conn.executescript(CONSENT_SCHEMA)
        conn.commit()
        conn.close()
    def cleanup(self):
        self.temp_db.close()
        os.unlink(self.temp_db.name)

class TestConsentManager(unittest.TestCase):
    def setUp(self):
        """Set up the ConsentManager for testing"""
        self.manager = ConsentManagerTempFile()

    def tearDown(self):
        """Clean up after each test"""
        self.manager.cleanup()

    def test_record_and_check_consent(self):
        """Test recording and checking consent"""
        self.assertFalse(self.manager.has_consent())
        self.manager.record_consent(True)
        self.assertTrue(self.manager.has_consent())
        self.manager.record_consent(False)
        self.assertFalse(self.manager.has_consent())

    def test_prompt_for_consent_yes(self):
        """Test prompt_for_consent method with 'yes' response"""
        with unittest.mock.patch('builtins.input', return_value='yes'):
            result = self.manager.prompt_for_consent()
            self.assertTrue(result)
            self.assertTrue(self.manager.has_consent())

    def test_prompt_for_consent_no(self):
        """Test prompt_for_consent method with 'no' response"""
        with unittest.mock.patch('builtins.input', return_value='no'):
            result = self.manager.prompt_for_consent()
            self.assertFalse(result)
            self.assertFalse(self.manager.has_consent())

    def test_enforce_consent_already_given(self):
        """Test enforce_consent method when consent is already given"""
        self.manager.record_consent(True)
        with unittest.mock.patch('builtins.input', return_value='no'):
            # Should not prompt, should just return True
            self.assertTrue(self.manager.enforce_consent())


if __name__ == "__main__":
    unittest.main()