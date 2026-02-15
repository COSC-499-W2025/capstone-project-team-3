import pytest
import sqlite3
from app.utils.retrieve_insights_utils import (
    get_portfolio_resume_insights,
    get_projects_by_signatures,
    format_date,
)

@pytest.fixture
def setup_test_db(tmp_path, monkeypatch):
    # Create a temporary SQLite DB
    db_path = tmp_path / "test.sqlite3"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # Create tables
    cur.execute("""
        CREATE TABLE PROJECT (
            project_signature TEXT PRIMARY KEY,
            name TEXT,
            score REAL,
            score_overridden INTEGER,
            score_overridden_value REAL,
            summary TEXT,
            created_at TEXT,
            last_modified TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE SKILL_ANALYSIS (
            project_id TEXT,
            skill TEXT,
            source TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE RESUME_SUMMARY (
            project_id TEXT,
            summary_text TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE DASHBOARD_DATA (
        project_id TEXT,
        metric_name TEXT,
        metric_value TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE GIT_HISTORY (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT,
            commit_hash TEXT,
            author_name TEXT,
            author_email TEXT,
            commit_date TEXT,
            message TEXT
        )
    """)

    # Insert test data
    cur.execute(
        """
        INSERT INTO PROJECT
        VALUES ('sig1', 'Test Project', 0.9, 0, NULL, 'A summary.', '2024-01-01 10:00:00', '2024-02-01 10:00:00')
        """
    )
    cur.execute(
        """
        INSERT INTO PROJECT
        VALUES ('sig2', 'Override Project', 0.4, 1, 0.95, 'B summary.', '2024-01-05 10:00:00', '2024-02-04 10:00:00')
        """
    )
    cur.execute("INSERT INTO SKILL_ANALYSIS VALUES ('sig1', 'Python', 'code')")
    cur.execute("INSERT INTO SKILL_ANALYSIS VALUES ('sig1', 'Testing', 'code')")
    cur.execute("INSERT INTO SKILL_ANALYSIS VALUES ('sig2', 'FastAPI', 'code')")
    cur.execute("INSERT INTO DASHBOARD_DATA VALUES ('sig1', 'author', 'James')")
    cur.execute("INSERT INTO DASHBOARD_DATA VALUES ('sig1', 'lines_of_code', 106)")
    cur.execute("INSERT INTO DASHBOARD_DATA VALUES ('sig2', 'author', 'Alice')")
    cur.execute("INSERT INTO RESUME_SUMMARY VALUES ('sig1', 'Built a test project.')")
    cur.execute("INSERT INTO RESUME_SUMMARY VALUES ('sig2', 'Built an override project.')")
    cur.execute("INSERT INTO GIT_HISTORY (project_id, commit_hash, author_name, commit_date, message) VALUES (?, ?, ?, ?, ?)",
                ('sig1', 'abc123', 'James', '2024-01-02 09:00:00', 'Initial commit'))
    conn.commit()
    conn.close()
    # Save the original connect function
    original_connect = sqlite3.connect
    # Monkeypatch sqlite3.connect to use our test DB
    monkeypatch.setattr("app.utils.retrieve_insights_utils.get_connection", lambda: original_connect(str(db_path)))
    yield
    # Cleanup
    db_path.unlink()
    
def test_format_date():
    assert format_date("2024-01-01 10:00:00") == "2024-01-01"
    assert format_date("") == ""

def test_get_portfolio_resume_insights(setup_test_db):
    portfolio, resume = get_portfolio_resume_insights()
    assert len(portfolio["projects"]) == 2

    test_project = next(p for p in portfolio["projects"] if p["project_signature"] == "sig1")
    override_project = next(p for p in portfolio["projects"] if p["project_signature"] == "sig2")

    assert test_project["name"] == "Test Project"
    assert "Python" in test_project["skills"]
    assert "Testing" in test_project["skills"]
    assert test_project["score"] == pytest.approx(0.9)
    assert test_project["score_overridden"] is False

    assert override_project["score"] == pytest.approx(0.95)
    assert override_project["score_original"] == pytest.approx(0.4)
    assert override_project["score_overridden"] is True
    assert override_project["display_score"] == pytest.approx(0.95)

    assert portfolio["top_projects"][0]["project_signature"] == "sig2"
    assert resume is not None


def test_get_projects_by_signatures_override_resolution(setup_test_db):
    project = get_projects_by_signatures("sig2")
    assert project["project_signature"] == "sig2"
    assert project["score"] == pytest.approx(0.95)
    assert project["score_original"] == pytest.approx(0.4)
    assert project["score_overridden"] is True
