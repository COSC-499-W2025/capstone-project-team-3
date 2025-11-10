from app.utils.scan_utils import (
    scan_project_files,
    extract_file_metadata,
    get_project_signature,
    extract_file_signature,
    store_project_in_db,
    project_signature_exists,
    get_all_file_signatures_from_db,
    calculate_project_score
)
from pathlib import Path
from unittest.mock import patch

def test_scan_project_files_excludes_patterns(tmp_path):
    """Test that files matching exclude patterns are not returned."""
    (tmp_path / "file1.py").write_text("print('hello')")
    (tmp_path / "file2.jpg").write_text("fake image")
    (tmp_path / "file3.pdf").write_text("fake pdf")
    (tmp_path / "file4.txt").write_text("hello txt")
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
    metadata = extract_file_metadata(file)
    assert metadata["file_name"] == "test.txt"
    assert metadata["file_path"].endswith("test.txt")
    assert metadata["size_bytes"] == 5
    assert "created_at" in metadata
    assert "last_modified" in metadata

def test_get_project_signature_consistency(tmp_path):
    """Test that the project signature is consistent for the same file signature list."""
    file1 = tmp_path / "a.txt"
    file2 = tmp_path / "b.txt"
    file1.write_text("a")
    file2.write_text("b")
    sig1 = extract_file_signature(file1, tmp_path)
    sig2 = extract_file_signature(file2, tmp_path)
    sig_list = [sig1, sig2]
    sig1_proj = get_project_signature(sig_list)
    sig2_proj = get_project_signature(list(reversed(sig_list)))
    assert sig1_proj == sig2_proj  # Order should not matter

def test_full_scan_and_signature(tmp_path):
    """Test scanning, file signature extraction, and project signature generation together."""
    (tmp_path / "a.py").write_text("print(1)")
    (tmp_path / "b.txt").write_text("hello")
    files = scan_project_files(tmp_path)
    file_signatures = [extract_file_signature(f, tmp_path) for f in files]
    signature = get_project_signature(file_signatures)
    assert isinstance(signature, str)
    assert len(signature) == 64  # sha256 hex digest length

def test_extract_file_signature(tmp_path):
    """Test that file signature is unique and consistent for the same file."""
    file = tmp_path / "unique.txt"
    file.write_text("data")
    sig1 = extract_file_signature(file, tmp_path)
    sig2 = extract_file_signature(file, tmp_path)
    assert isinstance(sig1, str)
    assert sig1 == sig2
    # Changing file should change signature
    file.write_text("new data")
    sig3 = extract_file_signature(file, tmp_path)
    assert sig1 != sig3

def test_store_and_check_project_signature(tmp_path):
    """Test storing a project in DB and checking its existence."""
    file = tmp_path / "test.txt"
    file.write_text("hello")
    file_sig = extract_file_signature(file, tmp_path)
    signature = get_project_signature([file_sig])
    name = "TestProject"
    path = str(tmp_path.resolve())
    size_bytes = file.stat().st_size
    store_project_in_db(signature, name, path, [file_sig], size_bytes)
    assert project_signature_exists(signature) is True

def test_get_all_file_signatures_from_db(tmp_path):
    """Test retrieving all file signatures from DB."""
    file1 = tmp_path / "a.txt"
    file2 = tmp_path / "b.txt"
    file1.write_text("a")
    file2.write_text("b")
    sig1 = extract_file_signature(file1, tmp_path)
    sig2 = extract_file_signature(file2, tmp_path)
    signature = get_project_signature([sig1, sig2])
    name = "TestProject2"
    path = str(tmp_path.resolve())
    size_bytes = file1.stat().st_size + file2.stat().st_size
    store_project_in_db(signature, name, path, [sig1, sig2], size_bytes)
    sigs = get_all_file_signatures_from_db()
    assert sig1 in sigs
    assert sig2 in sigs

def test_calculate_project_score(tmp_path):
    """Test calculation of project score based on file signatures in DB."""
    # Add one file to DB
    file1 = tmp_path / "score1.txt"
    file2 = tmp_path / "score2.txt"
    file1.write_text("score1")
    file2.write_text("score2")
    sig1 = extract_file_signature(file1, tmp_path)
    sig2 = extract_file_signature(file2, tmp_path)
    signature = get_project_signature([sig1, sig2])
    name = "ScoreProject"
    path = str(tmp_path.resolve())
    size_bytes = file1.stat().st_size + file2.stat().st_size
    store_project_in_db(signature, name, path, [sig1], size_bytes)
    # Now test score calculation
    score = calculate_project_score([sig1, sig2])
    assert score == 50.0  # Only one of two files is already in DB
    
def test_extract_file_signature_error(tmp_path):
    """Test that extract_file_signature returns ERROR_SIGNATURE for missing file."""
    missing_file = tmp_path / "does_not_exist.txt"
    sig = extract_file_signature(missing_file, tmp_path)
    assert sig == "ERROR_SIGNATURE"
    
from unittest.mock import patch
from app.utils.scan_utils import extract_file_signature
from pathlib import Path

def test_extract_file_signature_retries(tmp_path):
    """Test that extract_file_signature retries on error and eventually succeeds."""
    test_file = tmp_path / "retry.txt"
    test_file.write_text("data")
    root = tmp_path

    # Simulate stat raising FileNotFoundError on first call, then succeeding
    original_stat = Path.stat

    call_count = {"count": 0}
    def flaky_stat(self):
        if call_count["count"] == 0:
            call_count["count"] += 1
            raise FileNotFoundError("Simulated transient error")
        return original_stat(self)
    '''
    This uses unittest.mock.patch to temporarily replace Path.stat with 
    flaky_stat to simulate a error on the first attempt but secceeds on the second
    '''
    with patch.object(Path, "stat", flaky_stat):
        sig = extract_file_signature(test_file, root, retries=2)
        assert sig != "ERROR_SIGNATURE"