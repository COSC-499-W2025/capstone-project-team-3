"""FastAPI app wiring (routers, static files, CORS). Import this for ASGI or the sidecar."""
from __future__ import annotations

from pathlib import Path
import sys

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

load_dotenv()
from app.utils.env_utils import load_gemini_key_from_store_into_environ

load_gemini_key_from_store_into_environ()

from app.api.routes.upload_page import router as upload_page_router
from app.api.routes.privacy_consent import router as privacy_consent_router
from app.api.routes.get_upload_id import router as upload_resolver_router
from app.api.routes.resume import router as resume_router
from app.api.routes.user_preferences import router as user_preferences_router
from app.api.routes.skills import router as skills_router
from app.api.routes.projects import router as projects_router
from app.api.routes.portfolio import router as portfolio_router
from app.api.routes.analysis import router as analysis_router
from app.api.routes.health import router as health_router
from app.api.routes.post_thumbnail import router as thumbnail_router
from app.api.routes.chronological import router as chronological_router
from app.api.routes.ats import router as ats_router
from app.api.routes.cover_letter import router as cover_letter_router
from app.api.routes.gemini_settings import router as gemini_settings_router
from app.api.routes.learning import router as learning_router


def _resolve_static_dir() -> Path:
    """Dev: .../app/static. Frozen (PyInstaller): .../_internal/app/static from --add-data."""
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
        return base / "app" / "static"
    return Path(__file__).resolve().parent / "static"


app = FastAPI(title="Big Picture API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = _resolve_static_dir()
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

app.include_router(upload_page_router)
app.include_router(upload_resolver_router, prefix="/api")
app.include_router(privacy_consent_router, prefix="/api")
app.include_router(resume_router)
app.include_router(user_preferences_router, prefix="/api")
app.include_router(skills_router, prefix="/api")
app.include_router(projects_router, prefix="/api")
app.include_router(portfolio_router, prefix="/api")
app.include_router(analysis_router, prefix="/api")
app.include_router(health_router)
app.include_router(thumbnail_router, prefix="/api")
app.include_router(chronological_router, prefix="/api")
app.include_router(ats_router, prefix="/api")
app.include_router(cover_letter_router, prefix="/api")
app.include_router(gemini_settings_router, prefix="/api")
app.include_router(learning_router, prefix="/api")


@app.get("/")
def read_root():
    return {"message": "Welcome to the Project Insights!!"}
