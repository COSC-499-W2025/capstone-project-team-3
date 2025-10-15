"""
Consent management API routes.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models import ConsentRequest, ConsentResponse, ConsentHistoryItem, PrivacyPolicyResponse
from app.consent_service import (
    record_consent,
    check_consent,
    revoke_consent,
    get_user_consent_history,
    get_privacy_policy,
    requires_reconsent
)

router = APIRouter(prefix="/consent", tags=["consent"])


@router.get("/status/{user_id}", response_model=ConsentResponse)
async def get_consent_status(user_id: int):
    """
    Get the current consent status for a user.
    
    Args:
        user_id: The ID of the user
        
    Returns:
        ConsentResponse with current consent status
        
    Raises:
        HTTPException: If no consent record exists for the user
    """
    consent = check_consent(user_id)
    
    if consent is None:
        raise HTTPException(
            status_code=404, 
            detail=f"No consent record found for user {user_id}"
        )
    
    return consent


@router.post("/accept", response_model=ConsentResponse)
async def accept_consent(request: ConsentRequest):
    """
    Record that a user has accepted the consent.
    
    Args:
        request: ConsentRequest with user_id and policy_version
        
    Returns:
        ConsentResponse with the created consent record
    """
    if not request.consent_given:
        raise HTTPException(
            status_code=400,
            detail="Use /consent/decline endpoint to decline consent"
        )
    
    consent = record_consent(
        user_id=request.user_id,
        consent_given=True,
        policy_version=request.policy_version
    )
    
    return consent


@router.post("/decline", response_model=ConsentResponse)
async def decline_consent(request: ConsentRequest):
    """
    Record that a user has declined the consent.
    
    Args:
        request: ConsentRequest with user_id and policy_version
        
    Returns:
        ConsentResponse with the created consent record
    """
    if request.consent_given:
        raise HTTPException(
            status_code=400,
            detail="Use /consent/accept endpoint to accept consent"
        )
    
    consent = record_consent(
        user_id=request.user_id,
        consent_given=False,
        policy_version=request.policy_version
    )
    
    return consent


@router.post("/revoke/{user_id}", response_model=ConsentResponse)
async def revoke_user_consent(user_id: int):
    """
    Revoke consent for a user.
    
    Args:
        user_id: The ID of the user
        
    Returns:
        ConsentResponse with the updated consent record
    """
    consent = revoke_consent(user_id)
    return consent


@router.get("/history/{user_id}", response_model=List[ConsentHistoryItem])
async def get_consent_history(user_id: int):
    """
    Get the consent history for a user.
    
    Args:
        user_id: The ID of the user
        
    Returns:
        List of ConsentHistoryItem records
    """
    history = get_user_consent_history(user_id)
    return history


@router.get("/privacy-policy", response_model=PrivacyPolicyResponse)
async def get_privacy_policy_endpoint():
    """
    Get the current privacy policy.
    
    Returns:
        PrivacyPolicyResponse with policy content and version
    """
    policy = get_privacy_policy()
    return PrivacyPolicyResponse(**policy)


@router.get("/requires-consent/{user_id}")
async def check_requires_consent(user_id: int):
    """
    Check if a user needs to provide or update consent.
    
    Args:
        user_id: The ID of the user
        
    Returns:
        Dict with requires_consent boolean
    """
    needs_consent = requires_reconsent(user_id)
    return {
        "user_id": user_id,
        "requires_consent": needs_consent,
        "message": "User needs to provide consent" if needs_consent else "User has valid consent"
    }
