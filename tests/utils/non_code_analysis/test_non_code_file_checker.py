import pytest
from pathlib import Path
from app.utils.non_code_analysis.non_code_file_checker import is_non_code_file


def test_is_non_code_file_pdf():
    assert is_non_code_file("document.pdf") is True


def test_is_non_code_file_code():
    assert is_non_code_file("script.py") is False


def test_is_non_code_file_markdown():
    assert is_non_code_file("README.md") is True


def test_is_non_code_file_image():
    assert is_non_code_file("logo.png") is True


# Additional comprehensive tests

def test_is_non_code_file_multiple_document_types():
    """Test various document formats."""
    assert is_non_code_file("report.docx") is True
    assert is_non_code_file("old_doc.doc") is True
    assert is_non_code_file("notes.txt") is True
    assert is_non_code_file("presentation.ppt") is True
    assert is_non_code_file("slides.pptx") is True


def test_is_non_code_file_multiple_image_types():
    """Test various image formats."""
    assert is_non_code_file("photo.jpg") is True
    assert is_non_code_file("photo.jpeg") is True
    assert is_non_code_file("icon.gif") is True
    assert is_non_code_file("graphic.bmp") is True
    assert is_non_code_file("vector.svg") is True


def test_is_non_code_file_archive_types():
    """Test archive/compressed file formats."""
    assert is_non_code_file("package.zip") is True
    assert is_non_code_file("backup.tar") is True
    assert is_non_code_file("compressed.gz") is True


def test_is_non_code_file_spreadsheets():
    """Test spreadsheet formats."""
    assert is_non_code_file("data.xls") is True
    assert is_non_code_file("data.xlsx") is True


def test_is_non_code_file_various_code_extensions():
    """Test that code files are correctly identified as code."""
    assert is_non_code_file("app.js") is False
    assert is_non_code_file("style.css") is False
    assert is_non_code_file("index.html") is False
    assert is_non_code_file("Component.jsx") is False
    assert is_non_code_file("script.ts") is False
    assert is_non_code_file("main.java") is False
    assert is_non_code_file("program.cpp") is False
    assert is_non_code_file("module.go") is False
    assert is_non_code_file("script.rb") is False
    assert is_non_code_file("app.php") is False


def test_is_non_code_file_config_files():
    """Test configuration and data files."""
    assert is_non_code_file("config.json") is False
    assert is_non_code_file("data.xml") is False
    assert is_non_code_file("settings.yaml") is False
    assert is_non_code_file("config.yml") is False


def test_is_non_code_file_case_insensitive():
    """Test that extension checking is case-insensitive."""
    assert is_non_code_file("Document.PDF") is True
    assert is_non_code_file("Image.PNG") is True
    assert is_non_code_file("README.MD") is True
    assert is_non_code_file("Script.PY") is False


def test_is_non_code_file_with_path_object():
    """Test that function works with Path objects."""
    assert is_non_code_file(Path("document.pdf")) is True
    assert is_non_code_file(Path("script.py")) is False


def test_is_non_code_file_with_full_path():
    """Test with full file paths."""
    assert is_non_code_file("/home/user/documents/report.pdf") is True
    assert is_non_code_file("/home/user/projects/app.py") is False
    assert is_non_code_file("C:\\Users\\Documents\\file.docx") is True


def test_is_non_code_file_no_extension():
    """Test files without extensions."""
    assert is_non_code_file("Makefile") is False
    assert is_non_code_file("Dockerfile") is False
    assert is_non_code_file("README") is False


def test_is_non_code_file_dotfiles():
    """Test hidden files (dotfiles)."""
    assert is_non_code_file(".gitignore") is False
    assert is_non_code_file(".env") is False
    assert is_non_code_file(".dockerignore") is False


def test_is_non_code_file_multiple_dots_in_name():
    """Test files with multiple dots in filename."""
    assert is_non_code_file("my.backup.file.pdf") is True
    assert is_non_code_file("test.spec.js") is False
    assert is_non_code_file("archive.2024.01.15.zip") is True


@pytest.mark.parametrize("extension,expected", [
    # Non-code extensions
    (".pdf", True),
    (".docx", True),
    (".png", True),
    (".jpg", True),
    (".mp4", True),
    (".zip", True),
    (".txt", True),
    (".md", True),
    # Code extensions
    (".py", False),
    (".js", False),
    (".java", False),
    (".cpp", False),
    (".go", False),
    (".rs", False),
    (".rb", False),
    (".php", False),
    (".ts", False),
    (".jsx", False),
])
def test_is_non_code_file_parametrized(extension, expected):
    """Parametrized test for various extensions."""
    filename = f"testfile{extension}"
    assert is_non_code_file(filename) is expected