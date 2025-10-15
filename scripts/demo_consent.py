#!/usr/bin/env python3
"""
Demonstration script for the Consent Management System.

This script demonstrates the key features of the consent management system
including creating consents, checking status, and viewing history.
"""

import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.consent_service import (
    initialize_database,
    record_consent,
    check_consent,
    revoke_consent,
    get_user_consent_history,
    get_privacy_policy,
    requires_reconsent,
    CURRENT_POLICY_VERSION
)
from app.data.db import DB_PATH


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def demonstrate_consent_flow():
    """Demonstrate the complete consent management flow."""
    
    print_section("Consent Management System Demonstration")
    
    # Initialize database
    print("\n1. Initializing database...")
    initialize_database()
    print(f"   Database created at: {DB_PATH}")
    
    # Get privacy policy
    print_section("Privacy Policy")
    policy = get_privacy_policy()
    print(f"\n   Version: {policy['version']}")
    print(f"   Title: {policy['title']}")
    print(f"   Last Updated: {policy['last_updated']}")
    print(f"\n   Content preview:")
    print("   " + policy['content'][:200] + "...")
    
    # Check if user needs consent
    print_section("Checking Initial Consent Status")
    user_id = 1
    needs_consent = requires_reconsent(user_id)
    print(f"\n   User {user_id} requires consent: {needs_consent}")
    
    # Accept consent
    print_section("Accepting Consent")
    consent = record_consent(user_id, consent_given=True)
    print(f"\n   ✓ Consent accepted for user {user_id}")
    print(f"   - Policy version: {consent.policy_version}")
    print(f"   - Timestamp: {consent.timestamp}")
    print(f"   - Has consent: {consent.has_consent}")
    
    # Check consent status
    print_section("Checking Current Consent Status")
    status = check_consent(user_id)
    print(f"\n   User {user_id} consent status:")
    print(f"   - Consent given: {status.consent_given}")
    print(f"   - Has consent: {status.has_consent}")
    print(f"   - Version: {status.policy_version}")
    
    # Update consent (simulate policy change)
    print_section("Simulating Policy Update")
    print(f"\n   User previously consented to version {CURRENT_POLICY_VERSION}")
    print("   Updating to new version 2.0.0...")
    consent = record_consent(user_id, consent_given=True, policy_version="2.0.0")
    print(f"   ✓ Consent updated to version {consent.policy_version}")
    
    # Revoke consent
    print_section("Revoking Consent")
    revoked = revoke_consent(user_id)
    print(f"\n   ✗ Consent revoked for user {user_id}")
    print(f"   - Consent given: {revoked.consent_given}")
    print(f"   - Has consent: {revoked.has_consent}")
    
    # Re-accept consent
    print_section("Re-accepting Consent")
    consent = record_consent(user_id, consent_given=True)
    print(f"\n   ✓ Consent re-accepted for user {user_id}")
    
    # View consent history
    print_section("Viewing Consent History")
    history = get_user_consent_history(user_id)
    print(f"\n   User {user_id} has {len(history)} consent records:")
    for i, record in enumerate(history, 1):
        status_icon = "✓" if record.consent_given else "✗"
        print(f"\n   {i}. {status_icon} Version {record.policy_version}")
        print(f"      Consent given: {record.consent_given}")
        print(f"      Timestamp: {record.timestamp}")
    
    # Test multiple users
    print_section("Testing Multiple Users")
    user2_id = 2
    print(f"\n   Creating consent for user {user2_id}...")
    record_consent(user2_id, consent_given=False)
    
    print(f"\n   User {user_id} status:")
    status1 = check_consent(user_id)
    print(f"   - Has consent: {status1.has_consent}")
    
    print(f"\n   User {user2_id} status:")
    status2 = check_consent(user2_id)
    print(f"   - Has consent: {status2.has_consent}")
    
    print_section("Demonstration Complete")
    print("\n✓ All consent management features demonstrated successfully!")
    print(f"\nDatabase location: {DB_PATH}")
    print("\nYou can inspect the database using:")
    print(f"  sqlite3 {DB_PATH}")
    print("\nOr explore the API at:")
    print("  http://localhost:8000/docs")
    print()


if __name__ == "__main__":
    try:
        demonstrate_consent_flow()
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
