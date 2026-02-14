from fastapi.testclient import TestClient
from app.main import app
import pytest
import sqlite3

client = TestClient(app)

@pytest.fixture
def setup_test_db(tmp_path, monkeypatch):
    """Create temporary test database and override DB_PATH."""
    db_path = tmp_path / "test_consent.sqlite3"
    
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
    
    monkeypatch.setattr("app.data.db.DB_PATH", str(db_path))
    
    # Clear any cached connections
    from app.data import db
    if hasattr(db, '_connection'):
        monkeypatch.delattr(db, '_connection', raising=False)
    
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

def test_get_consent_text():
    """Test retrieving consent text."""
    response = client.get("/api/privacy-consent/text")
    assert response.status_code == 200
    data = response.json()
    assert "consent_message" in data
    assert "detailed_info" in data
    assert "granted_message" in data
    assert "declined_message" in data
    assert "already_provided_message" in data
    assert len(data["consent_message"]) > 0
    assert len(data["detailed_info"]) > 0
    assert len(data["granted_message"]) > 0
    assert len(data["declined_message"]) > 0
    assert len(data["already_provided_message"]) > 0
