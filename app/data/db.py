import sqlite3
from pathlib import Path

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR 
DB_PATH = DATA_DIR / "app.sqlite3"

# --- SQL Schema ---
SCHEMA = """
CREATE TABLE IF NOT EXISTS CONSENT (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    policy_version TEXT,
    consent_given INTEGER DEFAULT 0,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS USER_PREFERENCES (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    industry TEXT,
    education TEXT,
    custom_industry TEXT,
    custom_education TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS PROJECT (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    path TEXT,
    signature TEXT UNIQUE,
    size_bytes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS FILE_METADATA (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    file_path TEXT,
    file_type TEXT,
    size_bytes INTEGER,
    last_modified DATETIME,
    content_hash TEXT,
    FOREIGN KEY (project_id) REFERENCES PROJECT(id)
);

CREATE TABLE IF NOT EXISTS GIT_HISTORY (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    commit_hash TEXT,
    author_name TEXT,
    author_email TEXT,
    commit_date DATETIME,
    message TEXT,
    FOREIGN KEY (project_id) REFERENCES PROJECT(id)
);

CREATE TABLE IF NOT EXISTS SKILL_ANALYSIS (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    skill TEXT,
    confidence REAL,
    source TEXT, -- 'code' or 'non-code'
    FOREIGN KEY (project_id) REFERENCES PROJECT(id)
);

CREATE TABLE IF NOT EXISTS DASHBOARD_DATA (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    metric_name TEXT,
    metric_value TEXT,
    chart_type TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES PROJECT(id)
);

CREATE TABLE IF NOT EXISTS RESUME_SUMMARY (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    summary_text TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES PROJECT(id)
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
