/**
 * @file Re2c grammar for tree-sitter
 * @author Alexandre Muller <muller@outlook.com>
 * @author Amaan Qureshi <amaanq12@gmail.com>
 * @license MIT
 */

/* eslint-disable arrow-parens */
/* eslint-disable camelcase */
/* eslint-disable-next-line spaced-comment */
/// <reference types="tree-sitter-cli/dsl" />
// @ts-check

const NAME = /[a-zA-Z_][a-zA-Z0-9_]*/;
const LEX_BLOCK_END = /([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*/;

module.exports = grammar({
  name: 're2c',

  word: $ => $.identifier,

  extras: $ => [
    /\s/,
    $.comment,
  ],

  inline: $ => [
    $._name,
    $._label,
    $._block_name,
    $._field_identifier,
    $._string,
    $._filename,
    $._rule,
    $._directive,
    $._codepoint,
    $._esc_hex,
    $._esc_oct,
    $._clist,
    $._char_cls_expr,
    $._bracket_literal,
    $._linenum,
  ],

  conflicts: $ => [
    // Actions can be described as:
    // ```js
    //    action: $ => seq('{', $._code_in_braces, '}')
    // ```
    // The `_code_in_braces` is inlined code that may contain pairs of braces.
    //
    // To deal with code with missing braces, this parser creates a conflict
    // with all closing braces in the `code_in_braces`. The actions matches
    // the farthest closing brace.
    //
    // It seems to work surprinsly well:
    // See test/queries/action.txt
    [$._code_in_braces],
    // Inside a character class, the hyphen-minus `-` may be a
    // literal or a range separator.
    // The parser need to lookahead one more token to see if
    // this conflict.
    // Examples: `[a-]` (literal) and `[a-b]` (range)
    [$.character_class, $.range],
  ],

  supertypes: $ => [
    $._atom,
    $._escape,
  ],

  rules: {
    re2c: $ => repeat(choice(
      $.host_lang,
      $._block,
    )),

    host_lang: $ => token(/([^/]|\/[^*]|\/\*[^!])+/),

    _block: $ => seq(
      '\/*!',
      choice(
        $.global_block,
        $.local_block,
        $.rules_block,
        $.use_block,
        $.max_block,
        $.maxnmatch_block,
        $.stags_block,
        $.mtags_block,
        $.getstate_block,
        $.header_on_block,
        $.header_off_block,
        $.ignore_block,
      ),
      '*\/',
    ),

    global_block: $ => seq(token.immediate('re2c'), optional($._block_name), optional($.body)),
    local_block: $ => seq(suffix('local'), optional($._block_name), optional($.body)),
    rules_block: $ => seq(suffix('rules'), optional($._block_name), optional($.body)),

    _block_name: $ => seq(
      token.immediate(':'), alias(token.immediate(NAME), $.block_name),
    ),

    //
    // Block directives
    // ----------------
    use_block: $ => seq(suffix('use'), optional($._block_name)),
    max_block: $ => seq(suffix('max'), optional($.block_list)),
    maxnmatch_block: $ => seq(suffix('maxnmatch'), optional($.block_list)),
    types_block: $ => seq(suffix('types'), optional($.block_list)),
    getstate_block: $ => seq(suffix('getstate'), optional($.block_list)),
    stags_block: $ => seq(suffix('stags'), optional($.block_list), repeat($._tag_directive)),
    mtags_block: $ => seq(suffix('mtags'), optional($.block_list), repeat($._tag_directive)),

    include_block: $ => seq(suffix('include'), / /, $._filename),

    header_on_block: $ => seq(suffix(suffix('header'), 'on', true)),
    header_off_block: $ => seq(suffix(suffix('header'), 'off', true)),

    // NOTE: Single token
    ignore_block: $ => token(seq(suffix('ignore'), LEX_BLOCK_END)),

    block_list: $ => repeat1($._block_name),

    // LINT. Shall be dstring
    _filename: $ => field('filename', $._string),

    // LINT: Shall be dstring
    _tag_directive: $ => choice(
      $.format_directive,
      $.separator_directive,
    ),

    format_directive: $ => seq(
      'format', '=', field('format', $._string), ';',
    ),

    separator_directive: $ => seq(
      'separator', '=', field('separator', $._string), ';',
    ),

    //
    // Statements
    // ==========
    body: $ => repeat1(choice(
      $.named_definition,
      $.configuration,
      $._rule,
      $._directive,
      $.linedir,
    )),

    //
    // Named definition
    // ================
    // LINT: Cannot be recursive
    // LINT: Redefinition is an error
    named_definition: $ => seq(
      field('name', $._name), '=', field('value', $.regex), ';',
    ),

    _name: $ => alias($.identifier, $.name),

    //
    // Configuration
    // =============
    // Loads of oportunity to LINT.
    configuration: $ => seq(
      're2c', token.immediate(':'),
      choice(
        $.set_flags,
        $.define,
        $.set_cond,
        $.set_label,
        $.set_variable,
        $.set_yych,
        $.set_state,
        $.set_yybm,
        $.set_cgoto,
        $.set_api,
        $.set_tags,
        $.set_indent,
        $.set_yyfill,
        $.set_eof,
        $.set_sentinel,
        $.set_condprefix,
        $.set_condenumprefix,
        $.set_startlabel,
        $.set_posixcaptures,
        $.set_header,
      ),
      ';',
    ),

    _option_name: $ => seq(
      token.immediate(':'),
      field('option', alias(token.immediate(/[a-zA-Z0-9_:-]+/), $.option_name)),
      optional(seq(
        choice(token.immediate(':'), token.immediate('@')),
        field('field', alias(token.immediate(/[a-zA-Z0-9_:-]+/), $.option_name)),
      )),
    ),

    set_flags: $ => seq(token.immediate('flags'), $._option_name, '=', $._conf_value),
    define: $ => seq(token.immediate('define'), $._option_name, '=', $._conf_value),
    set_cond: $ => seq(token.immediate('cond'), $._option_name, '=', $._conf_value),
    set_label: $ => seq(token.immediate('label'), $._option_name, '=', $._conf_value),
    set_variable: $ => seq(token.immediate('variable'), $._option_name, '=', $._conf_value),
    set_yych: $ => seq(token.immediate('yych'), $._option_name, '=', $._conf_value),
    set_state: $ => seq(token.immediate('state'), $._option_name, '=', $._conf_value),
    set_yybm: $ => seq(token.immediate('yybm'), $._option_name, '=', $._conf_value),
    set_cgoto: $ => seq(token.immediate('cgoto'), $._option_name, '=', $._conf_value),
    set_api: $ => seq(token.immediate('api'), $._option_name, '=', $._conf_value),
    set_tags: $ => seq(token.immediate('tags'), optional($._option_name), '=', $._conf_value),
    set_indent: $ => seq(token.immediate('indent'), $._option_name, '=', $._conf_value),
    set_yyfill: $ => seq(token.immediate('yyfill'), $._option_name, '=', $._conf_value),
    // configurations without options
    set_eof: $ => seq(token.immediate('eof'), '=', $._conf_value),
    set_sentinel: $ => seq(token.immediate('sentinel'), '=', $._conf_value),
    set_condprefix: $ => seq(token.immediate('condprefix'), '=', $._conf_value),
    set_condenumprefix: $ => seq(token.immediate('condenumprefix'), '=', $._conf_value),
    set_labelprefix: $ => seq(token.immediate('labelprefix'), '=', $._conf_value),
    set_startlabel: $ => seq(token.immediate('startlabel'), '=', $._conf_value),
    set_posixcaptures: $ => seq(token.immediate('posix-captures'), '=', $._conf_value),
    set_header: $ => seq(token.immediate('header'), '=', $._conf_value),

    _conf_value: $ => field('value', choice(
      $.encoding_policy,
      $.input_conf,
      $.empty_class_conf,
      $.api_style,
      $._string,
      $.number,
      $._name,
      // C primaries
      $.field_expression,
    )),

    // only sypport very simple (yet the most common)
    // field expressions
    field_expression: $ => seq(
      field('argument', $.identifier),
      field('operator', choice('.', '->')),
      field('field', $._field_identifier),
    ),

    _field_identifier: $ => alias($.identifier, $.field_identifier),

    //
    // Configuration constants
    // -----------------------
    encoding_policy: $ => choice(
      'ignore',
      'substitute',
      'fail',
    ),

    input_conf: $ => choice(
      'default',
      'custom',
    ),

    empty_class_conf: $ => choice(
      'match-empty',
      'match-none',
      'error',
    ),

    api_style: $ => choice(
      'functions',
      'free-form',
    ),

    //
    // Rule
    // ====
    _rule: $ => choice(
      $.ordinary_rule,
      $.conditional_rule,
    ),

    ordinary_rule: $ => choice(
      seq($.pattern, $.action),
    ),

    conditional_rule: $ => choice(
      seq($.condition, $.pattern, $.action),
      seq($.condition, $.pattern, $.shortcut, $.action),
      seq($.condition, $.pattern, $.shortcut),
      // LINT: Special cases:
      seq($.condition, $.action),
      seq($.condition, $.shortcut, $.action),
      seq($.condition, $.shortcut),
    ),

    shortcut: $ => choice(
      seq('=>', field('condition', $._label)),
      seq(':=>', field('condition', $._label)),
    ),

    _label: $ => alias($.identifier, $.label),

    condition: $ => choice(
      seq('<', optional($._clist), '>'),
      seq('<', '!', optional($._clist), '>'),
    ),

    _clist: $ => choice(
      seq(repeat(seq($._label, ',')), $._label),
      seq(alias('*', $.any)),
    ),

    pattern: $ => choice(
      $.regex,
      alias('*', $.default),
      alias('$', $.end_of_input),
    ),

    action: $ => seq(
      '{', optional(alias($.code_block, $.host_lang)), prec.dynamic(1, '}'),
    ),

    code_block: $ => repeat1($._code_in_braces),

    _code_in_braces: $ => choice(
      // comments are consumed by (comment) in this parser
      // so, there is no need to deal with them here
      seq(/"([^"\\\n]|\\.)*"/),
      seq(/'([^'\\\n]|\\.)*'/),
      seq(/[^{}"'\/]+/),
      seq(/\\[^{}"'\/]/),
      seq('{', repeat($._code_in_braces), optional('}')),
      // Rust lifetimes
      /'\w+/,
    ),

    //
    // Directives
    // ==========
    _directive: $ => choice(
      $.use,
      $.include,
    ),

    use: $ => seq(
      '!use', $._block_name, ';',
    ),

    include: $ => seq(
      '!include', $._filename, ';',
    ),

    //
    // Regular expressions
    // ===================
    regex: $ => choice(
      $.lookahead,
      $._pattern_expr,
    ),

    lookahead: $ => seq(
      field('expr', $._pattern_expr),
      field('operator', '/'),
      field('lookahead', $._pattern_expr),
    ),

    _pattern_expr: $ => choice(
      $.alternation,
      $._alt_expr,
    ),

    // alternation as a list
    alternation: $ => seq(
      repeat1(seq($._branch, field('operator', '|'))), $._branch,
    ),

    _branch: $ => field(
      'branch',
      choice(
        $._alt_expr,
      ),
    ),

    _alt_expr: $ => choice(
      $.difference,
      $._dif_expr,
    ),

    difference: $ => prec.left(seq(
      field('left', $._alt_expr),
      field('operator', '\\'),
      field('right', $._alt_expr),
    )),

    _dif_expr: $ => choice(
      $.concat,
      $._cat_expr,
    ),

    // %right as posix regex
    concat: $ => seq(
      $._cat_expr, repeat1($._cat_expr),
    ),

    _cat_expr: $ => choice(
      $.repetition,
      $._atom,
    ),

    repetition: $ => choice(
      seq($._atom, $.limits),
      seq($._atom, $.close),
    ),

    close: $ => choice(
      token.immediate('*'),
      token.immediate('+'),
      token.immediate('?'),
    ),

    limits: $ => choice(
      seq(token.immediate('{'), $._mininum, token.immediate(','), $._maximum, token.immediate('}')),
      seq(token.immediate('{'), $._mininum, token.immediate(','), token.immediate('}')),
      seq(token.immediate('{'), $._exactly, token.immediate('}')),
    ),

    // LINT shall be positive
    _mininum: $ => field('minimum', alias(token.immediate(/[0-9]+/), $.number)),
    _maximum: $ => field('maximum', alias(token.immediate(/[0-9]+/), $.number)),
    _exactly: $ => field('exactly', alias(token.immediate(/[0-9]+/), $.number)),

    _atom: $ => choice(
      $.parenthesized, // not capture group
      $._string,
      $.character_class,
      $.wildcard,
      $._name,
      $.stag,
      $.mtag,
    ),

    parenthesized: $ => seq(
      '(', $._pattern_expr, ')',
    ),

    //
    // Character class
    // ---------------
    character_class: $ => seq(
      '[',
      optional(token.immediate('^')),
      optional($._bracket_literal),
      repeat($._char_cls_expr),
      token.immediate(']'),
    ),

    _bracket_literal: $ => alias(token.immediate(']'), $.literal),

    _char_cls_expr: $ => choice(
      $.range,
      $._codepoint,
    ),

    range: $ => seq(
      field('from', $._codepoint),
      alias(token.immediate(/-/), '-'),
      field('to', $._codepoint),
    ),

    wildcard: $ => alias('.', '.'), // WHY?

    //
    // Literals
    // ========
    _codepoint: $ => choice(
      $.literal,
      $._escape,
    ),

    literal: $ => choice(
      token.immediate(prec(-1, /./)),
      token.immediate(/-/), // create conflict
    ),

    //
    // String
    // ------
    dstring: $ => seq(/"([^\n\\"]|\\.)*"?/),
    sstring: $ => seq(/'([^\n\\']|\\.)*'?/),

    _string: $ => choice(
      $.dstring, // case sensitive
      $.sstring, // case insensitive
    ),

    //
    // Escape sequence
    // ---------------
    _escape: $ => choice(
      $.quote,
      $.ctrl_code,
      $.code_unit,
    ),

    quote: $ => token(seq(
      '\\', choice('\\', ']', '-', '"', '"'),
    )),

    ctrl_code: $ => token(seq(
      '\\', choice('a', 'b', 'f', 'n', 'r', 't', 'v'),
    )),

    code_unit: $ => choice(
      $._esc_hex,
      $._esc_oct,
    ),

    _esc_hex: $ => choice(
      token(seq('\\', 'x', /[0-9a-fA-F]{2}/)),
      token(seq('\\', 'u', /[0-9a-fA-F]{4}/)),
      token(seq('\\', 'X', /[0-9a-fA-F]{4}/)),
      token(seq('\\', 'U', /[0-9a-fA-F]{8}/)),
      // Next rules are used to improve error recovery.
      // tree-sitter-cli emits "MISSING hex_digit" on incomplete code
      seq(token(seq('\\', 'x', /[0-9a-fA-F]{0,1}/)), $.hex_digit),
      seq(token(seq('\\', 'u', /[0-9a-fA-F]{0,3}/)), $.hex_digit),
      seq(token(seq('\\', 'X', /[0-9a-fA-F]{0,3}/)), $.hex_digit),
      seq(token(seq('\\', 'U', /[0-9a-fA-F]{0,7}/)), $.hex_digit),
    ),

    _esc_oct: $ => choice(
      token(seq('\\', seq(/[0-2][0-7]{2}/))),
      // Improve error recovery. See note in _esc_hex
      seq(token(seq('\\', /[0-2][0-7]{0,1}/)), $.oct_digit),
    ),

    // Should only be used in used on error recovery.
    // See note in _esc_hex
    hex_digit: $ => token.immediate(/[0-9a-fA-F]/),
    oct_digit: $ => token.immediate(/[0-7]/),

    stag: $ => seq('@', token.immediate(NAME)),
    mtag: $ => seq('#', token.immediate(NAME)),

    identifier: $ => /[a-zA-Z_][a-zA-Z0-9_]*/,

    //
    // Numbers
    // =======
    number: $ => choice(
      '0',
      seq('-', token.immediate(/[1-9][0-9]*/)),
      seq(/[1-9][0-9]*/),
    ),

    //
    // Comments
    // ========
    // From tree-sitter-c
    comment: $ => choice(
      token(prec(2, seq('//', /(\\(.|\r?\n)|[^\\\n])*/))),
      token(prec(-1, seq(
        '/*',
        /[^*]*\*+([^/*][^*]*\*+)*/,
        '/',
      ))),
    ),

    linedir: $ => seq(
      '#', 'line',
      $._filename,
      optional($._linenum),
      /\r?\n/,
    ),

    // LINT: shall be positive
    _linenum: $ => field('linenum', $.number),

  },

});

// Helper function

// add suffix to string a after the ':' delimiter
// default suffix is re2c
function suffix(string, suffix = 're2c', nested = false) {
  return seq(nested ? string : token.immediate(string), token.immediate(':'), token.immediate(suffix));
}
