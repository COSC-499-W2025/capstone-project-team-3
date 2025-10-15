"""
Tests for consent API endpoints.
"""
import pytest
import tempfile
import os
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.data import db
from app.consent_service import CURRENT_POLICY_VERSION

client = TestClient(app)


@pytest.fixture(autouse=True)
def temp_db():
    """Create a temporary database for each test."""
    temp_dir = tempfile.mkdtemp()
    temp_db_path = Path(temp_dir) / "test.sqlite3"
    
    original_db_path = db.DB_PATH
    db.DB_PATH = temp_db_path
    
    db.init_db()
    
    yield temp_db_path
    
    db.DB_PATH = original_db_path
    if temp_db_path.exists():
        os.remove(temp_db_path)
    os.rmdir(temp_dir)


def test_accept_consent():
    """Test accepting consent via API."""
    response = client.post(
        "/consent/accept",
        json={"user_id": 1, "consent_given": True, "policy_version": "1.0.0"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 1
    assert data["consent_given"] is True
    assert data["has_consent"] is True


def test_accept_consent_with_false_flag_fails():
    """Test that accept endpoint rejects consent_given=False."""
    response = client.post(
        "/consent/accept",
        json={"user_id": 1, "consent_given": False, "policy_version": "1.0.0"}
    )
    
    assert response.status_code == 400


def test_decline_consent():
    """Test declining consent via API."""
    response = client.post(
        "/consent/decline",
        json={"user_id": 1, "consent_given": False, "policy_version": "1.0.0"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 1
    assert data["consent_given"] is False
    assert data["has_consent"] is False


def test_decline_consent_with_true_flag_fails():
    """Test that decline endpoint rejects consent_given=True."""
    response = client.post(
        "/consent/decline",
        json={"user_id": 1, "consent_given": True, "policy_version": "1.0.0"}
    )
    
    assert response.status_code == 400


def test_get_consent_status_existing():
    """Test getting consent status for existing user."""
    # First accept consent
    client.post(
        "/consent/accept",
        json={"user_id": 1, "consent_given": True, "policy_version": "1.0.0"}
    )
    
    # Then get status
    response = client.get("/consent/status/1")
    
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 1
    assert data["has_consent"] is True


def test_get_consent_status_nonexistent():
    """Test getting consent status for non-existent user."""
    response = client.get("/consent/status/999")
    assert response.status_code == 404


def test_revoke_consent():
    """Test revoking consent via API."""
    # First accept consent
    client.post(
        "/consent/accept",
        json={"user_id": 1, "consent_given": True, "policy_version": "1.0.0"}
    )
    
    # Then revoke it
    response = client.post("/consent/revoke/1")
    
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 1
    assert data["consent_given"] is False


def test_get_consent_history():
    """Test getting consent history via API."""
    # Record multiple consent actions
    client.post(
        "/consent/accept",
        json={"user_id": 1, "consent_given": True, "policy_version": "1.0.0"}
    )
    client.post(
        "/consent/decline",
        json={"user_id": 1, "consent_given": False, "policy_version": "1.0.0"}
    )
    client.post(
        "/consent/accept",
        json={"user_id": 1, "consent_given": True, "policy_version": "2.0.0"}
    )
    
    # Get history
    response = client.get("/consent/history/1")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["policy_version"] == "2.0.0"  # Most recent


def test_get_privacy_policy():
    """Test getting privacy policy via API."""
    response = client.get("/consent/privacy-policy")
    
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "title" in data
    assert "content" in data
    assert "last_updated" in data
    assert len(data["content"]) > 0


def test_check_requires_consent_new_user():
    """Test requires consent check for new user."""
    response = client.get("/consent/requires-consent/1")
    
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 1
    assert data["requires_consent"] is True


def test_check_requires_consent_consented_user():
    """Test requires consent check for user with consent."""
    # Accept consent first
    client.post(
        "/consent/accept",
        json={"user_id": 1, "consent_given": True, "policy_version": CURRENT_POLICY_VERSION}
    )
    
    # Check if consent required
    response = client.get("/consent/requires-consent/1")
    
    assert response.status_code == 200
    data = response.json()
    assert data["requires_consent"] is False


def test_check_requires_consent_old_policy():
    """Test requires consent check for user with old policy version."""
    # Accept old policy version
    client.post(
        "/consent/accept",
        json={"user_id": 1, "consent_given": True, "policy_version": "0.9.0"}
    )
    
    # Check if consent required
    response = client.get("/consent/requires-consent/1")
    
    assert response.status_code == 200
    data = response.json()
    assert data["requires_consent"] is True


def test_consent_flow_complete():
    """Test complete consent flow: accept -> check -> revoke -> check."""
    # Accept consent
    response = client.post(
        "/consent/accept",
        json={"user_id": 1, "consent_given": True, "policy_version": "1.0.0"}
    )
    assert response.status_code == 200
    
    # Check status (should be accepted)
    response = client.get("/consent/status/1")
    assert response.json()["has_consent"] is True
    
    # Revoke consent
    response = client.post("/consent/revoke/1")
    assert response.status_code == 200
    
    # Check status again (should be declined)
    response = client.get("/consent/status/1")
    assert response.json()["has_consent"] is False
