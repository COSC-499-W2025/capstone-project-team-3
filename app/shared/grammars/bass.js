/**
 * @file Bass grammar for tree-sitter
 * @author Alex Suraci <suraci.alex@gmail.com>
 * @author Amaan Qureshi <amaanq12@gmail.com>
 * @license MIT
 * @see {@link https://bass-lang.org|official website}
 */

/* eslint-disable arrow-parens */
/* eslint-disable camelcase */
/* eslint-disable-next-line spaced-comment */
/// <reference types="tree-sitter-cli/dsl" />
// @ts-check

const SYMBOL = token(
  /[^\t\n\v\f\r \u0085\u00A0,"()\[\]{};^/:.0-9][^\t\n\v\f\r \u0085\u00A0,"()\[\]{};^/:]*/,
);

const PATH = token(choice(
  /\.\/[A-Za-z0-9\.\/\-\*_]*/,
  /\/[A-Za-z0-9\.\/\-\*_]*/,
  /[A-Za-z0-9\.\/\-\*_]*\/[A-Za-z0-9\.\/\-\*_]*/,
));

module.exports = grammar({
  name: 'bass',

  extras: $ => [
    $.comment,
    /[\s,]/,
  ],

  supertypes: $ => [
    $.form,
    $.literal,
  ],

  word: $ => $.symbol,

  rules: {
    source: $ => repeat($.form),

    form: $ => choice(
      // literals
      $.literal,

      // Identifier
      $.symbol,

      $.keyword,

      // collections
      $.list,
      $.cons,
      $.scope,

      // paths
      $.command,
      $.path,
      $.symbind,

      // meta
      $.meta,
    ),

    keyword: $ => seq(':', choice($.symbol, $.path, $.command)),

    command: _ => token(seq('.', SYMBOL)),

    path: _ => PATH,

    symbind: $ => prec(1, seq(
      choice($.symbol, $.symbind),
      $.keyword,
    ),
    ),

    meta: $ => seq(
      field('marker', '^'),
      field('meta', $.form),
      $.form,
    ),

    list: $ => seq('(', repeat($.form), ')'),

    scope: $ => seq('{', repeat($.form), '}'),

    cons: $ => seq('[', repeat($.form), ']'),

    literal: $ => choice(
      $.number,
      $.boolean,
      $.string,
      $.ignore,
      $.null,
    ),

    number: _ => /[+-]?[0-9]+/,

    string: $ => seq(
      '"',
      repeat(choice(
        $.string_fragment,
        $._escape_sequence,
      )),
      '"',
    ),

    // Workaround to https://github.com/tree-sitter/tree-sitter/issues/1156
    // We give names to the token_ constructs containing a regexp
    // so as to obtain a node in the CST.
    string_fragment: _ => token.immediate(prec(1, /[^"\\]+/)),

    _escape_sequence: $ => choice(
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
      ),
    )),

    ignore: _ => '_',

    null: _ => 'null',

    boolean: _ => choice('false', 'true'),

    symbol: _ => SYMBOL,

    comment: _ => token(/(;|#!|# ).*/),
  },
});
