import json

import pytest

from app.data import db as dbmod
from app.utils.score_override_utils import (
    OverrideValidationError,
    ProjectNotFoundError,
    apply_project_score_override,
    clear_project_score_override,
    compute_project_breakdown,
    preview_project_score_override,
    resolve_effective_score,
)


@pytest.fixture
def isolated_db(tmp_path, monkeypatch):
    test_db = tmp_path / "score_override.sqlite3"
    monkeypatch.setattr(dbmod, "DB_PATH", test_db)
    dbmod.init_db()
    yield


def _insert_non_git_project(project_signature: str = "sig_non_git") -> str:
    conn = dbmod.get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO PROJECT (
            project_signature, name, score, score_overridden, score_overridden_value
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (project_signature, "Non Git Project", 0.62, 0, None),
    )

    metrics = {
        "total_files": 24,
        "total_lines": 3200,
        "code_files_changed": 18,
        "test_files_changed": 4,
        "complexity_analysis": {
            "maintainability_score": {
                "overall_score": 81.0
            }
        },
        "completeness_score": 0.9,
        "word_count": 1500,
    }

    for metric_name, metric_value in metrics.items():
        if isinstance(metric_value, (dict, list)):
            metric_value = json.dumps(metric_value)
        cur.execute(
            """
            INSERT INTO DASHBOARD_DATA (project_id, metric_name, metric_value)
            VALUES (?, ?, ?)
            """,
            (project_signature, metric_name, str(metric_value)),
        )

    conn.commit()
    conn.close()
    return project_signature


def test_resolve_effective_score_not_overridden():
    resolved = resolve_effective_score(0.7, 0, None)
    assert resolved["score"] == pytest.approx(0.7)
    assert resolved["score_original"] == pytest.approx(0.7)
    assert resolved["score_overridden"] is False
    assert resolved["score_overridden_value"] is None


def test_resolve_effective_score_overridden():
    resolved = resolve_effective_score(0.4, 1, 0.95)
    assert resolved["score"] == pytest.approx(0.95)
    assert resolved["score_original"] == pytest.approx(0.4)
    assert resolved["score_overridden"] is True
    assert resolved["score_overridden_value"] == pytest.approx(0.95)


def test_resolve_effective_score_string_override_flags():
    not_overridden = resolve_effective_score(0.7, "0", 0.95)
    assert not_overridden["score_overridden"] is False
    assert not_overridden["score"] == pytest.approx(0.7)

    overridden = resolve_effective_score(0.7, "1", 0.95)
    assert overridden["score_overridden"] is True
    assert overridden["score"] == pytest.approx(0.95)


def test_compute_project_breakdown_non_git(isolated_db):
    signature = _insert_non_git_project()
    payload = compute_project_breakdown(signature)

    assert payload["project_signature"] == signature
    assert payload["score_overridden"] is False
    assert payload["score"] == pytest.approx(0.62)
    assert payload["breakdown"]["code"]["type"] == "non_git"
    assert "total_lines" in payload["breakdown"]["code"]["metrics"]


def test_preview_override_excludes_metric(isolated_db):
    signature = _insert_non_git_project()
    preview = preview_project_score_override(signature, ["total_lines"])

    assert preview["project_signature"] == signature
    assert preview["exclude_metrics"] == ["total_lines"]
    assert 0.0 <= preview["preview_score"] <= 1.0
    assert "total_lines" not in preview["breakdown"]["code"]["metrics"]


def test_preview_override_rejects_excluding_all_code_metrics(isolated_db):
    signature = _insert_non_git_project()
    with pytest.raises(OverrideValidationError):
        preview_project_score_override(
            signature,
            [
                "total_files",
                "total_lines",
                "code_files_changed",
                "test_files_changed",
                "maintainability_score",
            ],
        )


def test_apply_then_clear_override_persists_state(isolated_db):
    signature = _insert_non_git_project()

    applied = apply_project_score_override(signature, ["test_files_changed"])
    assert applied["score_overridden"] is True
    assert applied["score_overridden_value"] == pytest.approx(applied["score"])
    assert applied["exclude_metrics"] == ["test_files_changed"]

    conn = dbmod.get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT score_overridden, score_overridden_value, score_override_exclusions
        FROM PROJECT
        WHERE project_signature = ?
        """,
        (signature,),
    )
    row = cur.fetchone()
    conn.close()
    assert row[0] == 1
    assert row[1] is not None
    assert json.loads(row[2]) == ["test_files_changed"]

    cleared = clear_project_score_override(signature)
    assert cleared["score_overridden"] is False
    assert cleared["score_overridden_value"] is None
    assert cleared["exclude_metrics"] == []
    assert cleared["score"] == pytest.approx(cleared["score_original"])


def test_compute_project_breakdown_not_found():
    with pytest.raises(ProjectNotFoundError):
        compute_project_breakdown("missing_signature")
