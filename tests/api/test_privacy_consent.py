from fastapi.testclient import TestClient
from app.main import app
import pytest
import sqlite3

client = TestClient(app)

@pytest.fixture
def setup_test_db(tmp_path, monkeypatch):
    """Create temporary test database and override DB_PATH."""
    db_path = tmp_path / "test_consent.sqlite3"
    
    # Create test database with schema
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS CONSENT (
            id INTEGER PRIMARY KEY,
            policy_version TEXT,
            consent_given INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    
    # Override DB_PATH
    monkeypatch.setattr("app.data.db.DB_PATH", db_path)
    
    yield db_path

def test_submit_consent_accept(setup_test_db):
    """Test accepting consent."""
    response = client.post("/api/privacy-consent", json={"accepted": True})
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_submit_consent_decline(setup_test_db):
    """Test declining consent."""
    response = client.post("/api/privacy-consent", json={"accepted": False})
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_get_consent_status(setup_test_db):
    """Test checking consent status."""
    response = client.get("/api/privacy-consent")
    assert response.status_code == 200
    assert "has_consent" in response.json()
    assert "timestamp" in response.json()

def test_revoke_consent(setup_test_db):
    """Test revoking consent."""
    # First give consent
    client.post("/api/privacy-consent", json={"accepted": True})
    # Then revoke it
    response = client.delete("/api/privacy-consent")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
