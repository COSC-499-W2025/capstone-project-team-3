"""
Tests for consent service layer.
"""
import pytest
import tempfile
import os
from pathlib import Path
from app.data import db
from app.consent_service import (
    record_consent,
    check_consent,
    revoke_consent,
    get_user_consent_history,
    get_privacy_policy,
    requires_reconsent,
    CURRENT_POLICY_VERSION
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
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


def test_record_consent_accept(temp_db):
    """Test recording acceptance of consent."""
    response = record_consent(user_id=1, consent_given=True)
    
    assert response.user_id == 1
    assert response.consent_given is True
    assert response.has_consent is True
    assert response.policy_version == CURRENT_POLICY_VERSION


def test_record_consent_decline(temp_db):
    """Test recording decline of consent."""
    response = record_consent(user_id=1, consent_given=False)
    
    assert response.user_id == 1
    assert response.consent_given is False
    assert response.has_consent is False


def test_check_consent_existing(temp_db):
    """Test checking consent for existing user."""
    # First record consent
    record_consent(user_id=1, consent_given=True)
    
    # Then check it
    consent = check_consent(user_id=1)
    
    assert consent is not None
    assert consent.user_id == 1
    assert consent.has_consent is True


def test_check_consent_nonexistent(temp_db):
    """Test checking consent for non-existent user."""
    consent = check_consent(user_id=999)
    assert consent is None


def test_revoke_consent(temp_db):
    """Test revoking consent."""
    # First accept consent
    record_consent(user_id=1, consent_given=True)
    
    # Then revoke it
    response = revoke_consent(user_id=1)
    
    assert response.user_id == 1
    assert response.consent_given is False
    assert response.has_consent is False


def test_get_user_consent_history(temp_db):
    """Test getting user consent history."""
    # Record multiple consent actions
    record_consent(user_id=1, consent_given=True)
    record_consent(user_id=1, consent_given=False)
    record_consent(user_id=1, consent_given=True)
    
    # Get history
    history = get_user_consent_history(user_id=1)
    
    assert len(history) == 3
    assert history[0].consent_given is True  # Most recent
    assert history[1].consent_given is False
    assert history[2].consent_given is True


def test_get_privacy_policy(temp_db):
    """Test getting privacy policy."""
    policy = get_privacy_policy()
    
    assert policy["version"] == CURRENT_POLICY_VERSION
    assert "title" in policy
    assert "content" in policy
    assert "last_updated" in policy
    assert len(policy["content"]) > 0


def test_requires_reconsent_no_consent(temp_db):
    """Test requires_reconsent when user has no consent."""
    assert requires_reconsent(user_id=1) is True


def test_requires_reconsent_current_version_accepted(temp_db):
    """Test requires_reconsent when user accepted current version."""
    record_consent(user_id=1, consent_given=True, policy_version=CURRENT_POLICY_VERSION)
    assert requires_reconsent(user_id=1) is False


def test_requires_reconsent_old_version(temp_db):
    """Test requires_reconsent when user has old policy version."""
    record_consent(user_id=1, consent_given=True, policy_version="0.9.0")
    assert requires_reconsent(user_id=1) is True


def test_requires_reconsent_declined(temp_db):
    """Test requires_reconsent when user declined consent."""
    record_consent(user_id=1, consent_given=False, policy_version=CURRENT_POLICY_VERSION)
    # Should return True because they declined and still need consent
    assert requires_reconsent(user_id=1) is True


def test_record_consent_with_custom_version(temp_db):
    """Test recording consent with a custom policy version."""
    response = record_consent(user_id=1, consent_given=True, policy_version="2.0.0")
    
    assert response.policy_version == "2.0.0"


def test_consent_history_maintains_order(temp_db):
    """Test that consent history maintains chronological order."""
    # Record consents with some delay to ensure different timestamps
    record_consent(user_id=1, consent_given=True, policy_version="1.0.0")
    record_consent(user_id=1, consent_given=False, policy_version="1.0.0")
    record_consent(user_id=1, consent_given=True, policy_version="2.0.0")
    
    history = get_user_consent_history(user_id=1)
    
    # Should be in descending order (most recent first)
    assert len(history) == 3
    assert history[0].policy_version == "2.0.0"
