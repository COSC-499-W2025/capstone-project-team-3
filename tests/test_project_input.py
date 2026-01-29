from app.utils.scan_utils import (
    run_scan_flow,
    scan_project_files,
    extract_file_metadata,
    get_project_signature,
    extract_file_signature,
    store_project_in_db,
    project_signature_exists,
    get_all_file_signatures_from_db,
    extract_project_timestamps
)
from pathlib import Path
from unittest.mock import patch
from datetime import datetime
from app.data.db import get_connection

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
        
def test_run_scan_flow_returns_files_and_stores_in_db(tmp_path):
    """Test that run_scan_flow returns the correct files and stores signatures in DB."""
    # Create some files in the temp directory
    (tmp_path / "a.py").write_text("print('a')")
    (tmp_path / "b.txt").write_text("hello")
    (tmp_path / "ignore.mp3").write_text("audio")

    # Exclude .mp3 files by default 
    scan_result = run_scan_flow(str(tmp_path), exclude=[])
    files = scan_result["files"]
    file_names = [f.name for f in files]

    # Should include a.py and b.txt, but not ignore.mp3
    assert "a.py" in file_names
    assert "b.txt" in file_names
    assert "ignore.mp3" not in file_names

    # Check that the project signature is now in the DB
    file_sigs = [extract_file_signature(f, tmp_path) for f in files]
    proj_sig = get_project_signature(file_sigs)
    assert project_signature_exists(proj_sig) is True
    
def test_extract_project_timestamps(tmp_path):
    """Test that project timestamps are correctly extracted from directory."""
    # Create a test file to ensure the directory has some content
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")
    
    # Extract timestamps
    timestamps = extract_project_timestamps(tmp_path)
    
    # Verify structure
    assert "created_at" in timestamps
    assert "last_modified" in timestamps
    assert isinstance(timestamps["created_at"], datetime)
    assert isinstance(timestamps["last_modified"], datetime)
    
    # Verify timestamps are recent (within last hour)
    now = datetime.now()
    time_diff_created = abs((now - timestamps["created_at"]).total_seconds())
    time_diff_modified = abs((now - timestamps["last_modified"]).total_seconds())
    
    assert time_diff_created < 3600  # Less than 1 hour
    assert time_diff_modified < 3600  # Less than 1 hour

def test_store_project_with_custom_timestamps(tmp_path):
    """Test storing project with specific timestamps."""
    # Create test file
    test_file = tmp_path / "timestamp_test.py"
    test_file.write_text("print('timestamp test')")
    
    # Create custom timestamps
    custom_created = datetime(2024, 1, 15, 10, 30, 0)
    custom_modified = datetime(2024, 11, 25, 14, 45, 0)
    
    # Generate signatures
    file_sig = extract_file_signature(test_file, tmp_path)
    project_sig = get_project_signature([file_sig])
    
    # Store with custom timestamps
    store_project_in_db(
        project_sig,
        "TimestampTestProject", 
        str(tmp_path),
        [file_sig],
        test_file.stat().st_size,
        custom_created,
        custom_modified
    )
    
    # Verify project exists
    assert project_signature_exists(project_sig)
    
    # Verify timestamps were stored correctly
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT created_at, last_modified FROM PROJECT 
        WHERE project_signature = ?
    """, (project_sig,))
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None
    stored_created = row[0]
    stored_modified = row[1]
    
    # Check that our custom timestamps are in the stored values
    assert "2024-01-15" in str(stored_created)
    assert "10:30" in str(stored_created)
    assert "2024-11-25" in str(stored_modified)
    assert "14:45" in str(stored_modified)

def test_run_scan_flow_with_real_timestamps(tmp_path):
    """Test that run_scan_flow extracts and stores real directory timestamps."""
    # Create test files
    (tmp_path / "main.py").write_text("print('main')")
    (tmp_path / "utils.py").write_text("def helper(): pass")
    (tmp_path / "README.md").write_text("# Test Project")
    
    # Run the scan flow
    scan_result = run_scan_flow(str(tmp_path), exclude=[])
    files = scan_result["files"]
    # Verify files were found
    assert len(files) == 3
    file_names = [f.name for f in files]
    assert "main.py" in file_names
    assert "utils.py" in file_names
    assert "README.md" in file_names
    
    # Verify project was stored in database
    file_sigs = [extract_file_signature(f, tmp_path) for f in files]
    project_sig = get_project_signature(file_sigs)
    
    assert project_signature_exists(project_sig)
    
    # Verify that timestamps were stored (should be recent)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, created_at, last_modified FROM PROJECT 
        WHERE project_signature = ?
    """, (project_sig,))
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None
    project_name = row[0]
    stored_created = row[1]
    stored_modified = row[2]
    
    # Verify project name matches directory name
    assert project_name == tmp_path.name
    
    # Verify timestamps are not None and contain recent date
    assert stored_created is not None
    assert stored_modified is not None
    current_year = str(datetime.now().year)
    assert current_year in str(stored_created) 
    assert current_year in str(stored_modified)

def test_store_project_without_timestamps_uses_defaults(tmp_path):
    """Test that when no timestamps are provided, current time is used."""
    # Create test file
    test_file = tmp_path / "default_timestamp_test.py" 
    test_file.write_text("print('default test')")
    
    # Generate signatures
    file_sig = extract_file_signature(test_file, tmp_path)
    project_sig = get_project_signature([file_sig])
    
    # Store WITHOUT providing timestamps (should use defaults)
    store_project_in_db(
        project_sig,
        "DefaultTimestampProject",
        str(tmp_path), 
        [file_sig],
        test_file.stat().st_size
        # No created_at or last_modified provided
    )
    
    # Verify project exists
    assert project_signature_exists(project_sig)
    
    # Verify default timestamps were used (should be very recent)
    conn = get_connection()
    cursor = conn.cursor() 
    cursor.execute("""
        SELECT created_at, last_modified FROM PROJECT 
        WHERE project_signature = ?
    """, (project_sig,))
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None
    stored_created = row[0]
    stored_modified = row[1]
    
    # Should contain current date/time (within last few seconds)
    assert stored_created is not None
    assert stored_modified is not None
    
    # Parse the stored timestamps and verify they're recent
    # (This handles different timestamp formats that SQLite might use)
    now = datetime.now()
    assert str(now.year) in str(stored_created)
    assert str(now.month) in str(stored_created) or f"{now.month:02d}" in str(stored_created)

def test_project_db_schema_has_timestamp_columns():
    """Test that the PROJECT table has the required timestamp columns."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get table schema
    cursor.execute("PRAGMA table_info(PROJECT)")
    columns = cursor.fetchall()
    conn.close()
    
    column_names = [col[1] for col in columns]  # col[1] is the column name
    
    # Verify timestamp columns exist
    assert "created_at" in column_names
    assert "last_modified" in column_names
    
    # Get column details for timestamp columns
    created_at_col = next((col for col in columns if col[1] == "created_at"), None)
    modified_col = next((col for col in columns if col[1] == "last_modified"), None)
    
    assert created_at_col is not None
    assert modified_col is not None
    
    # Verify they're TIMESTAMP type (col[2] is the type)
    assert "TIMESTAMP" in created_at_col[2].upper()
    assert "TIMESTAMP" in modified_col[2].upper()

def test_calculate_project_similarity():
    """Test the similarity calculation helper function."""
    from app.utils.scan_utils import calculate_project_similarity
    
    # Test identical projects
    sigs1 = ["file1", "file2", "file3"]
    sigs2 = ["file1", "file2", "file3"]
    assert calculate_project_similarity(sigs1, sigs2) == 100.0
    
    # Test partial overlap (50%)
    sigs1 = ["file1", "file2", "file3"]
    sigs2 = ["file1", "file2", "file4"]
    expected = (2 / 4) * 100  # 2 common / 4 total
    assert calculate_project_similarity(sigs1, sigs2) == expected
    
    # Test no overlap
    sigs1 = ["file1", "file2"]
    sigs2 = ["file3", "file4"]
    assert calculate_project_similarity(sigs1, sigs2) == 0.0
    
    # Test empty lists
    assert calculate_project_similarity([], ["file1"]) == 0.0
    assert calculate_project_similarity(["file1"], []) == 0.0

def test_find_and_update_similar_project_no_projects():
    """Test similarity function when no projects exist."""
    from app.utils.scan_utils import find_and_update_similar_project
    result = find_and_update_similar_project(["file1", "file2"], "test_sig_123", threshold=20.0)
    assert result is None

def test_find_and_update_similar_project_integration(tmp_path):
    """Test that similar projects are found and updated correctly."""
    from app.utils.scan_utils import (
        find_and_update_similar_project,
        extract_file_signature,
        get_project_signature,
        store_project_in_db
    )
    
    # Create initial project with 2 files
    file1 = tmp_path / "original1.txt"
    file2 = tmp_path / "original2.txt"
    file1.write_text("original content 1")
    file2.write_text("original content 2")
    
    sig1 = extract_file_signature(file1, tmp_path)
    sig2 = extract_file_signature(file2, tmp_path)
    old_project_sig = get_project_signature([sig1, sig2])
    
    # Store initial project
    store_project_in_db(old_project_sig, "TestProject", str(tmp_path), [sig1, sig2], 100)
    
    # Now upload similar project with 1 shared file + 1 new file
    file3 = tmp_path / "new_file.txt"
    file3.write_text("new content")
    sig3 = extract_file_signature(file3, tmp_path)
    
    # New upload's signatures and pre-calculated project signature
    new_upload_sigs = [sig1, sig3]
    new_project_sig = get_project_signature(new_upload_sigs)
    
    # Test similarity detection (sig1 is shared, sig3 is new)
    # Jaccard similarity = intersection / union = 1 / 3 = 33.3%
    # But due to DB state from previous tests, similarity might vary
    result = find_and_update_similar_project(new_upload_sigs, new_project_sig, threshold=20.0)
    
    assert result is not None
    project_name, similarity, returned_sig = result
    assert project_name == "TestProject"
    assert similarity >= 20.0  # Should meet threshold
    
    # The returned signature should be the new project signature we passed in
    assert returned_sig == new_project_sig
    assert returned_sig != old_project_sig  # Signature should have changed

def test_find_and_update_similar_project_default_threshold():
    """Test that the default threshold is 70%."""
    from app.utils.scan_utils import find_and_update_similar_project
    import inspect
    
    # Get the function signature
    sig = inspect.signature(find_and_update_similar_project)
    default_threshold = sig.parameters['threshold'].default
    
    # Verify default is 70%
    assert default_threshold == 70.0