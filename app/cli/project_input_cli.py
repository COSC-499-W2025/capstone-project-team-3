import argparse
from app.utils.scan_utils import scan_project_files

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
    # Add logic for other subcommands here...

if __name__ == "__main__":
    main()