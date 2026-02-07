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
        education_details JSON,
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
        user_id=1,
        name="Alice Example",
        email="alice@example.com",
        github_user="alicegit",
        education="BSc Computer Science",
        industry="Technology",
        job_title="Developer",
        education_details={"institution": "University of Example", "degree": "CS", "start_date": 2015, "end_date": 2019}
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
        user_id=1,
        name="Persist Name",
        email="persist@example.com",
        github_user="persistGH",
        education="BA",
        industry="Education",
        job_title="Instructor",
        education_details={"institution": "Persist University", "degree": "BA", "start_date": 2010, "end_date": 2014}
    )
    store1.close()

    store2 = UserPreferenceStore(db_path=str(db_path))
    prefs = store2.get_latest_preferences()
    store2.close()

    assert prefs["name"] == "Persist Name"
    assert prefs["github_user"] == "persistGH"

def test_latest_preference_retrieval (tmp_path):
    db_path = tmp_path / "prefs.db"
    store1 = UserPreferenceStore(db_path=str(db_path))
    create_user_pref_table(store1.conn)
    store1.save_preferences(
        user_id=1,
        name="Persist Name",
        email="persist@example.com",
        github_user="persistGH",
        education="BA",
        industry="Education",
        job_title="Instructor",
        education_details={"institution": "Persist University", "degree": "BA", "start_date": 2010, "end_date": 2014}
    )
    store1.close()
    # Ensure different timestamps between records
    time.sleep(1)


    store2 = UserPreferenceStore(db_path=str(db_path))
    store2.save_preferences(
        user_id=2,
        name="Latest Name",
        email="latest@example.com",
        github_user="latestGH",
        education="MA",
        industry="Technology",
        job_title="Senior Developer",
        education_details={"institution": "Latest University", "degree": "MA", "start_date": 2015, "end_date": 2020}
    )
    prefs = store2.get_latest_preferences()
    store2.close()

    assert prefs["name"] == "Latest Name"
    assert prefs["github_user"] == "latestGH"


def test_latest_preferences_no_email_lookup(temp_store, monkeypatch):
    """
    Ensure optimized lookup returns latest preferences
    without relying on email.
    """
    temp_store.save_preferences(
        user_id=1,
        name="No Email User",
        email="noemail@example.com",
        github_user="ghuser",
        education="PhD",
        industry="Research",
        job_title="Scientist",
        education_details={"institution": "Research University", "degree": "PhD", "start_date": 2010, "end_date": 2015}
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

    def save_preferences(self,user_id, name, email, github_user, education, industry, job_title, education_details=None):
        self.data.append({
            user_id: 1,
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
        user_id=1,
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