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
    project_id text,
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
    project_id TEXT,
    skill TEXT,
    source TEXT, -- 'code' or 'non-code'
    FOREIGN KEY (project_id) REFERENCES PROJECT(project_signature) ON DELETE CASCADE
);

-- Analyzed Dashbaord Data --

CREATE TABLE IF NOT EXISTS DASHBOARD_DATA (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT,
    metric_name TEXT,
    metric_value TEXT,
    chart_type TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES PROJECT(project_signature) ON DELETE CASCADE
);

-- Analyzed Resume Data --

CREATE TABLE IF NOT EXISTS RESUME_SUMMARY (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT,
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

def seed_db():
    """Insert test/seed data into tables."""
    conn = get_connection()
    cursor = conn.cursor()

       # --- CONSENT ---
    cursor.execute("INSERT OR IGNORE INTO CONSENT (id, policy_version, consent_given) VALUES (1, ?, ?)", 
                   ("v1.0", 1))

    # --- USER_PREFERENCES ---
    cursor.execute("INSERT OR IGNORE INTO USER_PREFERENCES (id, industry, education) VALUES (1, ?, ?)", 
                   ("Software", "Bachelor's"))

    # Simulate multiple projects from a zip
    projects = [
        {"name": "Alpha Project", "path": "/user/test/alpha", "signature": "sig_alpha", "size_bytes": 2048},
        {"name": "Beta Project", "path": "/user/test/beta", "signature": "sig_beta", "size_bytes": 4096},
        {"name": "Gamma Project", "path": "/user/test/gamma", "signature": "sig_gamma", "size_bytes": 1024},
    ]

    for proj in projects:
        cursor.execute("""
            INSERT OR IGNORE INTO PROJECT (name, path, signature, size_bytes) 
            VALUES (?, ?, ?, ?)
        """, (proj["name"], proj["path"], proj["signature"], proj["size_bytes"]))

        # Get project_id for relationships
        cursor.execute("SELECT id FROM PROJECT WHERE signature = ?", (proj["signature"],))
        project_id = cursor.fetchone()[0]

        # --- FILE_METADATA ---
        files = [
            {"file_path": "main.py", "file_type": "code", "size_bytes": 512, "content_hash": "hash_main"},
            {"file_path": "utils.py", "file_type": "code", "size_bytes": 256, "content_hash": "hash_utils"},
            {"file_path": "README.md", "file_type": "non-code", "size_bytes": 128, "content_hash": "hash_readme"},
        ]
        for f in files:
            cursor.execute("""
                INSERT OR IGNORE INTO FILE_METADATA (project_id, file_path, file_type, size_bytes, last_modified, content_hash) 
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
            """, (project_id, f["file_path"], f["file_type"], f["size_bytes"], f["content_hash"]))

        # --- GIT_HISTORY ---
        commits = [
            {"commit_hash": "c1", "author_name": "Alice", "author_email": "alice@example.com", "message": "Initial commit"},
            {"commit_hash": "c2", "author_name": "Bob", "author_email": "bob@example.com", "message": "Added utils"},
        ]
        for c in commits:
            cursor.execute("""
                INSERT OR IGNORE INTO GIT_HISTORY (project_id, commit_hash, author_name, author_email, commit_date, message) 
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
            """, (project_id, c["commit_hash"], c["author_name"], c["author_email"], c["message"]))

        # --- SKILL_ANALYSIS ---
        skills = [
            {"skill": "Python", "confidence": 0.95, "source": "code"},
            {"skill": "Git", "confidence": 0.9, "source": "non-code"},
        ]
        for s in skills:
            cursor.execute("""
                INSERT OR IGNORE INTO SKILL_ANALYSIS (project_id, skill, confidence, source) 
                VALUES (?, ?, ?, ?)
            """, (project_id, s["skill"], s["confidence"], s["source"]))

        # --- DASHBOARD_DATA ---
        metrics = [
            {"metric_name": "Lines of Code", "metric_value": str(sum(f["size_bytes"] for f in files)), "chart_type": "bar"},
            {"metric_name": "Files Count", "metric_value": str(len(files)), "chart_type": "pie"},
        ]
        for m in metrics:
            cursor.execute("""
                INSERT OR IGNORE INTO DASHBOARD_DATA (project_id, metric_name, metric_value, chart_type) 
                VALUES (?, ?, ?, ?)
            """, (project_id, m["metric_name"], m["metric_value"], m["chart_type"]))

        # --- RESUME_SUMMARY ---
        cursor.execute("""
            INSERT OR IGNORE INTO RESUME_SUMMARY (project_id, summary_text) 
            VALUES (?, ?)
        """, (project_id, f"Worked on {proj['name']}, implementing core functionality and utilities."))

    conn.commit()
    conn.close()

    print("Seed data inserted successfully")