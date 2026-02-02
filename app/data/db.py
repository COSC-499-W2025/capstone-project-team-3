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
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
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
    score REAL CHECK (score >= 0.0 AND score <= 1.0),
    score_overridden INTEGER DEFAULT 0,
    score_overridden_value REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    summary TEXT,
    thumbnail_path TEXT
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
    source TEXT, -- 'technical' or 'soft'
    FOREIGN KEY (project_id) REFERENCES PROJECT(project_signature) ON DELETE CASCADE
);

-- Analyzed Dashbaord Data --

CREATE TABLE IF NOT EXISTS DASHBOARD_DATA (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT,
    metric_name TEXT,
    metric_value TEXT,
    chart_type TEXT DEFAULT NONE,
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

-- Table for resume versions --
CREATE TABLE IF NOT EXISTS RESUME (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--Table to edited resume details --
CREATE TABLE IF NOT EXISTS RESUME_PROJECT (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_id INTEGER NOT NULL,
    project_id TEXT NOT NULL,

    project_name TEXT,     -- optional override
    start_date DATETIME,       -- optional override
    end_date DATETIME,         -- optional override
    skills JSON,
    bullets JSON,          -- optional edited bullets for this resume

    display_order INTEGER,

    FOREIGN KEY (resume_id) REFERENCES RESUME(id) ON DELETE CASCADE,
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
    _migrate_project_rank_to_score(cursor)
    _migrate_project_score_override_fields(cursor)
    _ensure_project_score_constraint(cursor)
    conn.commit()
    conn.close()
    print(f"Database initialized at: {DB_PATH}")

def _migrate_project_rank_to_score(cursor: sqlite3.Cursor) -> None:
    """Backfill PROJECT.score from legacy PROJECT.rank if needed."""
    cursor.execute("PRAGMA table_info(PROJECT)")
    columns = {row[1] for row in cursor.fetchall()}
    if "score" not in columns:
        cursor.execute("ALTER TABLE PROJECT ADD COLUMN score REAL")
    if "rank" in columns:
        cursor.execute("UPDATE PROJECT SET score = rank WHERE score IS NULL")

def _migrate_project_score_override_fields(cursor: sqlite3.Cursor) -> None:
    """Add override fields to PROJECT if missing."""
    cursor.execute("PRAGMA table_info(PROJECT)")
    columns = {row[1] for row in cursor.fetchall()}
    if "score_overridden" not in columns:
        cursor.execute("ALTER TABLE PROJECT ADD COLUMN score_overridden INTEGER DEFAULT 0")
    if "score_overridden_value" not in columns:
        cursor.execute("ALTER TABLE PROJECT ADD COLUMN score_overridden_value REAL")

def _ensure_project_score_constraint(cursor: sqlite3.Cursor) -> None:
    """Enforce score range [0, 1] on existing DBs via triggers."""
    cursor.execute("DROP TRIGGER IF EXISTS project_score_range_insert")
    cursor.execute("DROP TRIGGER IF EXISTS project_score_range_update")
    cursor.execute("DROP TRIGGER IF EXISTS project_score_override_range_insert")
    cursor.execute("DROP TRIGGER IF EXISTS project_score_override_range_update")
    cursor.execute("""
        CREATE TRIGGER project_score_range_insert
        BEFORE INSERT ON PROJECT
        FOR EACH ROW
        WHEN NEW.score IS NOT NULL AND (NEW.score < 0.0 OR NEW.score > 1.0)
        BEGIN
            SELECT RAISE(ABORT, 'project score must be between 0 and 1');
        END;
    """)
    cursor.execute("""
        CREATE TRIGGER project_score_range_update
        BEFORE UPDATE OF score ON PROJECT
        FOR EACH ROW
        WHEN NEW.score IS NOT NULL AND (NEW.score < 0.0 OR NEW.score > 1.0)
        BEGIN
            SELECT RAISE(ABORT, 'project score must be between 0 and 1');
        END;
    """)
    cursor.execute("""
        CREATE TRIGGER project_score_override_range_insert
        BEFORE INSERT ON PROJECT
        FOR EACH ROW
        WHEN NEW.score_overridden_value IS NOT NULL AND (NEW.score_overridden_value < 0.0 OR NEW.score_overridden_value > 1.0)
        BEGIN
            SELECT RAISE(ABORT, 'project overridden score must be between 0 and 1');
        END;
    """)
    cursor.execute("""
        CREATE TRIGGER project_score_override_range_update
        BEFORE UPDATE OF score_overridden_value ON PROJECT
        FOR EACH ROW
        WHEN NEW.score_overridden_value IS NOT NULL AND (NEW.score_overridden_value < 0.0 OR NEW.score_overridden_value > 1.0)
        BEGIN
            SELECT RAISE(ABORT, 'project overridden score must be between 0 and 1');
        END;
    """)

def seed_db():
    """Insert test/seed data aligned with new schema."""
    conn = get_connection()
    cursor = conn.cursor()

    # --- CONSENT ---
    cursor.execute("""
        INSERT OR IGNORE INTO CONSENT (id, policy_version, consent_given)
        VALUES (1, ?, 0)
    """, ("v1.0",))

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
            "score": 0.92,
            "created_at": "2024-01-15 10:30:00",  
            "last_modified": "2024-11-20 14:45:00", 
            "summary": "Alpha Project is a web-based task management application built with Python and Flask. "
            "It enables users to create, assign, and track tasks in real time, featuring user authentication, "
            "role-based access, and interactive dashboards. The project demonstrates strong skills in backend development, "
            "RESTful API design, and team collaboration."
        },
        {
            "project_signature": "sig_beta_project/hash",
            "name": "Beta Project",
            "path": "/user/test/beta",
            "file_signatures": ["beta_core_hash", "beta_helper_hash"],
            "size_bytes": 4096,
            "score": 0.85,
            "created_at": "2024-03-10 09:15:00",  
            "last_modified": "2024-11-22 16:20:00",
            "summary": "Beta Project is a machine learning pipeline developed in Python that automates data preprocessing, "
            "model training, and evaluation. It incorporates libraries such as Pandas, Scikit-learn, and TensorFlow to build predictive models. "
            "The project highlights expertise in data science, algorithm optimization, and end-to-end ML workflow."
        },
        {
            "project_signature": "sig_gamma_project/hash",
            "name": "Gamma Project",
            "path": "/user/test/gamma",
            "file_signatures": ["gamma_app_hash", "gamma_test_hash", "gamma_docs_hash"],
            "size_bytes": 1024,
            "score": 0.78,
            "created_at": "2024-06-05 11:00:00",  
            "last_modified": "2024-11-25 09:30:00",
            "summary": "Gamma Project is a mobile application developed using React Native that provides users with personalized fitness tracking. "
            "It features real-time activity monitoring, goal setting, and social sharing capabilities. "
        },
    ]

    for proj in projects:
        cursor.execute("""
            INSERT OR IGNORE INTO PROJECT (project_signature, name, path, file_signatures, size_bytes, score, created_at, last_modified, summary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            proj["project_signature"],
            proj["name"],
            proj["path"],
            json.dumps(proj["file_signatures"]),
            proj["size_bytes"],
            proj["score"],
            proj["created_at"],        
            proj["last_modified"],     
            proj["summary"]

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
        if proj["name"] == "Alpha Project":
            skills = [
                {"skill": "Python", "source": "code"},
                {"skill": "Flask", "source": "code"},
                {"skill": "Backend Development", "source": "code"},
                {"skill": "RESTful API Design", "source": "code"},
                {"skill": "Team Collaboration", "source": "non-code"},
                {"skill": "Git", "source": "code"},
                {"skill": "Agile Methodologies", "source": "non-code"},
            ]
        elif proj["name"] == "Beta Project":
            skills = [
                {"skill": "Machine Learning", "source": "code"},
                {"skill": "Data Preprocessing", "source": "code"},
                {"skill": "Feature Engineering", "source": "code"},
                {"skill": "Scikit-learn", "source": "code"},
                {"skill": "TensorFlow", "source": "code"},
                {"skill": "Pandas", "source": "code"},
                {"skill": "Algorithm Optimization", "source": "code"},
            ]
        elif proj["name"] == "Gamma Project":
            skills = [
                {"skill": "React Native", "source": "code"},
                {"skill": "Mobile Development", "source": "code"},
                {"skill": "Fitness Tracking", "source": "non-code"},
                {"skill": "Real-time Monitoring", "source": "code"},
                {"skill": "Goal Setting", "source": "non-code"},
                {"skill": "Social Sharing", "source": "non-code"},
                {"skill": "Sphinx", "source": "code"},
                {"skill": "CI/CD Integration", "source": "code"}
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
        resume_bullets = []
        if proj["name"] == "Alpha Project":
            resume_bullets = [
                "Designed and implemented a Flask-based web application for real-time task management.",
                "Integrated user authentication and role-based access control.",
                "Developed interactive dashboards for project tracking.",
                "Collaborated with a cross-functional team using Git and Agile methodologies."
            ]
        elif proj["name"] == "Beta Project":
            resume_bullets = [
                "Built a machine learning pipeline for customer churn prediction using scikit-learn.",
                "Automated data preprocessing and feature engineering workflows.",
                "Deployed predictive models and evaluated performance metrics.",
                "Utilized Pandas and TensorFlow for scalable data analysis."
            ]
        elif proj["name"] == "Gamma Project":
            resume_bullets = [
                "Developed a React Native mobile app for personalized fitness tracking.",
                "Implemented real-time activity monitoring and goal setting features.",
                "Enabled social sharing and user engagement functionalities.",
                "Automated documentation generation using Sphinx and CI/CD integration."
            ]
        for bullet in resume_bullets:
            cursor.execute("""
                INSERT OR IGNORE INTO RESUME_SUMMARY (project_id, summary_text)
                VALUES (?, ?)
            """, (project_id, bullet))
            
    # --- RESUME ---
    cursor.execute("""
        INSERT OR IGNORE INTO RESUME (id, name, created_at)
        VALUES (?, ?, ?)
    """, (1, "John's Resume", "2026-01-30"))

    # --- RESUME_PROJECT ---
    cursor.execute("""
        INSERT OR IGNORE INTO RESUME_PROJECT (
            resume_id, project_id, project_name, start_date, end_date, skills, bullets, display_order
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        1,  # resume_id
        "sig_alpha_project/hash",  # project_id
        "Alpha Project (Resume)",  # project_name override
        "2024-01-01",  # start_date
        "2024-06-01",  # end_date
        json.dumps(["Python", "Flask"]),  # skills
        json.dumps([
            "Built a Flask web app for task management.",
            "Led a team of 4 developers."
        ]),  # bullets
        1  # display_order
    ))

    conn.commit()
    conn.close()

    print("Seed data inserted successfully")
