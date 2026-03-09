import datetime
import pytest
from app.data.db import get_connection
from app.utils.delete_insights_utils import (
	get_projects,
	delete_project_by_signature,
)


@pytest.fixture(scope="function", autouse=True)
def isolated_db(tmp_path, monkeypatch):
	"""Use a per-test temporary SQLite DB so schema/data don't touch the real DB."""
	from app.data import db as dbmod
	test_db = tmp_path / "delete_insights.sqlite3"
	monkeypatch.setattr(dbmod, "DB_PATH", test_db)
	dbmod.init_db()
	yield


def _insert_project(project_signature: str, name: str):
	"""Helper to insert a project and related rows for cascade testing."""
	conn = get_connection()
	cur = conn.cursor()
	now = datetime.datetime.now().isoformat()
	# Insert or replace project row
	cur.execute(
		"""
		INSERT OR REPLACE INTO PROJECT
		(project_signature, name, path, file_signatures, size_bytes, created_at, last_modified)
		VALUES (?, ?, ?, ?, ?, ?, ?)
		""",
		(project_signature, name, "/tmp/test", "[]", 0, now, now),
	)
	# Related tables rows (to validate ON DELETE CASCADE)
	cur.execute(
		"INSERT OR IGNORE INTO GIT_HISTORY (project_id, commit_hash, author_name, author_email, commit_date, message) VALUES (?, 't1', 'n', 'e', ?, 'm')",
		(project_signature, now),
	)
	cur.execute(
		"INSERT OR IGNORE INTO SKILL_ANALYSIS (project_id, skill, source) VALUES (?, 'Python', 'code')",
		(project_signature,),
	)
	cur.execute(
		"INSERT OR IGNORE INTO DASHBOARD_DATA (project_id, metric_name, metric_value, chart_type) VALUES (?, 'Lines', '10', 'bar')",
		(project_signature,),
	)
	cur.execute(
		"INSERT OR IGNORE INTO RESUME_SUMMARY (project_id, summary_text) VALUES (?, 'summary')",
		(project_signature,),
	)
	conn.commit()
	conn.close()


def _count_rows_for_project(project_signature: str) -> dict:
	"""Return counts for project and related tables by signature."""
	conn = get_connection()
	cur = conn.cursor()
	cur.execute("SELECT COUNT(*) FROM PROJECT WHERE project_signature = ?", (project_signature,))
	project = cur.fetchone()[0]
	cur.execute("SELECT COUNT(*) FROM GIT_HISTORY WHERE project_id = ?", (project_signature,))
	git = cur.fetchone()[0]
	cur.execute("SELECT COUNT(*) FROM SKILL_ANALYSIS WHERE project_id = ?", (project_signature,))
	skill = cur.fetchone()[0]
	cur.execute("SELECT COUNT(*) FROM DASHBOARD_DATA WHERE project_id = ?", (project_signature,))
	dash = cur.fetchone()[0]
	cur.execute("SELECT COUNT(*) FROM RESUME_SUMMARY WHERE project_id = ?", (project_signature,))
	resume = cur.fetchone()[0]
	conn.close()
	return {"project": project, "git": git, "skill": skill, "dash": dash, "resume": resume}


def test_get_and_delete_by_signature_cascade():
	"""Insert a project, then delete by signature and assert cascade."""
	sig = "sig_test_delete_utils_1"
	name = "DeleteUtilsProjectOne"
	_insert_project(sig, name)

	# get_projects should include our dict with signature and name
	projs = get_projects()
	sigs = [p["project_signature"] for p in projs]
	assert sig in sigs
	names = [p["name"] for p in projs]
	assert name in names

	# Verify rows exist before deletion
	before = _count_rows_for_project(sig)
	assert before["project"] == 1
	assert before["git"] >= 1
	assert before["skill"] >= 1
	assert before["dash"] >= 1
	assert before["resume"] >= 1

	# Delete by exact signature
	assert delete_project_by_signature(sig) is True

	# All related rows should be removed due to ON DELETE CASCADE
	after = _count_rows_for_project(sig)
	assert after == {"project": 0, "git": 0, "skill": 0, "dash": 0, "resume": 0}


def test_delete_one_of_duplicate_names_preserve_other():
	"""When two projects share the same name, deleting by signature removes only the targeted one."""
	name = "DuplicateNameProject"
	sig1 = "sig_dup_1"
	sig2 = "sig_dup_2"

	_insert_project(sig1, name)
	_insert_project(sig2, name)

	# Both projects should exist
	before1 = _count_rows_for_project(sig1)
	before2 = _count_rows_for_project(sig2)
	assert before1["project"] == 1
	assert before2["project"] == 1
	assert before1["git"] >= 1 and before2["git"] >= 1

	# Sanity check via get_projects
	projs = get_projects()
	sigs = {p["project_signature"] for p in projs}
	assert sig1 in sigs and sig2 in sigs

	# Delete only sig1
	assert delete_project_by_signature(sig1) is True

	# sig1 should be fully removed, sig2 should remain intact
	after1 = _count_rows_for_project(sig1)
	after2 = _count_rows_for_project(sig2)
	assert after1 == {"project": 0, "git": 0, "skill": 0, "dash": 0, "resume": 0}
	assert after2["project"] == 1
	assert after2["git"] >= 1
	assert after2["skill"] >= 1
	assert after2["dash"] >= 1
	assert after2["resume"] >= 1


def test_delete_project_snapshots_into_resume_rows():
	"""When a project is deleted, RESUME_PROJECT rows that referenced it are kept and filled with snapshot data."""
	sig = "sig_snapshot_test"
	name = "Project To Delete"
	_insert_project(sig, name)

	conn = get_connection()
	cur = conn.cursor()
	cur.execute("INSERT INTO RESUME (id, name) VALUES (2, 'Test Resume')")
	cur.execute(
		"INSERT INTO RESUME_PROJECT (resume_id, project_id, display_order) VALUES (2, ?, 1)",
		(sig,),
	)
	conn.commit()
	conn.close()

	# Before delete: RESUME_PROJECT row has no snapshot (project_name etc. are NULL)
	conn = get_connection()
	cur = conn.cursor()
	cur.execute(
		"SELECT project_name, start_date, end_date, skills, bullets FROM RESUME_PROJECT WHERE resume_id = 2 AND project_id = ?",
		(sig,),
	)
	row_before = cur.fetchone()
	conn.close()
	assert row_before is not None
	assert row_before[0] is None  # project_name not set yet

	# Delete project (should snapshot into RESUME_PROJECT first)
	assert delete_project_by_signature(sig) is True

	# Project is gone from PROJECT and related tables
	after = _count_rows_for_project(sig)
	assert after["project"] == 0
	assert after["resume"] == 0  # RESUME_SUMMARY cascade

	# RESUME_PROJECT row still exists and has snapshot data
	conn = get_connection()
	cur = conn.cursor()
	cur.execute(
		"SELECT project_name, start_date, end_date, skills, bullets FROM RESUME_PROJECT WHERE resume_id = 2 AND project_id = ?",
		(sig,),
	)
	row_after = cur.fetchone()
	conn.close()
	assert row_after is not None
	assert row_after[0] == name
	assert row_after[1] is not None  # start_date (created_at)
	assert row_after[2] is not None  # end_date (last_modified)
	assert row_after[3] is not None  # skills JSON (e.g. ["Python"])
	assert row_after[4] is not None  # bullets JSON (e.g. ["summary"])


