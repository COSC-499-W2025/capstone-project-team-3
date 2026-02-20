import io
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from app.api.routes.post_thumbnail import router, update_project_thumbnail


@pytest.fixture
def dummy_image():
    """Create a simple PNG image in memory."""
    return io.BytesIO(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0bIDATx\x9cc``\x00\x00\x00\x02\x00\x01\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82")


def test_update_project_thumbnail_function(monkeypatch):
    """Test updating thumbnail path in database."""
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    
    monkeypatch.setattr("app.api.routes.post_thumbnail.get_connection", lambda: mock_conn)
    
    update_project_thumbnail("test_sig", "data/thumbnails/test.png")
    
    mock_cursor.execute.assert_called_once_with(
        "UPDATE PROJECT SET thumbnail_path = ? WHERE project_signature = ?",
        ("data/thumbnails/test.png", "test_sig")
    )
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("app.api.routes.post_thumbnail.update_project_thumbnail")
@patch("builtins.open", create=True)
@pytest.mark.anyio
async def test_upload_thumbnail_success(mock_open, mock_update, dummy_image):
    """Test successful thumbnail upload with correct path format."""
    from fastapi import UploadFile
    
    mock_file = Mock(spec=UploadFile)
    mock_file.content_type = "image/png"
    mock_file.filename = "test.png"
    
    async def async_read():
        return dummy_image.getvalue()
    mock_file.read = async_read
    
    from app.api.routes.post_thumbnail import set_project_thumbnail
    result = await set_project_thumbnail(project_id="test_project", image=mock_file)
    
    assert result["success"] is True
    assert result["thumbnail_path"].startswith("data/thumbnails/test_project")
    assert result["thumbnail_url"] == "/api/portfolio/project/thumbnail/test_project"
    mock_update.assert_called_once()


@pytest.mark.anyio
async def test_upload_thumbnail_invalid_type():
    """Test rejection of non-image files."""
    from fastapi import HTTPException
    from app.api.routes.post_thumbnail import set_project_thumbnail
    
    mock_file = Mock()
    mock_file.content_type = "text/plain"
    mock_file.filename = "test.txt"
    
    with pytest.raises(HTTPException) as exc_info:
        await set_project_thumbnail(project_id="test_project", image=mock_file)
    
    assert exc_info.value.status_code == 400
    assert "Unsupported file type" in exc_info.value.detail


@patch("app.api.routes.post_thumbnail.update_project_thumbnail")
@patch("builtins.open", create=True)
@pytest.mark.anyio
async def test_upload_svg_thumbnail(mock_open, mock_update):
    """Test successful SVG thumbnail upload."""
    from fastapi import UploadFile
    
    mock_file = Mock(spec=UploadFile)
    mock_file.content_type = "image/svg+xml"
    mock_file.filename = "test.svg"
    
    async def async_read():
        return b'<svg xmlns="http://www.w3.org/2000/svg"><circle r="10"/></svg>'
    mock_file.read = async_read
    
    from app.api.routes.post_thumbnail import set_project_thumbnail
    result = await set_project_thumbnail(project_id="test_project", image=mock_file)
    
    assert result["success"] is True
    assert result["thumbnail_path"].endswith(".svg")
    assert result["thumbnail_url"] == "/api/portfolio/project/thumbnail/test_project"


@patch("app.api.routes.post_thumbnail.update_project_thumbnail")
@patch("builtins.open", create=True)
@pytest.mark.anyio
async def test_upload_gif_thumbnail(mock_open, mock_update):
    """Test successful GIF thumbnail upload."""
    from fastapi import UploadFile
    
    mock_file = Mock(spec=UploadFile)
    mock_file.content_type = "image/gif"
    mock_file.filename = "test.gif"
    
    async def async_read():
        return b'GIF89a\x01\x00\x01\x00\x00\x00\x00;'
    mock_file.read = async_read
    
    from app.api.routes.post_thumbnail import set_project_thumbnail
    result = await set_project_thumbnail(project_id="test_project", image=mock_file)
    
    assert result["success"] is True
    assert result["thumbnail_path"].endswith(".gif")
    assert result["thumbnail_url"] == "/api/portfolio/project/thumbnail/test_project"


@pytest.mark.anyio
async def test_get_thumbnail_with_cache_headers():
    """Test that GET endpoint includes proper cache-control headers."""
    from app.api.routes.post_thumbnail import get_project_thumbnail
    from pathlib import Path
    
    # Create a mock that properly chains the Path and file operations
    with patch("app.api.routes.post_thumbnail.get_connection") as mock_get_conn, \
         patch("app.api.routes.post_thumbnail.FileResponse") as mock_file_response:
        
        # Setup database mock
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = ("data/thumbnails/test.png",)
        mock_get_conn.return_value = mock_conn
        
        # Setup Path mock to say file exists
        with patch.object(Path, 'exists', return_value=True):
            await get_project_thumbnail("test_project")
            
            # Verify FileResponse was called with cache headers
            mock_file_response.assert_called_once()
            call_kwargs = mock_file_response.call_args[1]
            
            assert "headers" in call_kwargs
            headers = call_kwargs["headers"]
            assert headers["Cache-Control"] == "no-cache, no-store, must-revalidate"
            assert headers["Pragma"] == "no-cache"
            assert headers["Expires"] == "0"


@pytest.mark.anyio
async def test_get_thumbnail_not_found(monkeypatch):
    """Test 404 when thumbnail doesn't exist."""
    from fastapi import HTTPException
    from app.api.routes.post_thumbnail import get_project_thumbnail
    
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    
    monkeypatch.setattr("app.api.routes.post_thumbnail.get_connection", lambda: mock_conn)
    
    with pytest.raises(HTTPException) as exc_info:
        await get_project_thumbnail("nonexistent_project")
    
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail.lower()
