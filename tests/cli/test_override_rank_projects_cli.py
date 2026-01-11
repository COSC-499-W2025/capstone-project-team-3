from unittest.mock import patch

import app.cli.override_rank_projects_cli as cli_mod


def test_override_rank_projects_cli_happy_path(capsys):
    mocked_projects = [
        {"name": "ProjA", "project_signature": "sig_a"},
        {"name": "ProjB", "project_signature": "sig_b"},
        {"name": "ProjC", "project_signature": "sig_c"},
    ]

    with (
        patch("app.cli.override_rank_projects_cli.get_projects", return_value=mocked_projects),
        patch("app.cli.override_rank_projects_cli.set_project_ranks") as set_fn,
        patch("builtins.input", side_effect=["1", "2", "3"]),
    ):
        cli_mod.main()

    out = capsys.readouterr().out
    assert "Projects:" in out
    assert "✅ Project ranks updated." in out
    set_fn.assert_called_once_with({"sig_a": 1, "sig_b": 2, "sig_c": 3})


def test_override_rank_projects_cli_no_projects(capsys):
    with (
        patch("app.cli.override_rank_projects_cli.get_projects", return_value=[]),
        patch("app.cli.override_rank_projects_cli.set_project_ranks") as set_fn,
    ):
        cli_mod.main()

    out = capsys.readouterr().out
    assert "No projects found." in out
    set_fn.assert_not_called()


def test_override_rank_projects_cli_duplicate_selection(capsys):
    mocked_projects = [
        {"name": "ProjA", "project_signature": "sig_a"},
        {"name": "ProjB", "project_signature": "sig_b"},
    ]

    with (
        patch("app.cli.override_rank_projects_cli.get_projects", return_value=mocked_projects),
        patch("app.cli.override_rank_projects_cli.set_project_ranks") as set_fn,
        patch("builtins.input", side_effect=["1", "1", "2", ""]),
    ):
        cli_mod.main()

    out = capsys.readouterr().out
    assert "That project is already ranked." in out
    set_fn.assert_called_once_with({"sig_a": 1, "sig_b": 2})
