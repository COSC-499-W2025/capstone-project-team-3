import json
import logging

from fastapi import APIRouter

from app.data.db import get_connection
from app.utils.generate_resume import build_resume_model
from app.utils.learning_recommendations import build_learning_payload, load_course_catalog

logger = logging.getLogger(__name__)

router = APIRouter()


def _latest_job_context() -> tuple[str, str]:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT job_title, industry
            FROM USER_PREFERENCES
            ORDER BY updated_at DESC
            LIMIT 1
            """
        )
        row = cursor.fetchone()
        if not row:
            return "", ""
        return (row[0] or "", row[1] or "")
    finally:
        conn.close()


@router.get("/learning/recommendations")
def get_learning_recommendations():
    """
    Curated courses scored from the master resume plus latest job title and industry.
    """
    try:
        catalog = load_course_catalog()
    except FileNotFoundError:
        logger.exception("course catalog missing")
        return {"based_on_resume": [], "next_steps": []}
    except (json.JSONDecodeError, ValueError) as e:
        logger.exception("invalid course catalog: %s", e)
        return {"based_on_resume": [], "next_steps": []}

    resume = build_resume_model(project_ids=None)
    job_title, industry = _latest_job_context()
    return build_learning_payload(
        catalog=catalog,
        resume=resume,
        job_title=job_title,
        industry=industry,
    )
