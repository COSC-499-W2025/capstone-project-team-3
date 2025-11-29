import argparse
import json
from pathlib import Path
from typing import Optional

from app.shared.text.root_input_text import RootInputText
from app.utils.path_utils import validate_read_access
from app.utils.project_extractor import extract_and_list_projects

def prompt_for_root() -> str:
    print(RootInputText.ROOT_INPUT_HELP)
    print("📦 Note: Only ZIP files are accepted.")
    while True:
        root = input(RootInputText.ROOT_INPUT_PROMPT).strip()
        if root.lower() in ['exit', 'quit', 'q']:
            return None
        if root:  # Not empty
            return root
        print("❌ Path cannot be empty. Please enter a valid ZIP file path or 'exit' to quit.")

def main(argv: Optional[list] = None):
    parser = argparse.ArgumentParser(prog="project-input-cli", description="Prompt for project root ZIP file and validate it.")
    parser.add_argument("--root", "-r", help="Optional: provide ZIP file path non-interactively")
    ns = parser.parse_args(argv)

    root = ns.root
    if not root:
        root = prompt_for_root()
        if root is None:  # User typed 'exit'
            return {"status": "error", "reason": "user_exit"}

    try:
        access = validate_read_access(root)
    except ValueError as exc:
        print(json.dumps({"status": "error", "reason": str(exc)}))
        return {"status": "error", "reason": str(exc)}

    if access.get("status") != "ok":
        print(json.dumps({"status": "error", "reason": access.get("reason", "access denied")}))
        return {"status": "error", "reason": access.get("reason", "access denied")}

    resolved = Path(access["path"])
    
    # Only accept ZIP files
    if resolved.suffix.lower() != ".zip":
        error_msg = "Only ZIP files are accepted. Please provide a .zip file."
        print(json.dumps({"status": "error", "reason": error_msg}))
        return {"status": "error", "reason": error_msg}
    
    result = {
        "status": "ok",
        "type": "zip",
        "path": str(resolved),
    }

    extract_res = extract_and_list_projects(str(resolved))
    if extract_res.get("status") != "ok":
        print(json.dumps({"status": "error", "reason": extract_res.get("reason", "zip extraction failed")}))
        return {"status": "error", "reason": extract_res.get("reason", "zip extraction failed")}
    
    # Check if any projects were found
    projects = extract_res.get("projects", [])
    if not projects:
        print(json.dumps({"status": "error", "reason": "no identifiable projects found in ZIP archive"}))
        return {"status": "error", "reason": "no identifiable projects found in ZIP archive"}
    
    result.update({
        "extracted_dir": extract_res.get("extracted_dir"),
        "projects": projects,
        "count": len(projects),
    })
    
    print(json.dumps(result, indent=2))
    return result

if __name__ == "__main__":
    raise SystemExit(main())