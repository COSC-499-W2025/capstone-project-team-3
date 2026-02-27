import sqlite3
import pytest
from collections import defaultdict
import app.utils.generate_resume as mod
from app.utils.generate_resume import (
    format_dates,
    limit_skills,
    load_user,
    load_projects,
    load_resume_bullets,
    load_skills,
    build_resume_model,
    load_resume_projects,
    load_edited_skills,
    load_saved_resume,
    save_resume_edits,
    load_resume_projects,
    resume_exists,
    create_resume,
    attach_projects_to_resume,
    remove_project_from_resume,
    list_resumes,
    ResumeServiceError,
    ResumeNotFoundError,
)
import json

import json

@pytest.fixture
def db_connection(monkeypatch):
    """
    Create an in-memory SQLite database matching the schema
    and patch get_connection() to return it.
    """
    # Use a shared in-memory database URI so each new connection sees the same DB
    uri = "file:test_resume_db?mode=memory&cache=shared"
    conn = sqlite3.connect(uri, uri=True)
    cursor = conn.cursor()

    # --- Schema ---
    cursor.executescript("""
        DROP TABLE IF EXISTS USER_PREFERENCES;
        DROP TABLE IF EXISTS PROJECT;
        DROP TABLE IF EXISTS RESUME_SUMMARY;
        DROP TABLE IF EXISTS SKILL_ANALYSIS;
        DROP TABLE IF EXISTS RESUME;
        DROP TABLE IF EXISTS RESUME_PROJECT;
        DROP TABLE IF EXISTS RESUME_SKILLS;

        CREATE TABLE USER_PREFERENCES (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            github_user TEXT,
            education TEXT,
            job_title TEXT,
            education_details JSON,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE PROJECT (
            project_signature TEXT PRIMARY KEY,
            name TEXT,
            score REAL,
            created_at TEXT,
            last_modified TEXT
        );

        CREATE TABLE RESUME_SUMMARY (
            project_id TEXT,
            summary_text TEXT
        );

        CREATE TABLE SKILL_ANALYSIS (
            project_id TEXT,
            skill TEXT
        );
        
        CREATE TABLE RESUME (
            id INTEGER PRIMARY KEY,
            name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE RESUME_PROJECT (
            resume_id INTEGER,
            project_id TEXT,
            project_name TEXT,
            start_date TEXT,
            end_date TEXT,
            skills TEXT,
            bullets TEXT,
            display_order INTEGER,
            UNIQUE (resume_id, project_id)
        );
        
        CREATE TABLE RESUME_SKILLS (
            resume_id INTEGER PRIMARY KEY,
            skills JSON,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # --- Seed Data ---
    cursor.execute("""
        INSERT INTO USER_PREFERENCES (user_id, name, email, github_user, education, job_title)
        VALUES (1, 'John Doe', 'john@example.com', 'johndoe', 'University X', 'Developer')
    """)

    cursor.execute("""
        INSERT INTO PROJECT
        VALUES ('p1', 'Alpha_Project', 0.9, '2024-01-01', '2024-06-01')
    """)
    cursor.execute("""
        INSERT INTO PROJECT
        VALUES ('p2', 'Beta Project', 0.8, '2023-01-01', '2023-12-01')
    """)

    cursor.executemany("""
        INSERT INTO RESUME_SUMMARY
        VALUES (?, ?)
    """, [
        ('p1', 'Built backend services'),
        ('p1', 'Designed REST APIs'),
        ('p2', 'Implemented ML pipeline'),
    ])

    cursor.executemany("""
        INSERT INTO SKILL_ANALYSIS
        VALUES (?, ?)
    """, [
        ('p1', 'Python'),
        ('p1', 'Flask'),
        ('p1', 'SQL'),
        ('p1', 'Docker'),
        ('p1', 'Git'),
        ('p1', 'ExtraSkill'), 
        ('p2', 'Python'),
        ('p2', 'Machine Learning'),
    ])
    
    cursor.execute("INSERT INTO RESUME (id) VALUES (1)")
    cursor.execute("""
        INSERT INTO RESUME_PROJECT
        VALUES (1, 'p1', 'Alpha_Project', '2024-01-01', '2024-06-01', ?, ?, 1)
    """, (
        json.dumps(["Python", "Flask", "SQL"]),  # skills as JSON array
        json.dumps(["Did stuff"]),               # bullets as JSON array
    ))
    cursor.execute("""
        INSERT INTO RESUME_SKILLS (resume_id, skills)
        VALUES (?, ?)
        """,
        (1, json.dumps(["Python","Flask","SQL","Machine Learning"]))
    )

    conn.commit()

    # Patch get_connection() to return a NEW connection to the same shared in-memory DB
    # This avoids 'Cannot operate on a closed database' when code closes its own connection.
    monkeypatch.setattr(mod, "get_connection", lambda: sqlite3.connect(uri, uri=True))

    yield conn
    conn.close()

def test_format_dates_valid():
    """Tests that format_dates converts valid ISO date strings into 'Mon YYYY – Mon YYYY' format."""
    assert format_dates("2024-01-01", "2024-06-01") == "Jan 2024 – Jun 2024"


def test_format_dates_invalid():
    """Tests that format_dates returns an empty string when given invalid date inputs."""
    assert format_dates("bad-date", "also-bad") == ""


def test_limit_skills_dedup_and_limit():
    """
    Tests that limit_skills removes duplicates while preserving order and enforces the maximum skill count.
    """
    skills = ["Python", "Flask", "Python", "SQL", "Docker", "Git"]
    result = limit_skills(skills, max_count=5)

    assert result == ["Python", "Flask", "SQL", "Docker", "Git"]
    assert len(result) == 5


def test_load_user(db_connection):
    """
    Tests that load_user returns the user's profile data and construct
    a GitHub link when a github_user is present.
    """
    cursor = db_connection.cursor()
    user = load_user(cursor)

    assert user["name"] == "John Doe"
    assert user["email"] == "john@example.com"
    assert user["education"] == "University X"
    assert user["job_title"] == "Developer"
    assert user["education_details"] is None  # No education_details in seed data
    assert user["links"][0]["url"] == "https://github.com/johndoe"


def test_load_projects_ordered_by_score(db_connection):
    """
    Tests that load_projects returns projects ordered by score in descending order.
    """
    cursor = db_connection.cursor()
    projects = load_projects(cursor)

    # score DESC → p1 first
    assert projects[0][0] == "p1"
    assert projects[1][0] == "p2"


def test_load_resume_bullets(db_connection):
    """Tests that load_resume_bullets group resume summary bullets by project_id.
    """
    cursor = db_connection.cursor()
    bullets = load_resume_bullets(cursor)

    assert bullets["p1"] == [
        "Built backend services",
        "Designed REST APIs",
    ]
    assert bullets["p2"] == ["Implemented ML pipeline"]


def test_load_skills(db_connection):
    """
    Tests that load_skills returns a mapping of project_id to all associated skills.
    """
    cursor = db_connection.cursor()
    skills = load_skills(cursor)

    assert "Python" in skills["p1"]
    assert "ExtraSkill" in skills["p1"]
    assert skills["p2"] == ["Python", "Machine Learning"]


def test_build_resume_model_filters_projects(db_connection):
    """Tests that build_resume_model filters projects by selected IDs and unions skills accordingly."""
    # Single project selection
    model_single = build_resume_model(project_ids=["p1"])
    assert isinstance(model_single, dict)
    assert len(model_single["projects"]) == 1
    assert model_single["projects"][0]["title"] == "Alpha_Project"
    # Top-level skills should include all skills from p1
    assert set(model_single["skills"]["Skills"]) == {
        "Python", "Flask", "SQL", "Docker", "Git", "ExtraSkill"
    }

    # Multiple project selection
    model_multi = build_resume_model(project_ids=["p1", "p2"])
    assert isinstance(model_multi, dict)
    # Ordered by score DESC → p1 then p2
    titles = [p["title"] for p in model_multi["projects"]]
    assert titles == ["Alpha_Project", "Beta Project"]
    # Union of skills from both projects
    assert set(model_multi["skills"]["Skills"]) == {
        "Python", "Flask", "SQL", "Docker", "Git", "ExtraSkill", "Machine Learning"
    }

def test_load_resume_projects(db_connection):
    """Test that load_resume_projects returns correct project data."""
    cursor = db_connection.cursor()
    rows = load_resume_projects(cursor, 1)
    assert len(rows) == 1
    assert rows[0][0] == 'p1'
    assert rows[0][1] == 'Alpha_Project'
    assert json.loads(rows[0][4]) == ["Python", "Flask", "SQL"]
    
def test_load_edited_skills(db_connection):
    """Test that load_edited_skills returns the edited skills string."""
    cursor = db_connection.cursor()
    row = load_edited_skills(cursor, 1)
    assert row is not None
    assert json.loads(row[0]) == ["Python","Flask","SQL","Machine Learning"]
    
def test_load_saved_resume(db_connection):
    """Test that load_saved_resume returns a complete resume model."""
    resume = load_saved_resume(1)
    assert resume["name"] == "John Doe"
    assert "Python" in resume["skills"]["Skills"]
    assert "Flask" in resume["skills"]["Skills"]
    assert "SQL" in resume["skills"]["Skills"]
    assert "Machine Learning" in resume["skills"]["Skills"]
    assert resume["projects"][0]["title"] == "Alpha_Project"
    assert "Python" in resume["projects"][0]["skills"]

def test_save_resume_edits_update(db_connection):
    """Test that save_resume_edits updates an existing RESUME_PROJECT row."""
    # First, insert initial data
    payload = {
        "projects": [
            {
                "project_id": "p1",
                "project_name": "Alpha_Project_Edited",
                "start_date": "2024-02-01",
                "end_date": "2024-07-01",
                "skills": ["Python", "Flask", "SQL", "FastAPI"],
                "bullets": ["Did stuff", "Added FastAPI"],
                "display_order": 1
            }
        ]
    }
    save_resume_edits(1, payload)
    # Now, update
    payload_update = {
        "projects": [
            {
                "project_id": "p1",
                "project_name": "Alpha_Project_Updated",
                "skills": ["Python", "Flask"],
                "display_order": 2
            }
        ]
    }
    save_resume_edits(1, payload_update)
    cursor = db_connection.cursor()
    rows = load_resume_projects(cursor, 1)
    assert len(rows) == 1
    assert rows[0][1] == "Alpha_Project_Updated"
    assert json.loads(rows[0][4]) == ["Python", "Flask"]
    assert rows[0][6] == 2

def test_save_resume_edits_update_resume_skills(db_connection):
    """Test that save_resume_edits updates RESUME_SKILLS and load_saved_resume reflects it."""
    # Update resume-level skills via payload
    payload_skills = {
        "skills": ["Python", "Flask", "GraphQL"]
    }
    save_resume_edits(1, payload_skills)

    # Verify RESUME_SKILLS row was updated to JSON payload
    cursor = db_connection.cursor()
    cursor.execute("SELECT skills FROM RESUME_SKILLS WHERE resume_id = ?", (1,))
    row = cursor.fetchone()
    assert row is not None
    assert json.loads(row[0]) == ["Python", "Flask", "GraphQL"]

    # Verify load_saved_resume picks up the edited resume-level skills
    resume = load_saved_resume(1)
    assert resume["skills"]["Skills"] == ["Python", "Flask", "GraphQL"]

def test_resume_exists_true_and_false(db_connection):
    """
    Tests that resume_exists returns True for an existing resume and False for a non-existent one.
    """
    # Existing resume (seeded as id=1)
    assert resume_exists(1) is True
    # Non-existent resume
    assert resume_exists(99999) is False

def test_create_resume_with_name(db_connection):
    """Test that create_resume accepts a valid name."""
    resume_id = create_resume("My Resume")
    assert resume_id > 0
    
    cursor = db_connection.cursor()
    cursor.execute("SELECT name FROM RESUME WHERE id = ?", (resume_id,))
    row = cursor.fetchone()
    assert row is not None
    assert row[0] == "My Resume"
    
def test_attach_projects_to_resume(db_connection):
    """
    Tests that attach_projects_to_resume attaches projects with display_order
    by last_modified DESC (newest first). Seed: p1 has 2024-06-01, p2 has 2023-12-01.
    """
    # Create a new resume
    cursor = db_connection.cursor()
    cursor.execute("INSERT INTO RESUME (id) VALUES (2)")
    db_connection.commit()

    # Attach two projects (input order p2, p1); stored order should be by date: p1 first, then p2
    attach_projects_to_resume(2, ["p2", "p1"])

    # Check RESUME_PROJECT table: order by last_modified DESC → p1 (newer), p2 (older)
    cursor = db_connection.cursor()
    cursor.execute("SELECT project_id, display_order FROM RESUME_PROJECT WHERE resume_id = ? ORDER BY display_order", (2,))
    rows = cursor.fetchall()

    assert len(rows) == 2
    assert rows[0][0] == "p1"
    assert rows[0][1] == 1
    assert rows[1][0] == "p2"
    assert rows[1][1] == 2


def test_remove_project_from_resume(db_connection):
    """
    Tests that remove_project_from_resume deletes the RESUME_PROJECT row for the given resume and project.
    Resume 1 has p1 attached in seed data.
    """
    cursor = db_connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM RESUME_PROJECT WHERE resume_id = 1 AND project_id = 'p1'")
    assert cursor.fetchone()[0] == 1

    remove_project_from_resume(1, "p1")

    cursor.execute("SELECT COUNT(*) FROM RESUME_PROJECT WHERE resume_id = 1 AND project_id = 'p1'")
    assert cursor.fetchone()[0] == 0
    # Project still exists in PROJECT table
    cursor.execute("SELECT 1 FROM PROJECT WHERE project_signature = 'p1'")
    assert cursor.fetchone() is not None


def test_remove_project_from_resume_idempotent(db_connection):
    """Removing a project that is not on the resume does not raise (idempotent)."""
    # Resume 1 has only p1; p2 is not attached
    remove_project_from_resume(1, "p2")
    # No exception; RESUME_PROJECT for resume 1 unchanged
    cursor = db_connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM RESUME_PROJECT WHERE resume_id = 1")
    assert cursor.fetchone()[0] == 1


def test_remove_project_from_resume_not_found(db_connection):
    """remove_project_from_resume raises ResumeNotFoundError when resume does not exist."""
    with pytest.raises(ResumeNotFoundError) as exc_info:
        remove_project_from_resume(99999, "p1")
    assert "99999" in str(exc_info.value)
    assert "not found" in str(exc_info.value).lower()


def test_list_resumes_returns_all_resumes(db_connection):
    """
    Tests that list_resumes returns all resumes ordered by id with correct structure.
    """
    # Seed has id=1, add more resumes
    cursor = db_connection.cursor()
    cursor.execute("INSERT INTO RESUME (id, name) VALUES (2, 'Software Engineer Resume')")
    cursor.execute("INSERT INTO RESUME (id, name) VALUES (3, 'Data Analyst Resume')")
    db_connection.commit()

    resumes = list_resumes()

    assert len(resumes) == 3
    assert resumes[0]["id"] == 1
    assert resumes[0]["is_master"] is True
    assert resumes[1]["id"] == 2
    assert resumes[1]["name"] == "Software Engineer Resume"
    assert resumes[1]["is_master"] is False
    assert resumes[2]["id"] == 3
    assert resumes[2]["name"] == "Data Analyst Resume"
    assert resumes[2]["is_master"] is False

def test_list_resumes_database_error(db_connection, monkeypatch):
    """
    Tests that list_resumes raises ResumeServiceError on database errors.
    """
    def mock_get_connection_error():
        # Return a connection that will raise an error
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()
        # Drop the table to cause an error
        cursor.execute("DROP TABLE IF EXISTS RESUME")
        conn.commit()
        return conn

    monkeypatch.setattr(mod, "get_connection", mock_get_connection_error)

    with pytest.raises(ResumeServiceError) as exc_info:
        list_resumes()

    assert "Failed listing resumes" in str(exc_info.value)