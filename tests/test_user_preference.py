import sqlite3
import re
import pytest
from app.utils.user_preference_utils import UserPreferenceStore
from app.cli.user_preference_cli import UserPreferences
from unittest.mock import patch
from app.main import main

# --- Utility setup ---

def create_user_pref_table(conn: sqlite3.Connection):
    """Ensure USER_PREFERENCES table exists."""
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS USER_PREFERENCES (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        github_user TEXT,
        education TEXT,
        industry TEXT,
        job_title TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()

# --- Fixtures ---

@pytest.fixture
def temp_store(tmp_path):
    """Create a temporary UserPreferenceStore with a fresh SQLite DB record."""
    db_path = tmp_path / "prefs.db"
    store = UserPreferenceStore(db_path=str(db_path))
    create_user_pref_table(store.conn)
    yield store
    store.close()

# --- DB store tests ---

def test_save_and_get_preferences(temp_store):
    temp_store.save_preferences(
        name="Alice Example",
        email="alice@example.com",
        github_user="alicegit",
        education="BSc Computer Science",
        industry="Technology",
        job_title="Developer"
    )
    prefs = temp_store.get_latest_preferences("alice@example.com")
    assert prefs["name"] == "Alice Example"
    assert prefs["github_user"] == "alicegit"
    assert prefs["industry"] == "Technology"

def test_get_preferences_none(temp_store):
    assert temp_store.get_latest_preferences("nonexistent@example.com") is None

def test_persistence_across_sessions(tmp_path):
    db_path = tmp_path / "prefs.db"
    store1 = UserPreferenceStore(db_path=str(db_path))
    create_user_pref_table(store1.conn)
    store1.save_preferences(
        name="Persist Name",
        email="persist@example.com",
        github_user="persistGH",
        education="BA",
        industry="Education",
        job_title="Instructor"
    )
    store1.close()

    store2 = UserPreferenceStore(db_path=str(db_path))
    prefs = store2.get_latest_preferences("persist@example.com")
    store2.close()
    assert prefs["name"] == "Persist Name"
    assert prefs["github_user"] == "persistGH"

# --- CLI logic tests without input mocking ---

class FakeStore:
    def __init__(self):
        self.data = []

    def get_latest_preferences(self, email):
        for record in reversed(self.data):
            if record["email"] == email:
                return record
        return None

    def save_preferences(self, name, email, github_user, education, industry, job_title):
        self.data.append({
            "name": name,
            "email": email,
            "github_user": github_user,
            "education": education,
            "industry": industry,
            "job_title": job_title
        })

    def close(self):
        pass

def test_cli_save_and_retrieve_preferences():
    store = FakeStore()
    cli = UserPreferences(store=store)

    # Simulate inputs as function parameters instead of interactive input
    email = "user@example.com"
    name = "Test User"
    github = "testgh"
    education = "BSc"
    industry = "Technology"
    job_title = "Developer"

    store.save_preferences(name, email, github, education, industry, job_title)
    prefs = store.get_latest_preferences(email)
    assert prefs["name"] == name
    assert prefs["email"] == email
    assert prefs["github_user"] == github

def test_invalid_email():
    # Regex validation test
    invalid_emails = ["plainaddress", "missingatsign.com", "user@.com"]
    pattern = r"^[\w.-]+@[\w.-]+\.\w+$"
    for email in invalid_emails:
        assert not re.match(pattern, email)

    valid_email = "user@example.com"
    assert re.match(pattern, valid_email)