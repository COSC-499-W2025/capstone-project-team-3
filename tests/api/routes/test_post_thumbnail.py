import io
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def dummy_image():
    # Create a simple PNG image in memory
    return io.BytesIO(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0bIDATx\x9cc``\x00\x00\x00\x02\x00\x01\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82")


def test_post_thumbnail_success(dummy_image, monkeypatch):
    # Patch update_project_thumbnail to avoid DB side effects
    def mock_update_project_thumbnail(project_id, image_path):
        assert project_id == "test_project"
        assert image_path.startswith("static/thumbnails/test_project_")
    monkeypatch.setattr("app.api.routes.post_thumbnail.update_project_thumbnail", mock_update_project_thumbnail)

    response = client.post(
        "/portfolio/project/thumbnail",
        files={"image": ("test.png", dummy_image.read(), "image/png")},
        data={"project_id": "test_project"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["thumbnail_path"].startswith("static/thumbnails/test_project_")


def test_post_thumbnail_invalid_file_type():
    response = client.post(
        "/portfolio/project/thumbnail",
        files={"image": ("test.txt", b"not an image", "text/plain")},
        data={"project_id": "test_project"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "File must be an image."
