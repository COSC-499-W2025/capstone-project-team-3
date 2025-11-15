import argparse
import json
from pathlib import Path
from typing import Optional

from app.shared.text.root_input_text import RootInputText
from app.utils.path_utils import validate_read_access
from app.utils.project_extractor import extract_and_list_projects

def prompt_for_root() -> str:
    print(RootInputText.ROOT_INPUT_HELP)
    while True:
        root = input(RootInputText.ROOT_INPUT_PROMPT).strip()
        if root:  # Not empty
            return root
        print("❌ Path cannot be empty. Please enter a valid path.")

def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(prog="project-input-cli", description="Prompt for project root and validate it.")
    parser.add_argument("--root", "-r", help="Optional: provide root path non-interactively (dir or .zip)")
    ns = parser.parse_args(argv)

    root = ns.root
    if not root:
        root = prompt_for_root()

    try:
        access = validate_read_access(root)
    except ValueError as exc:
        print(json.dumps({"status": "error", "reason": str(exc)}))
        return 1

    if access.get("status") != "ok":
        print(json.dumps({"status": "error", "reason": access.get("reason", "access denied")}))
        return 1

    resolved = Path(access["path"])
    result = {
        "status": "ok",
        "type": "zip" if resolved.suffix.lower() == ".zip" else "dir",
        "path": str(resolved),
    }

    if resolved.suffix.lower() == ".zip":
        extract_res = extract_and_list_projects(str(resolved))
        if extract_res.get("status") != "ok":
            print(json.dumps({"status": "error", "reason": extract_res.get("reason", "zip extraction failed")}))
            return 1
        
        # Check if any projects were found
        projects = extract_res.get("projects", [])
        if not projects:
            print(json.dumps({"status": "error", "reason": "no identifiable projects found in ZIP archive"}))
            return 1
        
        result.update({
            "extracted_dir": extract_res.get("extracted_dir"),
            "projects": projects,
            "count": len(projects),
        })
    #TODO: Call function to extract individual project path and store into projects attribute in results
    print(json.dumps(result, indent=2))
    return result

if __name__ == "__main__":
    raise SystemExit(main())