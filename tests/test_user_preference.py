import sqlite3
from pathlib import Path
import pytest
from app.utils.user_preference_utils import UserPreferenceStore
from app.cli.user_preference_cli import UserPreferences

# --- Utility setup ---

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
    """Create a temporary UserPreferenceStore with a fresh SQLite DB record."""
    db_path = tmp_path / "prefs.db"
    store = UserPreferenceStore(db_path=db_path)
    create_user_pref_table(store.conn)
    yield store
    store.close()


# --- Tests for the DB store ---

def test_save_and_get_preferences(temp_store):
    store = temp_store

    # Save one preference record
    store.save_preferences(
        user_id="user1",
        name="Alice Example",
        github_user="alicegit",
        education="BSc Computer Science",
        industry="Technology",
        job_title="Developer"
    )

    prefs = store.get_latest_preferences()
    assert prefs is not None
    assert prefs["name"] == "Alice Example"
    assert prefs["github_user"] == "alicegit"
    assert prefs["industry"] == "Technology"


def test_get_preferences_returns_none_when_empty(temp_store):
    """Ensure no crash when DB is empty."""
    assert temp_store.get_latest_preferences() is None


def test_save_preferences_overwrites_latest(temp_store):
    """Ensure the most recently updated record is retrieved."""
    store = temp_store
    store.save_preferences("user1", "First Name", "gh1", "MS", "Finance", "Analyst")

    prefs = store.get_latest_preferences()
    assert prefs["user_id"] == "user1"
    assert prefs["name"] == "First Name"


def test_persistence_across_sessions(tmp_path):
    """Ensure data persists when DB is reopened."""
    db_path = tmp_path / "prefs.db"

    s1 = UserPreferenceStore(db_path=db_path)
    create_user_pref_table(s1.conn)
    s1.save_preferences("persist_user", "Persist Name", "persistGH", "BA", "Education", "Instructor")
    s1.close()

    s2 = UserPreferenceStore(db_path=db_path)
    prefs = s2.get_latest_preferences()
    s2.close()

    assert prefs is not None
    assert prefs["name"] == "Persist Name"
    assert prefs["github_user"] == "persistGH"


# --- CLI Test ---

@pytest.fixture
def fake_store():
    """A fake in-memory store to test CLI logic without touching a DB."""
    class FakeStore:
        def __init__(self):
            self.data = []

        def get_latest_preferences(self):
            return self.data[-1] if self.data else None

        def save_preferences(self, user_id, name, github_user, education, industry, job_title):
            self.data.append({
                "user_id": user_id,
                "name": name,
                "github_user": github_user,
                "education": education,
                "industry": industry,
                "job_title": job_title
            })

        def close(self):
            pass

    return FakeStore()


def test_cli_creates_and_saves_preferences(monkeypatch, capsys, fake_store):
    """Simulate CLI user input and ensure preferences save correctly."""
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

    saved = fake_store.get_latest_preferences()
    assert saved is not None
    assert saved["name"] == "Test User"
    assert saved["github_user"] == "testgh"
    assert saved["industry"] == "Technology"
