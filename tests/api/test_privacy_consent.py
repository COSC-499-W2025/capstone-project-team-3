from fastapi.testclient import TestClient
from app.main import app
import pytest
import tempfile
import sqlite3
from pathlib import Path

client = TestClient(app)

@pytest.fixture
def test_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = Path(tmp.name)
        
        # Initialize test database with schema
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
        
        # Override DB_PATH in the router
        from app.api.routes import privacy_consent
        original_db_path = privacy_consent.DB_PATH
        privacy_consent.DB_PATH = db_path
        
        yield db_path
        
        # Restore original DB_PATH and cleanup
        privacy_consent.DB_PATH = original_db_path
        db_path.unlink(missing_ok=True)

def test_submit_consent_accept(test_db):
    """Test accepting consent."""
    response = client.post("/api/privacy-consent", json={"accepted": True})
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_submit_consent_decline(test_db):
    """Test declining consent."""
    response = client.post("/api/privacy-consent", json={"accepted": False})
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_get_consent_status(test_db):
    """Test checking consent status."""
    response = client.get("/api/privacy-consent")
    assert response.status_code == 200
    assert "has_consent" in response.json()
    assert "timestamp" in response.json()

def test_revoke_consent(test_db):
    """Test revoking consent."""
    # First give consent
    client.post("/api/privacy-consent", json={"accepted": True})
    # Then revoke it
    response = client.delete("/api/privacy-consent")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_error_handling(test_db):
    """Test that errors return proper HTTP status codes."""
    # Simulate error by using invalid DB path
    from app.api.routes import privacy_consent
    original_db_path = privacy_consent.DB_PATH
    privacy_consent.DB_PATH = Path("/invalid/path/db.sqlite3")
    
    response = client.post("/api/privacy-consent", json={"accepted": True})
    assert response.status_code == 500
    
    # Restore
    privacy_consent.DB_PATH = original_db_path
