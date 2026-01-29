import unittest
from unittest.mock import patch, MagicMock
import os
import requests
from app.cli.resume_cli import ResumeCLI  # assuming your class is in resume_cli.py


class TestResumeCLI(unittest.TestCase):
    """Unit tests for the ResumeCLI class."""

    @patch.dict(os.environ, {"API_URL": "http://testserver:1234"})
    def test_api_url_override(self):
        """Ensure API_URL is overridden by environment variable."""
        cli = ResumeCLI()
        self.assertEqual(cli.API_URL, "http://testserver:1234")

    @patch.dict(os.environ, {}, clear=True)
    def test_api_url_default(self):
        """Ensure API_URL defaults to localhost if env not set."""
        cli = ResumeCLI()
        self.assertEqual(cli.API_URL, "http://localhost:8000")

    @patch("requests.get")
    def test_fetch_projects_success(self, mock_get):
        """Ensure fetch_projects returns JSON on successful GET."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = [{"id": "1", "name": "Proj"}]
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        cli = ResumeCLI()
        projects = cli.fetch_projects()
        self.assertEqual(projects, [{"id": "1", "name": "Proj"}])
        mock_get.assert_called_once_with(f"{cli.API_URL}/api/projects", timeout=15)

    @patch("requests.get", side_effect=requests.exceptions.ConnectionError("fail"))
    def test_fetch_projects_failure(self, mock_get):
        """Ensure fetch_projects raises SystemExit on request failure."""
        cli = ResumeCLI()
        with self.assertRaises(SystemExit) as cm:
            cli.fetch_projects()
        self.assertIn("Failed to fetch projects", str(cm.exception))

    def test_build_preview_url_empty(self):
        """Ensure build_preview_url returns base URL when no projects given."""
        cli = ResumeCLI()
        url = cli.build_preview_url([])
        self.assertEqual(url, f"{cli.API_URL}/resume")

    def test_build_preview_url_multiple_projects(self):
        """Ensure build_preview_url encodes multiple project IDs correctly."""
        cli = ResumeCLI()
        project_ids = ["abc", "def 123"]
        url = cli.build_preview_url(project_ids)
        self.assertIn("project_ids=abc", url)
        self.assertIn("project_ids=def%20123", url)
        self.assertTrue(url.startswith(f"{cli.API_URL}/resume?"))

    @patch("builtins.input", return_value="1,2")
    @patch.object(ResumeCLI, "fetch_projects", return_value=[
        {"id": "p1", "name": "Project 1", "skills": ["a", "b", "c"]},
        {"id": "p2", "name": "Project 2", "skills": ["x", "y"]}
    ])
    def test_select_projects_valid_input(self, mock_fetch, mock_input):
        """Ensure select_projects returns correct project IDs for valid input."""
        cli = ResumeCLI()
        selected = cli.select_projects()
        self.assertEqual(selected, ["p1", "p2"])

    @patch("builtins.input", side_effect=["invalid", "1"])
    @patch.object(ResumeCLI, "fetch_projects", return_value=[
        {"id": "p1", "name": "Project 1", "skills": []}
    ])
    def test_select_projects_invalid_then_valid(self, mock_fetch, mock_input):
        """Ensure select_projects reprompts after invalid input."""
        cli = ResumeCLI()
        selected = cli.select_projects()
        self.assertEqual(selected, ["p1"])

if __name__ == "__main__":
    unittest.main()
