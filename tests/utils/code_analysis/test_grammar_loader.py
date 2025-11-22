import pytest
from pathlib import Path
from app.utils.code_analysis.grammar_loader import extract_rule_names


def test_extract_basic_rules(tmp_path):
    """Extracts simple top-level rule names."""
    content = """
    module.exports = grammar({
      rules: {
        ruleA: $ => 'a',
        ruleB: $ => seq('b'),
        ruleC: $ => choice('c')
      },
    });
    """
    path = tmp_path / "grammar.js"
    path.write_text(content)

    assert extract_rule_names(path) == ["ruleA", "ruleB", "ruleC"]


def test_ignores_internal_rules(tmp_path):
    """Ensures rule names including underscores are returned."""
    content = """
    rules: {
      _internal: $ => 'x',
      visible: $ => 'y'
    }
    """
    path = tmp_path / "grammar.js"
    path.write_text(content)

    assert extract_rule_names(path) == ["_internal", "visible"]


def test_extract_rule_names_deduplicates(tmp_path):
    """Ensures duplicate rule names are removed preserving order."""
    content = """
    rules: {
      alpha: $ => 'a',
      beta:  $ => 'b',
      alpha: $ => 'overwritten'
    }
    """
    path = tmp_path / "grammar.js"
    path.write_text(content)

    assert extract_rule_names(path) == ["alpha", "beta"]


def test_no_rules_block_returns_empty(tmp_path):
    """Returns empty list when no rules block is found."""
    path = tmp_path / "grammar.js"
    path.write_text("module.exports = grammar({ name: 'x' });")

    assert extract_rule_names(path) == []
    
def test_nested_objects_dont_create_fake_rules(tmp_path):
    """Ensures nested object keys are not treated as rule names."""
    content = """
    rules: {
      with_statement: $ => seq(
      optional('async'),
      'with',
      $.with_clause,
      ':',
      field('body', $._suite),
    ),

    with_clause: $ => choice(
      seq(commaSep1($.with_item), optional(',')),
      seq('(', commaSep1($.with_item), optional(','), ')'),
    ),'
    }
    """
    path = tmp_path / "grammar.js"
    path.write_text(content)

    assert extract_rule_names(path) == ["with_statement", "with_clause"]
