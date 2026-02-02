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
        INSERT OR REPLACE INTO PROJECT (project_signature, name, path, score, last_modified)
        VALUES 
            ('proj1', 'Test Project 1', '/path/to/proj1', 0.9, '2026-01-15 10:00:00'),
            ('proj2', 'Test Project 2', '/path/to/proj2', 0.8, '2026-01-18 14:00:00')
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


def test_get_skills_sorted_alphabetically(setup_test_db):
    """Test that skills are sorted alphabetically."""
    response = client.get("/api/skills")
    assert response.status_code == 200
    
    skills = response.json()
    skill_names = [skill["skill"] for skill in skills]
    
    # Check that skill names are in alphabetical order
    assert skill_names == sorted(skill_names)


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


def test_get_frequent_skills_returns_list(setup_test_db):
    """Test that GET /api/skills/frequent returns a list."""
    response = client.get("/api/skills/frequent")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_frequent_skills_default_limit(setup_test_db):
    """Test that frequent skills respects default limit."""
    response = client.get("/api/skills/frequent")
    assert response.status_code == 200
    
    skills = response.json()
    # Should return at most 10 skills (default limit)
    assert len(skills) <= 10


def test_get_frequent_skills_custom_limit(setup_test_db):
    """Test that frequent skills respects custom limit."""
    response = client.get("/api/skills/frequent?limit=3")
    assert response.status_code == 200
    
    skills = response.json()
    # Should return exactly 3 skills
    assert len(skills) == 3


def test_get_frequent_skills_sorted_by_frequency(setup_test_db):
    """Test that frequent skills are sorted by frequency (descending)."""
    response = client.get("/api/skills/frequent")
    assert response.status_code == 200
    
    skills = response.json()
    frequencies = [skill["frequency"] for skill in skills]
    
    # Check that frequencies are in descending order
    assert frequencies == sorted(frequencies, reverse=True)


def test_get_frequent_skills_most_common_first(setup_test_db):
    """Test that most frequently used skill appears first."""
    response = client.get("/api/skills/frequent")
    assert response.status_code == 200
    
    skills = response.json()
    
    # Python appears in both projects, so should be first (or tied for first)
    python_skill = next((s for s in skills if s["skill"] == "Python"), None)
    assert python_skill is not None
    assert python_skill["frequency"] == 2
    
    # First skill should have frequency >= Python's frequency
    assert skills[0]["frequency"] >= python_skill["frequency"]


def test_get_frequent_skills_limit_validation(setup_test_db):
    """Test that limit parameter is validated."""
    # Test limit too high (should still work, just capped)
    response = client.get("/api/skills/frequent?limit=100")
    assert response.status_code == 422  # Validation error
    
    # Test limit too low
    response = client.get("/api/skills/frequent?limit=0")
    assert response.status_code == 422  # Validation error


def test_get_chronological_skills_returns_list(setup_test_db):
    """Test that GET /api/skills/chronological returns a list."""
    response = client.get("/api/skills/chronological")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_chronological_skills_structure(setup_test_db):
    """Test that each skill has the correct structure with latest_use."""
    response = client.get("/api/skills/chronological")
    assert response.status_code == 200
    
    skills = response.json()
    assert len(skills) > 0
    
    for skill in skills:
        assert "skill" in skill
        assert "latest_use" in skill
        assert "source" in skill
        assert "frequency" in skill
        assert isinstance(skill["skill"], str)
        assert isinstance(skill["latest_use"], str)
        assert skill["source"] in ["technical", "soft"]
        assert isinstance(skill["frequency"], int)


def test_get_chronological_skills_sorted_by_date(setup_test_db):
    """Test that skills are sorted by most recent usage."""
    response = client.get("/api/skills/chronological")
    assert response.status_code == 200
    
    skills = response.json()
    dates = [skill["latest_use"] for skill in skills]
    
    # Check that dates are in descending order (most recent first)
    assert dates == sorted(dates, reverse=True)


def test_get_chronological_skills_most_recent_first(setup_test_db):
    """Test that skills from most recent project appear first."""
    response = client.get("/api/skills/chronological")
    assert response.status_code == 200
    
    skills = response.json()
    
    # proj2 has last_modified='2026-01-18 14:00:00' (most recent)
    # Skills from proj2: Python, JavaScript, Leadership
    most_recent_skills = [s["skill"] for s in skills[:3]]
    
    # JavaScript and Leadership are only in proj2, so they should appear in top results
    assert "JavaScript" in most_recent_skills or "Leadership" in most_recent_skills


def test_get_chronological_skills_default_limit(setup_test_db):
    """Test that chronological skills respects default limit."""
    response = client.get("/api/skills/chronological")
    assert response.status_code == 200
    
    skills = response.json()
    # Should return at most 10 skills (default limit)
    assert len(skills) <= 10

def test_get_chronological_skills_empty_database():
    """Test GET /api/skills/chronological with no skills in database."""
    # Clear all skills
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM SKILL_ANALYSIS")
    conn.commit()
    conn.close()
    
    response = client.get("/api/skills/chronological")
    assert response.status_code == 200
    assert response.json() == []
