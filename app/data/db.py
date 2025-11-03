import datetime
import json
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
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    github_user TEXT,
    industry TEXT,
    education TEXT,
    job_title TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    """Insert test/seed data aligned with new schema."""
    conn = get_connection()
    cursor = conn.cursor()

    # --- CONSENT ---
    cursor.execute("""
        INSERT OR IGNORE INTO CONSENT (id, policy_version, consent_given)
        VALUES (1, ?, ?)
    """, ("v1.0", 1))

    # --- USER_PREFERENCES ---
    cursor.execute("""
        INSERT OR IGNORE INTO USER_PREFERENCES (user_id, name, email, github_user, industry, education, job_title)
        VALUES (1,?, ?, ?, ?, ?, ?)
    """, ("John User","johnU@gmail.com", "testuser", "Technology", "Bachelor's", "Developer"))

    # --- Simulate multiple projects from a ZIP upload ---
    projects = [
        {
            "project_signature": "sig_alpha_project/hash",
            "name": "Alpha Project",
            "path": "/user/test/alpha",
            "file_signatures": ["alpha_main_hash", "alpha_utils_hash", "alpha_readme_hash"],
            "size_bytes": 2048,
            "rank": 1,
        },
        {
            "project_signature": "sig_beta_project/hash",
            "name": "Beta Project",
            "path": "/user/test/beta",
            "file_signatures": ["beta_core_hash", "beta_helper_hash"],
            "size_bytes": 4096,
            "rank": 2,
        },
        {
            "project_signature": "sig_gamma_project/hash",
            "name": "Gamma Project",
            "path": "/user/test/gamma",
            "file_signatures": ["gamma_app_hash", "gamma_test_hash", "gamma_docs_hash"],
            "size_bytes": 1024,
            "rank": 3,
        },
    ]

    for proj in projects:
        cursor.execute("""
            INSERT OR IGNORE INTO PROJECT (project_signature, name, path, file_signatures, size_bytes, rank)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            proj["project_signature"],
            proj["name"],
            proj["path"],
            json.dumps(proj["file_signatures"]),
            proj["size_bytes"],
            proj["rank"]
        ))

        project_id = proj["project_signature"]

        # --- GIT_HISTORY ---
        commits = [
            {"commit_hash": "c1", "author_name": "Alice", "author_email": "alice@example.com", "message": "Initial commit"},
            {"commit_hash": "c2", "author_name": "Bob", "author_email": "bob@example.com", "message": "Refactored utils"},
        ]
        for c in commits:
            cursor.execute("""
                INSERT OR IGNORE INTO GIT_HISTORY (project_id, commit_hash, author_name, author_email, commit_date, message)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                project_id,
                c["commit_hash"],
                c["author_name"],
                c["author_email"],
                datetime.datetime.now().isoformat(),
                c["message"]
            ))

        # --- SKILL_ANALYSIS ---
        skills = [
            {"skill": "Python", "source": "code"},
            {"skill": "Git", "source": "non-code"},
        ]
        for s in skills:
            cursor.execute("""
                INSERT OR IGNORE INTO SKILL_ANALYSIS (project_id, skill, source)
                VALUES (?, ?, ?)
            """, (project_id, s["skill"], s["source"]))

        # --- DASHBOARD_DATA ---
        metrics = [
            {"metric_name": "Lines of Code", "metric_value": str(proj["size_bytes"]), "chart_type": "bar"},
            {"metric_name": "Files Count", "metric_value": str(len(proj["file_signatures"])), "chart_type": "pie"},
        ]
        for m in metrics:
            cursor.execute("""
                INSERT OR IGNORE INTO DASHBOARD_DATA (project_id, metric_name, metric_value, chart_type)
                VALUES (?, ?, ?, ?)
            """, (project_id, m["metric_name"], m["metric_value"], m["chart_type"]))

        # --- RESUME_SUMMARY ---
        summary_text = f"{proj['name']} demonstrates skills in Python, Git, and collaborative project structure."
        cursor.execute("""
            INSERT OR IGNORE INTO RESUME_SUMMARY (project_id, summary_text)
            VALUES (?, ?)
        """, (project_id, summary_text))

    conn.commit()
    conn.close()

    print("Seed data inserted successfully")