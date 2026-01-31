import io
import pytest
from unittest.mock import Mock, patch
from app.api.routes.post_thumbnail import router, update_project_thumbnail


@pytest.fixture
def dummy_image():
    # Create a simple PNG image in memory
    return io.BytesIO(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0bIDATx\x9cc``\x00\x00\x00\x02\x00\x01\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82")


def test_update_project_thumbnail_function(monkeypatch):
    """Test the update_project_thumbnail function directly."""
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    
    monkeypatch.setattr("app.api.routes.post_thumbnail.get_connection", lambda: mock_conn)
    
    update_project_thumbnail("test_sig", "test_path.png")
    
    mock_cursor.execute.assert_called_once_with(
        "UPDATE PROJECT SET thumbnail_path = ? WHERE project_signature = ?",
        ("test_path.png", "test_sig")
    )
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("app.api.routes.post_thumbnail.update_project_thumbnail")
@patch("builtins.open", create=True)
@pytest.mark.anyio
async def test_set_project_thumbnail_success(mock_open, mock_update, dummy_image):
    """Test successful thumbnail upload."""
    from fastapi import UploadFile
    from io import BytesIO
    
    # Create a mock UploadFile
    mock_file = Mock(spec=UploadFile)
    mock_file.content_type = "image/png"
    mock_file.filename = "test.png"
    # Make read() async
    async def async_read():
        return dummy_image.getvalue()
    mock_file.read = async_read
    
    # Call the endpoint function directly
    from app.api.routes.post_thumbnail import set_project_thumbnail
    result = await set_project_thumbnail(project_id="test_project", image=mock_file)
    
    assert result["success"] is True
    assert result["thumbnail_path"].startswith("static/thumbnails/test_project_")
    mock_update.assert_called_once()


@pytest.mark.anyio
async def test_set_project_thumbnail_invalid_type():
    """Test rejection of non-image files."""
    from fastapi import UploadFile, HTTPException
    from app.api.routes.post_thumbnail import set_project_thumbnail
    
    # Create a mock non-image file
    mock_file = Mock(spec=UploadFile)
    mock_file.content_type = "text/plain"
    mock_file.filename = "test.txt"
    
    # Should raise HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await set_project_thumbnail(project_id="test_project", image=mock_file)
    
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "File must be an image."
