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
    get_project_thumbnail,
    remove_project_thumbnail
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
def temp_thumbnail_dir():
    """Create temporary thumbnail directory."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_db():
    """Mock database connection."""
    with patch('app.utils.thumbnail_utils.get_connection') as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.return_value.cursor.return_value = mock_cursor
        mock_conn.return_value.commit = MagicMock()
        mock_conn.return_value.close = MagicMock()
        yield mock_conn, mock_cursor


def test_validate_image_file_success(temp_image):
    """Test validation succeeds for valid image."""
    result = validate_image_file(temp_image)
    assert result["status"] == "ok"


def test_validate_image_file_invalid():
    """Test validation fails for non-existent file."""
    result = validate_image_file("/fake/path.png")
    assert result["status"] == "error"


def test_set_thumbnail_stores_relative_path(temp_image, mock_db, temp_thumbnail_dir):
    """Test that relative path is stored in DB."""
    mock_conn, mock_cursor = mock_db
    mock_cursor.rowcount = 1
    
    with patch('app.utils.thumbnail_utils.THUMBNAIL_DIR', temp_thumbnail_dir):
        result = set_project_thumbnail("sig123", temp_image)
    
    assert result["status"] == "ok"
    assert "data/thumbnails/" in result["thumbnail_path"]
    assert not result["thumbnail_path"].startswith("/")


def test_set_thumbnail_cleans_up_on_db_failure(temp_image, mock_db, temp_thumbnail_dir):
    """Test thumbnail deleted if DB update fails."""
    mock_conn, mock_cursor = mock_db
    mock_cursor.execute.side_effect = Exception("DB error")
    
    with patch('app.utils.thumbnail_utils.THUMBNAIL_DIR', temp_thumbnail_dir):
        result = set_project_thumbnail("sig123", temp_image)
    
    assert result["status"] == "error"
    assert "database" in result["reason"].lower()
    # Verify no files left in thumbnail dir
    assert len(list(temp_thumbnail_dir.glob("sig123.*"))) == 0


def test_get_thumbnail_converts_relative_to_absolute(mock_db, temp_thumbnail_dir):
    """Test relative path converted to absolute."""
    mock_conn, mock_cursor = mock_db
    test_file = temp_thumbnail_dir / "sig123.png"
    test_file.write_text("test")
    
    mock_cursor.fetchone.return_value = ("data/thumbnails/sig123.png",)
    
    with patch('app.utils.thumbnail_utils.THUMBNAIL_DIR', temp_thumbnail_dir):
        result = get_project_thumbnail("sig123")
    
    assert result == str(test_file)


def test_remove_thumbnail_success(mock_db):
    """Test thumbnail removal."""
    mock_conn, mock_cursor = mock_db
    
    with patch('app.utils.thumbnail_utils.get_project_thumbnail', return_value=None):
        result = remove_project_thumbnail("sig123")
    
    assert result["status"] == "ok"