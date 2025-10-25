import sqlite3
from pathlib import Path

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR 
DB_PATH = DATA_DIR / "app.sqlite3"

# --- SQL Schema ---
SCHEMA = """
CREATE TABLE IF NOT EXISTS CONSENT (
    id INTEGER PRIMARY KEY,
    policy_version TEXT,
    consent_given INTEGER DEFAULT 0,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS USER_PREFERENCES (
    id INTEGER PRIMARY KEY,
    industry TEXT,
    education TEXT,
    job_title TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS PROJECT (
    project_signature TEXT PRIMARY KEY,
    name TEXT,
    path TEXT,
    file_signatures JSON, -- file path signitures 
    size_bytes INTEGER,
    rank INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--Analyzed Git Data---

CREATE TABLE IF NOT EXISTS GIT_HISTORY (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    commit_hash TEXT,
    author_name TEXT,
    author_email TEXT,
    commit_date DATETIME,
    message TEXT,
    FOREIGN KEY (project_id) REFERENCES PROJECT(project_signature) ON DELETE CASCADE
);

-- Analyzed Skill Analysis Data --

CREATE TABLE IF NOT EXISTS SKILL_ANALYSIS (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    skill TEXT,
    source TEXT, -- 'code' or 'non-code'
    FOREIGN KEY (project_id) REFERENCES PROJECT(project_signature) ON DELETE CASCADE
);

-- Analyzed Dashbaord Data --

CREATE TABLE IF NOT EXISTS DASHBOARD_DATA (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    metric_name TEXT,
    metric_value TEXT,
    chart_type TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES PROJECT(project_signature) ON DELETE CASCADE
);

-- Analyzed Resume Data --

CREATE TABLE IF NOT EXISTS RESUME_SUMMARY (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    summary_text TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES PROJECT(project_signature) ON DELETE CASCADE
);
"""

# --- DB Setup Functions ---
def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def get_connection():
    ensure_data_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """Create database file and initial tables."""
    ensure_data_dir()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript(SCHEMA)
    conn.commit()
    conn.close()
    print(f"Database initialized at: {DB_PATH}")
