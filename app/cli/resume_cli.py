import os
import requests
import urllib.parse
import tempfile


class ResumeCLI:
    def __init__(self):
        # Allow overriding via env; default to localhost
        self.API_URL = os.getenv("API_URL", "http://localhost:8000")

    def run(self):
        project_ids = self.select_projects()

        # Generate preview link (GET) instead of opening browser
        preview_url = self.build_preview_url(project_ids)
        print("\nOpen this link in your browser to preview the resume:\n")
        print(preview_url)


    def select_projects(self):
        projects = self.fetch_projects()

        print("Select projects to include:\n")

        for i, p in enumerate(projects, start=1):
            skills_preview = ", ".join(p.get("skills", [])[:3])
            print(
                f"{i}. {p['name']} ({p['id']})"
                + (f" — {skills_preview}" if skills_preview else "")
            )

        raw = input("\nEnter numbers (comma-separated): ")
        try:
            indices = [int(x.strip()) - 1 for x in raw.split(",") if x.strip()]
        except ValueError:
            print("Invalid input. Please enter numbers like: 1,2,3")
            return self.select_projects()

        valid_indices = [i for i in indices if 0 <= i < len(projects)]
        if not valid_indices:
            print("No valid selections. Try again.")
            return self.select_projects()

        return [projects[i]["id"] for i in valid_indices]

    def fetch_projects(self):
        try:
            resp = requests.get(f"{self.API_URL}/api/projects", timeout=15)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise SystemExit(
                f"Failed to fetch projects from {self.API_URL}/api/projects.\n"
                f"Start the server (docker compose up -d) or set API_URL.\n"
                f"Error: {e}"
            )

    def build_preview_url(self, project_ids):
        """Return a GET URL to preview resume in browser."""
        if not project_ids:
            return f"{self.API_URL}/resume"
        # Encode multiple project_ids as query parameters
        query = "&".join(f"project_ids={urllib.parse.quote(pid)}" for pid in project_ids)
        return f"{self.API_URL}/resume?{query}"


def main():
    ResumeCLI().run()


if __name__ == "__main__":
    main()
