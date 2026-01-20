import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.data.db import get_connection, init_db

client = TestClient(app)


@pytest.fixture(scope="function")
def setup_test_db():
    """Setup test database with sample data."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    # Insert test projects
    cursor.execute("""
        INSERT OR REPLACE INTO PROJECT (project_signature, name, path, rank, last_modified)
        VALUES 
            ('proj1', 'Test Project 1', '/path/to/proj1', 1, '2026-01-15 10:00:00'),
            ('proj2', 'Test Project 2', '/path/to/proj2', 2, '2026-01-18 14:00:00')
    """)
    
    # Insert test skills
    cursor.execute("""
        INSERT INTO SKILL_ANALYSIS (project_id, skill, source)
        VALUES 
            ('proj1', 'Python', 'technical'),
            ('proj1', 'FastAPI', 'technical'),
            ('proj1', 'Communication', 'soft'),
            ('proj2', 'Python', 'technical'),
            ('proj2', 'JavaScript', 'technical'),
            ('proj2', 'Leadership', 'soft')
    """)
    
    conn.commit()
    conn.close()
    
    yield
    
    # Cleanup
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM SKILL_ANALYSIS")
    cursor.execute("DELETE FROM PROJECT WHERE project_signature IN ('proj1', 'proj2')")
    conn.commit()
    conn.close()


def test_get_skills_returns_list(setup_test_db):
    """Test that GET /api/skills returns a list."""
    response = client.get("/api/skills")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_skills_structure(setup_test_db):
    """Test that each skill has the correct structure."""
    response = client.get("/api/skills")
    assert response.status_code == 200
    
    skills = response.json()
    assert len(skills) > 0
    
    for skill in skills:
        assert "skill" in skill
        assert "frequency" in skill
        assert "source" in skill
        assert isinstance(skill["skill"], str)
        assert isinstance(skill["frequency"], int)
        assert skill["source"] in ["technical", "soft"]


def test_get_skills_frequency(setup_test_db):
    """Test that skills are returned with correct frequency count."""
    response = client.get("/api/skills")
    assert response.status_code == 200
    
    skills = response.json()
    
    # Python appears in both projects
    python_skill = next((s for s in skills if s["skill"] == "Python"), None)
    assert python_skill is not None
    assert python_skill["frequency"] == 2
    
    # FastAPI appears in only one project
    fastapi_skill = next((s for s in skills if s["skill"] == "FastAPI"), None)
    assert fastapi_skill is not None
    assert fastapi_skill["frequency"] == 1


def test_get_skills_sorted_by_frequency(setup_test_db):
    """Test that skills are sorted by frequency (descending)."""
    response = client.get("/api/skills")
    assert response.status_code == 200
    
    skills = response.json()
    frequencies = [skill["frequency"] for skill in skills]
    
    # Check that frequencies are in descending order
    assert frequencies == sorted(frequencies, reverse=True)


def test_get_skills_includes_technical_and_soft(setup_test_db):
    """Test that both technical and soft skills are returned."""
    response = client.get("/api/skills")
    assert response.status_code == 200
    
    skills = response.json()
    sources = [skill["source"] for skill in skills]
    
    assert "technical" in sources
    assert "soft" in sources


def test_get_skills_empty_database():
    """Test GET /api/skills with no skills in database."""
    # Clear all skills
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM SKILL_ANALYSIS")
    conn.commit()
    conn.close()
    
    response = client.get("/api/skills")
    assert response.status_code == 200
    assert response.json() == []
    

def test_get_skills_unique_by_source(setup_test_db):
    """Test that same skill from different sources is listed separately."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Add the same skill with different source
    cursor.execute("""
        INSERT INTO SKILL_ANALYSIS (project_id, skill, source)
        VALUES ('proj1', 'Python', 'soft')
    """)
    conn.commit()
    conn.close()
    
    response = client.get("/api/skills")
    assert response.status_code == 200
    
    skills = response.json()
    python_skills = [s for s in skills if s["skill"] == "Python"]
    
    # Should have two entries: one technical, one soft
    assert len(python_skills) == 2
    sources = [s["source"] for s in python_skills]
    assert "technical" in sources
    assert "soft" in sources
