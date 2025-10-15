"""
Data models for the application.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ConsentRequest(BaseModel):
    """Request model for consent actions."""
    user_id: int
    consent_given: bool
    policy_version: str = "1.0.0"


class ConsentResponse(BaseModel):
    """Response model for consent status."""
    user_id: int
    consent_given: bool
    policy_version: str
    timestamp: str
    has_consent: bool


class ConsentHistoryItem(BaseModel):
    """Model for a single consent history entry."""
    id: int
    user_id: int
    policy_version: str
    consent_given: bool
    timestamp: str


class PrivacyPolicyResponse(BaseModel):
    """Response model for privacy policy."""
    version: str
    title: str
    content: str
    last_updated: str
