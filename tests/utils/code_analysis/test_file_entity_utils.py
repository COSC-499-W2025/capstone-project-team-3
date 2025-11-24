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
    extract_single_method,
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

def make_node(type_name, text, start, end, children=None, start_line=0, end_line=None):
    """Create a mocked Tree-sitter Node with minimal attributes required by utilities."""
    node = MagicMock()
    node.type = type_name
    node.start_byte = start
    node.end_byte = end
    # Provide line/column tuples used for LOC calculations
    node.start_point = (start_line, 0)
    node.end_point = (end_line if end_line is not None else start_line, 0)
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
    # Added empty function_types set to match updated signature
    walk_class_nodes(node, text, {"class_declaration"}, set(), out, Path("foo.js"))

    assert len(out) == 1
    assert "methods" in out[0]

def test_extract_classes():
    """Verify extract_classes invokes walk_class_nodes and returns formatted class dicts."""
    text = "class Foo {}"
    class_node = make_node("class_declaration", text, 0, len(text), [])
    root = make_node("root", text, 0, len(text), [class_node])

    results = extract_classes(root, text, ["class_declaration"], [], Path("foo.js"))

    assert len(results) == 1
    assert "name" in results[0]
    assert "docstring" in results[0]

def test_extract_single_class_structure():
    """Verify extract_single_class returns the correct structured fields."""
    text = '"""Doc""" class Foo {}'
    identifier = make_node("identifier", text, 12, 15)
    class_node = make_node("class", text, 10, len(text), [identifier])

    extracted = extract_single_class(class_node, text, set(), Path("foo.py"))

    assert isinstance(extracted, dict)
    assert "name" in extracted
    assert "docstring" in extracted
    assert "methods" in extracted
    assert extracted["methods"] == []

def test_extract_single_class_with_method():
    """Ensure a class containing a method yields method entity details."""
    text = 'class Foo:\n    def bar(x): if x: baz()'
    # Method name identifier
    name_idx = text.index('bar')
    name_node = make_node('identifier', text, name_idx, name_idx + 3)
    # Parameter identifier inside parameter_list container
    param_idx = text.index('x')
    param_node = make_node('identifier', text, param_idx, param_idx + 1)
    param_container_start = text.index('(')
    param_container_end = text.index(')') + 1
    param_container = make_node('parameter_list', text, param_container_start, param_container_end, [param_node])
    # Call node for baz()
    call_idx = text.index('baz(')
    callee_identifier = make_node('identifier', text, call_idx, call_idx + 3)
    call_node = make_node('call_expression', text, call_idx, call_idx + 7, [callee_identifier])
    # Method node aggregates name + params + call
    method_start = text.index('def')
    method_node = make_node('function_definition', text, method_start, len(text), [name_node, param_container, call_node], start_line=1, end_line=1)
    class_start = text.index('class')
    class_node = make_node('class_declaration', text, class_start, len(text), [method_node])

    extracted = extract_single_class(class_node, text, {'function_definition'}, Path('foo.py'))

    assert extracted['methods']
    method = extracted['methods'][0]
    assert method['name'] == 'bar'
    assert method['parameters'] == ['x']
    assert method['lines_of_code'] == 1
    assert 'calls' in method and method['calls'] == ['baz']
    assert method['complexity'] >= 2  # "if" adds complexity

def test_extract_single_method_direct():
    """Directly test method entity extraction utility."""
    text = 'def qux(y): if y: alpha(); beta()'
    name_idx = text.index('qux')
    name_node = make_node('identifier', text, name_idx, name_idx + 3)
    param_idx = text.index('y')
    param_node = make_node('identifier', text, param_idx, param_idx + 1)
    param_container = make_node('parameter_list', text, text.index('('), text.index(')') + 1, [param_node])
    # Two call expressions alpha() and beta()
    alpha_idx = text.index('alpha(')
    alpha_identifier = make_node('identifier', text, alpha_idx, alpha_idx + 5)
    alpha_call = make_node('call_expression', text, alpha_idx, alpha_idx + 7, [alpha_identifier])
    beta_idx = text.index('beta(')
    beta_identifier = make_node('identifier', text, beta_idx, beta_idx + 4)
    beta_call = make_node('call_expression', text, beta_idx, beta_idx + 6, [beta_identifier])
    method_start = text.index('def')
    method_node = make_node('function_definition', text, method_start, len(text), [name_node, param_container, alpha_call, beta_call], start_line=0, end_line=0)

    method_entity = extract_single_method(method_node, text, Path('foo.py'))

    assert method_entity['name'] == 'qux'
    assert method_entity['parameters'] == ['y']
    assert method_entity['calls'] == ['alpha', 'beta']
    assert method_entity['complexity'] >= 2  # "if" keyword counted
