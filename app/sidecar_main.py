"""
Sidecar entrypoint for PyInstaller / Electron: API server only.

Avoid importing app.main so the interactive CLI and its dependency graph are not loaded at startup.
"""
from __future__ import annotations

import os

from app.data.db import init_db
from app.api_app import app
import uvicorn


def _run_runtime_diagnostics() -> None:
    """
    Optional dependency checks for frozen sidecar debugging.
    Enable with SIDECAR_DIAGNOSTICS=1.
    """
    checks: list[tuple[str, bool, str]] = []

    # 1) pygount import
    try:
        import pygount  # noqa: F401

        checks.append(("pygount", True, "import ok"))
    except Exception as exc:
        checks.append(("pygount", False, f"import failed: {exc}"))

    # 2) spaCy + model load (uses the same lazy loader as non-code analysis)
    try:
        from app.utils.non_code_analysis.non_3rd_party_analysis import get_nlp

        _ = get_nlp()
        checks.append(("spacy/en_core_web_sm", True, "model load ok"))
    except Exception as exc:
        checks.append(("spacy/en_core_web_sm", False, f"model load failed: {exc}"))

    # 3) KeyBERT model init (heavy, but this is opt-in diagnostics mode)
    try:
        from app.utils.non_code_analysis.non_3rd_party_analysis import get_keybert_model

        _ = get_keybert_model()
        checks.append(("keybert", True, "model init ok"))
    except Exception as exc:
        checks.append(("keybert", False, f"model init failed: {exc}"))

    print("\n[sidecar] runtime diagnostics")
    for name, ok, msg in checks:
        status = "OK" if ok else "FAIL"
        print(f"[sidecar] {status:>4}  {name}: {msg}")
    print("[sidecar] diagnostics complete\n")


if __name__ == "__main__":
    init_db()
    if os.environ.get("SIDECAR_DIAGNOSTICS", "0").strip().lower() in (
        "1",
        "true",
        "yes",
    ):
        _run_runtime_diagnostics()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="critical",
        access_log=False,
    )
