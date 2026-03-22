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
    linkedin TEXT,
    industry TEXT,
    education TEXT,
    job_title TEXT,
    personal_summary TEXT,
    education_details JSON,
    profile_picture_path TEXT,
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
    score_override_exclusions TEXT,
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
    date TEXT, -- When skill was acquired/used (YYYY-MM-DD)
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

-- Table for edited resume skills --
CREATE TABLE IF NOT EXISTS RESUME_SKILLS (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_id INTEGER NOT NULL UNIQUE,
    skills JSON NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resume_id) REFERENCES RESUME(id) ON DELETE CASCADE
);

-- Table for edited resume awards/honours (tailored resumes only)
CREATE TABLE IF NOT EXISTS RESUME_AWARDS (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_id INTEGER NOT NULL UNIQUE,
    awards JSON NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resume_id) REFERENCES RESUME(id) ON DELETE CASCADE
);

-- Table for edited resume work experience (tailored resumes only)
CREATE TABLE IF NOT EXISTS RESUME_WORK_EXPERIENCE (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_id INTEGER NOT NULL UNIQUE,
    work_experience JSON NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resume_id) REFERENCES RESUME(id) ON DELETE CASCADE
);

--Table to edited resume details. project_id has no FK to PROJECT so we snapshot on delete and keep rows.
CREATE TABLE IF NOT EXISTS RESUME_PROJECT (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_id INTEGER NOT NULL,
    project_id TEXT NOT NULL,

    project_name TEXT,     -- optional override / snapshot when project deleted
    start_date DATETIME,
    end_date DATETIME,
    skills JSON,
    bullets JSON,

    display_order INTEGER,

    FOREIGN KEY (resume_id) REFERENCES RESUME(id) ON DELETE CASCADE,
    UNIQUE (resume_id, project_id)
);

-- Cover letter  --
CREATE TABLE IF NOT EXISTS COVER_LETTER (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_id INTEGER NOT NULL,
    job_title TEXT NOT NULL,
    company TEXT NOT NULL,
    job_description TEXT NOT NULL,
    motivations JSON,           -- JSON array of motivation keys
    content TEXT NOT NULL,      -- the generated plain-text letter body
    generation_mode TEXT NOT NULL CHECK (generation_mode IN ('ai', 'local')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resume_id) REFERENCES RESUME(id) ON DELETE CASCADE
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
    # Ensure Master Resume is created
    cursor.execute("""INSERT OR IGNORE INTO RESUME (id, name) VALUES (1, 'Master Resume')""")
    # Ensure ON CONFLICT(resume_id) works even on pre-existing DBs
    cursor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_resume_skills_resume_id ON RESUME_SKILLS(resume_id)"
    )
    _ensure_project_override_exclusions_column(cursor)
    _ensure_user_preferences_linkedin_column(cursor)
    _ensure_user_preferences_profile_picture_column(cursor)
    _ensure_project_score_constraint(cursor)
    _ensure_resume_project_has_no_project_fk(cursor)
    _ensure_cover_letter_table(cursor)
    conn.commit()
    conn.close()
    print(f"Database initialized at: {DB_PATH}")

def _ensure_project_override_exclusions_column(cursor: sqlite3.Cursor) -> None:
    """Ensure PROJECT has score_override_exclusions column on existing DBs."""
    cursor.execute("PRAGMA table_info(PROJECT)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    if "score_override_exclusions" not in existing_columns:
        cursor.execute("ALTER TABLE PROJECT ADD COLUMN score_override_exclusions TEXT")

def _ensure_user_preferences_linkedin_column(cursor: sqlite3.Cursor) -> None:
    """Ensure USER_PREFERENCES has linkedin column on existing DBs."""
    cursor.execute("PRAGMA table_info(USER_PREFERENCES)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    if "linkden" in existing_columns and "linkedin" not in existing_columns:
        cursor.execute("ALTER TABLE USER_PREFERENCES RENAME COLUMN linkden TO linkedin")
    elif "linkedin" not in existing_columns:
        cursor.execute("ALTER TABLE USER_PREFERENCES ADD COLUMN linkedin TEXT")

def _ensure_user_preferences_profile_picture_column(cursor: sqlite3.Cursor) -> None:
    """Ensure USER_PREFERENCES has profile_picture_path column on existing DBs."""
    cursor.execute("PRAGMA table_info(USER_PREFERENCES)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    if "profile_picture_path" not in existing_columns:
        cursor.execute("ALTER TABLE USER_PREFERENCES ADD COLUMN profile_picture_path TEXT")

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


def _ensure_resume_project_has_no_project_fk(cursor: sqlite3.Cursor) -> None:
    """
    Ensure RESUME_PROJECT has no foreign key on project_id to PROJECT.

    Earlier schema versions may have created RESUME_PROJECT with:
      FOREIGN KEY (project_id) REFERENCES PROJECT(project_signature) ON DELETE CASCADE

    That would cause RESUME_PROJECT rows to be deleted when a PROJECT row is deleted,
    defeating the snapshot logic that preserves tailored resume entries.

    This migration:
      - Detects an existing FK from RESUME_PROJECT to PROJECT
      - Rebuilds RESUME_PROJECT without that FK, preserving all rows and data
    """
    # If table does not exist yet, nothing to do (SCHEMA above will create the correct version)
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='RESUME_PROJECT'"
    )
    row = cursor.fetchone()
    if row is None:
        return

    # Inspect existing foreign keys on RESUME_PROJECT
    cursor.execute("PRAGMA foreign_key_list(RESUME_PROJECT)")
    fks = cursor.fetchall()
    # PRAGMA foreign_key_list columns: (id, seq, table, from, to, on_update, on_delete, match)
    has_project_fk = any(fk[2] == "PROJECT" for fk in fks)
    if not has_project_fk:
        # Already on the new schema (only resume_id FK); nothing to do.
        return

    # Rebuild RESUME_PROJECT to drop the FK on project_id while preserving data.
    # New schema matches the SCHEMA definition above.
    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS RESUME_PROJECT_NEW (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_id INTEGER NOT NULL,
            project_id TEXT NOT NULL,

            project_name TEXT,
            start_date DATETIME,
            end_date DATETIME,
            skills JSON,
            bullets JSON,

            display_order INTEGER,

            FOREIGN KEY (resume_id) REFERENCES RESUME(id) ON DELETE CASCADE,
            UNIQUE (resume_id, project_id)
        );

        INSERT INTO RESUME_PROJECT_NEW (
            id,
            resume_id,
            project_id,
            project_name,
            start_date,
            end_date,
            skills,
            bullets,
            display_order
        )
        SELECT
            id,
            resume_id,
            project_id,
            project_name,
            start_date,
            end_date,
            skills,
            bullets,
            display_order
        FROM RESUME_PROJECT;

        DROP TABLE RESUME_PROJECT;
        ALTER TABLE RESUME_PROJECT_NEW RENAME TO RESUME_PROJECT;
        """
    )

def _ensure_cover_letter_table(cursor: sqlite3.Cursor) -> None:
    """Ensure COVER_LETTER table exists on existing DBs (created before this feature)."""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='COVER_LETTER'")
    if cursor.fetchone() is None:
        cursor.execute("""
            CREATE TABLE COVER_LETTER (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id INTEGER NOT NULL,
                job_title TEXT NOT NULL,
                company TEXT NOT NULL,
                job_description TEXT NOT NULL,
                motivations JSON,
                content TEXT NOT NULL,
                generation_mode TEXT NOT NULL CHECK (generation_mode IN ('ai', 'local')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resume_id) REFERENCES RESUME(id) ON DELETE CASCADE
            )
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
        INSERT OR IGNORE INTO USER_PREFERENCES (user_id, name, email, github_user, industry, education, job_title, education_details)
        VALUES (1,?, ?, ?, ?, ?, ?, ?)
    """, ("John User","johnU@gmail.com", "testuser", "Technology", "Bachelor's", "Developer", json.dumps([
        {
            "institution": "State University",
            "degree": "B.Sc. in Computer Science",
            "start_date": "2018-09-01",
            "end_date": "2022-06-01",
            "gpa": 3.8
        },
        {
            "institution": "Tech Bootcamp",
            "degree": "Full Stack Web Development Certificate",
            "start_date": "2023-01-15",
            "end_date": "2023-06-15",
            "details": "Intensive 6-month program covering MERN stack development."
        }
    ])))

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
                {"skill": "Python", "source": "code", "date": "2024-01-15"},
                {"skill": "Flask", "source": "code", "date": "2024-02-01"},
                {"skill": "Backend Development", "source": "code", "date": "2024-02-15"},
                {"skill": "RESTful API Design", "source": "code", "date": "2024-03-01"},
                {"skill": "Team Collaboration", "source": "non-code", "date": "2024-01-20"},
                {"skill": "Git", "source": "code", "date": "2024-01-15"},
                {"skill": "Agile Methodologies", "source": "non-code", "date": "2024-01-25"},
            ]
        elif proj["name"] == "Beta Project":
            skills = [
                {"skill": "Machine Learning", "source": "code", "date": "2024-03-10"},
                {"skill": "Data Preprocessing", "source": "code", "date": "2024-03-15"},
                {"skill": "Feature Engineering", "source": "code", "date": "2024-04-01"},
                {"skill": "Scikit-learn", "source": "code", "date": "2024-04-10"},
                {"skill": "TensorFlow", "source": "code", "date": "2024-05-01"},
                {"skill": "Pandas", "source": "code", "date": "2024-03-20"},
                {"skill": "Algorithm Optimization", "source": "code", "date": "2024-06-01"},
            ]
        elif proj["name"] == "Gamma Project":
            skills = [
                {"skill": "React Native", "source": "code", "date": "2024-06-05"},
                {"skill": "Mobile Development", "source": "code", "date": "2024-06-10"},
                {"skill": "Fitness Tracking", "source": "non-code", "date": "2024-06-15"},
                {"skill": "Real-time Monitoring", "source": "code", "date": "2024-07-01"},
                {"skill": "Goal Setting", "source": "non-code", "date": "2024-07-10"},
                {"skill": "Social Sharing", "source": "non-code", "date": "2024-08-01"},
                {"skill": "Sphinx", "source": "code", "date": "2024-08-15"},
                {"skill": "CI/CD Integration", "source": "code", "date": "2024-09-01"}
            ]
        for s in skills:
            cursor.execute("""
                INSERT OR IGNORE INTO SKILL_ANALYSIS (project_id, skill, source, date)
                VALUES (?, ?, ?, ?)
            """, (project_id, s["skill"], s["source"], s.get("date", "")))

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
    
    # --- RESUME_SKILLS ---
    cursor.execute("""
    INSERT OR IGNORE INTO RESUME_SKILLS (resume_id, skills)
    VALUES (?, ?)
    """, (
        1,  # resume_id (should match an existing RESUME)
        "Python,Flask,Backend, Java,Team Collaboration,Git,Agile Methodologies"
    ))

    # --- RESUME_AWARDS ---
    awards_data = [
        {
            "title": "Hackathon Winner",
            "issuer": "Tech Challenge Inc.",
            "date": "2024-03",
            "details": ["Won first place in 24-hour coding competition", "Led team of 3 developers"],
        }
    ]
    cursor.execute("""
        INSERT OR REPLACE INTO RESUME_AWARDS (resume_id, awards)
        VALUES (?, ?)
    """, (1, json.dumps(awards_data)))

    # --- RESUME_WORK_EXPERIENCE ---
    work_exp_data = [
        {
            "role": "Software Engineer",
            "company": "Tech Corp",
            "start_date": "2023-06",
            "end_date": "2024-12",
            "details": ["Developed backend services", "Collaborated with cross-functional teams"],
        }
    ]
    cursor.execute("""
        INSERT OR REPLACE INTO RESUME_WORK_EXPERIENCE (resume_id, work_experience)
        VALUES (?, ?)
    """, (1, json.dumps(work_exp_data)))

    # --- COVER_LETTER ---
    cursor.execute("""
        INSERT OR IGNORE INTO COVER_LETTER (resume_id, job_title, company, job_description, motivations, content, generation_mode)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        1,
        "Software Engineer",
        "Acme Corp",
        "We are looking for a software engineer with Python and Flask experience.",
        json.dumps(["problem_solving", "growth"]),
        "Dear Acme Corp Hiring Team,\n\nI am excited to apply for the Software Engineer position.\n\nSincerely,\nJohn User",
        "local"
    ))

    conn.commit()
    conn.close()

    print("Seed data inserted successfully")
