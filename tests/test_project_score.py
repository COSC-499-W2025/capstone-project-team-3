import math
import pytest

from app.utils.project_score import (
    _compute_git_code_score,
    _compute_non_code_score,
    _compute_non_git_code_score,
    _compute_contribution_percentages_single_project,
    compute_overall_project_contribution_score,
    compute_project_score_breakdown,
    compute_project_score_override,
)

# -------------------------------------------------------------------
# Sample inputs 
# -------------------------------------------------------------------

GIT_CODE_METRICS_SAMPLE = {
    "authors": ["john_doe", "jane_smith"],
    "total_commits": 47,
    "duration_days": 23,
    "files_added": 8,
    "files_modified": 12,
    "files_deleted": 2,
    "total_files_changed": 18,
    "code_files_changed": 15,
    "doc_files_changed": 3,
    "test_files_changed": 5,
    "languages": ["Python", "JavaScript", "TypeScript", "CSS"],
    "total_lines": 3247,
    "roles": ["backend", "frontend", "testing"],
    "technical_keywords": [
        "api", "authentication", "components", "database", "docker",
        "flask", "javascript", "models", "react", "routes",
        "testing", "utils", "validation", "webpack"
    ],
    "development_patterns": {
        "code_practices": ["Test-Driven Development", "Code Refactoring", "Documentation-Focused"],
        "project_evolution": ["Python Development", "JavaScript/Frontend Development"]
    }
}

NON_GIT_CODE_METRICS_SAMPLE = {
    "languages": ["Python", "JavaScript", "TypeScript"],
    "total_files": 23,
    "total_lines": 4523,
    "functions": 45,
    "components": 8,
    "classes": 12,
    "roles": ["backend", "frontend", "database"],
    "average_function_length": 18.7,
    "average_comment_ratio": 0.15,
    "code_files_changed": 20,
    "doc_files_changed": 2,
    "test_files_changed": 6,
    "technical_keywords": [
        "api", "authentication", "components", "database", "hooks",
        "models", "react", "routes", "services", "testing",
        "utils", "validation", "express", "middleware", "async"
    ],
    "code_patterns": {
        "frameworks_detected": ["React", "Flask", "Express.js"],
        "design_patterns": ["Observer Pattern", "Factory Pattern", "Repository Pattern"],
        "architectural_patterns": ["RESTful API Architecture", "Service-Oriented Architecture", "MVC Architecture"],
        "development_practices": [
            "React Hooks/Lifecycle (8 types)",
            "Component State Management",
            "Component Props/Data Flow (8 components)"
        ],
        "technology_stack": ["Python", "JavaScript", "TypeScript"]
    },
    "complexity_analysis": {
        "function_complexity": [12, 8, 45, 23, 15, 9, 34, 18, 7, 29],
        "component_complexity": [8, 12, 6, 15, 10, 7, 9, 11],
        "class_complexity": [25, 34, 18, 42, 28, 16, 31, 22, 19, 27, 33, 21],
        "maintainability_score": {
            "overall_score": 82.3,
            "average_complexity": 19.8,
            "total_code_units": 65,
            "complexity_distribution": {
                "low_complexity": 48,
                "medium_complexity": 15,
                "high_complexity": 2
            },
            "quality_indicators": {
                "functions_per_file": 2.83,
                "avg_lines_per_unit": 69.6,
                "complexity_trend": "good"
            }
        },
        "complexity_breakdown": {
            "functions": {
                "count": 45,
                "avg_complexity": 18.4,
                "high_complexity": 1
            },
            "classes": {
                "count": 12,
                "avg_complexity": 26.3,
                "high_complexity": 1
            },
            "components": {
                "count": 8,
                "avg_complexity": 9.8,
                "high_complexity": 0
            }
        }
    }
}


# -------------------------------------------------------------------
# Tests for _compute_git_code_score
# -------------------------------------------------------------------

def test_compute_git_code_score_sample_project():
    """
    Uses your real git_code_metrics sample.
    Expected score was precomputed ~0.78563.
    """
    score = _compute_git_code_score(GIT_CODE_METRICS_SAMPLE)

    assert 0.0 <= score <= 1.0
    assert score == pytest.approx(0.78563, rel=1e-5)


def test_compute_git_code_score_zero_metrics():
    """All-zero git metrics should yield a score of 0."""
    empty_metrics = {
        "total_commits": 0,
        "duration_days": 0,
        "total_lines": 0,
        "code_files_changed": 0,
        "test_files_changed": 0,
    }

    score = _compute_git_code_score(empty_metrics)
    assert score == 0.0


def test_compute_git_code_score_saturates_caps():
    """
    Very large values should saturate all normalized components at 1
    → final score should be exactly sum of weights (= 1.0).
    """
    huge_metrics = {
        "total_commits": 10_000,
        "duration_days": 365,
        "total_lines": 999_999,
        "code_files_changed": 1_000,
        "test_files_changed": 1_000,
    }

    score = _compute_git_code_score(huge_metrics)
    assert score == pytest.approx(1.0, rel=1e-6)


# -------------------------------------------------------------------
# Tests for _compute_non_code_score
# -------------------------------------------------------------------

def test_compute_non_code_score_normal_0_to_1():
    metrics = {"completeness_score": 0.75}
    score = _compute_non_code_score(metrics)
    assert score == pytest.approx(0.75)


def test_compute_non_code_score_percentage_input():
    """If completeness_score is e.g. 85, treat as 85% → 0.85."""
    metrics = {"completeness_score": 85}
    score = _compute_non_code_score(metrics)
    assert score == pytest.approx(0.85)


def test_compute_non_code_score_clamps_high():
    """Values > 100% should clamp to 1.0."""
    metrics = {"completeness_score": 150}
    score = _compute_non_code_score(metrics)
    assert score == 1.0


def test_compute_non_code_score_clamps_low():
    """Negative completeness should clamp to 0.0."""
    metrics = {"completeness_score": -0.3}
    score = _compute_non_code_score(metrics)
    assert score == 0.0


def test_compute_non_code_score_missing_defaults_zero():
    score = _compute_non_code_score({})
    assert score == 0.0


# -------------------------------------------------------------------
# Tests for _compute_non_git_code_score
# -------------------------------------------------------------------

def test_compute_non_git_code_score_sample_project():
    """
    Uses your real NON_GIT_CODE_METRICS_SAMPLE.
    Precomputed expected score ≈ 0.7241033.
    """
    score = _compute_non_git_code_score(NON_GIT_CODE_METRICS_SAMPLE)

    assert 0.0 <= score <= 1.0
    assert score == pytest.approx(0.7209233333, rel=1e-5)


def test_compute_non_git_code_score_zero_metrics():
    """
    All zeros in structural metrics + maintainability_score should yield 0.
    """
    metrics = {
        "total_files": 0,
        "total_lines": 0,
        "code_files_changed": 0,
        "test_files_changed": 0,
        "complexity_analysis": {
            "maintainability_score": {
                "overall_score": 0,
                "average_complexity": 0,
            }
        },
    }

    score = _compute_non_git_code_score(metrics)
    assert score == 0.0


def test_compute_non_git_code_score_saturates_caps():
    """
    Very large values + high maintainability/complexity should saturate all
    components at 1 → final score should be 1.0.
    """
    metrics = {
        "total_files": 999,
        "total_lines": 99999,
        "code_files_changed": 999,
        "test_files_changed": 999,
        "complexity_analysis": {
            "maintainability_score": {
                "overall_score": 999,
                "average_complexity": 999,
            }
        },
    }

    score = _compute_non_git_code_score(metrics)
    assert score == pytest.approx(1.0, rel=1e-6)


# -------------------------------------------------------------------
# Tests for _compute_contribution_percentages_single_project
# -------------------------------------------------------------------

def test_contribution_percentages_git_project():
    """
    Git project: should use git_code_metrics['total_lines'].
    Non-code side uses word_count → doc_line_equiv = word_count / 7.
    """
    non_code_metrics = {
        "word_count": 2100,
        "completeness_score": 0.8,  # not used here, but realistic
    }

    result = _compute_contribution_percentages_single_project(
        code_metrics={},
        git_code_metrics=GIT_CODE_METRICS_SAMPLE,
        non_code_metrics=non_code_metrics,
    )

    code_lines = GIT_CODE_METRICS_SAMPLE["total_lines"]
    doc_line_equiv = 2100 / 7.0
    total = code_lines + doc_line_equiv
    expected_code_pct = code_lines / total
    expected_non_code_pct = doc_line_equiv / total

    assert result["code_percentage"] == pytest.approx(expected_code_pct, rel=1e-6)
    assert result["non_code_percentage"] == pytest.approx(expected_non_code_pct, rel=1e-6)
    assert pytest.approx(result["code_percentage"] + result["non_code_percentage"], rel=1e-6) == 1.0


def test_contribution_percentages_non_git_project():
    """
    Non-Git project: should use code_metrics['total_lines'].
    """
    non_code_metrics = {
        "word_count": 3000,
        "completeness_score": 0.9,
    }

    result = _compute_contribution_percentages_single_project(
        code_metrics=NON_GIT_CODE_METRICS_SAMPLE,
        git_code_metrics={},
        non_code_metrics=non_code_metrics,
    )

    code_lines = NON_GIT_CODE_METRICS_SAMPLE["total_lines"]
    doc_line_equiv = 3000 / 7.0
    total = code_lines + doc_line_equiv
    expected_code_pct = code_lines / total
    expected_non_code_pct = doc_line_equiv / total

    assert result["code_percentage"] == pytest.approx(expected_code_pct, rel=1e-6)
    assert result["non_code_percentage"] == pytest.approx(expected_non_code_pct, rel=1e-6)
    assert pytest.approx(result["code_percentage"] + result["non_code_percentage"], rel=1e-6) == 1.0


def test_contribution_percentages_zero_totals():
    """If both code lines and word count are zero, both percentages should be 0."""
    result = _compute_contribution_percentages_single_project(
        code_metrics={"total_lines": 0},
        git_code_metrics={},
        non_code_metrics={"word_count": 0},
    )

    assert result == {
        "code_percentage": 0.0,
        "non_code_percentage": 0.0,
    }


# -------------------------------------------------------------------
# Tests for compute_overall_project_contribution_score
# -------------------------------------------------------------------

def test_overall_score_git_project_integration():
    """
    Full integration path for a Git project.
    Uses:
      - GIT_CODE_METRICS_SAMPLE
      - non_code_metrics with completeness_score=0.8, word_count=2100

    Precomputed expected final score ≈ 0.78684539.
    """
    non_code_metrics = {
        "completeness_score": 0.8,
        "word_count": 2100,
    }

    final_score = compute_overall_project_contribution_score(
        code_metrics={},
        git_code_metrics=GIT_CODE_METRICS_SAMPLE,
        non_code_metrics=non_code_metrics,
    )

    assert 0.0 <= final_score <= 1.0
    assert final_score == pytest.approx(0.78684539, rel=1e-5)


def test_overall_score_non_git_project_integration():
    """
    Full integration path for a Non-Git project.
    Uses:
      - NON_GIT_CODE_METRICS_SAMPLE
      - non_code_metrics with completeness_score=0.9, word_count=3000

    Precomputed expected final score ≈ 0.73932765.
    """
    non_code_metrics = {
        "completeness_score": 0.9,
        "word_count": 3000,
    }

    final_score = compute_overall_project_contribution_score(
        code_metrics=NON_GIT_CODE_METRICS_SAMPLE,
        git_code_metrics={},
        non_code_metrics=non_code_metrics,
    )

    assert 0.0 <= final_score <= 1.0
    assert final_score == pytest.approx(0.7364228861, rel=1e-5)


def test_overall_score_all_non_code():
    """
    If total_lines is 0 but there is non-code content,
    the final score should lean entirely on non_code_score.
    """
    code_metrics = {"total_lines": 0}
    git_code_metrics = {}
    non_code_metrics = {
        "completeness_score": 0.9,
        "word_count": 3500,
    }

    final_score = compute_overall_project_contribution_score(
        code_metrics=code_metrics,
        git_code_metrics=git_code_metrics,
        non_code_metrics=non_code_metrics,
    )

    # With no code lines, code_percentage should be 0 and final ~ non_code_score
    assert final_score == pytest.approx(0.9, rel=1e-5)


# -------------------------------------------------------------------
# Tests for compute_project_score_breakdown
# -------------------------------------------------------------------

def test_breakdown_git_matches_overall_score():
    non_code_metrics = {
        "completeness_score": 0.8,
        "word_count": 2100,
    }

    breakdown = compute_project_score_breakdown(
        code_metrics={},
        git_code_metrics=GIT_CODE_METRICS_SAMPLE,
        non_code_metrics=non_code_metrics,
    )

    final_score = compute_overall_project_contribution_score(
        code_metrics={},
        git_code_metrics=GIT_CODE_METRICS_SAMPLE,
        non_code_metrics=non_code_metrics,
    )

    assert breakdown["code"]["type"] == "git"
    assert breakdown["final_score"] == pytest.approx(final_score, rel=1e-6)
    assert set(breakdown["code"]["metrics"].keys()) == {
        "total_commits",
        "duration_days",
        "total_lines",
        "code_files_changed",
        "test_files_changed",
    }
    assert 0.0 <= breakdown["blend"]["code_percentage"] <= 1.0
    assert 0.0 <= breakdown["blend"]["non_code_percentage"] <= 1.0


def test_breakdown_non_git_matches_overall_score():
    non_code_metrics = {
        "completeness_score": 0.9,
        "word_count": 3000,
    }

    breakdown = compute_project_score_breakdown(
        code_metrics=NON_GIT_CODE_METRICS_SAMPLE,
        git_code_metrics={},
        non_code_metrics=non_code_metrics,
    )

    final_score = compute_overall_project_contribution_score(
        code_metrics=NON_GIT_CODE_METRICS_SAMPLE,
        git_code_metrics={},
        non_code_metrics=non_code_metrics,
    )

    assert breakdown["code"]["type"] == "non_git"
    assert breakdown["final_score"] == pytest.approx(final_score, rel=1e-6)
    assert set(breakdown["code"]["metrics"].keys()) == {
        "total_files",
        "total_lines",
        "code_files_changed",
        "test_files_changed",
        "maintainability_score",
    }


def test_override_git_renormalizes_weights():
    non_code_metrics = {
        "completeness_score": 0.8,
        "word_count": 2100,
    }

    breakdown = compute_project_score_override(
        code_metrics={},
        git_code_metrics=GIT_CODE_METRICS_SAMPLE,
        non_code_metrics=non_code_metrics,
        exclude_metrics=["test_files_changed"],
    )

    weights_sum = sum(
        item["weight"] for item in breakdown["code"]["metrics"].values()
    )
    assert breakdown["code"]["type"] == "git"
    assert "test_files_changed" not in breakdown["code"]["metrics"]
    assert weights_sum == pytest.approx(1.0, rel=1e-6)


def test_override_non_git_removes_metric():
    non_code_metrics = {
        "completeness_score": 0.9,
        "word_count": 3000,
    }

    breakdown = compute_project_score_override(
        code_metrics=NON_GIT_CODE_METRICS_SAMPLE,
        git_code_metrics={},
        non_code_metrics=non_code_metrics,
        exclude_metrics=["total_lines"],
    )

    assert breakdown["code"]["type"] == "non_git"
    assert "total_lines" not in breakdown["code"]["metrics"]
    weights_sum = sum(
        item["weight"] for item in breakdown["code"]["metrics"].values()
    )
    assert weights_sum == pytest.approx(1.0, rel=1e-6)


def test_override_raises_when_all_metrics_excluded():
    non_code_metrics = {
        "completeness_score": 0.8,
        "word_count": 2100,
    }

    with pytest.raises(ValueError):
        compute_project_score_override(
            code_metrics={},
            git_code_metrics=GIT_CODE_METRICS_SAMPLE,
            non_code_metrics=non_code_metrics,
            exclude_metrics=[
                "total_commits",
                "duration_days",
                "total_lines",
                "code_files_changed",
                "test_files_changed",
            ],
        )


def test_override_ignores_unknown_metric():
    non_code_metrics = {
        "completeness_score": 0.8,
        "word_count": 2100,
    }

    breakdown = compute_project_score_override(
        code_metrics={},
        git_code_metrics=GIT_CODE_METRICS_SAMPLE,
        non_code_metrics=non_code_metrics,
        exclude_metrics=["unknown_metric", "total_lines"],
    )

    assert "total_lines" not in breakdown["code"]["metrics"]


def test_override_respects_caps():
    huge_metrics = {
        "total_commits": 10_000,
        "duration_days": 365,
        "total_lines": 999_999,
        "code_files_changed": 1_000,
        "test_files_changed": 1_000,
    }
    non_code_metrics = {
        "completeness_score": 0.5,
        "word_count": 0,
    }

    breakdown = compute_project_score_override(
        code_metrics={},
        git_code_metrics=huge_metrics,
        non_code_metrics=non_code_metrics,
        exclude_metrics=["test_files_changed"],
    )

    assert breakdown["code"]["metrics"]["total_commits"]["normalized"] == pytest.approx(1.0)
