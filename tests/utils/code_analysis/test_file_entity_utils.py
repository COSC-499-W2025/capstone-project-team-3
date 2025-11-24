import pytest
from pathlib import Path
from unittest.mock import MagicMock
from app.utils.code_analysis.file_entity_utils import (
    classify_node_types,
    extract_class_names,
    walk_class_nodes,
    extract_single_class,
    extract_classes,
    extract_single_method,
    extract_methods_from_class,
    extract_method_name,
    extract_method_parameters,
    extract_method_calls,
    extract_functions,
    extract_entities,
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

def test_extract_single_class_structure():
    """Verify extract_single_class returns the correct structured fields."""
    text = '"""Doc""" class Foo {}'
    identifier = make_node("identifier", text, 12, 15)
    class_node = make_node("class", text, 10, len(text), [identifier])

    extracted = extract_single_class(class_node, text, set(), Path("foo.py"))

    assert isinstance(extracted, dict)
    assert "name" in extracted
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


def test_extract_methods_from_class_including_decorated():
    """Ensure extract_methods_from_class finds direct and decorated methods inside various body node types."""
    text = (
        'class Foo:\n'
        '    @decor\n'
        '    def bar(a, self): pass\n'
        '    def baz(x): pass'
    )
    # bar method (decorated definition wrapper)
    bar_name_idx = text.index('bar')
    bar_name = make_node('identifier', text, bar_name_idx, bar_name_idx + 3)
    bar_param_a_idx = text.index('(a') + 1
    bar_param_a = make_node('identifier', text, bar_param_a_idx, bar_param_a_idx + 1)
    bar_param_self_idx = text.index('self')
    bar_param_self = make_node('identifier', text, bar_param_self_idx, bar_param_self_idx + 4)
    bar_param_list = make_node('parameter_list', text, text.index('('), text.index(')') + 1, [bar_param_a, bar_param_self])
    inner_bar_fn = make_node('function_definition', text, text.index('def bar'), text.index('pass') + 4, [bar_name, bar_param_list], start_line=1, end_line=1)
    decorated_bar = make_node('decorated_definition', text, text.index('@decor'), text.index('pass') + 4, [inner_bar_fn])
    # baz method
    baz_name_idx = text.index('baz(')
    baz_name = make_node('identifier', text, baz_name_idx, baz_name_idx + 3)
    baz_param_x_idx = text.index('x)')
    baz_param_x = make_node('identifier', text, baz_param_x_idx, baz_param_x_idx + 1)
    baz_param_list = make_node('parameter_list', text, text.index('('), text.index(')') + 1, [baz_param_x])
    baz_fn = make_node('function_definition', text, text.index('def baz'), text.rindex('pass') + 4, [baz_name, baz_param_list], start_line=2, end_line=2)
    # class body container
    class_body = make_node('class_body', text, text.index('\n    @decor'), len(text), [decorated_bar, baz_fn])
    class_node = make_node('class_declaration', text, 0, len(text), [class_body])
    methods = extract_methods_from_class(class_node, text, {'function_definition'}, Path('foo.py'))
    names = sorted(m['name'] for m in methods)
    assert names == ['bar', 'baz']
    # ensure implicit receiver 'self' removed, 'a' kept
    bar_entity = next(m for m in methods if m['name'] == 'bar')
    assert bar_entity['parameters'] == ['a']


def test_extract_method_name_nested():
    """Method name nested one level deep should be found."""
    text = 'def wrapper;'
    inner_name_idx = text.index('wrapper')
    inner_name = make_node('identifier', text, inner_name_idx, inner_name_idx + 7)
    wrapper = make_node('declarator', text, inner_name_idx, inner_name_idx + 7, [inner_name])
    fn = make_node('function_definition', text, 0, len(text), [wrapper])
    assert extract_method_name(fn, text) == 'wrapper'


def test_extract_method_parameters_nested_and_cleanup():
    """Parameters nested under wrapper and implicit receivers removed and deduplicated."""
    text = 'def f(self, this, a, a): pass'
    a1_idx = text.index('a, a')
    a1 = make_node('identifier', text, a1_idx, a1_idx + 1)
    a2_idx = a1_idx + 3
    a2 = make_node('identifier', text, a2_idx, a2_idx + 1)
    self_idx = text.index('self')
    self_node = make_node('identifier', text, self_idx, self_idx + 4)
    this_idx = text.index('this')
    this_node = make_node('identifier', text, this_idx, this_idx + 4)
    inner_container = make_node('parameter_list', text, text.index('('), text.index(')') + 1, [self_node, this_node, a1, a2])
    wrapper = make_node('declarator', text, text.index('('), text.index(')') + 1, [inner_container])
    fn = make_node('function_definition', text, 0, len(text), [wrapper])
    params = extract_method_parameters(fn, text)
    assert params == ['a']


def test_extract_method_calls_variants_and_filters():
    """Extract calls from direct, nested attribute, and filter duplicates/single char/numeric."""
    text = 'alpha(); obj.beta(); gamma(); alpha(); a(); 123();'
    # Direct alpha call
    alpha_idx = text.index('alpha(')
    alpha_id = make_node('identifier', text, alpha_idx, alpha_idx + 5)
    alpha_call = make_node('call_expression', text, alpha_idx, alpha_idx + 7, [alpha_id])
    # Attribute call obj.beta()
    beta_idx = text.index('beta(')
    beta_id = make_node('property_identifier', text, beta_idx, beta_idx + 4)
    attr_expr = make_node('attribute_expression', text, beta_idx, beta_idx + 4, [beta_id])
    beta_call = make_node('call_expression', text, beta_idx, beta_idx + 6, [attr_expr])
    # gamma call
    gamma_idx = text.index('gamma(')
    gamma_id = make_node('identifier', text, gamma_idx, gamma_idx + 5)
    gamma_call = make_node('call_expression', text, gamma_idx, gamma_idx + 7, [gamma_id])
    # duplicate alpha second occurrence
    alpha2_idx = text.rindex('alpha(')
    alpha2_id = make_node('identifier', text, alpha2_idx, alpha2_idx + 5)
    alpha2_call = make_node('call_expression', text, alpha2_idx, alpha2_idx + 7, [alpha2_id])
    # single char a()
    a_idx = text.index('a();')
    a_id = make_node('identifier', text, a_idx, a_idx + 1)
    a_call = make_node('call_expression', text, a_idx, a_idx + 4, [a_id])
    # numeric 123() should be ignored
    n_idx = text.index('123(')
    n_id = make_node('identifier', text, n_idx, n_idx + 3)
    n_call = make_node('call_expression', text, n_idx, n_idx + 5, [n_id])
    fn = make_node('function_definition', text, 0, len(text), [alpha_call, beta_call, gamma_call, alpha2_call, a_call, n_call])
    calls = extract_method_calls(fn, text)
    assert calls == ['alpha', 'beta', 'gamma']


def test_extract_functions_free_standing_and_fallback():
    """Verify free-standing functions detected and fallback heuristic catches unknown types."""
    text = 'def foo(x): pass\nfunction bar(y): pass'
    # foo function (recognized type)
    foo_name_idx = text.index('foo')
    foo_name = make_node('identifier', text, foo_name_idx, foo_name_idx + 3)
    foo_param_idx = text.index('x')
    foo_param = make_node('identifier', text, foo_param_idx, foo_param_idx + 1)
    foo_param_list = make_node('parameter_list', text, text.index('('), text.index(')') + 1, [foo_param])
    foo_fn = make_node('function_definition', text, text.index('def'), text.index('pass') + 4, [foo_name, foo_param_list], start_line=0, end_line=0)
    # bar function (fallback detection: unknown node type with params + body)
    bar_name_idx = text.index('bar')
    bar_name = make_node('identifier', text, bar_name_idx, bar_name_idx + 3)
    bar_param_idx = text.index('y')
    bar_param = make_node('identifier', text, bar_param_idx, bar_param_idx + 1)
    bar_param_list = make_node('parameters', text, text.index('(y'), text.index('(y') + 3, [bar_param])
    body_block = make_node('block', text, text.index('bar'), text.rindex('pass') + 4, [])
    bar_unknown = make_node('unknown_wrapper', text, text.index('function'), text.rindex('pass') + 4, [bar_name, bar_param_list, body_block], start_line=1, end_line=1)
    root = make_node('root', text, 0, len(text), [foo_fn, bar_unknown])
    funcs = extract_functions(root, text, ['function_definition'], ['class_declaration'], Path('foo.py'))
    names = sorted(f['name'] for f in funcs if f['name'])
    assert names == ['bar', 'foo']


def test_extract_functions_no_nested_inside_class():
    """Ensure functions inside class are not returned as free-standing."""
    text = 'class C { def inner(): pass } def outer(): pass'
    inner_name_idx = text.index('inner')
    inner_name = make_node('identifier', text, inner_name_idx, inner_name_idx + 5)
    inner_param_list = make_node('parameter_list', text, text.index('()'), text.index('()') + 2, [])
    inner_fn = make_node('function_definition', text, text.index('def inner'), text.index('pass') + 4, [inner_name, inner_param_list])
    class_node = make_node('class_declaration', text, text.index('class'), text.index('}') + 1, [inner_fn])
    outer_name_idx = text.index('outer')
    outer_name = make_node('identifier', text, outer_name_idx, outer_name_idx + 5)
    outer_param_list = make_node('parameter_list', text, text.rindex('()'), text.rindex('()') + 2, [])
    outer_fn = make_node('function_definition', text, text.index('def outer'), len(text), [outer_name, outer_param_list])
    root = make_node('root', text, 0, len(text), [class_node, outer_fn])
    funcs = extract_functions(root, text, ['function_definition'], ['class_declaration'], Path('foo.py'))
    names = [f['name'] for f in funcs if f['name']]
    assert names == ['outer']


def test_extract_entities_structure():
    """Extract entities returns expected structured keys and includes both classes & functions."""
    text = 'class D { def m(): pass } def f(): pass'
    m_name_idx = text.index('m')
    m_name = make_node('identifier', text, m_name_idx, m_name_idx + 1)
    m_param_list = make_node('parameter_list', text, text.index('()'), text.index('()') + 2, [])
    m_fn = make_node('function_definition', text, text.index('def m'), text.index('pass') + 4, [m_name, m_param_list])
    class_node = make_node('class_declaration', text, text.index('class'), text.index('}') + 1, [m_fn])
    f_name_idx = text.index('f():')
    f_name = make_node('identifier', text, f_name_idx, f_name_idx + 1)
    f_param_list = make_node('parameter_list', text, text.rindex('()'), text.rindex('()') + 2, [])
    f_fn = make_node('function_definition', text, text.index('def f'), len(text), [f_name, f_param_list])
    root = make_node('root', text, 0, len(text), [class_node, f_fn])
    tree_mock = MagicMock()
    tree_mock.root_node = root
    entities = extract_entities(tree_mock, text, ['class_declaration'], ['function_definition'], [], Path('foo.py'))
    assert set(entities.keys()) == {'classes', 'functions', 'components'}
    assert entities['components'] == []
    assert len(entities['classes']) == 1
    assert len(entities['functions']) == 1
