"""
Tests for consent enforcement middleware.
"""
import pytest
import tempfile
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.data import db
from app.consent_middleware import ConsentMiddleware, is_exempt_path
from app.consent_service import record_consent


# Create a test app with middleware enabled
test_app = FastAPI()
test_app.add_middleware(ConsentMiddleware)


@test_app.get("/")
def root():
    return {"message": "Root"}


@test_app.get("/protected")
def protected():
    return {"message": "Protected resource"}


@test_app.get("/consent/status")
def consent_status():
    return {"message": "Consent status"}


client = TestClient(test_app)


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


def test_is_exempt_path():
    """Test path exemption logic."""
    assert is_exempt_path("/") is True
    assert is_exempt_path("/docs") is True
    assert is_exempt_path("/consent/status") is True
    assert is_exempt_path("/consent/accept") is True
    assert is_exempt_path("/protected") is False
    assert is_exempt_path("/api/data") is False


def test_root_path_exempt():
    """Test that root path is accessible without consent."""
    response = client.get("/")
    assert response.status_code == 200


def test_consent_path_exempt():
    """Test that consent paths are accessible without consent."""
    response = client.get("/consent/status")
    assert response.status_code == 200


def test_protected_path_no_user_id():
    """Test that protected path requires user ID."""
    response = client.get("/protected")
    assert response.status_code == 401
    assert "User ID required" in response.json()["detail"]


def test_protected_path_no_consent():
    """Test that protected path requires consent."""
    response = client.get("/protected", headers={"X-User-ID": "1"})
    assert response.status_code == 403
    assert "Consent required" in response.json()["detail"]


def test_protected_path_with_consent():
    """Test that protected path is accessible with consent."""
    # Record consent
    record_consent(user_id=1, consent_given=True)
    
    # Access protected path
    response = client.get("/protected", headers={"X-User-ID": "1"})
    assert response.status_code == 200
    assert response.json()["message"] == "Protected resource"


def test_protected_path_declined_consent():
    """Test that protected path is blocked when consent is declined."""
    # Record declined consent
    record_consent(user_id=1, consent_given=False)
    
    # Try to access protected path
    response = client.get("/protected", headers={"X-User-ID": "1"})
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]


def test_user_id_from_query_param():
    """Test that user ID can be provided via query parameter."""
    # Record consent
    record_consent(user_id=1, consent_given=True)
    
    # Access with user_id in query params
    response = client.get("/protected?user_id=1")
    assert response.status_code == 200


def test_invalid_user_id_format():
    """Test that invalid user ID format is rejected."""
    response = client.get("/protected", headers={"X-User-ID": "invalid"})
    assert response.status_code == 400
    assert "Invalid user ID format" in response.json()["detail"]


def test_multiple_users_isolated():
    """Test that consent is isolated per user."""
    # User 1 has consent
    record_consent(user_id=1, consent_given=True)
    
    # User 1 can access
    response = client.get("/protected", headers={"X-User-ID": "1"})
    assert response.status_code == 200
    
    # User 2 cannot access (no consent)
    response = client.get("/protected", headers={"X-User-ID": "2"})
    assert response.status_code == 403
