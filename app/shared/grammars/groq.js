/**
 * @file Query language made at Sanity.io for filtering and projecting JSON documents
 * @author Alan Russell <ajrussellaudio@gmail.com>
 * @license MIT
 */

/// <reference types="tree-sitter-cli/dsl" />
// @ts-check

module.exports = grammar({
  name: 'groq',

  extras: $ => [
    /\s/,
    $.comment,
  ],

  conflicts: $ => [
    [$.object, $.projection],
  ],

  rules: {
    source_file: $ => $._query,

    _query: $ => choice(
      $.pipe_expression,
      $._expression,
    ),

    pipe_expression: $ => prec.left(-1, seq(
      $.expression,
      '|',
      $.expression,
    )),

    _expression: $ => choice(
      $._primary_expression,
      $.unary_expression,
      $.binary_expression,
      $.attribute_access,
    ),

    expression: $ => $._expression,

    attribute_access: $ => prec.left(9, seq(
      $.expression,
      choice(
        seq('.', $.identifier),
        seq('->', optional($.identifier)),
        seq('[', optional($._query), ']'),
        $.projection,
      ),
    )),

    _primary_expression: $ => choice(
      $.parent,
      $.this,
      $.star,
      $.identifier,
      $.literal,
      $.array,
      $.object,
      $.projection,
      $.parenthesis_expression,
      $.function_call,
      $.parameter,
      $.spread_operator,
      $.select_statement,
    ),

    parenthesis_expression: $ => seq('(', $._query, ')'),

    unary_expression: $ => prec.left(8, seq(choice('!', '-'), $.expression)),

    binary_expression: $ => choice(
      prec.left(7, seq($.expression, '**', $.expression)),
      prec.left(6, seq($.expression, choice('*', '/', '%'), $.expression)),
      prec.left(5, seq($.expression, choice('+', '-'), $.expression)),
      prec.left(4, seq($.expression, choice('..', '...'), $.expression)),
      prec.left(3, seq($.expression, choice('==', '!=', '>', '>=', '<', '<='), $.expression)),
      prec.left(2, seq($.expression, choice('in', 'match'), $.expression)),
      prec.left(1, seq($.expression, '&&', $.expression)),
      prec.left(0, seq($.expression, '||', $.expression)),
    ),

    literal: $ => choice(
      $.string,
      $.number,
      $.true,
      $.false,
      $.null,
    ),

    string: _ => choice(
      seq('"', repeat(choice(/[^"\\]+/, /\\./)), '"'),
      seq('\'', repeat(choice(/[^'\\]+/, /\\./)), '\''),
    ),

    number: _ => /\d+(\.\d+)?([eE][+-]?\d+)?[i]?/,

    true: _ => 'true',
    false: _ => 'false',
    null: _ => 'null',

    array: $ => seq(
      '[',
      sepBy(',', $._query),
      ']',
    ),

    object: $ => seq(
      '{',
      sepBy(',', $.pair),
      '}',
    ),

    pair: $ => seq(
      $._query,
      ':',
      $._query,
    ),

    projection: $ => prec(2, seq(
      '{',
      sepBy(',', choice($._query, $.pair, $.conditional_projection)),
      optional(','),
      '}',
    )),

    conditional_projection: $ => seq(
      $._query,
      '=>',
      $.projection,
    ),

    select_statement: $ => seq(
      '...',
      'select',
      '(',
      $._query,
      '=>',
      $.projection,
      ')',
    ),

    function_call: $ => choice(
      $.order_function,
      seq(
        $.identifier,
        '(',
        sepBy(',', $._query),
        ')',
      ),
    ),

    order_function: $ => seq(
      'order',
      '(',
      sepBy(',', seq($._query, optional(choice('asc', 'desc')))),
      ')',
    ),

    parent: _ => '^',
    this: _ => '@',
    star: _ => '*',

    identifier: _ => /[a-zA-Z_][a-zA-Z0-9_]*/,

    parameter: $ => seq('$', $.identifier),

    spread_operator: $ => prec.left(10, seq('...', optional($._expression))),

    comment: _ => token(seq('//', /.*/)),
  },
});

/**
 *
 * @param {string} sep
 * @param {Rule} rule
 */
function sepBy1(sep, rule) {
  return seq(rule, repeat(seq(sep, rule)));
}

/**
 *
 * @param {string} sep
 * @param {Rule} rule
 */
function sepBy(sep, rule) {
  return optional(sepBy1(sep, rule));
}
