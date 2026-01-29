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
)

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
        CREATE TABLE USER_PREFERENCES (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            github_user TEXT,
            education TEXT,
            job_title TEXT,
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
    model_single = mod.build_resume_model(project_ids=["p1"])
    assert isinstance(model_single, dict)
    assert len(model_single["projects"]) == 1
    assert model_single["projects"][0]["title"] == "Alpha_Project"
    # Top-level skills should include all skills from p1
    assert set(model_single["skills"]["Skills"]) == {
        "Python", "Flask", "SQL", "Docker", "Git", "ExtraSkill"
    }

    # Multiple project selection
    model_multi = mod.build_resume_model(project_ids=["p1", "p2"])
    assert isinstance(model_multi, dict)
    # Ordered by score DESC → p1 then p2
    titles = [p["title"] for p in model_multi["projects"]]
    assert titles == ["Alpha_Project", "Beta Project"]
    # Union of skills from both projects
    assert set(model_multi["skills"]["Skills"]) == {
        "Python", "Flask", "SQL", "Docker", "Git", "ExtraSkill", "Machine Learning"
    }
