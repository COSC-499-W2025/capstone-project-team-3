import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.utils.env_utils import (
    check_gemini_api_key,
    clear_persisted_gemini_api_key,
    persist_gemini_api_key,
)

router = APIRouter()


class GeminiKeyBody(BaseModel):
    api_key: str = Field(..., min_length=1)


class GeminiKeyStatus(BaseModel):
    configured: bool
    valid: bool
    masked_suffix: str | None = None


def _mask_key(key: str | None) -> str | None:
    if not key or len(key.strip()) < 4:
        return None
    k = key.strip()
    return f"…{k[-4:]}"


@router.get("/gemini-key/status", response_model=GeminiKeyStatus)
def gemini_key_status():
    key = os.getenv("GEMINI_API_KEY")
    configured = bool(key and key.strip())
    valid, _ = check_gemini_api_key()
    return GeminiKeyStatus(
        configured=configured,
        valid=valid,
        masked_suffix=_mask_key(key) if configured else None,
    )


@router.post("/gemini-key")
def gemini_key_save(body: GeminiKeyBody):
    try:
        persist_gemini_api_key(body.api_key)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Gemini API key format")
    return {"ok": True}


@router.delete("/gemini-key")
def gemini_key_delete():
    clear_persisted_gemini_api_key()
    return {"ok": True}
