from app.utils.delete_insights_utils import get_projects
from app.utils.rank_override_utils import set_project_ranks

def _choose_project(projects, prompt):
    while True:
        choice = input(prompt).strip()
        if choice == "":
            return None
        if not choice.isdigit():
            print("Please enter a valid number or press Enter to skip.")
            continue
        idx = int(choice)
        if idx < 1 or idx > len(projects):
            print("Number out of range. Try again.")
            continue
        return projects[idx - 1]

def main():
    projects = get_projects()
    if not projects:
        print("No projects found.")
        return

    print("Projects:")
    for idx, p in enumerate(projects, start=1):
        sig = p["project_signature"] or ""
        print(f"  {idx}. {p['name']} — signature: {sig[:12]}...")

    # Pick ranks 1-3; enforce uniqueness
    selected = {}
    used = set()

    for rank in (1, 2, 3):
        while True:
            proj = _choose_project(projects, f"Select project for rank {rank} (or press Enter to skip): ")
            if proj is None:
                break
            sig = proj["project_signature"]
            if sig in used:
                print("That project is already ranked. Pick a different one.")
                continue
            selected[sig] = rank
            used.add(sig)
            break

    if not selected:
        print("No ranks updated.")
        return

    set_project_ranks(selected)
    print("✅ Project ranks updated.")
