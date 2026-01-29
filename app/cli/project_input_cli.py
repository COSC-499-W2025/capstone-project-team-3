import argparse
from pathlib import Path
from app.utils.scan_utils import (
    run_scan_flow
)

def has_consent():
    # TODO: Replace with ConsentManager once PR is merged
    # Simulate consent always granted for now
    return True

def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="project-input-cli",
        description="CLI for Project Input & Initialization"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Scan subcommand
    scan_parser = subparsers.add_parser("scan", help="Scan files in a project folder")
    scan_parser.add_argument("--root", type=str, required=True, help="Root directory to scan")
    scan_parser.add_argument("--exclude", type=str, nargs="*", default=[], help="Additional file patterns to exclude (e.g., *.pdf *.docx)")
    scan_parser.add_argument("--similarity-threshold", type=float, default=70.0, help="Similarity threshold for project matching (default: 70.0)")

    # Add other subcommands for your teammates here...

    args = parser.parse_args(argv)

    if args.command == "scan":
        if not has_consent():
            print("User consent not found. Please run the consent CLI first.")
            return
        print("Consent verified. Scanning files...")
        
        # Use the updated scan flow with similarity detection
        result = run_scan_flow(args.root, exclude=args.exclude, similarity_threshold=args.similarity_threshold)
        
        if result["skip_analysis"]:
            if result["reason"] == "no_files":
                print("No files found to scan in the specified directory. Skipping analysis.")
            elif result["reason"] == "already_analyzed":
                print("Project already analyzed. Skipping analysis.")
            return 0
        elif result["reason"] == "updated_existing":
            print(f"Updated existing project '{result['updated_project']}' with new files.")
            return 1
        else:
            print("Stored new project and file signatures in DB. Proceeding with analysis.")
            return 1
    
    # Add logic for other subcommands here...

if __name__ == "__main__":
    main()