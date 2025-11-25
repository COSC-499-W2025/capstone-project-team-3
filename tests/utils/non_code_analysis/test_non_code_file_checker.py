import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from app.utils.non_code_analysis.non_code_file_checker import (
    is_non_code_file,
    filter_non_code_files,
    collect_git_non_code_files_with_metadata,
    filter_non_code_files_by_collaboration,
    get_git_user_identity,
    verify_user_in_files,
    classify_non_code_files_with_user_verification
)

# ============================================================================
# Tests for is_non_code_file() 
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


# ============================================================================
# Tests for collect_git_non_code_files_with_metadata() 
# ============================================================================

def _make_mock_commit(author_email, files):
    """Helper to create mock commit objects."""
    commit = MagicMock()
    commit.author = MagicMock()
    commit.author.email = author_email
    commit.stats = MagicMock()
    commit.stats.files = files
    return commit


def test_collect_git_non_code_files_basic():
    """Test basic collection of non-code files from git repo."""
    commit1 = _make_mock_commit("alice@example.com", {"doc.pdf": {}, "script.py": {}})
    commit2 = _make_mock_commit("bob@example.com", {"doc.pdf": {}})
    
    with patch("app.utils.non_code_analysis.non_code_file_checker.get_repo") as mock_get_repo:
        mock_repo = MagicMock()
        mock_repo.iter_commits.return_value = [commit1, commit2]
        mock_get_repo.return_value = mock_repo
        
        result = collect_git_non_code_files_with_metadata("/fake/repo")
        
        assert "doc.pdf" in result
        assert "script.py" not in result
        assert len(result["doc.pdf"]["authors"]) == 2
        assert result["doc.pdf"]["commit_count"] == 2


def test_collect_git_non_code_files_single_author():
    """Test file with single author."""
    commit = _make_mock_commit("alice@example.com", {"README.md": {}})
    
    with patch("app.utils.non_code_analysis.non_code_file_checker.get_repo") as mock_get_repo:
        mock_repo = MagicMock()
        mock_repo.iter_commits.return_value = [commit]
        mock_get_repo.return_value = mock_repo
        
        result = collect_git_non_code_files_with_metadata("/fake/repo")
        
        assert "README.md" in result
        assert result["README.md"]["authors"] == ["alice@example.com"]
        assert result["README.md"]["commit_count"] == 1


def test_collect_git_non_code_files_filters_code():
    """Test that code files are excluded."""
    commit = _make_mock_commit("alice@example.com", {
        "script.py": {},
        "app.js": {},
        "doc.pdf": {},
        "image.png": {}
    })
    
    with patch("app.utils.non_code_analysis.non_code_file_checker.get_repo") as mock_get_repo:
        mock_repo = MagicMock()
        mock_repo.iter_commits.return_value = [commit]
        mock_get_repo.return_value = mock_repo
        
        result = collect_git_non_code_files_with_metadata("/fake/repo")
        
        assert "doc.pdf" in result
        assert "image.png" in result
        assert "script.py" not in result
        assert "app.js" not in result


def test_collect_git_non_code_files_invalid_repo():
    """Test handling of invalid repository."""
    with patch("app.utils.non_code_analysis.non_code_file_checker.get_repo") as mock_get_repo:
        mock_get_repo.side_effect = Exception("Not a git repo")
        
        result = collect_git_non_code_files_with_metadata("/not/a/repo")
        
        assert result == {}


def test_collect_git_non_code_files_multiple_commits_same_author():
    """Test multiple commits by same author on same file."""
    commit1 = _make_mock_commit("alice@example.com", {"doc.pdf": {}})
    commit2 = _make_mock_commit("alice@example.com", {"doc.pdf": {}})
    commit3 = _make_mock_commit("alice@example.com", {"doc.pdf": {}})
    
    with patch("app.utils.non_code_analysis.non_code_file_checker.get_repo") as mock_get_repo:
        mock_repo = MagicMock()
        mock_repo.iter_commits.return_value = [commit1, commit2, commit3]
        mock_get_repo.return_value = mock_repo
        
        result = collect_git_non_code_files_with_metadata("/fake/repo")
        
        assert result["doc.pdf"]["authors"] == ["alice@example.com"]
        assert result["doc.pdf"]["commit_count"] == 3


def test_collect_git_non_code_files_multiple_files_multiple_authors():
    """Test multiple files with different author combinations."""
    commit1 = _make_mock_commit("alice@example.com", {"doc1.pdf": {}, "doc2.pdf": {}})
    commit2 = _make_mock_commit("bob@example.com", {"doc1.pdf": {}})
    commit3 = _make_mock_commit("charlie@example.com", {"doc2.pdf": {}})
    
    with patch("app.utils.non_code_analysis.non_code_file_checker.get_repo") as mock_get_repo:
        mock_repo = MagicMock()
        mock_repo.iter_commits.return_value = [commit1, commit2, commit3]
        mock_get_repo.return_value = mock_repo
        
        result = collect_git_non_code_files_with_metadata("/fake/repo")
        
        assert len(result["doc1.pdf"]["authors"]) == 2
        assert set(result["doc1.pdf"]["authors"]) == {"alice@example.com", "bob@example.com"}
        assert result["doc1.pdf"]["commit_count"] == 2
        
        assert len(result["doc2.pdf"]["authors"]) == 2
        assert set(result["doc2.pdf"]["authors"]) == {"alice@example.com", "charlie@example.com"}
        assert result["doc2.pdf"]["commit_count"] == 2


def test_collect_git_non_code_files_handles_commit_stats_errors():
    """Test graceful handling of commits with missing stats."""
    good_commit = _make_mock_commit("alice@example.com", {"doc.pdf": {}})
    
    bad_commit = MagicMock()
    bad_commit.author.email = "bob@example.com"
    bad_commit.stats.files = None
    
    with patch("app.utils.non_code_analysis.non_code_file_checker.get_repo") as mock_get_repo:
        mock_repo = MagicMock()
        mock_repo.iter_commits.return_value = [good_commit, bad_commit]
        mock_get_repo.return_value = mock_repo
        
        result = collect_git_non_code_files_with_metadata("/fake/repo")
        
        assert "doc.pdf" in result
        assert result["doc.pdf"]["commit_count"] == 1


def test_collect_git_non_code_files_unknown_author():
    """Test handling of commits with missing author info."""
    commit = MagicMock()
    commit.author = MagicMock()
    commit.author.email = None
    commit.stats = MagicMock()
    commit.stats.files = {"doc.pdf": {}}
    
    with patch("app.utils.non_code_analysis.non_code_file_checker.get_repo") as mock_get_repo:
        mock_repo = MagicMock()
        mock_repo.iter_commits.return_value = [commit]
        mock_get_repo.return_value = mock_repo
        
        result = collect_git_non_code_files_with_metadata("/fake/repo")
        
        assert result["doc.pdf"]["authors"] == ["unknown"]


def test_collect_git_non_code_files_authors_sorted():
    """Test that authors are returned in sorted order."""
    commit1 = _make_mock_commit("zebra@example.com", {"doc.pdf": {}})
    commit2 = _make_mock_commit("alice@example.com", {"doc.pdf": {}})
    commit3 = _make_mock_commit("bob@example.com", {"doc.pdf": {}})
    
    with patch("app.utils.non_code_analysis.non_code_file_checker.get_repo") as mock_get_repo:
        mock_repo = MagicMock()
        mock_repo.iter_commits.return_value = [commit1, commit2, commit3]
        mock_get_repo.return_value = mock_repo
        
        result = collect_git_non_code_files_with_metadata("/fake/repo")
        
        assert result["doc.pdf"]["authors"] == ["alice@example.com", "bob@example.com", "zebra@example.com"]


def test_collect_git_non_code_files_empty_repo():
    """Test empty repository with no commits."""
    with patch("app.utils.non_code_analysis.non_code_file_checker.get_repo") as mock_get_repo:
        mock_repo = MagicMock()
        mock_repo.iter_commits.return_value = []
        mock_get_repo.return_value = mock_repo
        
        result = collect_git_non_code_files_with_metadata("/fake/repo")
        
        assert result == {}


def test_collect_git_non_code_files_only_code_in_repo():
    """Test repo that only contains code files."""
    commit = _make_mock_commit("alice@example.com", {
        "app.py": {},
        "main.js": {},
        "config.json": {}
    })
    
    with patch("app.utils.non_code_analysis.non_code_file_checker.get_repo") as mock_get_repo:
        mock_repo = MagicMock()
        mock_repo.iter_commits.return_value = [commit]
        mock_get_repo.return_value = mock_repo
        
        result = collect_git_non_code_files_with_metadata("/fake/repo")
        
        assert result == {}


# ============================================================================
# Tests for filter_non_code_files_by_collaboration() 
# ============================================================================

def test_filter_by_collaboration_single_author():
    """Test file with single author is non-collaborative."""
    metadata = {
        "doc.pdf": {
            "path": "/repo/doc.pdf",
            "authors": ["alice@example.com"],
            "commit_count": 5
        }
    }
    
    result = filter_non_code_files_by_collaboration(metadata)
    
    assert len(result["collaborative"]) == 0
    assert len(result["non_collaborative"]) == 1
    assert "/repo/doc.pdf" in result["non_collaborative"]


def test_filter_by_collaboration_two_authors():
    """Test file with 2 authors is collaborative."""
    metadata = {
        "doc.pdf": {
            "path": "/repo/doc.pdf",
            "authors": ["alice@example.com", "bob@example.com"],
            "commit_count": 10
        }
    }
    
    result = filter_non_code_files_by_collaboration(metadata)
    
    assert len(result["collaborative"]) == 1
    assert len(result["non_collaborative"]) == 0
    assert "/repo/doc.pdf" in result["collaborative"]


def test_filter_by_collaboration_mixed():
    """Test mix of collaborative and non-collaborative files."""
    metadata = {
        "doc.pdf": {
            "path": "/repo/doc.pdf",
            "authors": ["alice@example.com", "bob@example.com"],
            "commit_count": 5
        },
        "README.md": {
            "path": "/repo/README.md",
            "authors": ["alice@example.com"],
            "commit_count": 2
        },
        "logo.png": {
            "path": "/repo/logo.png",
            "authors": ["alice@example.com", "charlie@example.com", "dave@example.com"],
            "commit_count": 8
        }
    }
    
    result = filter_non_code_files_by_collaboration(metadata)
    
    assert len(result["collaborative"]) == 2
    assert "/repo/doc.pdf" in result["collaborative"]
    assert "/repo/logo.png" in result["collaborative"]
    
    assert len(result["non_collaborative"]) == 1
    assert "/repo/README.md" in result["non_collaborative"]


def test_filter_by_collaboration_custom_threshold():
    """Test with custom author threshold."""
    metadata = {
        "doc1.pdf": {
            "path": "/repo/doc1.pdf",
            "authors": ["alice@example.com", "bob@example.com"],
            "commit_count": 5
        },
        "doc2.pdf": {
            "path": "/repo/doc2.pdf",
            "authors": ["alice@example.com", "bob@example.com", "charlie@example.com"],
            "commit_count": 8
        }
    }
    
    # Threshold=2 means need 3+ authors for collaborative
    result = filter_non_code_files_by_collaboration(metadata, author_threshold=2)
    
    assert len(result["collaborative"]) == 1
    assert "/repo/doc2.pdf" in result["collaborative"]
    
    assert len(result["non_collaborative"]) == 1
    assert "/repo/doc1.pdf" in result["non_collaborative"]


def test_filter_by_collaboration_empty_input():
    """Test with empty metadata."""
    result = filter_non_code_files_by_collaboration({})
    
    assert result["collaborative"] == []
    assert result["non_collaborative"] == []


def test_filter_by_collaboration_all_collaborative():
    """Test when all files are collaborative."""
    metadata = {
        "doc1.pdf": {
            "path": "/repo/doc1.pdf",
            "authors": ["alice@example.com", "bob@example.com"],
            "commit_count": 3
        },
        "doc2.pdf": {
            "path": "/repo/doc2.pdf",
            "authors": ["alice@example.com", "charlie@example.com"],
            "commit_count": 5
        }
    }
    
    result = filter_non_code_files_by_collaboration(metadata)
    
    assert len(result["collaborative"]) == 2
    assert len(result["non_collaborative"]) == 0


def test_filter_by_collaboration_all_non_collaborative():
    """Test when all files are non-collaborative."""
    metadata = {
        "doc1.pdf": {
            "path": "/repo/doc1.pdf",
            "authors": ["alice@example.com"],
            "commit_count": 3
        },
        "doc2.pdf": {
            "path": "/repo/doc2.pdf",
            "authors": ["bob@example.com"],
            "commit_count": 2
        }
    }
    
    result = filter_non_code_files_by_collaboration(metadata)
    
    assert len(result["collaborative"]) == 0
    assert len(result["non_collaborative"]) == 2


def test_filter_by_collaboration_empty_authors_list():
    """Test handling of empty authors list."""
    metadata = {
        "doc.pdf": {
            "path": "/repo/doc.pdf",
            "authors": [],
            "commit_count": 0
        }
    }
    
    result = filter_non_code_files_by_collaboration(metadata)
    
    assert len(result["non_collaborative"]) == 1
    assert len(result["collaborative"]) == 0


def test_filter_by_collaboration_missing_authors_key():
    """Test handling of missing authors key."""
    metadata = {
        "doc.pdf": {
            "path": "/repo/doc.pdf",
            "commit_count": 5
        }
    }
    
    result = filter_non_code_files_by_collaboration(metadata)
    
    assert len(result["non_collaborative"]) == 1
    assert len(result["collaborative"]) == 0


def test_filter_by_collaboration_many_authors():
    """Test file with many authors."""
    metadata = {
        "doc.pdf": {
            "path": "/repo/doc.pdf",
            "authors": [f"user{i}@example.com" for i in range(10)],
            "commit_count": 50
        }
    }
    
    result = filter_non_code_files_by_collaboration(metadata)
    
    assert len(result["collaborative"]) == 1
    assert len(result["non_collaborative"]) == 0


def test_filter_by_collaboration_threshold_edge_case():
    """Test edge case where author count equals threshold."""
    metadata = {
        "doc.pdf": {
            "path": "/repo/doc.pdf",
            "authors": ["alice@example.com", "bob@example.com"],
            "commit_count": 5
        }
    }
    
    # Threshold=2: need MORE than 2 authors
    result = filter_non_code_files_by_collaboration(metadata, author_threshold=2)
    
    # 2 authors is NOT > 2, so non-collaborative
    assert len(result["non_collaborative"]) == 1
    assert len(result["collaborative"]) == 0


def test_filter_by_collaboration_realistic_scenario():
    """Test realistic collaborative repo scenario."""
    metadata = {
        "shared_design.pdf": {
            "path": "/repo/shared_design.pdf",
            "authors": ["alice@example.com", "bob@example.com"],
            "commit_count": 12
        },
        "alice_notes.md": {
            "path": "/repo/alice_notes.md",
            "authors": ["alice@example.com"],
            "commit_count": 5
        },
        "bob_draft.docx": {
            "path": "/repo/bob_draft.docx",
            "authors": ["bob@example.com"],
            "commit_count": 3
        },
        "team_presentation.pptx": {
            "path": "/repo/team_presentation.pptx",
            "authors": ["alice@example.com", "bob@example.com", "charlie@example.com"],
            "commit_count": 20
        }
    }
    
    result = filter_non_code_files_by_collaboration(metadata)
    
    assert len(result["collaborative"]) == 2
    assert "/repo/shared_design.pdf" in result["collaborative"]
    assert "/repo/team_presentation.pptx" in result["collaborative"]
    
    assert len(result["non_collaborative"]) == 2
    assert "/repo/alice_notes.md" in result["non_collaborative"]
    assert "/repo/bob_draft.docx" in result["non_collaborative"]


@pytest.mark.parametrize("author_count,threshold,expected_collaborative", [
    (1, 1, False),  # 1 author, threshold 1: non-collaborative
    (2, 1, True),   # 2 authors, threshold 1: collaborative
    (3, 1, True),   # 3 authors, threshold 1: collaborative
    (2, 2, False),  # 2 authors, threshold 2: non-collaborative (need >2)
    (3, 2, True),   # 3 authors, threshold 2: collaborative
    (5, 3, True),   # 5 authors, threshold 3: collaborative
])
def test_filter_by_collaboration_parametrized(author_count, threshold, expected_collaborative):
    """Parametrized test for various author counts and thresholds."""
    metadata = {
        "doc.pdf": {
            "path": "/repo/doc.pdf",
            "authors": [f"user{i}@example.com" for i in range(author_count)],
            "commit_count": 10
        }
    }
    
    result = filter_non_code_files_by_collaboration(metadata, author_threshold=threshold)
    
    if expected_collaborative:
        assert len(result["collaborative"]) == 1
        assert len(result["non_collaborative"]) == 0
    else:
        assert len(result["collaborative"]) == 0
        assert len(result["non_collaborative"]) == 1

# ============================================================================
# Tests for get_git_user_identity()
# ============================================================================

@patch('app.utils.non_code_analysis.non_code_file_checker.get_repo')
def test_get_git_user_identity_success(mock_get_repo):
    """Test getting git user identity."""
    mock_repo = Mock()
    mock_config = Mock()
    mock_config.get_value.side_effect = lambda section, key, default="": {
        ("user", "name"): "Alice Smith",
        ("user", "email"): "alice@example.com"
    }.get((section, key), default)
    
    mock_repo.config_reader.return_value = mock_config
    mock_get_repo.return_value = mock_repo
    
    result = get_git_user_identity('/path/to/repo')
    
    assert result["name"] == "Alice Smith"
    assert result["email"] == "alice@example.com"


@patch('app.utils.non_code_analysis.non_code_file_checker.get_repo')
def test_get_git_user_identity_not_configured(mock_get_repo):
    """Test getting identity when git user not configured."""
    mock_repo = Mock()
    mock_config = Mock()
    mock_config.get_value.return_value = ""
    mock_repo.config_reader.return_value = mock_config
    mock_get_repo.return_value = mock_repo
    
    result = get_git_user_identity('/path/to/repo')
    
    assert result["name"] == ""
    assert result["email"] == ""


@patch('app.utils.non_code_analysis.non_code_file_checker.get_repo')
def test_get_git_user_identity_invalid_repo(mock_get_repo):
    """Test handling invalid repository."""
    mock_get_repo.side_effect = Exception("Not a git repo")
    result = get_git_user_identity('/invalid/path')
    assert result == {}



# ============================================================================
# Tests for verify_user_in_files()
# ============================================================================

def test_verify_user_in_files_mixed():
    """Test verifying user in files with mixed authorship."""
    metadata = {
        "collab.pdf": {
            "path": "/path/collab.pdf",
            "authors": ["user@example.com", "other@example.com"]
        },
        "solo.md": {
            "path": "/path/solo.md",
            "authors": ["user@example.com"]
        },
        "others.docx": {
            "path": "/path/others.docx",
            "authors": ["other@example.com", "another@example.com"]
        }
    }
    
    result = verify_user_in_files(metadata, "user@example.com")
    
    assert len(result["user_collaborative"]) == 1
    assert "/path/collab.pdf" in result["user_collaborative"]
    
    assert len(result["user_solo"]) == 1
    assert "/path/solo.md" in result["user_solo"]
    
    assert len(result["others_only"]) == 1
    assert "/path/others.docx" in result["others_only"]


def test_verify_user_in_files_user_not_in_any():
    """Test when user hasn't contributed to any files."""
    metadata = {
        "file1.pdf": {
            "path": "/path/file1.pdf",
            "authors": ["other@example.com"]
        },
        "file2.md": {
            "path": "/path/file2.md",
            "authors": ["another@example.com"]
        }
    }
    
    result = verify_user_in_files(metadata, "user@example.com")
    
    assert result["user_collaborative"] == []
    assert result["user_solo"] == []
    assert len(result["others_only"]) == 2


def test_verify_user_in_files_empty_metadata():
    """Test verifying user with empty metadata."""
    result = verify_user_in_files({}, "user@example.com")
    assert result["user_collaborative"] == []
    assert result["user_solo"] == []
    assert result["others_only"] == []

def test_verify_user_in_files_includes_readme_for_collaborative():
    """README files should always be included in user_collaborative, even if user is not an author."""
    metadata = {
        "README.md": {
            "path": "/repo/README.md",
            "authors": ["other@example.com"]
        },
        "readme.txt": {
            "path": "/repo/readme.txt",
            "authors": []
        },
        "ReadMe.docx": {
            "path": "/repo/ReadMe.docx",
            "authors": ["someone@example.com"]
        },
        "notes.pdf": {
            "path": "/repo/notes.pdf",
            "authors": ["other@example.com"]
        }
    }
    result = verify_user_in_files(metadata, "user@example.com")
    # All README variants should be in user_collaborative
    assert "/repo/README.md" in result["user_collaborative"]
    assert "/repo/readme.txt" in result["user_collaborative"]
    assert "/repo/ReadMe.docx" in result["user_collaborative"]
    # notes.pdf should not be in user_collaborative
    assert "/repo/notes.pdf" not in result["user_collaborative"]

# ============================================================================
# Tests for classify_non_code_files_with_user_verification()
# ============================================================================

@patch('app.utils.non_code_analysis.non_code_file_checker.detect_git')
@patch('app.utils.non_code_analysis.non_code_file_checker.get_git_user_identity')
@patch('app.utils.non_code_analysis.non_code_file_checker.collect_git_non_code_files_with_metadata')
def test_classify_git_repo_with_user_basic(mock_collect, mock_identity, mock_detect_git):
    """Test basic classification in a git repo with user verification."""
    mock_detect_git.return_value = True
    mock_identity.return_value = {"name": "Alice", "email": "alice@example.com"}
    
    mock_collect.return_value = {
        "collab.pdf": {
            "path": "/repo/collab.pdf",
            "authors": ["alice@example.com", "bob@example.com"]
        },
        "solo.md": {
            "path": "/repo/solo.md",
            "authors": ["alice@example.com"]
        },
        "others.docx": {
            "path": "/repo/others.docx",
            "authors": ["bob@example.com"]
        }
    }
    
    result = classify_non_code_files_with_user_verification('/path/to/repo')
    
    assert result["is_git_repo"] is True
    assert result["user_identity"]["email"] == "alice@example.com"
    assert len(result["collaborative"]) == 1
    assert "/repo/collab.pdf" in result["collaborative"]
    assert len(result["non_collaborative"]) == 1
    assert "/repo/solo.md" in result["non_collaborative"]
    assert len(result["excluded"]) == 1
    assert "/repo/others.docx" in result["excluded"]


@patch('app.utils.non_code_analysis.non_code_file_checker.detect_git')
@patch('app.utils.non_code_analysis.non_code_file_checker.get_git_user_identity')
@patch('app.utils.non_code_analysis.non_code_file_checker.collect_git_non_code_files_with_metadata')
def test_classify_git_repo_all_collaborative(mock_collect, mock_identity, mock_detect_git):
    """Test when all files are collaborative."""
    mock_detect_git.return_value = True
    mock_identity.return_value = {"name": "Alice", "email": "alice@example.com"}
    
    mock_collect.return_value = {
        "doc1.pdf": {
            "path": "/repo/doc1.pdf",
            "authors": ["alice@example.com", "bob@example.com"]
        },
        "doc2.md": {
            "path": "/repo/doc2.md",
            "authors": ["alice@example.com", "charlie@example.com"]
        }
    }
    
    result = classify_non_code_files_with_user_verification('/path/to/repo')
    
    assert len(result["collaborative"]) == 2
    assert len(result["non_collaborative"]) == 0
    assert len(result["excluded"]) == 0


@patch('app.utils.non_code_analysis.non_code_file_checker.detect_git')
@patch('app.utils.non_code_analysis.non_code_file_checker.get_git_user_identity')
@patch('app.utils.non_code_analysis.non_code_file_checker.collect_git_non_code_files_with_metadata')
def test_classify_git_repo_all_solo(mock_collect, mock_identity, mock_detect_git):
    """Test when all user's files are solo work."""
    mock_detect_git.return_value = True
    mock_identity.return_value = {"name": "Alice", "email": "alice@example.com"}
    
    mock_collect.return_value = {
        "notes.txt": {
            "path": "/repo/notes.txt",
            "authors": ["alice@example.com"]
        },
        "draft.md": {
            "path": "/repo/draft.md",
            "authors": ["alice@example.com"]
        }
    }
    
    result = classify_non_code_files_with_user_verification('/path/to/repo')
    
    assert len(result["collaborative"]) == 0
    assert len(result["non_collaborative"]) == 2
    assert len(result["excluded"]) == 0


@patch('app.utils.non_code_analysis.non_code_file_checker.detect_git')
@patch('app.utils.non_code_analysis.non_code_file_checker.get_git_user_identity')
@patch('app.utils.non_code_analysis.non_code_file_checker.collect_git_non_code_files_with_metadata')
def test_classify_git_repo_all_excluded(mock_collect, mock_identity, mock_detect_git):
    """Test when user hasn't contributed to any files."""
    mock_detect_git.return_value = True
    mock_identity.return_value = {"name": "Alice", "email": "alice@example.com"}
    
    mock_collect.return_value = {
        "bob_file.pdf": {
            "path": "/repo/bob_file.pdf",
            "authors": ["bob@example.com"]
        },
        "charlie_file.md": {
            "path": "/repo/charlie_file.md",
            "authors": ["charlie@example.com"]
        }
    }
    
    result = classify_non_code_files_with_user_verification('/path/to/repo')
    
    assert len(result["collaborative"]) == 0
    assert len(result["non_collaborative"]) == 0
    assert len(result["excluded"]) == 2


@patch('app.utils.non_code_analysis.non_code_file_checker.detect_git')
@patch('app.utils.non_code_analysis.non_code_file_checker.get_git_user_identity')
def test_classify_git_repo_no_user_identity(mock_identity, mock_detect_git):
    """Test handling when git user identity cannot be determined."""
    mock_detect_git.return_value = True
    mock_identity.return_value = {"name": "", "email": ""}
    
    result = classify_non_code_files_with_user_verification('/path/to/repo')
    
    assert result["is_git_repo"] is True
    assert "error" in result
    assert result["error"] == "Could not determine git user identity"
    assert result["collaborative"] == []
    assert result["non_collaborative"] == []
    assert result["excluded"] == []


@patch('app.utils.non_code_analysis.non_code_file_checker.detect_git')
@patch('app.utils.non_code_analysis.non_code_file_checker.collect_git_non_code_files_with_metadata')
def test_classify_git_repo_with_custom_email(mock_collect, mock_detect_git):
    """Test classification with custom user email provided."""
    mock_detect_git.return_value = True
    
    mock_collect.return_value = {
        "file.pdf": {
            "path": "/repo/file.pdf",
            "authors": ["custom@example.com", "other@example.com"]
        }
    }
    
    result = classify_non_code_files_with_user_verification(
        '/path/to/repo',
        user_email="custom@example.com"
    )
    
    assert result["user_identity"]["email"] == "custom@example.com"
    assert result["user_identity"]["name"] == ""
    assert len(result["collaborative"]) == 1


@patch('app.utils.non_code_analysis.non_code_file_checker.detect_git')
@patch('app.utils.non_code_analysis.non_code_file_checker.get_git_user_identity')
@patch('app.utils.non_code_analysis.non_code_file_checker.collect_git_non_code_files_with_metadata')
def test_classify_git_repo_empty_metadata(mock_collect, mock_identity, mock_detect_git):
    """Test when git repo has no non-code files."""
    mock_detect_git.return_value = True
    mock_identity.return_value = {"name": "Alice", "email": "alice@example.com"}
    mock_collect.return_value = {}
    
    result = classify_non_code_files_with_user_verification('/path/to/repo')
    
    assert result["is_git_repo"] is True
    assert result["collaborative"] == []
    assert result["non_collaborative"] == []
    assert result["excluded"] == []


@patch('app.utils.non_code_analysis.non_code_file_checker.detect_git')
@patch('app.utils.non_code_analysis.non_code_file_checker.scan_project_files')
@patch('app.utils.non_code_analysis.non_code_file_checker.filter_non_code_files')
def test_classify_non_git_directory_basic(mock_filter, mock_scan, mock_detect_git, tmp_path):
    """Test classifying files in a non-git directory."""
    mock_detect_git.return_value = False
    mock_scan.return_value = [
        str(tmp_path / "doc.pdf"),
        str(tmp_path / "script.py"),
        str(tmp_path / "readme.md")
    ]
    mock_filter.return_value = [
        str(tmp_path / "doc.pdf"),
        str(tmp_path / "readme.md")
    ]
    
    result = classify_non_code_files_with_user_verification(tmp_path)
    
    assert result["is_git_repo"] is False
    assert result["user_identity"] == {}
    assert result["collaborative"] == []
    assert len(result["non_collaborative"]) == 2
    assert result["excluded"] == []


@patch('app.utils.non_code_analysis.non_code_file_checker.detect_git')
@patch('app.utils.non_code_analysis.non_code_file_checker.scan_project_files')
@patch('app.utils.non_code_analysis.non_code_file_checker.filter_non_code_files')
def test_classify_non_git_directory_empty(mock_filter, mock_scan, mock_detect_git, tmp_path):
    """Test non-git directory with no non-code files."""
    mock_detect_git.return_value = False
    mock_scan.return_value = [str(tmp_path / "script.py")]
    mock_filter.return_value = []
    
    result = classify_non_code_files_with_user_verification(tmp_path)
    
    assert result["is_git_repo"] is False
    assert result["non_collaborative"] == []


@patch('app.utils.non_code_analysis.non_code_file_checker.detect_git')
@patch('app.utils.non_code_analysis.non_code_file_checker.scan_project_files')
@patch('app.utils.non_code_analysis.non_code_file_checker.filter_non_code_files')
def test_classify_non_git_directory_only_non_code(mock_filter, mock_scan, mock_detect_git, tmp_path):
    """Test non-git directory with only non-code files."""
    mock_detect_git.return_value = False
    
    files = [
        str(tmp_path / "doc1.pdf"),
        str(tmp_path / "doc2.md"),
        str(tmp_path / "image.png")
    ]
    mock_scan.return_value = files
    mock_filter.return_value = files
    
    result = classify_non_code_files_with_user_verification(tmp_path)
    
    assert len(result["non_collaborative"]) == 3


@patch('app.utils.non_code_analysis.non_code_file_checker.detect_git')
@patch('app.utils.non_code_analysis.non_code_file_checker.get_git_user_identity')
@patch('app.utils.non_code_analysis.non_code_file_checker.collect_git_non_code_files_with_metadata')
def test_classify_multiple_authors_on_file(mock_collect, mock_identity, mock_detect_git):
    """Test file with multiple authors including user."""
    mock_detect_git.return_value = True
    mock_identity.return_value = {"name": "Alice", "email": "alice@example.com"}
    
    mock_collect.return_value = {
        "team_doc.pdf": {
            "path": "/repo/team_doc.pdf",
            "authors": ["alice@example.com", "bob@example.com", "charlie@example.com"]
        }
    }
    
    result = classify_non_code_files_with_user_verification('/path/to/repo')
    
    assert len(result["collaborative"]) == 1
    assert "/repo/team_doc.pdf" in result["collaborative"]


@patch('app.utils.non_code_analysis.non_code_file_checker.detect_git')
@patch('app.utils.non_code_analysis.non_code_file_checker.get_git_user_identity')
@patch('app.utils.non_code_analysis.non_code_file_checker.collect_git_non_code_files_with_metadata')
def test_classify_realistic_mixed_scenario(mock_collect, mock_identity, mock_detect_git):
    """Test realistic scenario with mix of all categories."""
    mock_detect_git.return_value = True
    mock_identity.return_value = {"name": "Alice", "email": "alice@example.com"}
    
    mock_collect.return_value = {
        # Collaborative (user + others)
        "design_doc.pdf": {
            "path": "/repo/design_doc.pdf",
            "authors": ["alice@example.com", "bob@example.com"]
        },
        "presentation.pptx": {
            "path": "/repo/presentation.pptx",
            "authors": ["alice@example.com", "charlie@example.com", "dave@example.com"]
        },
        # Solo (user only)
        "alice_notes.txt": {
            "path": "/repo/alice_notes.txt",
            "authors": ["alice@example.com"]
        },
        "my_draft.md": {
            "path": "/repo/my_draft.md",
            "authors": ["alice@example.com"]
        },
        # Others only
        "bob_report.docx": {
            "path": "/repo/bob_report.docx",
            "authors": ["bob@example.com"]
        },
        "team_diagram.png": {
            "path": "/repo/team_diagram.png",
            "authors": ["charlie@example.com", "dave@example.com"]
        }
    }
    
    result = classify_non_code_files_with_user_verification('/path/to/repo')
    
    assert len(result["collaborative"]) == 2
    assert "/repo/design_doc.pdf" in result["collaborative"]
    assert "/repo/presentation.pptx" in result["collaborative"]
    
    assert len(result["non_collaborative"]) == 2
    assert "/repo/alice_notes.txt" in result["non_collaborative"]
    assert "/repo/my_draft.md" in result["non_collaborative"]
    
    assert len(result["excluded"]) == 2
    assert "/repo/bob_report.docx" in result["excluded"]
    assert "/repo/team_diagram.png" in result["excluded"]


@patch('app.utils.non_code_analysis.non_code_file_checker.detect_git')
@patch('app.utils.non_code_analysis.non_code_file_checker.get_git_user_identity')
@patch('app.utils.non_code_analysis.non_code_file_checker.collect_git_non_code_files_with_metadata')
def test_classify_user_email_case_sensitive(mock_collect, mock_identity, mock_detect_git):
    """Test that user email matching is case-sensitive (as git stores it)."""
    mock_detect_git.return_value = True
    mock_identity.return_value = {"name": "Alice", "email": "alice@example.com"}
    
    mock_collect.return_value = {
        "file1.pdf": {
            "path": "/repo/file1.pdf",
            "authors": ["alice@example.com"]  # Exact match
        },
        "file2.pdf": {
            "path": "/repo/file2.pdf",
            "authors": ["Alice@example.com"]  # Different case - won't match
        }
    }
    
    result = classify_non_code_files_with_user_verification('/path/to/repo')
    
    # Only exact match should be in user's files
    assert len(result["non_collaborative"]) == 1
    assert "/repo/file1.pdf" in result["non_collaborative"]
    assert len(result["excluded"]) == 1
    assert "/repo/file2.pdf" in result["excluded"]


@patch('app.utils.non_code_analysis.non_code_file_checker.detect_git')
@patch('app.utils.non_code_analysis.non_code_file_checker.get_git_user_identity')
@patch('app.utils.non_code_analysis.non_code_file_checker.collect_git_non_code_files_with_metadata')
def test_classify_with_pathlib_path(mock_collect, mock_identity, mock_detect_git, tmp_path):
    """Test that function works with Path objects."""
    mock_detect_git.return_value = True
    mock_identity.return_value = {"name": "Alice", "email": "alice@example.com"}
    mock_collect.return_value = {}
    
    # Pass Path object instead of string
    result = classify_non_code_files_with_user_verification(tmp_path)
    
    assert result["is_git_repo"] is True


@patch('app.utils.non_code_analysis.non_code_file_checker.detect_git')
@patch('app.utils.non_code_analysis.non_code_file_checker.scan_project_files')
@patch('app.utils.non_code_analysis.non_code_file_checker.filter_non_code_files')
def test_classify_non_git_with_pathlib_path(mock_filter, mock_scan, mock_detect_git, tmp_path):
    """Test non-git classification with Path objects."""
    mock_detect_git.return_value = False
    mock_scan.return_value = []
    mock_filter.return_value = []
    
    # Pass Path object
    result = classify_non_code_files_with_user_verification(tmp_path)
    
    assert result["is_git_repo"] is False


@patch('app.utils.non_code_analysis.non_code_file_checker.detect_git')
def test_classify_git_repo_custom_email_empty_string(mock_detect_git):
    """Test with custom email as empty string."""
    mock_detect_git.return_value = True
    
    result = classify_non_code_files_with_user_verification(
        '/path/to/repo',
        user_email=""
    )
    
    assert "error" in result
    assert result["error"] == "Could not determine git user identity"


@patch('app.utils.non_code_analysis.non_code_file_checker.detect_git')
@patch('app.utils.non_code_analysis.non_code_file_checker.scan_project_files')
@patch('app.utils.non_code_analysis.non_code_file_checker.filter_non_code_files')
def test_classify_non_git_ignores_user_email(mock_filter, mock_scan, mock_detect_git):
    """Test that user_email is ignored for non-git directories."""
    mock_detect_git.return_value = False
    mock_scan.return_value = []
    mock_filter.return_value = []
    
    # user_email should be ignored
    result = classify_non_code_files_with_user_verification(
        '/path/to/local',
        user_email="any@example.com"
    )
    
    assert result["is_git_repo"] is False
    assert result["user_identity"] == {}


@patch('app.utils.non_code_analysis.non_code_file_checker.detect_git')
@patch('app.utils.non_code_analysis.non_code_file_checker.get_git_user_identity')
@patch('app.utils.non_code_analysis.non_code_file_checker.collect_git_non_code_files_with_metadata')
def test_classify_returns_all_expected_keys(mock_collect, mock_identity, mock_detect_git):
    """Test that result contains all expected keys."""
    mock_detect_git.return_value = True
    mock_identity.return_value = {"name": "Alice", "email": "alice@example.com"}
    mock_collect.return_value = {}
    
    result = classify_non_code_files_with_user_verification('/path/to/repo')
    
    assert "is_git_repo" in result
    assert "user_identity" in result
    assert "collaborative" in result
    assert "non_collaborative" in result
    assert "excluded" in result


@patch('app.utils.non_code_analysis.non_code_file_checker.detect_git')
@patch('app.utils.non_code_analysis.non_code_file_checker.scan_project_files')
@patch('app.utils.non_code_analysis.non_code_file_checker.filter_non_code_files')
def test_classify_non_git_returns_all_expected_keys(mock_filter, mock_scan, mock_detect_git):
    """Test that non-git result contains all expected keys."""
    mock_detect_git.return_value = False
    mock_scan.return_value = []
    mock_filter.return_value = []
    
    result = classify_non_code_files_with_user_verification('/path/to/local')
    
    assert "is_git_repo" in result
    assert "user_identity" in result
    assert "collaborative" in result
    assert "non_collaborative" in result
    assert "excluded" in result


@patch('app.utils.non_code_analysis.non_code_file_checker.detect_git')
@patch('app.utils.non_code_analysis.non_code_file_checker.get_git_user_identity')
@patch('app.utils.non_code_analysis.non_code_file_checker.collect_git_non_code_files_with_metadata')
def test_classify_integration_example(mock_collect, mock_identity, mock_detect_git):
    """Test example from docstring."""
    mock_detect_git.return_value = True
    mock_identity.return_value = {"name": "Shreya", "email": "shreya@example.com"}
    
    mock_collect.return_value = {
        "design.pdf": {
            "path": "/capstone/docs/design.pdf",
            "authors": ["shreya@example.com", "teammate@example.com"]
        },
        "notes.txt": {
            "path": "/capstone/notes.txt",
            "authors": ["shreya@example.com"]
        }
    }
    
    result = classify_non_code_files_with_user_verification('/capstone')
    
    # Should match example behavior
    assert len(result["collaborative"]) >= 1
    assert len(result["non_collaborative"]) >= 1


@pytest.mark.parametrize("user_email,expected_collab,expected_solo", [
    ("alice@example.com", 1, 1),  # Alice has both types
    ("bob@example.com", 1, 1),    # Bob has both types
    ("charlie@example.com", 0, 0), # Charlie has no files
])
@patch('app.utils.non_code_analysis.non_code_file_checker.detect_git')
@patch('app.utils.non_code_analysis.non_code_file_checker.collect_git_non_code_files_with_metadata')
def test_classify_parametrized_users(mock_collect, mock_detect_git, user_email, expected_collab, expected_solo):
    """Parametrized test for different users."""
    mock_detect_git.return_value = True
    
    mock_collect.return_value = {
        "shared.pdf": {
            "path": "/repo/shared.pdf",
            "authors": ["alice@example.com", "bob@example.com"]
        },
        "alice_solo.md": {
            "path": "/repo/alice_solo.md",
            "authors": ["alice@example.com"]
        },
        "bob_solo.txt": {
            "path": "/repo/bob_solo.txt",
            "authors": ["bob@example.com"]
        }
    }
    
    result = classify_non_code_files_with_user_verification(
        '/path/to/repo',
        user_email=user_email
    )
    
    assert len(result["collaborative"]) == expected_collab
    assert len(result["non_collaborative"]) == expected_solo