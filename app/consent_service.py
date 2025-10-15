"""
Consent management service layer.
"""
from app.data.db import (
    init_db, 
    create_consent, 
    get_consent_status, 
    update_consent,
    get_consent_history
)
from app.models import ConsentResponse, ConsentHistoryItem
from typing import Optional, List

# Current policy version
CURRENT_POLICY_VERSION = "1.0.0"

# Privacy policy content
PRIVACY_POLICY_CONTENT = """
# Privacy Policy - Productivity Analyzer

**Version:** 1.0.0  
**Last Updated:** October 15, 2025

## Overview
This Privacy Policy describes how the Productivity Analyzer collects, uses, and protects your personal information.

## Information We Collect
- Application usage data and activity patterns
- Productivity metrics and statistics
- System performance information
- User preferences and settings

## How We Use Your Information
We use the collected information to:
- Analyze and improve your productivity
- Generate personalized insights and recommendations
- Improve application performance and user experience
- Provide statistical reports on your work patterns

## Data Storage and Security
- All data is stored locally on your device
- We implement industry-standard security measures
- No data is shared with third parties without your explicit consent
- You can request deletion of your data at any time

## Your Consent
By using this application, you consent to:
- Collection of application usage data
- Local storage of productivity metrics
- Processing of your data for analysis purposes
- Generation of productivity reports

## Your Rights
You have the right to:
- Access your personal data
- Request correction of inaccurate data
- Request deletion of your data
- Withdraw consent at any time
- Opt-out of certain data collection features

## Tiered Consent Options
- **Basic Analysis:** Essential productivity tracking and basic reports
- **Enhanced Analysis:** Advanced analytics, detailed insights, and ML-powered recommendations

## Contact Us
If you have questions about this Privacy Policy, please contact us through the application settings.

## Changes to This Policy
We may update this Privacy Policy from time to time. We will notify you of any changes by updating the version number and last updated date.
"""


def initialize_database():
    """Initialize the database with required tables."""
    init_db()


def record_consent(user_id: int, consent_given: bool, policy_version: str = None) -> ConsentResponse:
    """Record a consent decision for a user."""
    if policy_version is None:
        policy_version = CURRENT_POLICY_VERSION
    
    consent_id = create_consent(user_id, policy_version, consent_given)
    
    # Get the created consent record
    consent = get_consent_status(user_id)
    
    return ConsentResponse(
        user_id=consent["user_id"],
        consent_given=consent["consent_given"],
        policy_version=consent["policy_version"],
        timestamp=consent["timestamp"],
        has_consent=consent["consent_given"]
    )


def check_consent(user_id: int) -> Optional[ConsentResponse]:
    """Check if a user has given consent."""
    consent = get_consent_status(user_id)
    
    if consent is None:
        return None
    
    return ConsentResponse(
        user_id=consent["user_id"],
        consent_given=consent["consent_given"],
        policy_version=consent["policy_version"],
        timestamp=consent["timestamp"],
        has_consent=consent["consent_given"]
    )


def revoke_consent(user_id: int) -> ConsentResponse:
    """Revoke consent for a user."""
    return record_consent(user_id, False, CURRENT_POLICY_VERSION)


def get_user_consent_history(user_id: int) -> List[ConsentHistoryItem]:
    """Get consent history for a user."""
    history = get_consent_history(user_id)
    return [
        ConsentHistoryItem(
            id=item["id"],
            user_id=item["user_id"],
            policy_version=item["policy_version"],
            consent_given=item["consent_given"],
            timestamp=item["timestamp"]
        )
        for item in history
    ]


def get_privacy_policy() -> dict:
    """Get the current privacy policy."""
    return {
        "version": CURRENT_POLICY_VERSION,
        "title": "Privacy Policy - Productivity Analyzer",
        "content": PRIVACY_POLICY_CONTENT,
        "last_updated": "2025-10-15"
    }


def requires_reconsent(user_id: int) -> bool:
    """Check if user needs to re-consent due to policy version change."""
    consent = get_consent_status(user_id)
    
    if consent is None:
        return True
    
    # If policy version has changed, require re-consent
    if consent["policy_version"] != CURRENT_POLICY_VERSION:
        return True
    
    # If consent was previously declined, no need to re-consent
    return not consent["consent_given"]
