class RootInputText:
    """
    Prompts and help text for asking the user to provide a project root
    (directory or .zip). Kept separate from consent text for easier PR review.
    """
    ROOT_INPUT_PROMPT = (
        "Enter the FULL project root path to analyze.\n"
        "Examples:\n"
        "  - ZIP file:  /Users/you/projects.zip\n\n"
        "Path> "
    )

    ROOT_INPUT_HELP = (
        "\n"
        "Please provide the absolute (full) path to a .zip file.\n"
        "Relative paths like './project' or '/Desktop' will not work."
    )

    INVALID_PATH_TEMPLATE = "❌ Invalid path: {reason}"