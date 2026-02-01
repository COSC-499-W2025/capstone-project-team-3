"""
Pytest configuration for API route tests.
Configures anyio to only use asyncio backend (not trio).
"""
import pytest


@pytest.fixture(scope="session")
def anyio_backend():
    """Force all anyio tests to use asyncio backend only."""
    return "asyncio"
