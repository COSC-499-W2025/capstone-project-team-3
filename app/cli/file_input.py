import json
import requests
from app.utils.path_utils import validate_read_access
from app.utils.project_extractor import extract_and_list_projects
from pathlib import Path

# URLS
UPLOAD_PAGE_URL = "http://localhost:8000/upload-file"
RESOLVE_URL = "http://localhost:8000/api/resolve-upload"

def main(argv=None):
    print("📤 Please upload your ZIP file using your browser:")
    print(f"➡  {UPLOAD_PAGE_URL}")
    print("\nWaiting for upload...")

    upload_id = None
    exit_keywords = {"exit", "quit", "q"}

    # Ask user to type the upload ID from the success screen
    while not upload_id:
        upload_id = input("Enter Upload ID (shown after upload completes) or type 'q' to exit: ").strip()
        if upload_id.lower() in exit_keywords:
            print("👋 Exiting upload.")
            return {"status": "error", "reason": "user_exit"}

    print("⏳ Checking server...")

    # Keep asking for a valid upload id until resolved
    while True:
        resp = requests.get(f"{RESOLVE_URL}/{upload_id}").json()
        if resp.get("status") == "ok":
            zip_path = resp["path"]
            print(f"📦 File found at {zip_path} inside the container")
            break
        print("❌ Upload not detected. Enter correct Upload ID or type 'q' to exit.")
        upload_id = input("Upload ID: ").strip()
        if upload_id.lower() in exit_keywords:
            print("👋 Exiting upload.")
            return {"status": "error", "reason": "user_exit"}
        if not upload_id:
            continue

    
    access = validate_read_access(zip_path)
    if access["status"] != "ok":
        return access

    resolved = Path(access["path"])

    # Extract and list projects
    extract_res = extract_and_list_projects(str(resolved))

    if extract_res.get("status") != "ok":
        return {"status": "error", "reason": extract_res["reason"]}

    projects = extract_res.get("projects", [])
    if not projects:
        return {"status": "error", "reason": "No projects found"}

    result = {
        "status": "ok",
        "type": "zip",
        "path": str(resolved),
        "projects": projects,
        "count": len(projects),
    }

    return result