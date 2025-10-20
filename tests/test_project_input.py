from app.utils.scan_utils import scan_project_files

def test_scan_project_files_excludes_patterns(tmp_path):
    """Test that files matching exclude patterns are not returned."""
    # Setup: create files of various types
    (tmp_path / "file1.py").write_text("print('hello')")
    (tmp_path / "file2.jpg").write_text("fake image")
    (tmp_path / "file3.pdf").write_text("fake pdf")
    (tmp_path / "file4.txt").write_text("hello txt")

    # Call the utility directly
    files = scan_project_files(tmp_path, exclude_patterns=["*.jpg", "*.pdf"])
    file_names = [f.name for f in files]

    assert "file1.py" in file_names
    assert "file4.txt" in file_names
    assert "file2.jpg" not in file_names
    assert "file3.pdf" not in file_names
    
def test_scan_project_files_empty_dir(tmp_path):
    """Test that scanning an empty directory returns an empty list."""
    files = scan_project_files(tmp_path)
    assert files == []

def test_scan_project_files_excludes_hidden_and_system(tmp_path):
    """Test that hidden/system files can be excluded."""
    (tmp_path / ".DS_Store").write_text("system file")
    (tmp_path / "normal.txt").write_text("normal file")
    files = scan_project_files(tmp_path, exclude_patterns=[".DS_Store"])
    file_names = [f.name for f in files]
    assert "normal.txt" in file_names
    assert ".DS_Store" not in file_names

def test_scan_project_files_nested_dirs(tmp_path):
    """Test that files in nested directories are scanned and exclusions apply."""
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "file5.py").write_text("print('nested')")
    (subdir / "file6.mp3").write_text("audio")
    files = scan_project_files(tmp_path, exclude_patterns=["*.mp3"])
    file_names = [f.name for f in files]
    assert "file5.py" in file_names
    assert "file6.mp3" not in file_names

def test_scan_project_files_excludes_by_folder(tmp_path):
    """Test that entire folders can be excluded by name."""
    subdir = tmp_path / "node_modules"
    subdir.mkdir()
    (subdir / "lib.js").write_text("js code")
    (tmp_path / "main.py").write_text("main code")
    files = scan_project_files(tmp_path, exclude_patterns=["node_modules"])
    file_names = [f.name for f in files]
    assert "main.py" in file_names
    assert "lib.js" not in file_names
    
def test_extract_file_metadata(tmp_path):
    """Test metadata extraction for a single file."""
    file = tmp_path / "test.txt"
    file.write_text("hello")
    from app.utils.scan_utils import extract_file_metadata
    metadata = extract_file_metadata(file)
    assert metadata["file_name"] == "test.txt"
    assert metadata["file_path"].endswith("test.txt")
    assert metadata["size_bytes"] == 5
    assert "created_at" in metadata
    assert "last_modified" in metadata

def test_get_project_metadata_signature_consistency():
    """Test that the signature is consistent for the same metadata list."""
    from app.utils.scan_utils import get_project_metadata_signature
    metadata_list = [
        {"file_path": "/a/b.txt", "last_modified": 123},
        {"file_path": "/a/c.txt", "last_modified": 456},
    ]
    sig1 = get_project_metadata_signature(metadata_list)
    sig2 = get_project_metadata_signature(list(reversed(metadata_list)))
    assert sig1 == sig2  # Order should not matter

def test_full_scan_and_signature(tmp_path):
    """Test scanning, metadata extraction, and signature generation together."""
    (tmp_path / "a.py").write_text("print(1)")
    (tmp_path / "b.txt").write_text("hello")
    from app.utils.scan_utils import scan_project_files, extract_file_metadata, get_project_metadata_signature
    files = scan_project_files(tmp_path)
    metadata_list = [extract_file_metadata(f) for f in files]
    signature = get_project_metadata_signature(metadata_list)
    assert isinstance(signature, str)
    assert len(signature) == 64  # sha256 hex digest length