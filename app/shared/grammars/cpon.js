/**
 * @file ChainPack Object Notation (CPON) grammar for tree-sitter
 * @author Fanda Vacek <fvacek@elektroline.cz>
 * @author Amaan Qureshi <amaanq12@gmail.com>
 * @license MIT
 * @see {@link https://github.com/silicon-heaven/libshv/wiki/ChainPack-RPC#cpon-chainpack-object-notation|official syntax spec}
 * @see {@link https://github.com/silicon-heaven/libshv/wiki/cpon|additional info}
 */

/* eslint-disable arrow-parens */
/* eslint-disable camelcase */
/* eslint-disable-next-line spaced-comment */
/// <reference types="tree-sitter-cli/dsl" />
// @ts-check

module.exports = grammar({
  name: 'cpon',

  extras: $ => [
    $.comment,
    /\s/,
  ],

  rules: {
    document: $ => $._value,

    _value: $ => seq(
      optional($.meta_map),
      choice(
        $.map,
        $.imap,
        $.array,
        $.number,
        $.float,
        $.datetime,
        $.string,
        $.hex_blob,
        $.esc_blob,
        $.boolean,
        $.null,
      ),
    ),

    meta_map: $ => seq('<', optionalCommaSep($.meta_pair), '>'),

    meta_pair: $ => seq(
      field('key', choice($.string, $.number, $.float)),
      ':',
      field('value', $._value),
    ),

    map: $ => seq('{', optionalCommaSep($.pair), '}'),

    pair: $ => seq(
      field('key', $.string),
      ':',
      field('value', $._value),
    ),

    imap: $ => seq('i', '{', optionalCommaSep($.ipair), '}'),

    ipair: $ => seq(
      field('key', choice($.number, $.float)),
      ':',
      field('value', $._value),
    ),

    array: $ => seq('[', optionalCommaSep($._value), ']'),

    string: $ => seq(
      '"',
      repeat(choice(
        $.string_content,
        $._escape_sequence,
      )),
      '"',
    ),

    string_content: _ => token(prec(-1, /[^"\\]+/)),

    _escape_sequence: $ =>
      choice(
        prec(2, token.immediate(seq('\\', /[^abfnrtvxu'\"\\\?]/))),
        prec(1, $.escape_sequence),
      ),
    escape_sequence: _ => token.immediate(seq(
      '\\',
      choice(
        /[^xu0-7]/,
        /[0-7]{1,3}/,
        /x[0-9a-fA-F]{2}/,
        /u[0-9a-fA-F]{4}/,
        /u\{[0-9a-fA-F]+\}/,
      ))),

    number: _ => {
      const hex_literal = seq(
        choice('0x', '0X'),
        /[\da-fA-F]+u?/,
      );

      const int_literal = /\d+u?/;

      const decimal_digits = /\d+/;
      const signed_integer = seq(optional(choice('-', '+')), decimal_digits);

      const decimal_integer_literal =choice(
        '0',
        seq(/[1-9]/, optional(decimal_digits)),
      );

      const decimal_literal = choice(
        seq(optional(choice('-', '+')), decimal_integer_literal),
        decimal_digits,
        signed_integer,
      );

      return token(choice(
        hex_literal,
        decimal_literal,
        int_literal,
      ));
    },

    float: _ => /[+-]?(\d+(\.\d+)?|\.\d+)([Ee][+-]?\d+)?/,

    datetime: _ => seq(
      'd',
      '"',
      // eslint-disable-next-line max-len
      /(\d{4})-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])T(0[0-9]|1[0-9]|2[0123]):([012345][0-9]):([012345][0-9])(\.\d{3})?(Z|[+-](0[1-9]|1[012])([012345][0-9])?)?/,
      '"',
    ),

    boolean: _ => choice('true', 'false'),

    null: _ => 'null',

    // hexblob: _ => /x"([0-9a-fA-F]{2})*"/,
    hex_blob: _ => seq(
      'x',
      '"',
      /([0-9a-fA-F]{2})*/,
      '"',
    ),
    // escblob: _ => /b"(\\[0-9a-fA-F]{2}|[ -~]|\\\\)*"/,
    esc_blob: $ => seq(
      'b',
      '"',
      repeat(choice(
        $.string_content,
        $._escape_sequence,
      )),
      '"',
    ),

    // http://stackoverflow.com/questions/13014947/regex-to-match-a-c-style-multiline-comment/36328890#36328890
    comment: _ => token(choice(
      seq('//', /.*/),
      seq(
        '/*',
        /[^*]*\*+([^/*][^*]*\*+)*/,
        '/',
      ),
    )),
  },
});

/**
 * Creates a rule to match one or more of the rules optionally separated by commas
 *
 * @param {Rule} rule
 *
 * @return {SeqRule}
 *
 */
function optionalCommaSep1(rule) {
  return seq(rule, repeat(seq(repeat(','), rule)), repeat(','));
}

/**
 * Creates a rule to optionally match one or more of the rules optionally separated by commas
 *
 * @param {Rule} rule
 *
 * @return {ChoiceRule}
 *
 */
function optionalCommaSep(rule) {
  return optional(optionalCommaSep1(rule));
}
