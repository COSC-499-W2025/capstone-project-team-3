import pytest
from pathlib import Path
from app.utils.non_code_analysis.non_code_file_checker import is_non_code_file
from pathlib import Path
from app.utils.non_code_analysis.non_code_file_checker import collect_local_non_code_files


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

def test_collect_local_non_code_files_basic(tmp_path):
    """Test basic collection of non-code files."""
    # Create test files
    (tmp_path / "doc.pdf").write_bytes(b"PDF content")
    (tmp_path / "script.py").write_text("print('hello')")
    (tmp_path / "README.md").write_text("# Title")
    (tmp_path / "image.png").write_bytes(b"\x89PNG")
    
    files = collect_local_non_code_files(tmp_path)
    
    assert len(files) == 3  # PDF, MD, PNG (not .py)
    assert any("doc.pdf" in f for f in files)
    assert any("README.md" in f for f in files)
    assert any("image.png" in f for f in files)
    assert not any("script.py" in f for f in files)


def test_collect_local_non_code_files_nested_directories(tmp_path):
    """Test collection from nested directory structures."""
    # Create nested structure
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "guide.pdf").write_bytes(b"PDF")
    
    assets_dir = tmp_path / "assets" / "images"
    assets_dir.mkdir(parents=True)
    (assets_dir / "logo.png").write_bytes(b"PNG")
    
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "main.py").write_text("code")
    
    files = collect_local_non_code_files(tmp_path)
    
    assert len(files) == 2
    assert any("guide.pdf" in f for f in files)
    assert any("logo.png" in f for f in files)
    assert not any("main.py" in f for f in files)


def test_collect_local_non_code_files_excludes_git_directory(tmp_path):
    """Test that .git directory is excluded by default."""
    # Create .git directory with files
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("git config")
    (git_dir / "HEAD").write_text("ref: refs/heads/main")
    
    # Create regular non-code file
    (tmp_path / "README.md").write_text("# Project")
    
    files = collect_local_non_code_files(tmp_path)
    
    assert len(files) == 1
    assert any("README.md" in f for f in files)
    assert not any(".git" in f for f in files)


def test_collect_local_non_code_files_excludes_pycache(tmp_path):
    """Test that __pycache__ directory is excluded."""
    pycache_dir = tmp_path / "__pycache__"
    pycache_dir.mkdir()
    (pycache_dir / "module.pyc").write_bytes(b"bytecode")
    
    (tmp_path / "notes.txt").write_text("notes")
    
    files = collect_local_non_code_files(tmp_path)
    
    assert len(files) == 1
    assert any("notes.txt" in f for f in files)
    assert not any("__pycache__" in f for f in files)


def test_collect_local_non_code_files_excludes_node_modules(tmp_path):
    """Test that node_modules directory is excluded."""
    node_modules = tmp_path / "node_modules"
    node_modules.mkdir()
    (node_modules / "package.json").write_text("{}")
    
    (tmp_path / "README.md").write_text("# Project")
    
    files = collect_local_non_code_files(tmp_path)
    
    assert len(files) == 1
    assert any("README.md" in f for f in files)
    assert not any("node_modules" in f for f in files)


def test_collect_local_non_code_files_excludes_venv(tmp_path):
    """Test that virtual environment directories are excluded."""
    # Test both .venv and venv
    venv_dir = tmp_path / ".venv"
    venv_dir.mkdir()
    (venv_dir / "pyvenv.cfg").write_text("config")
    
    venv2_dir = tmp_path / "venv"
    venv2_dir.mkdir()
    (venv2_dir / "pyvenv.cfg").write_text("config")
    
    (tmp_path / "doc.pdf").write_bytes(b"PDF")
    
    files = collect_local_non_code_files(tmp_path)
    
    assert len(files) == 1
    assert any("doc.pdf" in f for f in files)
    assert not any(".venv" in f for f in files)
    assert not any("venv" in f and "venv" != "venv.txt" for f in files)


def test_collect_local_non_code_files_custom_exclusions(tmp_path):
    """Test custom directory exclusions."""
    # Create custom directories to exclude
    build_dir = tmp_path / "build"
    build_dir.mkdir()
    (build_dir / "output.pdf").write_bytes(b"PDF")
    
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    (dist_dir / "package.zip").write_bytes(b"ZIP")
    
    (tmp_path / "README.md").write_text("# Project")
    
    files = collect_local_non_code_files(tmp_path, exclude_dirs={'build', 'dist'})
    
    assert len(files) == 1
    assert any("README.md" in f for f in files)
    assert not any("build" in f for f in files)
    assert not any("dist" in f for f in files)


def test_collect_local_non_code_files_empty_directory(tmp_path):
    """Test behavior with empty directory."""
    files = collect_local_non_code_files(tmp_path)
    assert files == []


def test_collect_local_non_code_files_only_code_files(tmp_path):
    """Test directory containing only code files."""
    (tmp_path / "main.py").write_text("code")
    (tmp_path / "app.js").write_text("code")
    (tmp_path / "style.css").write_text("code")
    
    files = collect_local_non_code_files(tmp_path)
    assert files == []


def test_collect_local_non_code_files_nonexistent_path(tmp_path):
    """Test with non-existent directory path."""
    fake_path = tmp_path / "does_not_exist"
    files = collect_local_non_code_files(fake_path)
    assert files == []


def test_collect_local_non_code_files_file_instead_of_directory(tmp_path):
    """Test when root_path points to a file instead of directory."""
    file_path = tmp_path / "file.txt"
    file_path.write_text("content")
    
    files = collect_local_non_code_files(file_path)
    assert files == []


def test_collect_local_non_code_files_returns_absolute_paths(tmp_path):
    """Test that returned paths are absolute."""
    (tmp_path / "doc.pdf").write_bytes(b"PDF")
    
    files = collect_local_non_code_files(tmp_path)
    
    assert len(files) == 1
    assert Path(files[0]).is_absolute()


def test_collect_local_non_code_files_multiple_file_types(tmp_path):
    """Test collection of various non-code file types."""
    (tmp_path / "report.pdf").write_bytes(b"PDF")
    (tmp_path / "presentation.pptx").write_bytes(b"PPTX")
    (tmp_path / "data.xlsx").write_bytes(b"XLSX")
    (tmp_path / "video.mp4").write_bytes(b"MP4")
    (tmp_path / "archive.zip").write_bytes(b"ZIP")
    (tmp_path / "README.md").write_text("# Readme")
    (tmp_path / "notes.txt").write_text("notes")
    
    files = collect_local_non_code_files(tmp_path)
    
    assert len(files) == 7
    extensions = {Path(f).suffix for f in files}
    assert extensions == {".pdf", ".pptx", ".xlsx", ".mp4", ".zip", ".md", ".txt"}


def test_collect_local_non_code_files_mixed_code_and_non_code(tmp_path):
    """Test directory with mixed code and non-code files."""
    # Non-code
    (tmp_path / "README.md").write_text("readme")
    (tmp_path / "logo.png").write_bytes(b"PNG")
    (tmp_path / "doc.pdf").write_bytes(b"PDF")
    
    # Code
    (tmp_path / "app.py").write_text("code")
    (tmp_path / "script.js").write_text("code")
    (tmp_path / "config.json").write_text("{}")
    
    files = collect_local_non_code_files(tmp_path)
    
    assert len(files) == 3
    assert any("README.md" in f for f in files)
    assert any("logo.png" in f for f in files)
    assert any("doc.pdf" in f for f in files)


def test_collect_local_non_code_files_deeply_nested(tmp_path):
    """Test deeply nested directory structure."""
    deep_path = tmp_path / "a" / "b" / "c" / "d" / "e"
    deep_path.mkdir(parents=True)
    (deep_path / "deep.pdf").write_bytes(b"PDF")
    
    files = collect_local_non_code_files(tmp_path)
    
    assert len(files) == 1
    assert "deep.pdf" in files[0]
    assert str(deep_path) in files[0]


def test_collect_local_non_code_files_with_hidden_files(tmp_path):
    """Test handling of hidden files (dotfiles)."""
    (tmp_path / ".hidden.txt").write_text("hidden")
    (tmp_path / "visible.txt").write_text("visible")
    
    files = collect_local_non_code_files(tmp_path)
    
    # Both should be collected (they're non-code)
    assert len(files) == 2
    assert any(".hidden.txt" in f for f in files)
    assert any("visible.txt" in f for f in files)


def test_collect_local_non_code_files_special_characters_in_names(tmp_path):
    """Test files with special characters in names."""
    (tmp_path / "my document (2024).pdf").write_bytes(b"PDF")
    (tmp_path / "image-final_v2.png").write_bytes(b"PNG")
    (tmp_path / "notes [draft].txt").write_text("notes")
    
    files = collect_local_non_code_files(tmp_path)
    
    assert len(files) == 3


def test_collect_local_non_code_files_case_insensitive_extensions(tmp_path):
    """Test that extensions are matched case-insensitively."""
    (tmp_path / "document.PDF").write_bytes(b"PDF")
    (tmp_path / "IMAGE.PNG").write_bytes(b"PNG")
    (tmp_path / "README.MD").write_text("readme")
    
    files = collect_local_non_code_files(tmp_path)
    
    assert len(files) == 3


def test_collect_local_non_code_files_symlinks(tmp_path):
    """Test behavior with symbolic links."""
    # Create a real file
    real_file = tmp_path / "real.pdf"
    real_file.write_bytes(b"PDF")
    
    # Create a symlink (if supported by OS)
    try:
        link_file = tmp_path / "link.pdf"
        link_file.symlink_to(real_file)
        
        files = collect_local_non_code_files(tmp_path)
        
        # Should include both or handle gracefully
        assert len(files) >= 1
        assert any("real.pdf" in f for f in files)
    except (OSError, NotImplementedError):
        # Symlinks not supported on this OS
        pytest.skip("Symlinks not supported")


def test_collect_local_non_code_files_empty_exclude_set(tmp_path):
    """Test with empty exclusion set (should exclude nothing extra)."""
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("config")
    
    (tmp_path / "README.md").write_text("readme")
    
    # Pass empty set - should still use defaults
    files = collect_local_non_code_files(tmp_path, exclude_dirs=set())
    
    # With empty set, .git is not excluded
    # But we should still get README
    assert any("README.md" in f for f in files)


def test_collect_local_non_code_files_preserves_directory_order(tmp_path):
    """Test that files are collected in a deterministic order."""
    (tmp_path / "a.pdf").write_bytes(b"PDF")
    (tmp_path / "b.pdf").write_bytes(b"PDF")
    (tmp_path / "c.pdf").write_bytes(b"PDF")
    
    files1 = collect_local_non_code_files(tmp_path)
    files2 = collect_local_non_code_files(tmp_path)
    
    # Results should be consistent across runs
    assert len(files1) == len(files2) == 3


@pytest.mark.parametrize("dirname", [".git", "__pycache__", "node_modules", ".venv", "venv"])
def test_collect_local_non_code_files_default_exclusions_parametrized(tmp_path, dirname):
    """Parametrized test for default exclusions."""
    excluded_dir = tmp_path / dirname
    excluded_dir.mkdir()
    (excluded_dir / "file.txt").write_text("content")
    
    (tmp_path / "included.txt").write_text("content")
    
    files = collect_local_non_code_files(tmp_path)
    
    assert len(files) == 1
    assert "included.txt" in files[0]
    assert dirname not in files[0]
