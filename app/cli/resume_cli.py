import requests

class ResumeCLI:
    def __init__(self, api_base="http://localhost:8000"):
        self.api_base = api_base
        self.selected_project_ids: list[str] = []

    def fetch_projects(self):
        resp = requests.get(f"{self.api_base}/api/projects")
        resp.raise_for_status()
        return resp.json()

    def select_projects(self, projects):
        print("\nAvailable Projects:\n")

        for i, p in enumerate(projects, start=1):
            skills = ", ".join(p["skills"])
            print(f"{i}. {p['name']} [{skills}]")

        raw = input(
            "\nEnter project numbers separated by commas (e.g. 1,3): "
        )

        indices = [int(x.strip()) - 1 for x in raw.split(",")]
        return [projects[i]["id"] for i in indices]

    def generate_resume_preview(self):
        if not self.selected_project_ids:
            print("No projects selected.")
            return

        resp = requests.post(
            f"{self.api_base}/resume/generate",
            json={"project_ids": self.selected_project_ids},
        )
        resp.raise_for_status()

        print("\n=== Resume Preview (LaTeX) ===\n")
        print(resp.text[:2000])  # truncate for terminal

    def download_pdf(self, filename="resume.pdf"):
        if not self.selected_project_ids:
            print("No projects selected.")
            return

        resp = requests.post(
            f"{self.api_base}/resume/download-pdf",
            json={"project_ids": self.selected_project_ids},
        )
        resp.raise_for_status()

        with open(filename, "wb") as f:
            f.write(resp.content)

        print(f"PDF saved as {filename}")
        
    def run(self):
        projects = self.fetch_projects()
        self.select_projects(projects)

        self.generate_resume_preview()

        choice = input("\nDownload PDF? (y/n): ")
        if choice.lower() == "y":
            self.download_pdf()

def main():
    ResumeCLI().run()


if __name__ == "__main__":
    main()