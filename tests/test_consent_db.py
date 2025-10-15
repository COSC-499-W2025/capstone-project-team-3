"""
Tests for consent management database operations.
"""
import pytest
import sqlite3
import tempfile
import os
from pathlib import Path
from app.data import db


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    # Create a temporary directory and database
    temp_dir = tempfile.mkdtemp()
    temp_db_path = Path(temp_dir) / "test.sqlite3"
    
    # Override the database path for testing
    original_db_path = db.DB_PATH
    db.DB_PATH = temp_db_path
    
    # Initialize the database
    db.init_db()
    
    yield temp_db_path
    
    # Cleanup
    db.DB_PATH = original_db_path
    if temp_db_path.exists():
        os.remove(temp_db_path)
    os.rmdir(temp_dir)


def test_init_db_creates_tables(temp_db):
    """Test that init_db creates the required tables."""
    with sqlite3.connect(temp_db) as conn:
        cursor = conn.cursor()
        
        # Check USER table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='USER'")
        assert cursor.fetchone() is not None
        
        # Check CONSENT table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='CONSENT'")
        assert cursor.fetchone() is not None


def test_create_consent(temp_db):
    """Test creating a consent record."""
    consent_id = db.create_consent(user_id=1, policy_version="1.0.0", consent_given=True)
    assert consent_id > 0
    
    # Verify the record was created
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM CONSENT WHERE id = ?", (consent_id,))
        row = cursor.fetchone()
        assert row is not None
        assert row[1] == 1  # user_id
        assert row[2] == "1.0.0"  # policy_version
        assert row[3] == 1  # consent_given


def test_get_consent_status_existing(temp_db):
    """Test getting consent status for an existing user."""
    # Create a consent record
    db.create_consent(user_id=1, policy_version="1.0.0", consent_given=True)
    
    # Get the consent status
    status = db.get_consent_status(user_id=1)
    
    assert status is not None
    assert status["user_id"] == 1
    assert status["policy_version"] == "1.0.0"
    assert status["consent_given"] is True


def test_get_consent_status_nonexistent(temp_db):
    """Test getting consent status for a non-existent user."""
    status = db.get_consent_status(user_id=999)
    assert status is None


def test_get_consent_status_returns_latest(temp_db):
    """Test that get_consent_status returns the most recent record."""
    # Create multiple consent records for the same user
    db.create_consent(user_id=1, policy_version="1.0.0", consent_given=True)
    db.create_consent(user_id=1, policy_version="1.0.0", consent_given=False)
    db.create_consent(user_id=1, policy_version="2.0.0", consent_given=True)
    
    # Get the consent status
    status = db.get_consent_status(user_id=1)
    
    # Should return the latest record (policy 2.0.0)
    assert status["policy_version"] == "2.0.0"
    assert status["consent_given"] is True


def test_update_consent(temp_db):
    """Test updating consent (creates new record)."""
    # Create initial consent
    db.create_consent(user_id=1, policy_version="1.0.0", consent_given=True)
    
    # Update consent
    new_id = db.update_consent(user_id=1, policy_version="2.0.0", consent_given=False)
    
    assert new_id > 0
    
    # Verify latest status reflects the update
    status = db.get_consent_status(user_id=1)
    assert status["policy_version"] == "2.0.0"
    assert status["consent_given"] is False


def test_get_consent_history(temp_db):
    """Test getting consent history for a user."""
    # Create multiple consent records
    db.create_consent(user_id=1, policy_version="1.0.0", consent_given=True)
    db.create_consent(user_id=1, policy_version="1.0.0", consent_given=False)
    db.create_consent(user_id=1, policy_version="2.0.0", consent_given=True)
    
    # Get history
    history = db.get_consent_history(user_id=1)
    
    # Should have 3 records, most recent first
    assert len(history) == 3
    assert history[0]["policy_version"] == "2.0.0"
    assert history[1]["policy_version"] == "1.0.0"
    assert history[2]["policy_version"] == "1.0.0"


def test_consent_given_boolean_conversion(temp_db):
    """Test that consent_given is properly converted to boolean."""
    # Create with False
    db.create_consent(user_id=1, policy_version="1.0.0", consent_given=False)
    status = db.get_consent_status(user_id=1)
    assert status["consent_given"] is False
    
    # Create with True
    db.create_consent(user_id=2, policy_version="1.0.0", consent_given=True)
    status = db.get_consent_status(user_id=2)
    assert status["consent_given"] is True
