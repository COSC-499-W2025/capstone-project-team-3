import sqlite3
import pytest
import time
from app.utils.user_preference_utils import UserPreferenceStore

# --- Utility setup ---

def create_user_pref_table(conn: sqlite3.Connection):
    """Ensure USER_PREFERENCES table exists."""
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS USER_PREFERENCES (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
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
    prefs = temp_store.get_latest_preferences()
    assert prefs["name"] == "Alice Example"
    assert prefs["github_user"] == "alicegit"
    assert prefs["industry"] == "Technology"

def test_get_preferences_none(temp_store):
    assert temp_store.get_latest_preferences() is None

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
    prefs = store2.get_latest_preferences()
    store2.close()

    assert prefs["name"] == "Persist Name"
    assert prefs["github_user"] == "persistGH"

def test_latest_preference_retrieval (tmp_path):
    """Test that updating preferences replaces the existing single user record."""
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
    
    # Verify first save worked
    prefs1 = store1.get_latest_preferences()
    assert prefs1["name"] == "Persist Name"
    store1.close()
    
    # Ensure different timestamps between updates
    time.sleep(1)

    # Update the same user record (user_id=1)
    store2 = UserPreferenceStore(db_path=str(db_path))
    store2.save_preferences(
        name="Latest Name",
        email="latest@example.com",
        github_user="latestGH",
        education="MA",
        industry="Technology",
        job_title="Senior Developer"
    )
    prefs = store2.get_latest_preferences()
    
    # Verify the record was updated, not duplicated
    assert prefs["name"] == "Latest Name"
    assert prefs["github_user"] == "latestGH"
    
    # Verify only ONE row exists (single-user app)
    cur = store2.conn.cursor()
    cur.execute("SELECT COUNT(*) FROM USER_PREFERENCES")
    count = cur.fetchone()[0]
    assert count == 1, "Should only have one user record"
    
    store2.close()


def test_latest_preferences_no_email_lookup(temp_store, monkeypatch):
    """
    Ensure optimized lookup returns latest preferences
    without relying on email.
    """
    temp_store.save_preferences(
        name="No Email User",
        email="noemail@example.com",
        github_user="ghuser",
        education="PhD",
        industry="Research",
        job_title="Scientist",
    )

    # Ensure static lookup uses the temp DB, not the default app DB
    monkeypatch.setattr(
        "app.utils.user_preference_utils.get_connection",
        lambda: temp_store.conn
    )
    prefs = UserPreferenceStore.get_latest_preferences_no_email()
    assert prefs["industry"] == "Research"
    assert prefs["job_title"] == "Scientist"
    assert prefs["education"] == "PhD"

# --- CLI logic tests (store-like behavior, no input mocking) ---

class FakeStore:
    def __init__(self):
        self.data = []

    def get_latest_preferences(self):
        return self.data[-1] if self.data else None

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

def test_store_like_save_and_retrieve_preferences():
    store = FakeStore()

    store.save_preferences(
        name="Test User",
        email="user@example.com",
        github_user="testgh",
        education="BSc",
        industry="Technology",
        job_title="Developer"
    )

    prefs = store.get_latest_preferences()
    assert prefs["name"] == "Test User"
    assert prefs["email"] == "user@example.com"
    assert prefs["github_user"] == "testgh"