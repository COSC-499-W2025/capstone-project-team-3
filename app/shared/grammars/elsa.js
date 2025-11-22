/**
 * @file Elsa grammar for tree-sitter
 * @author Miles Glapa-Grossklag <miles@glapa-grossklag.com>
 * @author Amaan Qureshi <amaanq12@gmail.com>
 * @license MIT
 * @see {@link https://github.com/ucsd-progsys/elsa|official source}
 * @see {@link https://github.com/ucsd-progsys/elsa#semantics-of-elsa-programs|official syntax spec}
 */

/* eslint-disable arrow-parens */
/* eslint-disable camelcase */
/* eslint-disable-next-line spaced-comment */
/// <reference types="tree-sitter-cli/dsl" />
// @ts-check

module.exports = grammar({
  name: 'elsa',

  extras: $ => [
    $.comment,
    /\s/,
  ],

  rules: {
    source_file: $ => seq(repeat($.definition), repeat($.reduction)),

    definition: $ => seq(
      'let',
      alias($.identifier, $.function),
      '=',
      $.term,
    ),

    reduction: $ =>
      seq(
        'eval',
        alias($.identifier, $.method),
        ':',
        $.term,
        repeat(seq($.step, $.term)),
      ),

    abstraction: $ => seq(
      '\\',
      field('parameters', repeat1(alias($.identifier, $.parameter))),
      '->',
      field('body', $.term),
    ),

    application: $ => prec.left(1,
      seq(
        field('abstraction', $.term),
        field('argument', $.term),
      ),
    ),

    term: $ => choice(
      seq('(', $.term, ')'),
      choice($.identifier, $.abstraction, $.application),
    ),

    step: _ => choice('=a>', '=b>', '=d>', '=*>', '=~>'),

    identifier: _ => token(/[A-Za-z_]+[A-Za-z_0-9]*/),

    comment: _ => token(seq('--', /(\\(.|\r?\n)|[^\\\n])*/)),
  },
});
