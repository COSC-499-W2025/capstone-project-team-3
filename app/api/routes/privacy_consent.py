from fastapi import APIRouter
from pydantic import BaseModel
from app.utils.consent_utils import record_consent, has_consent, revoke_consent
from pathlib import Path
import sqlite3

router = APIRouter()
DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "app.sqlite3"

class ConsentRequest(BaseModel):
    accepted: bool

@router.post("/privacy-consent")
def submit_consent(request: ConsentRequest):
    """Record user consent decision."""
    success = record_consent(DB_PATH, request.accepted)
    if success:
        return {"status": "ok", "message": "Consent recorded successfully"}
    return {"status": "error", "message": "Failed to record consent"}

@router.get("/privacy-consent")
def get_consent_status():
    """Check if user has given consent."""
    has_given_consent = has_consent(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp FROM CONSENT ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    
    return {
        "has_consent": has_given_consent,
        "timestamp": result[0] if result else None
    }

@router.delete("/privacy-consent")
def revoke_user_consent():
    """Revoke user consent."""
    try:
        revoke_consent(DB_PATH)
        return {"status": "ok", "message": "Consent revoked successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
