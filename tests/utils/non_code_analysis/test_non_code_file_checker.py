import pytest
from pathlib import Path
from app.utils.non_code_analysis.non_code_file_checker import is_non_code_file, filter_non_code_files


# ============================================================================
# Tests for is_non_code_file() - KEEP ALL EXISTING TESTS
# ============================================================================

def test_is_non_code_file_pdf():
    assert is_non_code_file("document.pdf") is True


def test_is_non_code_file_code():
    assert is_non_code_file("script.py") is False


def test_is_non_code_file_markdown():
    assert is_non_code_file("README.md") is True


def test_is_non_code_file_image():
    assert is_non_code_file("logo.png") is True


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


# ============================================================================
# Tests for filter_non_code_files() - NEW TESTS
# ============================================================================

def test_filter_non_code_files_basic(tmp_path):
    """Test basic filtering of pre-scanned file list."""
    # Create test files
    doc = tmp_path / "report.pdf"
    doc.write_bytes(b"PDF")
    
    code = tmp_path / "script.py"
    code.write_text("print('hello')")
    
    readme = tmp_path / "README.md"
    readme.write_text("# Title")
    
    # Simulate scan_project_files() output
    scanned_files = [str(doc), str(code), str(readme)]
    
    non_code = filter_non_code_files(scanned_files)
    
    assert len(non_code) == 2
    assert any("report.pdf" in f for f in non_code)
    assert any("README.md" in f for f in non_code)
    assert not any("script.py" in f for f in non_code)


def test_filter_non_code_files_empty_list():
    """Test with empty input list."""
    result = filter_non_code_files([])
    assert result == []


def test_filter_non_code_files_all_code_files(tmp_path):
    """Test with list containing only code files."""
    py_file = tmp_path / "app.py"
    py_file.write_text("code")
    
    js_file = tmp_path / "script.js"
    js_file.write_text("code")
    
    scanned_files = [str(py_file), str(js_file)]
    
    result = filter_non_code_files(scanned_files)
    assert result == []


def test_filter_non_code_files_all_non_code_files(tmp_path):
    """Test with list containing only non-code files."""
    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"PDF")
    
    png = tmp_path / "image.png"
    png.write_bytes(b"PNG")
    
    md = tmp_path / "README.md"
    md.write_text("readme")
    
    scanned_files = [str(pdf), str(png), str(md)]
    
    result = filter_non_code_files(scanned_files)
    assert len(result) == 3


def test_filter_non_code_files_mixed_list(tmp_path):
    """Test with mixed code and non-code files."""
    # Non-code
    pdf = tmp_path / "report.pdf"
    pdf.write_bytes(b"PDF")
    
    docx = tmp_path / "doc.docx"
    docx.write_bytes(b"DOCX")
    
    png = tmp_path / "logo.png"
    png.write_bytes(b"PNG")
    
    # Code
    py = tmp_path / "main.py"
    py.write_text("code")
    
    js = tmp_path / "app.js"
    js.write_text("code")
    
    json_file = tmp_path / "config.json"
    json_file.write_text("{}")
    
    scanned_files = [str(pdf), str(py), str(docx), str(js), str(png), str(json_file)]
    
    result = filter_non_code_files(scanned_files)
    
    assert len(result) == 3
    assert any("report.pdf" in f for f in result)
    assert any("doc.docx" in f for f in result)
    assert any("logo.png" in f for f in result)


def test_filter_non_code_files_returns_absolute_paths(tmp_path):
    """Test that returned paths are absolute."""
    doc = tmp_path / "file.pdf"
    doc.write_bytes(b"PDF")
    
    result = filter_non_code_files([str(doc)])
    
    assert len(result) == 1
    assert Path(result[0]).is_absolute()


def test_filter_non_code_files_with_string_paths(tmp_path):
    """Test that function accepts string paths."""
    doc = tmp_path / "doc.pdf"
    doc.write_bytes(b"PDF")
    
    # Pass as string instead of Path
    result = filter_non_code_files([str(doc)])
    
    assert len(result) == 1
    assert "doc.pdf" in result[0]


def test_filter_non_code_files_with_path_objects(tmp_path):
    """Test that function accepts Path objects."""
    doc = tmp_path / "doc.pdf"
    doc.write_bytes(b"PDF")
    
    result = filter_non_code_files([doc])
    
    assert len(result) == 1
    assert "doc.pdf" in result[0]


def test_filter_non_code_files_skips_nonexistent_files(tmp_path):
    """Test that non-existent files are safely skipped."""
    existing = tmp_path / "exists.pdf"
    existing.write_bytes(b"PDF")
    
    nonexistent = tmp_path / "missing.pdf"
    
    result = filter_non_code_files([str(existing), str(nonexistent)])
    
    assert len(result) == 1
    assert "exists.pdf" in result[0]


def test_filter_non_code_files_skips_directories(tmp_path):
    """Test that directories in the list are skipped."""
    doc = tmp_path / "file.pdf"
    doc.write_bytes(b"PDF")
    
    a_dir = tmp_path / "somedir"
    a_dir.mkdir()
    
    result = filter_non_code_files([str(doc), str(a_dir)])
    
    assert len(result) == 1
    assert "file.pdf" in result[0]


def test_filter_non_code_files_multiple_extensions(tmp_path):
    """Test various non-code extensions."""
    files = []
    extensions = [".pdf", ".docx", ".png", ".mp4", ".zip", ".md", ".txt"]
    
    for i, ext in enumerate(extensions):
        f = tmp_path / f"file{i}{ext}"
        f.write_bytes(b"content")
        files.append(str(f))
    
    result = filter_non_code_files(files)
    
    assert len(result) == len(extensions)


def test_filter_non_code_files_case_insensitive(tmp_path):
    """Test case-insensitive extension matching."""
    pdf_upper = tmp_path / "DOC.PDF"
    pdf_upper.write_bytes(b"PDF")
    
    png_mixed = tmp_path / "Image.PnG"
    png_mixed.write_bytes(b"PNG")
    
    result = filter_non_code_files([str(pdf_upper), str(png_mixed)])
    
    assert len(result) == 2


def test_filter_non_code_files_special_characters(tmp_path):
    """Test files with special characters in names."""
    file1 = tmp_path / "my document (2024).pdf"
    file1.write_bytes(b"PDF")
    
    file2 = tmp_path / "report-final_v2.docx"
    file2.write_bytes(b"DOCX")
    
    result = filter_non_code_files([str(file1), str(file2)])
    
    assert len(result) == 2


def test_filter_non_code_files_preserves_order(tmp_path):
    """Test that order is preserved."""
    a = tmp_path / "a.pdf"
    a.write_bytes(b"PDF")
    
    b = tmp_path / "b.pdf"
    b.write_bytes(b"PDF")
    
    c = tmp_path / "c.pdf"
    c.write_bytes(b"PDF")
    
    input_order = [str(a), str(b), str(c)]
    result = filter_non_code_files(input_order)
    
    # Check that a comes before b comes before c
    a_idx = next(i for i, p in enumerate(result) if "a.pdf" in p)
    b_idx = next(i for i, p in enumerate(result) if "b.pdf" in p)
    c_idx = next(i for i, p in enumerate(result) if "c.pdf" in p)
    
    assert a_idx < b_idx < c_idx


def test_filter_non_code_files_nested_paths(tmp_path):
    """Test files from nested directory structures."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    doc = docs_dir / "guide.pdf"
    doc.write_bytes(b"PDF")
    
    assets_dir = tmp_path / "assets" / "images"
    assets_dir.mkdir(parents=True)
    img = assets_dir / "logo.png"
    img.write_bytes(b"PNG")
    
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    code = src_dir / "main.py"
    code.write_text("code")
    
    scanned_files = [str(doc), str(img), str(code)]
    result = filter_non_code_files(scanned_files)
    
    assert len(result) == 2
    assert any("guide.pdf" in f for f in result)
    assert any("logo.png" in f for f in result)


def test_filter_non_code_files_duplicate_paths(tmp_path):
    """Test handling of duplicate file paths in input."""
    doc = tmp_path / "file.pdf"
    doc.write_bytes(b"PDF")
    
    # Pass same file twice
    scanned_files = [str(doc), str(doc)]
    result = filter_non_code_files(scanned_files)
    
    # Should return both (no deduplication by default)
    assert len(result) == 2


def test_filter_non_code_files_with_relative_paths(tmp_path):
    """Test with relative paths (should still work)."""
    doc = tmp_path / "doc.pdf"
    doc.write_bytes(b"PDF")
    
    # Use relative path
    import os
    original_dir = os.getcwd()
    try:
        os.chdir(tmp_path)
        result = filter_non_code_files(["doc.pdf"])
        assert len(result) == 1
        # Result should be absolute
        assert Path(result[0]).is_absolute()
    finally:
        os.chdir(original_dir)


@pytest.mark.parametrize("extension", [
    ".pdf", ".docx", ".png", ".jpg", ".mp4", ".zip", ".md", ".txt"
])
def test_filter_non_code_files_parametrized(tmp_path, extension):
    """Parametrized test for various non-code extensions."""
    f = tmp_path / f"file{extension}"
    f.write_bytes(b"content")
    
    result = filter_non_code_files([str(f)])
    
    assert len(result) == 1
    assert extension in result[0]


def test_filter_non_code_files_large_list(tmp_path):
    """Test performance with large file list."""
    files = []
    
    # Create 100 files (mix of code and non-code)
    for i in range(50):
        pdf = tmp_path / f"doc{i}.pdf"
        pdf.write_bytes(b"PDF")
        files.append(str(pdf))
        
        py = tmp_path / f"script{i}.py"
        py.write_text("code")
        files.append(str(py))
    
    result = filter_non_code_files(files)
    
    # Should only return the 50 PDFs
    assert len(result) == 50
    assert all(".pdf" in f for f in result)


def test_filter_non_code_files_integration_pattern(tmp_path):
    """Test realistic integration scenario with scan_project_files pattern."""
    # Create project structure (what scan_project_files would return)
    (tmp_path / "README.md").write_text("readme")
    (tmp_path / "app.py").write_text("code")
    (tmp_path / "logo.png").write_bytes(b"PNG")
    
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "main.py").write_text("code")
    (src_dir / "guide.pdf").write_bytes(b"PDF")
    
    # Simulate scan_project_files output (already excludes .git, node_modules, etc.)
    scanned_files = [
        str(tmp_path / "README.md"),
        str(tmp_path / "app.py"),
        str(tmp_path / "logo.png"),
        str(src_dir / "main.py"),
        str(src_dir / "guide.pdf")
    ]
    
    result = filter_non_code_files(scanned_files)
    
    assert len(result) == 3
    assert any("README.md" in f for f in result)
    assert any("logo.png" in f for f in result)
    assert any("guide.pdf" in f for f in result)
    assert not any("app.py" in f for f in result)
    assert not any("main.py" in f for f in result)