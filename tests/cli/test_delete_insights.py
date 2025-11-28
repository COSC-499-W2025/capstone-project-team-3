from unittest.mock import patch
import app.cli.delete_insights as cli_mod


def test_delete_insights_cli_happy_path(capsys):
	"""Select project 1, confirm, type name+sig prefix, and delete succeeds."""

	# Single mocked project; signature prefix is 'abcd'
	mocked_projects = [
		{"name": "CliProj", "project_signature": "abcdef1234"},
	]

	# Inputs simulate: choose #1, answer yes, type "cliprojabcd" for final confirmation
	with (patch("app.cli.delete_insights.get_projects", return_value=mocked_projects) as _gp,
		 patch("app.cli.delete_insights.delete_project_by_signature", return_value=True) as del_fn,
		 patch("builtins.input", side_effect=["1", "yes", "cliprojabcd"])
    ):

		cli_mod.main()

	# Verify important output lines
	out = capsys.readouterr().out
	assert "Previously generated insights (projects):" in out
	assert "1. CliProj — signature: abcdef1234..." in out
	assert "Deleted insights for project 'CliProj'." in out

	# Ensure we deleted by exact signature, not by name
	del_fn.assert_called_once_with("abcdef1234")


def test_delete_insights_cli_cancel(capsys):
	"""User cancels at yes/no confirmation; no deletion call occurs."""

	mocked_projects = [
		{"name": "CliProj", "project_signature": "abcdef1234"},
	]

	# Inputs: choose #1, then say 'no' to confirmation
	with (patch("app.cli.delete_insights.get_projects", return_value=mocked_projects) as _gp,
		 patch("app.cli.delete_insights.delete_project_by_signature") as del_fn,
		 patch("builtins.input", side_effect=["1", "no"])
    ):

		cli_mod.main()

	out = capsys.readouterr().out
	assert "Deletion cancelled." in out
	del_fn.assert_not_called()


def test_delete_insights_cli_no_projects(capsys):
	"""No projects in DB prints a helpful message and exits."""

	# get_projects returns empty; input should not be called
	with (patch("app.cli.delete_insights.get_projects", return_value=[]),
		 patch("builtins.input") as input_fn
    ):
		cli_mod.main()

	out = capsys.readouterr().out
	assert "No projects found" in out
