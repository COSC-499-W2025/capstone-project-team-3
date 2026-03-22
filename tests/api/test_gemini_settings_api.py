import os

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes.gemini_settings import router


def _client_with_env(tmp_path, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("PROJECT_INSIGHTS_CONFIG_DIR", str(tmp_path))
    app = FastAPI()
    app.include_router(router, prefix="/api")
    return TestClient(app)


def test_status_not_configured(tmp_path, monkeypatch):
    client = _client_with_env(tmp_path, monkeypatch)
    r = client.get("/api/gemini-key/status")
    assert r.status_code == 200
    data = r.json()
    assert data["configured"] is False
    assert data["valid"] is False
    assert data["masked_suffix"] is None


def test_post_invalid_key(tmp_path, monkeypatch):
    client = _client_with_env(tmp_path, monkeypatch)
    r = client.post("/api/gemini-key", json={"api_key": "not-a-valid-key"})
    assert r.status_code == 400


def test_post_save_and_status(tmp_path, monkeypatch):
    client = _client_with_env(tmp_path, monkeypatch)
    key = "AIzaSyDummyKeyForTestingOnly1234567890"
    r = client.post("/api/gemini-key", json={"api_key": key})
    assert r.status_code == 200
    assert r.json()["ok"] is True

    r = client.get("/api/gemini-key/status")
    assert r.status_code == 200
    data = r.json()
    assert data["configured"] is True
    assert data["valid"] is True
    assert data["masked_suffix"] == "…7890"

    store = tmp_path / "gemini.env"
    assert store.is_file()
    assert "GEMINI_API_KEY=" in store.read_text()
    assert key in store.read_text()


def test_delete_clears_file_and_env(tmp_path, monkeypatch):
    monkeypatch.setenv("PROJECT_INSIGHTS_CONFIG_DIR", str(tmp_path))
    key = "AIzaSyAnotherDummyKeyForTest0000000000"
    monkeypatch.setenv("GEMINI_API_KEY", key)

    app = FastAPI()
    app.include_router(router, prefix="/api")
    client = TestClient(app)

    client.post("/api/gemini-key", json={"api_key": key})
    assert (tmp_path / "gemini.env").is_file()

    r = client.delete("/api/gemini-key")
    assert r.status_code == 200
    assert not (tmp_path / "gemini.env").is_file()
    assert os.environ.get("GEMINI_API_KEY") is None
