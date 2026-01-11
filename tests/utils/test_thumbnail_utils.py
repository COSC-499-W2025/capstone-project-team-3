"""
Unit tests for thumbnail_utils.py
Tests core thumbnail management functionality.
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from app.utils.thumbnail_utils import (
    validate_image_file,
    set_project_thumbnail,
    get_project_thumbnail
)


@pytest.fixture
def temp_image():
    """Create a temporary test image file."""
    temp_dir = tempfile.mkdtemp()
    image_path = Path(temp_dir) / "test_image.png"
    image_path.write_text("fake image content")
    yield str(image_path)
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_db_connection():
    """Mock database connection."""
    with patch('app.utils.thumbnail_utils.get_connection') as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.return_value.cursor.return_value = mock_cursor
        mock_conn.return_value.commit = MagicMock()
        mock_conn.return_value.close = MagicMock()
        yield mock_conn, mock_cursor


def test_validate_image_file_success(temp_image):
    """Test validation succeeds for valid image file."""
    result = validate_image_file(temp_image)
    assert result["status"] == "ok"
    assert "path" in result


def test_set_project_thumbnail_success(temp_image, mock_db_connection):
    """Test successfully setting a thumbnail."""
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.rowcount = 1
    
    result = set_project_thumbnail("test_sig_123", temp_image)
    
    assert result["status"] == "ok"
    assert "thumbnail_path" in result
    assert mock_cursor.execute.called
    assert mock_conn.return_value.commit.called


def test_get_project_thumbnail_exists(temp_image, mock_db_connection):
    """Test retrieving an existing thumbnail."""
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = (temp_image,)
    
    result = get_project_thumbnail("test_sig_123")
    
    assert result == temp_image
    assert mock_cursor.execute.called