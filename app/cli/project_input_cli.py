import argparse
from pathlib import Path
from app.utils.scan_utils import (
    scan_project_files,
    get_project_signature,
    extract_file_metadata,
    extract_file_signature,
    store_project_in_db,
    project_signature_exists,
    calculate_project_score
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

    # Add other subcommands for your teammates here...

    args = parser.parse_args(argv)

    if args.command == "scan":
        if not has_consent():
            print("User consent not found. Please run the consent CLI first.")
            return
        print("Consent verified. Scanning files...")
        files = scan_project_files(args.root, exclude_patterns=args.exclude)
        print(f"Scanned files (excluding patterns {args.exclude}):")
        for f in files:
            print(f)
        metadata_list = [extract_file_metadata(f) for f in files]
        file_signatures = [extract_file_signature(f, args.root) for f in files]
        signature = get_project_signature(file_signatures)
        size_bytes = sum(m["size_bytes"] for m in metadata_list)
        name = Path(args.root).name
        path = str(Path(args.root).resolve())
        
        score = calculate_project_score(file_signatures)
        print(f"Project analysis score: {score}% of files already analyzed.")
        if project_signature_exists(signature):
            print("Project already analyzed. Skipping analysis.")
            return 0
        else:
            store_project_in_db(signature, name, path, file_signatures, size_bytes)
            print("Stored project and file signatures in DB. Proceeding with analysis.")
            return 1
    
    # Add logic for other subcommands here...

if __name__ == "__main__":
    main()