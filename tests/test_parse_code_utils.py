import pytest
from pathlib import Path
from app.utils.code.parse_code_utils import (detect_language,
                                             count_lines_of_code,
                                             count_lines_of_documentation,
                                             extract_contents)

@pytest.fixture
def sample_file(tmp_path):
    """Create a sample Python file for testing."""
    file_path = tmp_path / "test.py"
    content = '"""\nSample docstring\n"""\nprint("Hello")\n'
    file_path.write_text(content)
    return file_path, content

def test_detect_language(sample_file):
    """
    Test for detecting a language in the given file.
    """
    file_path, _ = sample_file
    language = detect_language(file_path)
    assert language.lower() == "python"

def test_count_lines_of_code(sample_file):
    """
    Test for counting the number of code lines in a file.
    """
    file_path, _ = sample_file
    count = count_lines_of_code(file_path)
    assert count == 1  # Only the print line is code

def test_count_lines_of_documentation(sample_file):
    """
    Test for counting the number of documentation lines in a file.
    """
    file_path, _ = sample_file
    count = count_lines_of_documentation(file_path)
    assert count == 3  # Docstring lines

def test_extract_contents(sample_file):
    """
    Test for extracting the full contents of a file.
    """
    file_path, content = sample_file
    extracted = extract_contents(file_path)
    assert extracted == content
