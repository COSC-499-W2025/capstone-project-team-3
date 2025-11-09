import pytest
from pathlib import Path
from tree_sitter import Node 
from unittest.mock import MagicMock, patch
from app.utils.code.parse_code_utils import (detect_language,
                                             count_lines_of_code,
                                             count_lines_of_documentation,
                                             extract_contents,
                                             collect_node_types,
                                            traverse_imports,
                                            extract_with_treesitter_dynamic,
                                            extract_imports,
                                            extract_libraries,
                                            map_language_for_treesitter)

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
    
class MockNode:
    """Simple mock for a Tree-sitter Node."""
    def __init__(self, type_, start_byte=0, end_byte=0, children=None):
        self.type = type_
        self.start_byte = start_byte
        self.end_byte = end_byte
        self.children = children or []
        
def test_collect_node_types_nested():
    """Test recursively collecting node types from a tree."""
    root = MockNode("root", children=[
        MockNode("child1"),
        MockNode("child2", children=[MockNode("grandchild")])
    ])
    types = collect_node_types(root)
    assert types == {"root", "child1", "child2", "grandchild"}
    
def test_traverse_imports_collects_import_statement():
    """Test that traverse_imports collects import statements from nodes."""
    content = "import os\nprint('Hi')"
    root = MockNode("root", children=[MockNode("import_statement", start_byte=0, end_byte=10)])
    imports = []
    traverse_imports(root, content, {"import_statement"}, imports)
    assert imports == ["import os"]
    
def test_extract_with_treesitter_dynamic_finds_imports_via_heuristic():
    """Test dynamic extraction when language has no predefined import types."""
    file_content = "require('fs');\nconsole.log('hello');"
    
    # Build mock tree: a 'require_call' node (heuristic will match "require")
    require_node = MockNode("require_call", start_byte=0, end_byte=13)
    root = MockNode("program", children=[require_node])
    
    # Mock Parser to return this tree
    mock_tree = MagicMock()
    mock_tree.root_node = root
    mock_parser = MagicMock()
    mock_parser.parse.return_value = mock_tree

    # Patch _TS_IMPORT_NODES to be empty for this language (forces heuristic)
    with patch("app.utils.code.parse_code_utils._TS_IMPORT_NODES", {}):
        with patch("app.utils.code.parse_code_utils.Parser", return_value=mock_parser):
            # Act
            result = extract_with_treesitter_dynamic(
                file_content, 
                ts_lang="fake_js_lang", 
                language="javascript"  # note: not in _TS_IMPORT_NODES due to patch
            )
    assert result == ["require('fs')"]

def test_map_language_for_treesitter_maps_known_language():
    """Test that map_language_for_treesitter correctly maps known language names to Tree-sitter names."""
    mock_mapping = {"Python": "python", "C++": "cpp"}

    with patch("app.utils.code.parse_code_utils._TS_LANGUAGE_MAPPING", mock_mapping):

        # Should match a known language (case-insensitive)
        assert map_language_for_treesitter("PYTHON") == "python"
        # Should trim whitespace
        assert map_language_for_treesitter("  C++  ") == "cpp"
        # Should fall back to lowercase when not in mapping
        assert map_language_for_treesitter("Rust") == "rust"
        
def test_extract_imports_handles_unsupported_language_gracefully():
    """Test that extract_imports returns empty list when language is unsupported."""
    content = "import x from 'y';"
    with patch("app.utils.code.parse_code_utils.get_language", side_effect=ValueError("Language not supported")):
        result = extract_imports(content, "unknownlang")
    assert result == []
    
def test_extract_imports_falls_back_to_regex_when_treesitter_fails():
    """Test that extract_imports uses regex fallback when Tree-sitter returns no imports."""
    file_content = "const fs = require('fs');"
    language = "javascript"

    # Mock get_language to succeed (so Tree-sitter is attempted)
    # But mock Tree-sitter to return no imports (e.g., parser fails or finds nothing)
    with patch("app.utils.code.parse_code_utils.get_language", return_value="mock_js_lang"):
        with patch("app.utils.code.parse_code_utils.extract_with_treesitter_dynamic", return_value=[]):
            # Provide a regex config for JavaScript that matches 'require'
            mock_regex_config = [{
                "language": "javascript",
                "import_patterns": [r"require\s*\(", r"import\s+.*from"]
            }]
            with patch("app.utils.code.parse_code_utils._TS_IMPORT_REGEX", mock_regex_config):
                result = extract_imports(file_content, language)
    assert result == ["const fs = require('fs');"]
    
def test_extract_libraries_filters_relative_and_extracts_symbols():
    """Test that extract_libraries returns modules and symbols correctly, ignoring relative imports."""
    import_statements = [
        "import os, json",
        "import ./local_module",
        "from pathlib import Path",
        "from typing import Optional,Union"
    ]

    patterns_python = {
        "python": [
            r"from\s+([\w\.]+)\s+import\s+([*\w\.\s,]+)",
            r"import\s+([\w\.]+(?:\s*,\s*[\w\.]+)*)"
        ]
    }

    with patch("app.utils.code.parse_code_utils._TS_IMPORT_QUERIES", patterns_python):
        result = extract_libraries(import_statements, "python")
        
    expected = {'Optional', 'Path', 'Union', 'json', 'os', 'pathlib', 'typing'}
    assert set(result) == expected
