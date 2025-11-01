import sqlite3
from pathlib import Path
import pytest
from app.utils.user_preference_utils import UserPreferenceStore
from app.cli.user_preference_cli import UserPreferences

# --- Utility functions ---

def create_user_pref_table(conn: sqlite3.Connection):
    """Ensure USER_PREFERENCES table exists."""
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS USER_PREFERENCES (
            user_id TEXT PRIMARY KEY,
            name TEXT,
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
    """Create a temporary UserPreferenceStore with a fresh SQLite DB."""
    db_path = tmp_path / "prefs.db"
    store = UserPreferenceStore(db_path=db_path)
    create_user_pref_table(store.conn)
    yield store
    store.close()


# --- Tests for the DB store ---

def test_save_and_get_preferences(temp_store):
    store = temp_store

    store.save_preferences(
        user_id="user1",
        name="Alice Example",
        github_user="alicegit",
        education="BSc Computer Science",
        industry="Technology",
        job_title="Developer"
    )

    prefs = store.get_preferences("user1")
    assert prefs is not None
    assert prefs["name"] == "Alice Example"
    assert prefs["github_user"] == "alicegit"
    assert prefs["industry"] == "Technology"


def test_get_preferences_returns_none_for_missing_user(temp_store):
    assert temp_store.get_preferences("missing_user") is None


def test_save_preferences_updates_existing_row(temp_store):
    store = temp_store

    store.save_preferences("user2", "First Name", "gh1", "MS", "Finance", "Analyst")
    store.save_preferences("user2", "Second Name", "gh2", "PhD", "Healthcare", "Senior Analyst")

    prefs = store.get_preferences("user2")
    assert prefs["name"] == "Second Name"
    assert prefs["github_user"] == "gh2"
    assert prefs["industry"] == "Healthcare"


def test_persistence_after_reopen(tmp_path):
    db_path = tmp_path / "prefs.db"
    s1 = UserPreferenceStore(db_path=db_path)
    create_user_pref_table(s1.conn)
    s1.save_preferences("persist_user", "Persist Name", "persistGH", "BA", "Education", "Instructor")
    s1.close()

    s2 = UserPreferenceStore(db_path=db_path)
    prefs = s2.get_preferences("persist_user")
    s2.close()

    assert prefs is not None
    assert prefs["name"] == "Persist Name"
    assert prefs["github_user"] == "persistGH"


def test_sql_injection_protection(temp_store):
    malicious_id = "1; DROP TABLE USER_PREFERENCES; --"
    temp_store.save_preferences(malicious_id, "Bad Actor", "badgh", "None", "Other", "None")
    prefs = temp_store.get_preferences(malicious_id)
    assert prefs is not None
    assert prefs["user_id"] == malicious_id

    # Ensure table still exists
    cur = temp_store.conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='USER_PREFERENCES';")
    assert cur.fetchone() is not None


# --- CLI Test (No real DB) ---

@pytest.fixture
def fake_store():
    """A fake in-memory store to test CLI logic without DB access."""
    class FakeStore:
        def __init__(self):
            self.data = {}

        def get_preferences(self, user_id):
            return self.data.get(user_id)

        def save_preferences(self, user_id, name, github_user, education, industry, job_title):
            self.data[user_id] = {
                "user_id": user_id,
                "name": name,
                "github_user": github_user,
                "education": education,
                "industry": industry,
                "job_title": job_title
            }

        def close(self):
            pass

    return FakeStore()


def test_cli_creates_and_saves_preferences(monkeypatch, capsys, fake_store):
    inputs = iter([
        "testuser",        # user id
        "Test User",       # name
        "testgh",          # github_user
        "BSc",             # education
        "Technology",      # industry
        "Developer"        # job title
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    cli = UserPreferences(store=fake_store)
    cli.manage_preferences()

    out = capsys.readouterr().out
    assert "Preferences saved successfully" in out

    saved = fake_store.data.get("testuser")
    assert saved is not None
    assert saved["name"] == "Test User"
    assert saved["github_user"] == "testgh"
