import pytest
import sqlite3
from app.utils.retrieve_insights_utils import get_portfolio_resume_insights, format_date

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
            rank INTEGER,
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

    # Insert test data
    cur.execute("INSERT INTO PROJECT VALUES ('sig1', 'Test Project', 1, 'A summary.', '2024-01-01 10:00:00', '2024-02-01 10:00:00')")
    cur.execute("INSERT INTO SKILL_ANALYSIS VALUES ('sig1', 'Python', 'code')")
    cur.execute("INSERT INTO SKILL_ANALYSIS VALUES ('sig1', 'Testing', 'code')")
    cur.execute("INSERT INTO DASHBOARD_DATA VALUES ('sig1', 'author', 'James')")
    cur.execute("INSERT INTO DASHBOARD_DATA VALUES ('sig1', 'lines_of_code', 106)")
    cur.execute("INSERT INTO RESUME_SUMMARY VALUES ('sig1', 'Built a test project.')")
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
    assert len(portfolio["projects"]) == 1
    assert portfolio["projects"][0]["name"] == "Test Project"
    assert "Python" in portfolio["projects"][0]["skills"]
    assert "Testing" in portfolio["projects"][0]["skills"]
    assert resume is not None