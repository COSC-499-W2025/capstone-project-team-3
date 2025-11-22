/**
 * @file NQC grammar for tree-sitter
 * @author Amaan Qureshi <amaanq12@gmail.com>
 * @license MIT
 */

/* eslint-disable arrow-parens */
/* eslint-disable camelcase */
/* eslint-disable-next-line spaced-comment */
/// <reference types="tree-sitter-cli/dsl" />
// @ts-check

const C = require('tree-sitter-c/grammar');

module.exports = grammar(C, {
  name: 'nqc',

  rules: {
    _top_level_item: ($, original) => choice(
      original,
      $.task_definition,
    ),

    _non_case_statement: ($, original) => choice(
      original,
      $.until_statement,
      $.acquire_statement,
      $.monitor_statement,
      $.start_statement,
      $.stop_statement,
    ),

    _top_level_statement: ($, original) => choice(
      original,
      $.until_statement,
      $.acquire_statement,
      $.monitor_statement,
      $.start_statement,
      $.stop_statement,
    ),

    task_definition: $ => seq(
      'task',
      $.identifier,
      field('parameters', $.parameter_list),
      field('body', $.compound_statement),
    ),

    subroutine_definition: $ => seq(
      'sub',
      $.identifier,
      '(',
      ')',
      field('body', $.compound_statement),
    ),

    until_statement: $ => seq(
      'until',
      field('condition', $.parenthesized_expression),
      field('body', $._statement),
    ),

    acquire_statement: $ => prec.right(seq(
      'acquire',
      field('item', $.parenthesized_expression),
      field('body', $._statement),
      optional($.catch_clause),
    )),

    catch_clause: $ => seq(
      'catch',
      optional(seq(
        '(',
        field('event', $._expression),
        ')',
      )),
      field('body', $.compound_statement),
    ),

    monitor_statement: $ => prec.right(seq(
      'monitor',
      field('item', $.parenthesized_expression),
      field('body', $._statement),
      repeat($.catch_clause),
    )),

    start_statement: $ => seq(
      'start',
      field('task', $.identifier),
    ),

    stop_statement: $ => seq(
      'stop',
      field('task', $.identifier),
    ),
  },
});
