"""
Clear stored analysis artifacts when a project cannot be analyzed
(e.g. all files excluded by user filters).
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from app.data.db import get_connection


def _find_project_signatures(project_path: str, project_name: str) -> List[str]:
    """Resolve DB project_signature rows for this extracted folder (path) or unique name match."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        paths = {project_path}
        try:
            paths.add(str(Path(project_path).resolve()))
        except OSError:
            pass

        sigs: set[str] = set()
        for p in paths:
            cur.execute("SELECT project_signature FROM PROJECT WHERE path = ?", (p,))
            for (sig,) in cur.fetchall():
                if sig:
                    sigs.add(sig)

        if not sigs:
            cur.execute("SELECT project_signature FROM PROJECT WHERE name = ?", (project_name,))
            rows = cur.fetchall()
            if len(rows) == 1 and rows[0][0]:
                sigs.add(rows[0][0])

        return list(sigs)
    finally:
        cur.close()
        conn.close()


def clear_project_analysis_data(project_signature: str) -> None:
    """Remove metrics, skills, summaries, git history for one project; reset summary/score."""
    if not project_signature:
        return
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM GIT_HISTORY WHERE project_id = ?", (project_signature,))
        cur.execute("DELETE FROM SKILL_ANALYSIS WHERE project_id = ?", (project_signature,))
        cur.execute("DELETE FROM RESUME_SUMMARY WHERE project_id = ?", (project_signature,))
        cur.execute("DELETE FROM DASHBOARD_DATA WHERE project_id = ?", (project_signature,))
        cur.execute(
            """
            UPDATE PROJECT
            SET summary = '', score = 0, last_modified = CURRENT_TIMESTAMP
            WHERE project_signature = ?
            """,
            (project_signature,),
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()


def clear_project_analysis_when_skipped_no_files(
    project_path: str,
    project_name: str,
    project_signature: Optional[str] = None,
) -> None:
    """
    Called when /analysis/run skips because nothing is left to analyze.
    Clears stale insights so the UI does not show previous-run data.
    """
    ordered: List[str] = []
    seen: set[str] = set()
    if project_signature and project_signature not in seen:
        seen.add(project_signature)
        ordered.append(project_signature)
    for sig in _find_project_signatures(project_path, project_name):
        if sig and sig not in seen:
            seen.add(sig)
            ordered.append(sig)
    for sig in ordered:
        clear_project_analysis_data(sig)
