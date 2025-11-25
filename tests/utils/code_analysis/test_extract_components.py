import pytest
from pathlib import Path
from unittest.mock import MagicMock

from app.utils.code_analysis.file_entity_utils import (
    extract_components,
)


def make_node(type_name, text, start, end, children=None, start_line=0, end_line=None):
    """Create a mocked Tree-sitter Node similar to other tests."""
    node = MagicMock()
    node.type = type_name
    node.start_byte = start
    node.end_byte = end
    node.start_point = (start_line, 0)
    node.end_point = (end_line if end_line is not None else start_line, 0)
    node.children = children or []
    return node


def test_function_component_with_jsx_detected():
    """Uppercase function containing JSX should be extracted as a component."""
    text = 'function MyWidget() { return <div /> }'
    name_idx = text.index('MyWidget')
    name_node = make_node('identifier', text, name_idx, name_idx + len('MyWidget'))
    jsx_start = text.index('<div')
    jsx_node = make_node('jsx_element', text, jsx_start, jsx_start + len('<div />'))
    params_node = make_node('parameter_list', text, text.index('('), text.index(')') + 1, [])
    fn_node = make_node('function_definition', text, text.index('function'), len(text), [name_node, params_node, jsx_node])
    root = make_node('root', text, 0, len(text), [fn_node])
    comps = extract_components(root, text, [], Path('MyWidget.jsx'))
    assert any(c['name'] == 'MyWidget' for c in comps)


def test_function_component_requires_jsx():
    """Without JSX an uppercase function (current logic) should NOT be treated as component."""
    text = 'function PlainThing() { const x = 1; }'
    name_idx = text.index('PlainThing')
    name_node = make_node('identifier', text, name_idx, name_idx + len('PlainThing'))
    params_node = make_node('parameter_list', text, text.index('('), text.index(')') + 1, [])
    fn_node = make_node('function_definition', text, text.index('function'), len(text), [name_node, params_node])
    root = make_node('root', text, 0, len(text), [fn_node])
    comps = extract_components(root, text, [], Path('PlainThing.jsx'))
    assert all(c['name'] != 'PlainThing' for c in comps)


def test_class_component_suffix_and_lifecycle():
    """Class with Component suffix and lifecycle-like method should be detected."""
    text = 'class UserCardComponent { ngOnInit() {} likes = 0 }'
    cls_name_idx = text.index('UserCardComponent')
    cls_name = make_node('identifier', text, cls_name_idx, cls_name_idx + len('UserCardComponent'))
    # lifecycle method
    method_name_idx = text.index('ngOnInit')
    method_name = make_node('identifier', text, method_name_idx, method_name_idx + len('ngOnInit'))
    method_node = make_node('method_definition', text, method_name_idx, method_name_idx + len('ngOnInit() {}'), [method_name])
    # field
    field_idx = text.index('likes')
    field_id = make_node('property_identifier', text, field_idx, field_idx + len('likes'))
    field_def = make_node('public_field_definition', text, field_idx, field_idx + len('likes = 0'), [field_id])
    class_body = make_node('class_body', text, text.index('{'), text.index('}') + 1, [method_node, field_def])
    class_node = make_node('class_declaration', text, text.index('class'), len(text), [cls_name, class_body])
    root = make_node('root', text, 0, len(text), [class_node])
    comps = extract_components(root, text, [], Path('UserCardComponent.ts'))
    comp = next((c for c in comps if c['name'] == 'UserCardComponent'), None)
    assert comp is not None
    assert 'likes' in comp['state_variables']
    assert any(h.lower().startswith('ngoninit') for h in comp['hooks_used'])


def test_component_from_grammar_node_type():
    """Grammar-level component node (jsx_element) should produce a component record."""
    text = '<CustomThing attr="x" />'
    tag_idx = text.index('CustomThing')
    tag_name = make_node('identifier', text, tag_idx, tag_idx + len('CustomThing'))
    attr_idx = text.index('attr')
    attr_name = make_node('identifier', text, attr_idx, attr_idx + len('attr'))
    attr_node = make_node('jsx_attribute', text, attr_idx, attr_idx + len('attr="x"'), [attr_name])
    jsx_node = make_node('jsx_element', text, 0, len(text), [tag_name, attr_node])
    root = make_node('root', text, 0, len(text), [jsx_node])
    comps = extract_components(root, text, ['jsx_element'], Path('Inline.jsx'))
    comp = next((c for c in comps if c['name'] == 'CustomThing'), None)
    assert comp is not None
    assert comp['props'] == ['attr']
    assert comp['state_variables'] == []
    assert comp['hooks_used'] == []


def test_extract_components_deduplicates():
    """Duplicate component definitions should be deduplicated by name."""
    text = '<X /> <X />'
    first_x = text.index('X')
    second_x = text.rindex('X')
    x1 = make_node('identifier', text, first_x, first_x + 1)
    jsx1 = make_node('jsx_element', text, first_x - 1, first_x - 1 + len('<X />'), [x1])  # span includes leading '<'
    x2 = make_node('identifier', text, second_x, second_x + 1)
    jsx2 = make_node('jsx_element', text, second_x - 1, second_x - 1 + len('<X />'), [x2])
    root = make_node('root', text, 0, len(text), [jsx1, jsx2])
    comps = extract_components(root, text, ['jsx_element'], Path('Dup.jsx'))
    names = [c['name'] for c in comps]
    assert names.count('X') == 1
