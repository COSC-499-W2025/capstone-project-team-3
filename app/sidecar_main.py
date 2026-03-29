"""
Sidecar entrypoint for PyInstaller / Electron: API server only.

Avoid importing app.main so the interactive CLI and its dependency graph are not loaded at startup.
"""
from __future__ import annotations

import atexit
import os
import signal
import socket
import sys

import uvicorn

# NOTE: Do not import `app.api_app` or `init_db` at module load time. PyInstaller + FastAPI pull in a
# large import graph that can take minutes on cold start. Electron waits for SIDECAR_LISTENING on
# stdout before polling /health; those imports must run *after* that line.

_pdf_cache_clear_ran = False

# Electron parses this exact prefix on stdout (line-buffered / flushed) to learn the listen URL.
_SIDECAR_READY_PREFIX = "SIDECAR_LISTENING "


def _bind_probe(port: int) -> bool:
    """Return True if TCP port appears free on 0.0.0.0 (same bind uvicorn will use)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(("0.0.0.0", port))
        return True
    except OSError:
        return False
    finally:
        s.close()


def _scan_bounds() -> tuple[int, int]:
    """Inclusive port range for auto-pick. Override with SIDECAR_PORT_SCAN_LO / SIDECAR_PORT_SCAN_HI."""

    def _env_int(name: str, default: int) -> int:
        raw = os.environ.get(name, "").strip()
        return int(raw) if raw.isdigit() else default

    lo = _env_int("SIDECAR_PORT_SCAN_LO", 8000)
    hi = _env_int("SIDECAR_PORT_SCAN_HI", 8099)
    if lo > hi:
        lo, hi = hi, lo
    if not (1 <= lo <= 65535 and 1 <= hi <= 65535):
        print(f"[sidecar] invalid SIDECAR_PORT_SCAN_LO/HI range ({lo}-{hi})", file=sys.stderr)
        sys.exit(1)
    return lo, hi


def _resolve_listen_port() -> int:
    """
    Pick a port for the sidecar.
    - If SIDECAR_PORT is set, use only that port or exit.
    - Otherwise scan [SIDECAR_PORT_SCAN_LO, SIDECAR_PORT_SCAN_HI] (default 8000–8099) for the first free port.
    """
    raw = os.environ.get("SIDECAR_PORT", "").strip()
    if raw.isdigit():
        port = int(raw)
        if not (1 <= port <= 65535):
            print(f"[sidecar] invalid SIDECAR_PORT={raw!r}", file=sys.stderr)
            sys.exit(1)
        if not _bind_probe(port):
            print(f"[sidecar] SIDECAR_PORT={port} is already in use", file=sys.stderr)
            sys.exit(1)
        return port

    lo, hi = _scan_bounds()
    for port in range(lo, hi + 1):
        if _bind_probe(port):
            return port
    print(
        f"[sidecar] no free TCP port in range {lo}-{hi}. "
        f"Set SIDECAR_PORT to a specific free port or widen SIDECAR_PORT_SCAN_LO/HI.",
        file=sys.stderr,
    )
    sys.exit(1)


def _announce_listen_url(port: int) -> None:
    """Tell Electron which URL to poll; uvicorn is not accepting connections until imports + init_db finish."""
    url = f"http://127.0.0.1:{port}"
    print(f"{_SIDECAR_READY_PREFIX}{url}", flush=True)


def _maybe_clear_resume_pdf_cache() -> None:
    """Desktop Electron sets CLEAR_RESUME_PDF_CACHE_ON_EXIT=1 so PDFs are not kept after quit."""
    global _pdf_cache_clear_ran
    if _pdf_cache_clear_ran:
        return
    if os.environ.get("CLEAR_RESUME_PDF_CACHE_ON_EXIT", "").strip().lower() not in (
        "1",
        "true",
        "yes",
    ):
        return
    _pdf_cache_clear_ran = True
    try:
        from app.api.routes.resume import clear_resume_pdf_cache

        n = clear_resume_pdf_cache()
        if n:
            print(f"[sidecar] cleared {n} cached resume PDF(s)", file=sys.stderr)
    except Exception as exc:
        print(f"[sidecar] resume PDF cache clear failed: {exc}", file=sys.stderr)


def _register_pdf_cache_cleanup() -> None:
    atexit.register(_maybe_clear_resume_pdf_cache)

    def _on_signal(_signum, _frame) -> None:
        _maybe_clear_resume_pdf_cache()
        sys.exit(0)

    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            signal.signal(sig, _on_signal)
        except ValueError:
            pass


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
    _register_pdf_cache_cleanup()
    port = _resolve_listen_port()
    _announce_listen_url(port)

    from app.data.db import init_db
    from app.api_app import app

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
        port=port,
        log_level="critical",
        access_log=False,
    )
