"""
Minimal Python entry point.
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
from app.consent_routes import router as consent_router
from app.consent_service import initialize_database
# Uncomment the line below to enable consent enforcement middleware
# from app.consent_middleware import ConsentMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for application startup and shutdown."""
    # Startup
    initialize_database()
    yield
    # Shutdown (if needed in the future)


app = FastAPI(
    title="Productivity Analyzer API",
    description="API for productivity tracking with consent management",
    version="1.0.0",
    lifespan=lifespan
)

# Include consent management routes
app.include_router(consent_router)

# Uncomment the line below to enable consent enforcement on all protected endpoints
# app.add_middleware(ConsentMiddleware)

@app.get("/")
def read_root():
    return {"message": "Hello, world!"}

if __name__ == "__main__":
    print("App started")
    uvicorn.run(app, host="0.0.0.0", port=8000)
