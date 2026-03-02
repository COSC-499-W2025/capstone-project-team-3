import json
import sqlite3
from typing import Any, Dict, Iterable, List, Optional

from app.data.db import get_connection
from app.utils.project_score import (
    compute_project_score_breakdown,
    compute_project_score_override,
)


class ProjectNotFoundError(ValueError):
    """Raised when project signature does not exist."""


class OverrideValidationError(ValueError):
    """Raised when override input is invalid."""


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def resolve_effective_score(
    score: Any,
    score_overridden: Any,
    score_overridden_value: Any,
) -> Dict[str, Any]:
    """
    Resolve base/override/effective values for consistent API/retrieve display.
    """
    score_original = _to_float(score, 0.0)
    is_overridden = _to_int(score_overridden, 0) == 1
    overridden_value = (
        _to_float(score_overridden_value)
        if score_overridden_value is not None
        else None
    )
    effective_score = (
        overridden_value
        if is_overridden and overridden_value is not None
        else score_original
    )
    return {
        "score": effective_score,
        "score_original": score_original,
        "score_overridden": is_overridden,
        "score_overridden_value": overridden_value,
    }


def get_project_score_state_map(
    cursor: Any,
    project_ids: Iterable[str],
) -> Dict[str, Dict[str, Any]]:
    """
    Return override state for projects keyed by project_signature.
    """
    project_ids = list(project_ids or [])
    if not project_ids:
        return {}

    placeholders = ",".join(["?"] * len(project_ids))
    try:
        cursor.execute(
            f"""
            SELECT project_signature, score_overridden, score_overridden_value, score_override_exclusions
            FROM PROJECT
            WHERE project_signature IN ({placeholders})
            """,
            project_ids,
        )
        rows = cursor.fetchall()
    except sqlite3.OperationalError:
        cursor.execute(
            f"""
            SELECT project_signature, score_overridden, score_overridden_value
            FROM PROJECT
            WHERE project_signature IN ({placeholders})
            """,
            project_ids,
        )
        rows = [(*row, None) for row in cursor.fetchall()]

    states: Dict[str, Dict[str, Any]] = {}
    for (
        project_signature,
        score_overridden,
        score_overridden_value,
        score_override_exclusions,
    ) in rows:
        states[project_signature] = {
            "score_overridden": _to_int(score_overridden, 0) == 1,
            "score_overridden_value": (
                _to_float(score_overridden_value)
                if score_overridden_value is not None
                else None
            ),
            "score_override_exclusions": _parse_exclusions(score_override_exclusions),
        }
    return states


def _parse_metric_value(metric_value: Any) -> Any:
    if not isinstance(metric_value, str):
        return metric_value
    stripped = metric_value.strip()
    if not stripped:
        return metric_value
    try:
        return json.loads(stripped)
    except (json.JSONDecodeError, TypeError, ValueError):
        return metric_value


def _parse_exclusions(raw_exclusions: Any) -> List[str]:
    if not raw_exclusions:
        return []
    if isinstance(raw_exclusions, list):
        return [
            value.strip()
            for value in raw_exclusions
            if isinstance(value, str) and value.strip()
        ]
    if isinstance(raw_exclusions, str):
        try:
            parsed = json.loads(raw_exclusions)
        except (json.JSONDecodeError, TypeError, ValueError):
            return []
        if isinstance(parsed, list):
            return [
                value.strip()
                for value in parsed
                if isinstance(value, str) and value.strip()
            ]
    return []


def _normalize_exclusions(
    exclude_metrics: Optional[List[str]],
    allowed_metrics: Iterable[str],
) -> List[str]:
    exclusions: List[str] = []
    for metric_name in exclude_metrics or []:
        if not isinstance(metric_name, str):
            continue
        cleaned = metric_name.strip()
        if not cleaned:
            continue
        if cleaned not in exclusions:
            exclusions.append(cleaned)

    allowed = {
        metric_name
        for metric_name in allowed_metrics
        if isinstance(metric_name, str) and metric_name.strip()
    }
    if not allowed and exclusions:
        raise OverrideValidationError("No code metrics available for override")

    unknown = [metric_name for metric_name in exclusions if metric_name not in allowed]
    if unknown:
        unknown_text = ", ".join(unknown)
        allowed_text = ", ".join(sorted(allowed))
        raise OverrideValidationError(
            f"Unknown code metric exclusions: {unknown_text}. "
            f"Allowed metrics: {allowed_text}"
        )

    return exclusions


def _load_project_and_metrics(project_signature: str) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        try:
            cursor.execute(
                """
                SELECT
                    project_signature,
                    name,
                    score,
                    score_overridden,
                    score_overridden_value,
                    score_override_exclusions
                FROM PROJECT
                WHERE project_signature = ?
                """,
                (project_signature,),
            )
            project_row = cursor.fetchone()
        except sqlite3.OperationalError:
            cursor.execute(
                """
                SELECT
                    project_signature,
                    name,
                    score,
                    score_overridden,
                    score_overridden_value
                FROM PROJECT
                WHERE project_signature = ?
                """,
                (project_signature,),
            )
            legacy_row = cursor.fetchone()
            project_row = (*legacy_row, None) if legacy_row else None
        if not project_row:
            raise ProjectNotFoundError("Project not found")

        (
            signature,
            name,
            score,
            score_overridden,
            score_overridden_value,
            score_override_exclusions,
        ) = project_row

        cursor.execute(
            """
            SELECT metric_name, metric_value
            FROM DASHBOARD_DATA
            WHERE project_id = ?
            """,
            (project_signature,),
        )
        metrics: Dict[str, Any] = {}
        for metric_name, metric_value in cursor.fetchall():
            metrics[metric_name] = _parse_metric_value(metric_value)

        return {
            "project_signature": signature,
            "name": name,
            "score": score,
            "score_overridden": score_overridden,
            "score_overridden_value": score_overridden_value,
            "exclude_metrics": _parse_exclusions(score_override_exclusions),
            "metrics": metrics,
        }
    finally:
        conn.close()


def _is_git_project(metrics: Dict[str, Any]) -> bool:
    return any(
        key in metrics
        for key in (
            "authors",
            "total_commits",
            "duration_days",
            "files_added",
            "files_modified",
            "files_deleted",
            "total_files_changed",
        )
    )


def _build_non_code_metrics(metrics: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "completeness_score": metrics.get("completeness_score", 0.0),
        "word_count": _to_int(metrics.get("word_count", 0), 0),
    }


def _build_git_code_metrics(metrics: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "total_commits": _to_int(metrics.get("total_commits", 0), 0),
        "duration_days": _to_int(metrics.get("duration_days", 0), 0),
        "total_lines": _to_int(metrics.get("total_lines", 0), 0),
        "code_files_changed": _to_int(metrics.get("code_files_changed", 0), 0),
        "test_files_changed": _to_int(metrics.get("test_files_changed", 0), 0),
    }


def _build_non_git_code_metrics(metrics: Dict[str, Any]) -> Dict[str, Any]:
    complexity_analysis = metrics.get("complexity_analysis")
    if not isinstance(complexity_analysis, dict):
        complexity_analysis = {}

    maintainability = complexity_analysis.get("maintainability_score")
    if not isinstance(maintainability, dict):
        maintainability = {}
    maintainability.setdefault("overall_score", 0)
    complexity_analysis["maintainability_score"] = maintainability

    return {
        "total_files": _to_int(metrics.get("total_files", 0), 0),
        "total_lines": _to_int(metrics.get("total_lines", 0), 0),
        "code_files_changed": _to_int(metrics.get("code_files_changed", 0), 0),
        "test_files_changed": _to_int(metrics.get("test_files_changed", 0), 0),
        "complexity_analysis": complexity_analysis,
    }


def _build_scoring_inputs(metrics: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    non_code_metrics = _build_non_code_metrics(metrics)
    if _is_git_project(metrics):
        return {
            "code_metrics": {},
            "git_code_metrics": _build_git_code_metrics(metrics),
            "non_code_metrics": non_code_metrics,
        }
    return {
        "code_metrics": _build_non_git_code_metrics(metrics),
        "git_code_metrics": {},
        "non_code_metrics": non_code_metrics,
    }


def compute_project_breakdown(project_signature: str) -> Dict[str, Any]:
    """
    Compute current breakdown for a single project.
    """
    project_data = _load_project_and_metrics(project_signature)
    score_fields = resolve_effective_score(
        project_data["score"],
        project_data["score_overridden"],
        project_data["score_overridden_value"],
    )
    scoring_inputs = _build_scoring_inputs(project_data["metrics"])
    breakdown = compute_project_score_breakdown(**scoring_inputs)


    return {
        "project_signature": project_data["project_signature"],
        "name": project_data["name"],
        **score_fields,
        "exclude_metrics": project_data.get("exclude_metrics", []),
        "breakdown": breakdown,
    }


def preview_project_score_override(
    project_signature: str,
    exclude_metrics: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Preview override result without writing to DB.
    """
    project_data = _load_project_and_metrics(project_signature)
    scoring_inputs = _build_scoring_inputs(project_data["metrics"])
    base_breakdown = compute_project_score_breakdown(**scoring_inputs)
    available_code_metrics = list(
        base_breakdown.get("code", {}).get("metrics", {}).keys()
    )
    exclusions = _normalize_exclusions(exclude_metrics, available_code_metrics)

    try:
        breakdown = compute_project_score_override(
            **scoring_inputs,
            exclude_metrics=exclusions,
        )
    except ValueError as exc:
        raise OverrideValidationError(str(exc)) from exc

    current_fields = resolve_effective_score(
        project_data["score"],
        project_data["score_overridden"],
        project_data["score_overridden_value"],
    )
    preview_score = _to_float(breakdown.get("final_score", 0.0), 0.0)
    preview_fields = resolve_effective_score(project_data["score"], 1, preview_score)

    return {
        "project_signature": project_data["project_signature"],
        "name": project_data["name"],
        "exclude_metrics": exclusions,
        "current_score": current_fields["score"],
        "score_original": current_fields["score_original"],
        "preview_score": preview_fields["score"],
        "breakdown": breakdown,
    }


def apply_project_score_override(
    project_signature: str,
    exclude_metrics: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Persist an override score.
    """
    preview = preview_project_score_override(project_signature, exclude_metrics)
    new_score = _to_float(preview["preview_score"], 0.0)

    conn = get_connection()
    cursor = conn.cursor()
    try:
        try:
            cursor.execute(
                """
                UPDATE PROJECT
                SET score_overridden = 1,
                    score_overridden_value = ?,
                    score_override_exclusions = ?
                WHERE project_signature = ?
                """,
                (new_score, json.dumps(preview["exclude_metrics"]), project_signature),
            )
        except sqlite3.OperationalError:
            cursor.execute(
                """
                UPDATE PROJECT
                SET score_overridden = 1,
                    score_overridden_value = ?
                WHERE project_signature = ?
                """,
                (new_score, project_signature),
            )
        if cursor.rowcount <= 0:
            raise ProjectNotFoundError("Project not found")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return {
        "project_signature": preview["project_signature"],
        "name": preview["name"],
        "exclude_metrics": preview["exclude_metrics"],
        "score": new_score,
        "score_original": _to_float(preview["score_original"], 0.0),
        "score_overridden": True,
        "score_overridden_value": new_score,
        "breakdown": preview["breakdown"],
    }


def clear_project_score_override(project_signature: str) -> Dict[str, Any]:
    """
    Clear persisted override score.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT name, score
            FROM PROJECT
            WHERE project_signature = ?
            """,
            (project_signature,),
        )
        row = cursor.fetchone()
        if not row:
            raise ProjectNotFoundError("Project not found")
        name, score = row

        try:
            cursor.execute(
                """
                UPDATE PROJECT
                SET score_overridden = 0,
                    score_overridden_value = NULL,
                    score_override_exclusions = NULL
                WHERE project_signature = ?
                """,
                (project_signature,),
            )
        except sqlite3.OperationalError:
            cursor.execute(
                """
                UPDATE PROJECT
                SET score_overridden = 0,
                    score_overridden_value = NULL
                WHERE project_signature = ?
                """,
                (project_signature,),
            )
        conn.commit()
    finally:
        conn.close()

    score_fields = resolve_effective_score(score, 0, None)
    return {
        "project_signature": project_signature,
        "name": name,
        "exclude_metrics": [],
        **score_fields,
    }
