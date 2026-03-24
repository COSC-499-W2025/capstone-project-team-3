"""Tests for clearing analysis when no files are analyzed."""
import pytest

from app.data.db import get_connection, init_db
from app.utils.analysis_clear_utils import clear_project_analysis_data


@pytest.fixture(scope="function", autouse=True)
def isolated_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test_clear.sqlite"
    monkeypatch.setattr("app.data.db.DB_PATH", db_path)
    monkeypatch.setattr("app.data.db.DATA_DIR", tmp_path)
    init_db()
    yield


def test_clear_project_analysis_data_removes_children_and_resets_project():
    sig = "test-sig-abc"
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO PROJECT (project_signature, name, path, summary, score)
        VALUES (?, 'P', '/tmp/p', 'old summary', 0.8)
        """,
        (sig,),
    )
    cur.execute(
        "INSERT INTO SKILL_ANALYSIS (project_id, skill, source, date) VALUES (?, ?, ?, ?)",
        (sig, "Python", "technical_skill", "2026-01-01"),
    )
    cur.execute(
        "INSERT INTO DASHBOARD_DATA (project_id, metric_name, metric_value) VALUES (?, ?, ?)",
        (sig, "m1", "1"),
    )
    cur.execute(
        "INSERT INTO RESUME_SUMMARY (project_id, summary_text) VALUES (?, ?)",
        (sig, "[]"),
    )
    cur.execute(
        "INSERT INTO GIT_HISTORY (project_id, commit_hash, author_name, author_email, commit_date, message) "
        "VALUES (?, 'h1', 'a', 'e@e.com', '2026-01-01', 'm')",
        (sig,),
    )
    conn.commit()
    cur.close()
    conn.close()

    clear_project_analysis_data(sig)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM SKILL_ANALYSIS WHERE project_id = ?", (sig,))
    assert cur.fetchone()[0] == 0
    cur.execute("SELECT COUNT(*) FROM DASHBOARD_DATA WHERE project_id = ?", (sig,))
    assert cur.fetchone()[0] == 0
    cur.execute("SELECT COUNT(*) FROM RESUME_SUMMARY WHERE project_id = ?", (sig,))
    assert cur.fetchone()[0] == 0
    cur.execute("SELECT COUNT(*) FROM GIT_HISTORY WHERE project_id = ?", (sig,))
    assert cur.fetchone()[0] == 0
    cur.execute("SELECT summary, score FROM PROJECT WHERE project_signature = ?", (sig,))
    row = cur.fetchone()
    assert row[0] == ""
    assert row[1] == 0
    cur.close()
    conn.close()
