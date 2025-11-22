/// Two following lines are used to enable type-checking:
/// <reference types="tree-sitter-cli/dsl" />
/// @ts-check

/**
 * @file Ohm grammar for Tree-sitter
 * @author Novus Nota (https://github.com/novusnota)
 * @license MIT
 */

/**
 * Creates a rule to match one or more of the rules separated by a symbol
 *
 * @param {Rule} rule
 * @param {string} symbol
 *
 * @return {SeqRule}
 *
 */
function makeNonemptyListOf(rule, symbol) {
  return seq(rule, repeat(seq(symbol, rule)));
}

/**
 * Creates a rule to optionally match one or more of the rules separated by a symbol
 *
 * @param {Rule} rule
 * @param {string} symbol
 *
 * @return {ChoiceRule}
 *
 */
function makeListOf(rule, symbol) {
  return optional(makeNonemptyListOf(rule, symbol));
}

/**
 * Ohm grammar, refined and adapted from https://github.com/ohmjs/ohm/blob/main/packages/ohm-js/src/ohm-grammar.ohm
 */
module.exports = grammar({
  name: "ohm",

  /* The name of a token that will match keywords for their extraction optimization */
  word: ($) => $.identifier,

  /* An array of tokens that may appear anywhere in the language */
  extras: ($) => [/\s/, $.singleline_comment, $.multiline_comment],

  /* An array of token names which can be returned by an external scanner. */
  externals: ($) => [$._unicode_char, $.multiline_comment],

  // reserved: ($) => [],
  // see: https://github.com/tree-sitter/tree-sitter/pull/1635

  /* Each inner array represents a set of rules that's involved in an LR(1) conflict
 that is intended to exist in the grammar and be resolved by Tree-sitter at runtime using GLR algorithm */
  conflicts: ($) => [
    [$.terminal_string, $.one_char_terminal],
    [$.seq],
    [$.rule],
  ],

  /* Mapping of grammar rule names to rule builder functions */
  rules: {
    source_file: ($) => repeat($.grammar),

    /* Grammar and SuperGrammar */

    grammar: ($) =>
      seq(
        field("name", $.identifier),
        field("inherits", optional($.super_grammar)),
        field("body", $.grammar_body),
      ),

    super_grammar: ($) => seq("<:", field("name", $.identifier)),

    grammar_body: ($) => seq("{", repeat($.rule), "}"),

    /* Rule */

    rule: ($) =>
      seq(
        field("name", $.identifier),
        field("formals", optional($.formals)),
        choice(
          seq(
            field("description", optional($.rule_descr)),
            field("case", alias("=", $.define)), // define
            field("body", optional($.rule_body)),
          ),
          seq(
            field("case", alias(":=", $.override)), // override
            field("body", optional($.override_rule_body)),
          ),
          seq(
            field("case", alias("+=", $.extend)), // extend
            field("body", optional($.rule_body)),
          ),
        ),
      ),

    formals: ($) => seq("<", makeListOf($.identifier, ","), ">"),

    rule_descr: (_) => seq("(", /[^\n\)]*/, ")"),

    /* RuleBody and OverrideRuleBody */

    rule_body: ($) =>
      seq(optional("|"), makeNonemptyListOf($.top_level_term, "|")),

    top_level_term: ($) =>
      choice(
        seq(field("sequence", $.seq), field("name", $.case_name)),
        field("sequence", $.seq),
        field("name", $.case_name),
      ),

    override_rule_body: ($) =>
      seq(optional("|"), makeNonemptyListOf($.override_top_level_term, "|")),

    override_top_level_term: ($) =>
      choice(
        seq(
          field("sequence", choice(alias("...", $.super_splice), $.seq)),
          field("name", $.case_name),
        ),
        seq(field("sequence", choice(alias("...", $.super_splice), $.seq))),
        seq(field("name", $.case_name)),
      ),

    case_name: ($) => seq("--", $.identifier, /[^\n]*/),
    // see: inline rule declaration

    /* Seq */

    seq: ($) => repeat1($.term),

    term: ($) =>
      seq(
        field(
          "predicate",
          optional(
            choice(
              alias("&", $.lookahead), // lookahead
              alias("~", $.negative_lookahead), // not
            ),
          ),
        ),
        field(
          "lexification", // NOTE: lexifier?
          optional(
            alias("#", $.lexification), // lex
          ),
        ),
        field("base", $._base),
        field(
          "quantification", // NOTE: quantifier?
          optional(
            choice(
              alias("*", $.zero_or_more), // star
              alias("+", $.one_or_more), // plus
              alias("?", $.zero_or_one), // opt
            ),
          ),
        ),
      ),

    _base: ($) =>
      choice(
        seq(
          // application
          $.identifier,
          optional($.params),
        ),
        seq(
          // range
          $.one_char_terminal,
          "..",
          $.one_char_terminal,
        ),
        seq(
          // terminal
          $.terminal_string,
        ),
        // paren
        $.alt,
      ),

    /* Params, Alt */

    params: ($) => seq("<", makeListOf(alias($.seq, $.param), ","), ">"),

    alt: ($) => seq("(", makeNonemptyListOf($.seq, "|"), ")"),

    /* terminal, oneCharTerminal */

    terminal_string: ($) =>
      seq('"', repeat($._terminal_char), token.immediate('"')),

    one_char_terminal: ($) => seq('"', $._terminal_char, token.immediate('"')),

    _terminal_char: ($) => choice($._unicode_char, $.escape_char),

    escape_char: (_) =>
      token.immediate(
        choice(
          "\\\\", // backslash
          '\\"', // doubleQuote
          "\\'", // singleQuote
          "\\b", // backspace
          "\\n", // lineFeed
          "\\r", // carriageReturn
          "\\t", // tab
          /\\u\{[0-9a-fA-F]{1,6}\}/, // unicodeCodePoint
          /\\u[0-9a-fA-F]{4}/, // unicodeEscape
          /\\x[0-9a-fA-F]{2}/, // hexEscape
        ),
      ),

    /* Identifiers */

    identifier: (_) => /(r#)?[\p{XID_Start}_][\p{XID_Start}0-9_]*/,
    // see:
    // 1. https://www.regular-expressions.info/unicode.html#category
    // 2. https://unicode.org/reports/tr31/

    /* Comments */

    singleline_comment: (_) => token(seq("//", /[^\n]*/)),
    // multiline_comment is handled in src/scanner.c
  },
});
