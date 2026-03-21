# Create a new file for environment utilities

import os
import re
from pathlib import Path

from platformdirs import user_config_dir

# Matches a .env assignment line for GEMINI_API_KEY only (not GEMINI_API_KEY_*).
_GEMINI_API_KEY_ASSIGNMENT = re.compile(r"^\s*GEMINI_API_KEY\s*=")

# Directory for gemini.env (UI-saved key). In Docker, mount this path and set the var in compose.
_CONFIG_DIR_ENV = "PROJECT_INSIGHTS_CONFIG_DIR"


def get_gemini_key_store_path() -> Path:
    """Path to the file where the UI/API persists GEMINI_API_KEY (not the project .env)."""
    override = os.environ.get(_CONFIG_DIR_ENV)
    if override:
        return Path(override) / "gemini.env"
    return Path(user_config_dir("ProjectInsights", appauthor=False)) / "gemini.env"


def validate_gemini_api_key_value(api_key: str | None) -> tuple[bool, str]:
    """
    Validate a Gemini API key string (same rules as runtime env check).
    Returns (is_valid, message code).
    """
    if api_key is None:
        return False, "missing"
    if api_key.strip() == "":
        return False, "empty"
    if not api_key.startswith(("AIza", "ya29.")):
        return False, "invalid_format"
    return True, "valid"


def check_gemini_api_key() -> tuple[bool, str]:
    """
    Check if GEMINI_API_KEY is available and valid.
    Returns (is_valid, message)
    """
    return validate_gemini_api_key_value(os.getenv("GEMINI_API_KEY"))


def _parse_gemini_key_from_assignment_line(line: str) -> str | None:
    m = re.match(r"^\s*GEMINI_API_KEY\s*=\s*(.*)$", line.rstrip("\r\n"))
    if not m:
        return None
    v = m.group(1).strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1]
    return v


def read_persisted_gemini_api_key() -> str | None:
    """Read GEMINI_API_KEY from the UI key store file (gemini.env), if present."""
    path = get_gemini_key_store_path()
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    for raw in text.splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        if _GEMINI_API_KEY_ASSIGNMENT.match(raw):
            return _parse_gemini_key_from_assignment_line(raw)
    return None


def persist_gemini_api_key(api_key: str) -> None:
    """Write GEMINI_API_KEY to the key store file and update os.environ."""
    ok, _ = validate_gemini_api_key_value(api_key)
    if not ok:
        raise ValueError("Invalid Gemini API key format")
    path = get_gemini_key_store_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# Managed by Project Insights — do not commit\n"
        f"GEMINI_API_KEY={api_key.strip()}\n",
        encoding="utf-8",
    )
    os.environ["GEMINI_API_KEY"] = api_key.strip()


def clear_persisted_gemini_api_key() -> None:
    """Remove the key store file and unset GEMINI_API_KEY in this process."""
    path = get_gemini_key_store_path()
    if path.is_file():
        path.unlink()
    os.environ.pop("GEMINI_API_KEY", None)


def load_gemini_key_from_store_into_environ() -> None:
    """
    After load_dotenv(), apply the UI-saved key if gemini.env exists.

    If the store file has a key, it overrides GEMINI_API_KEY from project .env or the shell
    so the in-app Save remains authoritative after first use.
    """
    key = read_persisted_gemini_api_key()
    if key:
        os.environ["GEMINI_API_KEY"] = key


def get_env_file_path() -> Path:
    """Get the expected project .env path (optional; for CLI / dev templates)."""
    return Path.cwd() / ".env"


def create_env_template():
    """Create a template .env file with instructions."""
    env_path = get_env_file_path()
    template = """# Project Insights Environment Variables
# 
# Get your Gemini API key from: https://aistudio.google.com/app/apikey
# 
GEMINI_API_KEY=your_api_key_here

# SSL Configuration (Development Only)
# Uncomment if you encounter SSL certificate errors with the Canadian institutions API
# This should not be enabled in production
# DISABLE_SSL_VERIFY=true

# Other optional variables
# PROMPT_ROOT=1
"""

    if not env_path.exists():
        env_path.write_text(template)
        return True
    return False
