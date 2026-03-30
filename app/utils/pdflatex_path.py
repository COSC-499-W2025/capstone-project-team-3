"""Resolve the pdflatex binary for resume/cover-letter PDF export."""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

# Optional override: full path to pdflatex (desktop installers / CI).
_ENV_PDFLATEX = "PDFLATEX_PATH"


def resolve_pdflatex_executable() -> str | None:
    """
    Return a path to pdflatex, or None if not found.

    Order: PDFLATEX_PATH env, PATH (shutil.which), then macOS BasicTeX/MacTeX default location.
    Electron on macOS often starts with a minimal PATH, so the /Library/TeX/texbin fallback matters.
    """
    override = os.environ.get(_ENV_PDFLATEX, "").strip()
    if override:
        p = Path(override)
        if p.is_file():
            return str(p)
        if shutil.which(override):
            return shutil.which(override)

    found = shutil.which("pdflatex")
    if found:
        return found

    if sys.platform == "darwin":
        mac = Path("/Library/TeX/texbin/pdflatex")
        if mac.is_file():
            return str(mac)

    return None
