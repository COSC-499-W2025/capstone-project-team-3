from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.utils.job_match_utils import recommend_jobs_from_profile, simulate_job_match

router = APIRouter()


class JobMatchRequest(BaseModel):
    job_description: str = Field(..., min_length=20)
    top_k: int = Field(default=5, ge=1, le=10)


@router.post("/job-match/simulate")
def run_job_match(payload: JobMatchRequest) -> Dict[str, Any]:
    try:
        return simulate_job_match(
            job_description=payload.job_description,
            top_k=payload.top_k,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to simulate job match: {exc}")


@router.get("/job-match/profile-postings")
def get_profile_job_postings(
    top_k: int = Query(default=12, ge=3, le=20),
    work_types: str = Query(default="onsite,remote,hybrid"),
    selected_skills: str = Query(default=""),
    easy_apply: bool = Query(default=True),
    posted_within_days: int = Query(default=7, ge=1, le=30),
) -> Dict[str, Any]:
    try:
        parsed_work_types = [
            item.strip().lower()
            for item in work_types.split(",")
            if item.strip()
        ]
        parsed_selected_skills = [
            item.strip()
            for item in selected_skills.split(",")
            if item.strip()
        ]
        return recommend_jobs_from_profile(
            top_k=top_k,
            work_types=parsed_work_types,
            selected_skills=parsed_selected_skills,
            easy_apply=easy_apply,
            posted_within_days=posted_within_days,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch profile LinkedIn links: {exc}")
