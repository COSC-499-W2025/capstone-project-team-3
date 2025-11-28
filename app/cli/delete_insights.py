from app.utils.delete_insights_utils import (
	get_projects,
	delete_project_by_signature,
)


def main():
	projects = get_projects()
 
    # If no projects found, inform user
	if not projects:
		print("No projects found")
		return

    # Show user a number, project name and first 12 characters of the project signature
	print("Previously generated insights (projects):")
	for idx, p in enumerate(projects, start=1):
		sig = p["project_signature"] or ""
		print(f"  {idx}. {p['name']} — signature: {sig[:12]}...")

	while True:
        # Prompt user to enter number of project they want to delete and make sure it is verifyable
		choice = input("Enter the number of the project to delete: ").strip()
		if not choice.isdigit():
			print("Please enter a valid number.")
			continue
		idx = int(choice)
		if idx < 1 or idx > len(projects):
			print("Number out of range. Try again.")
			continue
		selected = projects[idx - 1]
		break

    # Confirm user wants to delete the file with a simple yes/no
	confirm = input(
		f"Are you sure you want to delete '{selected['name']}'? (yes/no): "
	).strip().lower()
	if confirm not in ("y", "yes"):
		print("Deletion cancelled.")
		return

    # Before deletion, confirm again by telling the user to enter name of project+ first 4 letters of project signature
	expected_name = selected["name"].lower()
	sig_prefix = (selected["project_signature"] or "")[:4]
 
	typed = input(f'Type "{expected_name}{sig_prefix}" to confirm: ').strip().lower()
	if typed != f"{expected_name}{sig_prefix}":
		print("Confirmation did not match. Deletion cancelled.")
		return

    # Check if deletion happened and print status to the user
	if delete_project_by_signature(selected["project_signature"]):
		print(f"Deleted insights for project '{selected['name']}'.")
	else:
		print(f"Project '{selected['name']}' not found or already deleted.")


if __name__ == "__main__":
	main()
