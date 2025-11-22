import pytest
from pathlib import Path
from unittest.mock import MagicMock
from app.utils.code_analysis.file_entity_utils import (
    classify_node_types,
    extract_class_names,
    extract_doc_blocks_from_text,
    match_docs_to_node,
    extract_docstrings,
    walk_class_nodes,
    extract_single_class,
    extract_classes,
)

def test_classify_node_types():
    """Ensure grammar rule names are classified into class, function, and component types."""
    rules = [
        "class_declaration",
        "function_definition",
        "jsx_element",
        "enum_specifier",
        "_internal_pattern",
        "method_signature",
    ]

    classes, functions, components = classify_node_types(rules)

    assert "class_declaration" in classes
    assert "enum_specifier" in classes
    assert "function_definition" in functions
    assert "method_signature" in functions
    assert "jsx_element" in components
    assert "_internal_pattern" not in classes

def make_node(type_name, text, start, end, children=None):
    """Create a mocked Tree-sitter Node."""
    node = MagicMock()
    node.type = type_name
    node.start_byte = start
    node.end_byte = end
    node.children = children or []
    return node

def test_extract_class_names_simple():
    """Verify simple class name extraction from a single identifier."""
    text = "class Foo {}"
    id_node = make_node("identifier", text, 6, 9)
    class_node = make_node("class", text, 0, len(text), [id_node])

    result = extract_class_names(class_node, text)

    assert result == ["Foo"]

def test_extract_doc_blocks_from_text_python():
    """Verify Python triple-quoted docstring blocks are extracted."""
    content = '''
        """Class doc"""
        class Foo:
            pass
    '''
    blocks = extract_doc_blocks_from_text(Path("foo.py"), content)

    assert len(blocks) == 1
    assert "Class doc" in blocks[0]


def test_extract_doc_blocks_from_text_comments():
    """Verify comment blocks are grouped together as documentation."""
    content = """
        // This is a comment
        // Another comment
        class Foo {}
    """
    blocks = extract_doc_blocks_from_text(Path("foo.js"), content)
    assert len(blocks) >= 1
    combined = blocks[0]
    assert "This is a comment" in combined

def test_match_docs_to_node_attaches_preceding_block():
    """Ensure doc blocks immediately preceding a node are attached to it."""
    text = """
    /** Doc block */ class Foo {}
    """
    doc_blocks = ["/** Doc block */"]

    node = make_node("class", text, text.index("class"), text.index("class") + 5)

    matched = match_docs_to_node(node, text, doc_blocks)

    assert matched is not None
    assert doc_blocks[0] in matched


def test_match_docs_to_node_none():
    """Verify no docs are matched when unrelated blocks exist."""
    text = "class Foo {}"
    result = match_docs_to_node(
        make_node("class", text, 0, len(text)), text, ["// unrelated"]
    )

    assert result is None

def test_extract_docstrings_integration():
    """Ensure extract_docstrings wires block extraction + matching."""
    content = '''
        /** Doc for Foo */ class Foo {}
    '''
    node = make_node("class", content, content.index("class"), len(content))

    docs = extract_docstrings(node, content, Path("foo.js"))

    assert docs is not None
    assert "Doc for Foo" in docs[0]

def test_walk_class_nodes_collects_classes():
    """Verify DFS walk finds class nodes and extracts them."""
    text = "class Foo {}"
    node = make_node("class_declaration", text, 0, len(text), [])

    out = []
    walk_class_nodes(node, text, {"class_declaration"}, out, Path("foo.js"))

    assert len(out) == 1
    assert "methods" in out[0]

def test_extract_classes():
    """Verify extract_classes invokes walk_class_nodes and returns formatted class dicts."""
    text = "class Foo {}"
    class_node = make_node("class_declaration", text, 0, len(text), [])
    root = make_node("root", text, 0, len(text), [class_node])

    results = extract_classes(root, text, ["class_declaration"], Path("foo.js"))

    assert len(results) == 1
    assert "name" in results[0]
    assert "docstring" in results[0]

def test_extract_single_class_structure():
    """Verify extract_single_class returns the correct structured fields."""
    text = '"""Doc""" class Foo {}'
    identifier = make_node("identifier", text, 12, 15)
    class_node = make_node("class", text, 10, len(text), [identifier])

    extracted = extract_single_class(class_node, text, Path("foo.py"))

    assert isinstance(extracted, dict)
    assert "name" in extracted
    assert "docstring" in extracted
    assert "methods" in extracted
    assert extracted["methods"] == []
