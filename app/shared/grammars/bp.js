function commaSeparatedOptTrailing(elem) {
  return seq(elem, repeat(seq(",", elem)), optional(","))
}

function commaSeparatedNoTrailing(elem) {
  return seq(elem, repeat(seq(",", elem)))
}

function commaSeparatedTrailing(elem) {
  return repeat(seq(elem, ","))
}

module.exports = grammar({
  name: "bp",

  extras: ($) => [
    /\s+/,
    $.comment,
  ],

  rules: {
    source_file: ($) => repeat($._definition),

    _definition: ($) => choice(
      $.assignment,
      $.module,
    ),

    comment: (_) => choice(
      seq("//", /(\\+(.|\r?\n)|[^\\\n])*/),
      seq("/*", /[^*]*\*+([^/*][^*]*\*+)*/, "/"),
    ),

    // Definitions {{{

    assignment: ($) => seq(
      field("left", $.identifier),
      field("operator", alias(choice("=", "+="), $.operator)),
      field("right", $._expr),
    ),

    module: ($) => choice(
      $._old_module,
      $._new_module,
    ),

    // This syntax is deprecated, but still accepted
    _old_module: ($) => seq(
      field("type", $.identifier),
      "{",
      optional(commaSeparatedOptTrailing(
        alias(field("property", $._colon_property), $.property)
      )),
      "}",
    ),

    _new_module: ($) => seq(
      field("type", $.identifier),
      "(",
      optional(commaSeparatedOptTrailing(
        alias(field("property", $._equal_property), $.property)
      )),
      ")",
    ),

    // }}}

    // Expressions {{{

    _expr: ($) => choice(
      // Literals
      $.identifier,
      $.boolean_literal,
      $.integer_literal,
      $._string_literal,
      // Conditionals
      $.select_expression,
      // Composites
      $.list_expression,
      $.map_expression,
      // Operators
      $.binary_expression,
    ),

    // The Blueprint scanner makes use of Go's lexer, so copy their rule
    identifier: (_) => /[_\p{XID_Start}][_\p{XID_Continue}]*/,

    boolean_literal: (_) => choice("true", "false"),

    integer_literal: (_) => seq(optional("-"), /[0-9]+/),

    // The Blueprint scanner makes use of Go's lexer, so copy their rule
    _string_literal: ($) => choice(
      $.raw_string_literal,
      $.interpreted_string_literal,
    ),

    raw_string_literal: (_) => token(seq(
      "`",
      /[^`]+/,
      "`",
    )),

    interpreted_string_literal: $ => seq(
      '"',
      repeat(choice(
        // Allow all characters without special meaning, disallow newlines
        /[^"\n\\]+/,
        $.escape_sequence,
      )),
      token.immediate('"'),
    ),

    escape_sequence: (_) => token.immediate(seq(
      '\\',
      choice(
        /[^xuU]/,
        /\d{2,3}/,
        /x[0-9a-fA-F]{2,}/,
        /u[0-9a-fA-F]{4}/,
        /U[0-9a-fA-F]{8}/,
      ),
    )),

    select_expression: ($) => seq(
      "select",
      "(",
      $.select_value,
      ",",
      $.select_cases,
      ")",
    ),

    select_value: ($) => choice(
      $.condition,
      seq("(", commaSeparatedOptTrailing($.condition), ")"),
    ),

    condition: ($) => seq(
      field("name", $.identifier),
      "(",
      field("arguments", optional(commaSeparatedNoTrailing($._string_literal))),
      ")",
    ),

    select_cases: ($) => seq(
      "{",
      optional(commaSeparatedOptTrailing($.select_case)),
      "}",
    ),

    select_case: ($) => seq(
      field("pattern", $.select_pattern),
      ":",
      field("value", $._case_value)
    ),

    select_pattern: ($) => choice(
      $._select_pattern,
      seq("(", commaSeparatedOptTrailing($._select_pattern), ")"),
    ),

    _select_pattern: ($) => choice(
      $._string_literal,
      $.boolean_literal,
      $.integer_literal,
      alias("any", $.any),
      $.pattern_binding,
      alias("default", $.default),
    ),

    pattern_binding: ($) => seq(
      field("value", alias("any", $.any)),
      field("operator", alias("@", $.operator)),
      field("binding", $.identifier),
    ),

    _case_value: ($) => choice(
      alias("unset", $.unset),
      $._expr,
    ),

    list_expression: ($) => seq(
      "[",
      optional(commaSeparatedOptTrailing(field("element", $._expr))),
      "]",
    ),

    map_expression: ($) => seq(
      "{",
      optional(commaSeparatedOptTrailing(
        alias(field("property", $._colon_property), $.property)
      )),
      "}",
    ),

    binary_expression: ($) => prec.left(seq(
      field("left", $._expr),
      field("operator", alias("+", $.operator)),
      field("right", $._expr),
    )),

    // }}}

    // Properties {{{

    _colon_property: ($) => seq(
      field("field", $.identifier),
      ":",
      field("value", $._expr),
    ),

    _equal_property: ($) => seq(
      field("field", $.identifier),
      "=",
      field("value", $._expr),
    ),

    // }}}
  }
});

// vim: foldmethod=marker sw=2
