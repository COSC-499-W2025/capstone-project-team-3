/**
 * @file Tree-sitter grammar definition
 * @author ObserverOfTime
 * @license MIT
 */

/// <reference types="tree-sitter-cli/dsl"/>

/**
 * @param {GrammarSymbols<'escape'>} $
 * @param {'"' | "'"} quote
 * @returns SeqRule
 */
const __string = ($, quote) => seq(
  field('quote', quote),
  field(
    'content',
    repeat(choice(
      new RegExp(`[^${quote}\\\r\n]`),
      $.escape
    ))
  ),
  field('quote', quote),
);

/**
 * @param {GrammarSymbols<'comment'>} $
 * @param {Rule} main
 * @returns PrecRightRule
 */
const __body = ($, main) => prec.right(
  repeat1(choice($.comment, main))
);

module.exports = grammar({
  name: 'chatito',

  extras: _ => [],

  supertypes: $ => [$.definition],

  inline: $ => [$._eq],

  rules: {
    source: $ => repeat(choice(
      $.definition,
      $.import,
      $.comment,
      prec(-2, $._eol)
    )),

    definition: $ => choice(
      $.intent_def,
      $.slot_def,
      $.alias_def
    ),

    intent_def: $ => seq(
      '%[',
      alias(/[^\]?]+/, $.intent),
      ']',
      optional($._space),
      optional($.arguments),
      $._eol,
      $.intent_body
    ),

    slot_def: $ => seq(
      '@[',
      alias(/[^\]#?]+/, $.slot),
      optional($.variation),
      ']',
      optional($._space),
      optional($.arguments),
      $._eol,
      $.slot_body
    ),

    alias_def: $ => seq(
      '~[',
      alias(/[^\]?]+/, $.alias),
      ']',
      optional($._space),
      optional($.arguments),
      $._eol,
      $.alias_body
    ),

    import: $ => seq(
      'import',
      $._space,
      alias(/.+/, $.file),
      optional($._space),
      $._eol
    ),

    comment: $ => seq(/(\/\/|#).*/, $._eol),

    intent_body: $ => __body($, seq(
      $._indent,
      optional($.probability),
      repeat1(choice(
        $.slot_ref,
        $.alias_ref,
        $._space,
        $.word
      )),
      $._eol
    )),

    slot_body: $ => __body($, seq(
      $._indent,
      optional($.probability),
      repeat1(choice(
        $.alias_ref,
        $._space,
        $.word
      )),
      $._eol
    )),

    alias_body: $ => __body($, seq(
      $._indent,
      repeat1(choice(
        $.slot_ref,
        $.alias_ref,
        $._space,
        $.word
      )),
      $._eol
    )),

    slot_ref: $ => seq(
      '@[',
      alias(/[^\]#?]+/, $.slot),
      optional($.variation),
      optional('?'),
      ']',
    ),

    alias_ref: $ => seq(
      '~[',
      alias(/[^\]?]+/, $.alias),
      optional('?'),
      ']',
    ),

    word: _ => prec.left(-1, repeat1(/\S/)),

    variation: _ => seq(
      '#', field('id', /[^\]#?]+/)
    ),

    probability: $ => seq(
      '*[', $.number, optional('%'), ']'
    ),

    number: _ => /(0|[1-9][0-9]*)(\.[0-9]+)?/,

    arguments: $ => seq(
      '(',
      optional($._space),
      $.argument,
      repeat(seq(
        optional($._space),
        ',',
        optional($._space),
        $.argument
      )),
      optional($._space),
      ')'
    ),

    argument: $ => seq(
      field('key', $.string),
      optional($._space),
      field('eq', $._eq),
      optional($._space),
      field('value', $.string)
    ),

    _eq: _ => ':',

    string: $ => choice(
      __string($, '"'),
      __string($, "'")
    ),

    escape: _ => token(choice(
      /\\['"\\bfnrtv]/,
      /\\u[0-9a-fA-F]{4}/
    )),

    _eol: _ => /\r?\n/,

    _indent: _ => '    ',

    _space: _ => token(prec(-1, /[ ]+/))
  }
});
