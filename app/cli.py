"""
Command-Line Interface (CLI) entry point for the project.
"""

import argparse

def main(argv=None):
    """
    Args:
        argv (list[str] or None): a list of command-line arguments to parse.
            - If None → argparse reads directly from sys.argv (normal usage).
            - If a list → tests can supply their own args to isolate from pytest's args.
    When pytest runs with flags like "-v", those flags can confuse argparse.
    By allowing argv to be passed in, we can test the CLI without argparse
    accidentally reading pytest’s own flags.
    """
    # Create a command-line parser object
    parser = argparse.ArgumentParser(
        prog="capstone-cli",
        description="CLI for the Productivity Analyzer (Milestone 1 setup)"
    )

    # Adds a simple --version flag
    parser.add_argument(
        "--version",
        action="version",
        version="Capstone CLI 0.1.0"
    )

    # Parse the arguments.
    # Using argv (passed from tests) keeps pytest's flags from leaking in.
    _ = parser.parse_args(argv)

    # The only behavior for now — print confirmation message.
    # This placeholder ensures the CLI wiring works and can be expanded later.
    print("CLI started. Future commands will go here.")

# If this script is executed directly (not imported),
# run the main() function with no args, i.e., use sys.argv by default.
if __name__ == "__main__":
    main()
