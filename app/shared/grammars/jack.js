/// <reference types="tree-sitter-cli/dsl" />
// @ts-check
module.exports = grammar({
  name: 'jack',

  // name of token matching keywords
  word: $ => $.identifier,

  // Tokens that can appear anywhere
  extras: $ => [
    /\s+/,
    $.doc_comment,
    $.comment
  ],

  // Replace usages w/ their definitions
  inline: $ => [
    $.statement,
    $.expression,
    $.term,
  ],

  // hidden rule names to be considered supertypes in generated node types file
  supertypes: $ => [
    $.statement,
    $.expression,
  ],

  // LR(1) conflicts
  conflicts: $ => [],

  precedences: $ => [
    [
      'member',
      // 'call',
      'unary',
      'binary_times',
      'binary_plus',
      'binary_compare',
      'binary_equality',
      'logical_and',
      'logical_or',
      $.sequence_expression,
    ],
    [
      'member',
      // 'call',
      $.expression
    ],
  ],

  rules: {
    source_file: $ => optional($.class_declaration),

    // ---------------------------------------------------------------
    /// Declarations

    class_declaration: $ => seq(
      'class',
      field('name', $.identifier),
      field('body', $.class_body),
    ),

    class_body: $ => seq(
      '{',
      repeat($.class_variable_declaration),
      repeat($.subroutine_declaration),
      '}',
    ),

    _variable_declaration: $ => seq(
      $.type,
      sep1($.identifier, ','),
      ';',
    ),

    class_variable_declaration: $ => seq(
      choice('field', 'static'),
      $._variable_declaration
    ),

    local_variable_declaration: $ => seq('var', $._variable_declaration),

    type: $ => choice(
      'int',
      'char',
      'boolean',
      alias($.identifier, $.class_name),
    ),

    subroutine_declaration: $ => seq(
      field('kind', choice('constructor', 'function', 'method')),
      field('type', alias(choice('void', $.type), $.type)),
      field('name', $.identifier),
      field('parameters', $.formal_parameters),
      field('body', $.subroutine_body)
    ),

    parameter: $ => seq(
      $.type,
      $.identifier,
    ),

    formal_parameters: $ => seq('(', commaSep($.parameter), ')'),

    subroutine_body: $ => seq(
      '{',
      repeat($.local_variable_declaration),
      repeat($.statement),
      '}',
    ),

    // ---------------------------------------------------------------
    /// Statements

    statement_block: $ => seq('{', repeat($.statement), '}'),

    statement: $ => choice(
      $.let_statement,
      $.if_statement,
      $.while_statement,
      $.do_statement,
      $.return_statement
    ),

    let_statement: $ => seq(
      'let',
      choice($.identifier, $.subscript_expression),
      '=',
      $.expression,
      ';',
    ),

    else_clause: $ => seq('else', $.statement_block),

    if_statement: $ => seq(
      'if',
      field('condition', $.parenthesized_expression),
      field('consequence', $.statement_block),
      optional(field('alternative', $.else_clause)),
    ),

    while_statement: $ => seq(
      'while',
      field('condition', $.parenthesized_expression),
      field('body', $.statement_block),
    ),

    do_statement: $ => seq(
      'do',
      $.call_expression,
      ';',
    ),

    return_statement: $ => seq(
      'return',
      optional($.expression),
      ';',
    ),

    // ---------------------------------------------------------------
    /// Expressions

    expression: $ => choice(
      $.term,
      $.unary_expression,
      $.binary_expression,
    ),

    parenthesized_expression: $ => seq('(', $.expression, ')'),

    sequence_expression: $ => seq(
      field('left', $.expression),
      ",",
      field('right', choice($.sequence_expression, $.expression)),
    ),

    unary_expression: $ => prec.left('unary', seq(
      field('operator', choice('-', '~')),
      field('argument', $.expression),
    )),

    // Note: precendences not specified in Jack language definition
    binary_expression: $ => choice(
      ...[
        ['&', 'logical_and'],
        ['|', 'logical_or'],
        ['+', 'binary_plus'],
        ['-', 'binary_plus'],
        ['*', 'binary_times'],
        ['/', 'binary_times'],
        ['<', 'binary_compare'],
        ['>', 'binary_compare'],
        ['=', 'binary_equality'],
      ].map(([operator, precedence, assoc]) =>
        (assoc == 'right' ? prec.right : prec.left)(precedence, seq(
          field('left', $.expression),
          field('operator', operator),
          field('right', $.expression),
        ))
      )),

    subscript_expression: $ => prec('member', seq(
      field('object', $.identifier),
      '[', field('index', $.expression), ']'
    )),

    member_expression: $ => prec('member', seq(
      field('object', $.term),
      '.',
      field('property', $.identifier),
    )),

    term: $ => choice(
      $.integer,
      $.string,
      alias("this", $.this),
      alias("false", $.false),
      alias("true", $.true),
      alias("null", $.null),
      $.identifier,
      $.subscript_expression,
      $.member_expression,
      $.parenthesized_expression,
      $.call_expression,
    ),

    arguments: $ => seq('(', commaSep($.expression, ','), ')'),

    call_expression: $ => prec('member', seq(
      field('function', $.term),
      field('arguments', $.arguments),
    )),

    identifier: $ => token(seq(
      /[A-Za-z_]/,
      repeat(/[A-Za-z0-9_]/),
    )),

    integer: $ => /\d+/,

    // Strings can't contain newlines or double-quotes
    string: $ => token(seq('"', repeat(/[^"\n]/), '"')),

    doc_comment: $ => token(seq(
      '/**',
      /[^*]*\*+([^/*][^*]*\*+)*/,
      '/',
    )),

    comment: $ => token(choice(
      seq('//', /.*/),
      seq(
        '/*',
        /[^*]*\*+([^/*][^*]*\*+)*/,
        '/'
      ),
    )),
  }
});

function sep1(rule, separator) {
  return seq(rule, repeat(seq(separator, rule)));
}

function commaSep(rule) {
  return optional(sep1(rule, ','));
}
