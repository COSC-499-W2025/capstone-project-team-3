from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_submit_consent_accept():
    """Test accepting consent."""
    response = client.post("/api/privacy-consent", json={"accepted": True})
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_submit_consent_decline():
    """Test declining consent."""
    response = client.post("/api/privacy-consent", json={"accepted": False})
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_get_consent_status():
    """Test checking consent status."""
    response = client.get("/api/privacy-consent")
    assert response.status_code == 200
    assert "has_consent" in response.json()
    assert "timestamp" in response.json()

def test_revoke_consent():
    """Test revoking consent."""
    # First give consent
    client.post("/api/privacy-consent", json={"accepted": True})
    # Then revoke it
    response = client.delete("/api/privacy-consent")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
