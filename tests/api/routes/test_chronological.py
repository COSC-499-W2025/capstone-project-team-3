"""
Tests for the chronological API endpoints (/api/chronological/...).
One happy-path + one error case per endpoint.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.data.db import get_connection, init_db

client = TestClient(app)

SIG1 = "chrono_proj1"
SIG_MISSING = "chrono_nonexistent"


@pytest.fixture(autouse=True)
def setup_test_db():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO PROJECT (project_signature, name, path, created_at, last_modified) "
        "VALUES (?, 'Chrono Project One', '/p/one', '2024-01-15', '2024-06-20')",
        (SIG1,),
    )
    cursor.execute("DELETE FROM SKILL_ANALYSIS WHERE project_id = ?", (SIG1,))
    cursor.execute(
        "INSERT INTO SKILL_ANALYSIS (project_id, skill, source, date) VALUES (?, 'Python', 'code', '2024-01-15'), (?, 'Flask', 'code', '2024-02-01')",
        (SIG1, SIG1),
    )
    conn.commit()
    conn.close()
    yield
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM SKILL_ANALYSIS WHERE project_id = ?", (SIG1,))
    cursor.execute("DELETE FROM PROJECT WHERE project_signature = ?", (SIG1,))
    conn.commit()
    conn.close()


def _skill_id(skill_name: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM SKILL_ANALYSIS WHERE skill = ? AND project_id = ?", (skill_name, SIG1))
    row = cursor.fetchone()
    conn.close()
    return row[0]


# GET /api/chronological/projects
def test_list_projects():
    r = client.get("/api/chronological/projects")
    assert r.status_code == 200
    assert any(p["project_signature"] == SIG1 for p in r.json())


# GET /api/chronological/projects/{signature}
def test_get_project_found():
    r = client.get(f"/api/chronological/projects/{SIG1}")
    assert r.status_code == 200
    assert r.json()["project_signature"] == SIG1

def test_get_project_not_found():
    assert client.get(f"/api/chronological/projects/{SIG_MISSING}").status_code == 404


# PATCH /api/chronological/projects/{signature}/dates
def test_update_project_dates():
    r = client.patch(f"/api/chronological/projects/{SIG1}/dates",
                     json={"created_at": "2023-03-01", "last_modified": "2024-07-15"})
    assert r.status_code == 200
    assert r.json()["created_at"] == "2023-03-01"

def test_update_project_dates_not_found():
    assert client.patch(f"/api/chronological/projects/{SIG_MISSING}/dates",
                        json={"created_at": "2023-01-01", "last_modified": "2023-12-31"}).status_code == 404


# GET /api/chronological/projects/{signature}/skills
def test_get_project_skills():
    r = client.get(f"/api/chronological/projects/{SIG1}/skills")
    assert r.status_code == 200
    dates = [s["date"] for s in r.json()]
    assert dates == sorted(dates)

def test_get_project_skills_not_found():
    assert client.get(f"/api/chronological/projects/{SIG_MISSING}/skills").status_code == 404


# POST /api/chronological/projects/{signature}/skills
def test_add_skill():
    r = client.post(f"/api/chronological/projects/{SIG1}/skills",
                    json={"skill": "Docker", "source": "code", "date": "2024-04-01"})
    assert r.status_code == 201
    assert r.json()["skill"] == "Docker"

def test_add_skill_invalid():
    assert client.post(f"/api/chronological/projects/{SIG1}/skills",
                       json={"skill": "", "source": "code", "date": "2024-01-01"}).status_code == 400


# PATCH /api/chronological/skills/{skill_id}/date
def test_update_skill_date():
    r = client.patch(f"/api/chronological/skills/{_skill_id('Python')}/date", json={"date": "2024-01-30"})
    assert r.status_code == 200
    assert r.json()["date"] == "2024-01-30"

def test_update_skill_date_not_found():
    assert client.patch("/api/chronological/skills/999999/date", json={"date": "2024-01-01"}).status_code == 404


# PATCH /api/chronological/skills/{skill_id}/name
def test_update_skill_name():
    r = client.patch(f"/api/chronological/skills/{_skill_id('Flask')}/name", json={"skill": "Flask-RESTful"})
    assert r.status_code == 200
    assert r.json()["skill"] == "Flask-RESTful"

def test_update_skill_name_empty():
    assert client.patch(f"/api/chronological/skills/{_skill_id('Python')}/name", json={"skill": ""}).status_code == 400


# DELETE /api/chronological/skills/{skill_id}
def test_delete_skill():
    assert client.delete(f"/api/chronological/skills/{_skill_id('Flask')}").status_code == 204

def test_delete_skill_not_found():
    assert client.delete("/api/chronological/skills/999999").status_code == 404
