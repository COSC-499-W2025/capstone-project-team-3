/**
 * @file .Xresources grammar for tree-sitter
 * @author Omar Valdez <omarantoniovaldezf2@gmail.com>
 * @license MIT
 */

/// <reference types="tree-sitter-cli/dsl" />
// @ts-check

const ANY_CHAR = /[^\x00\n]/;
const WHITE_SPACE = /[ \t]/;
const NEWLINE = /\n/;
const C_IDENTIFIER = /[a-zA-Z_]\w*/;

module.exports = grammar({
  name: 'xresources',

  extras: $ => [WHITE_SPACE, $.preprocessor_comment],

  rules: {
    resources: $ => repeat($._line),

    _line: $ => seq(optional($._statement), NEWLINE),

    _statement: $ => choice(
      $.comment,
      $.define_directive,
      $.define_function_directive,
      $.if_directive,
      $.ifdef_directive,
      $.include_directive,
      $.resource,
      $.simple_directive,
      $.undef_directive,
    ),

    comment: _ => token.immediate(seq('!', repeat(ANY_CHAR))),

    // C style comments handled by the C preprocessor,
    // rule definition taken from tree-sitter-c
    preprocessor_comment: _ => token(choice(
      seq('//', /(\\+(.|\r?\n)|[^\\\n])*/),
      seq('/*', /[^*]*\*+([^/*][^*]*\*+)*/, '/'),
    )),

    resource: $ => seq(
      field('name', $.components),
      ':',
      repeat(WHITE_SPACE),
      field('value', $.resource_value),
    ),

    components: $ => seq(
      repeat($.binding),
      repeat(seq(
        choice($.component, $.any_component),
        repeat1($.binding)),
      ),
      $.component,
    ),
    binding: _ => choice('.', '*'),
    component: _ => /[a-zA-Z0-9_-]+/,
    any_component: _ => '?',

    escape_sequence: _ => token(seq('\\', choice('n', '\\', '\t', '\n', ' ', /[0-7]{3}/))),
    resource_value: $ => repeat1(choice(ANY_CHAR, $.escape_sequence)),
    string: $ => seq('"', alias(/[^\n"]*/, $.string_content), '"'),

    // Preprocessor directives
    include_directive: $ => seq(directive('include'), field('file', $.string)),

    define_directive: $ => seq(
      directive('define'),
      field('name', $.identifier),
      field('value', optional($.expansion)),
    ),

    define_function_directive: $ => seq(
      directive('define'),
      field('name', $.identifier),
      field('parameters', $.parameters),
      field('value', optional($.expansion)),
    ),

    parameters: $ => seq(
      token.immediate('('),
      optional(sep1(choice($.identifier, '...'), ',')),
      ')',
    ),

    expansion: _ => token(prec(-1, /\S([^/\n]|\/[^*]|\\\r?\n)*/)),

    undef_directive: $ => seq(directive('undef'), field('name', $.identifier)),

    if_directive: $ => seq(
      directive('if'),
      field('condition', $.expansion),
      NEWLINE,
      $._if_directive_body,
    ),

    ifdef_directive: $ => seq(
      choice(directive('ifdef'), directive('ifndef')),
      field('condition', $.identifier),
      NEWLINE,
      $._if_directive_body,
    ),

    _if_directive_body: $ => seq(
      field('consequence', alias(repeat($._line), $.body)),
      repeat(field('alternative', choice($.elif_directive, $.elifdef_directive))),
      optional(field('alternative', $.else_directive)),
      directive('endif'),
    ),

    elif_directive: $ => seq(
      directive('elif'),
      field('condition', $.expansion),
      repeat($._line),
    ),

    elifdef_directive: $ => seq(
      choice(directive('elifdef'), directive('elifndef')),
      field('condition', $.identifier),
      repeat($._line),
    ),

    else_directive: $ => seq(directive('else'), NEWLINE, repeat($._line)),

    simple_directive: $ => seq(
      field('name', $.directive),
      field('value', optional($.expansion)),
    ),

    directive: _ => token(seq('#', repeat(WHITE_SPACE), C_IDENTIFIER)),

    identifier: _ => C_IDENTIFIER,
  },
});


/**
 * @param {string} name Name of the preprocessor directive
 * @returns {Rule} Preprocessor rule
 */
function directive(name) {
  return alias(token(seq('#', repeat(WHITE_SPACE), name)), '#' + name);
}

/**
 * `rule` one or more times separated by `separator`.
 *
 * @param {Rule} rule
 * @param {String} separator
 * @returns {Rule}
 */
function sep1(rule, separator) {
  return seq(rule, repeat(seq(separator, rule)));
}
