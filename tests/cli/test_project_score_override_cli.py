from unittest.mock import patch

from app.cli.project_score_override_cli import (
    format_project_score_display,
    run_project_score_override_cli,
)


def test_format_project_score_display_shows_override_marker():
    project = {"display_score": 0.8123, "score_overridden": True}
    assert format_project_score_display(project) == "0.812*"


def test_run_project_score_override_cli_preview_apply_clear_flow(capsys):
    projects = [
        {
            "project_signature": "sig-1",
            "name": "Project One",
            "score": 0.70,
            "display_score": 0.70,
            "score_overridden": False,
        }
    ]
    breakdown_payload = {
        "display_score": 0.70,
        "breakdown": {
            "code": {"type": "non_git", "subtotal": 0.60, "metrics": {"total_lines": 100}},
            "non_code": {"subtotal": 0.90},
            "blend": {"code_percentage": 0.7, "non_code_percentage": 0.3},
            "final_score": 0.70,
        },
    }

    with (
        patch("app.cli.project_score_override_cli.get_projects_by_signatures", return_value=projects) as get_projects,
        patch("app.cli.project_score_override_cli.compute_project_breakdown", return_value=breakdown_payload) as breakdown,
        patch(
            "app.cli.project_score_override_cli.preview_project_score_override",
            return_value={"preview_score": 0.80, "current_score": 0.70},
        ) as preview,
        patch(
            "app.cli.project_score_override_cli.apply_project_score_override",
            return_value={"display_score": 0.82},
        ) as apply_override,
        patch(
            "app.cli.project_score_override_cli.clear_project_score_override",
            return_value={"display_score": 0.70},
        ) as clear_override,
        patch(
            "builtins.input",
            side_effect=[
                "yes",
                "1",
                "preview",
                "total_lines",
                "1",
                "apply",
                "total_lines",
                "1",
                "clear",
                "done",
            ],
        ),
    ):
        run_project_score_override_cli(["sig-1"])

    output = capsys.readouterr().out
    assert "* indicates an overridden score." in output
    assert "Preview score: 0.800 (current: 0.700)" in output
    assert "Override applied. New score: 0.820*" in output
    assert "Override cleared. Score restored to 0.700" in output

    assert get_projects.call_count == 4
    assert breakdown.call_count == 3
    preview.assert_called_once_with("sig-1", ["total_lines"])
    apply_override.assert_called_once_with("sig-1", ["total_lines"])
    clear_override.assert_called_once_with("sig-1")
