/**
 * @file Tree-sitter grammar definition
 * @author ObserverOfTime
 * @license MIT
 */

/// <reference types="tree-sitter-cli/dsl" />
// @ts-check

module.exports = grammar({
  name: 'pymanifest',

  extras: _ => [],

  inline: $ => [$._lb_pattern],

  rules: {
    manifest: $ => repeat(
      choice($.command, $._end_of_line)
    ),

    command: $ => seq(
      optional($._space),
      choice(
        $._include,
        $._exclude,
        $._recursive_include,
        $._recursive_exclude,
        $._global_include,
        $._global_exclude,
        $._graft,
        $._prune
      )
    ),

    _include: $ => seq(
      alias('include', $.keyword),
      prec.right(repeat1($._lb_pattern)),
      $._end_of_line
    ),

    _exclude: $ => seq(
      alias('exclude', $.keyword),
      prec.right(repeat1($._lb_pattern)),
      $._end_of_line
    ),

    _recursive_include: $ => seq(
      alias('recursive-include', $.keyword),
      field('dir_pattern', $._lb_pattern),
      prec.right(repeat1($._lb_pattern)),
      $._end_of_line
    ),

    _recursive_exclude: $ => seq(
      alias('recursive-exclude', $.keyword),
      field('dir_pattern', $._lb_pattern),
      prec.right(repeat1($._lb_pattern)),
      $._end_of_line
    ),

    _global_include: $ => seq(
      alias('global-include', $.keyword),
      prec.right(repeat1($._lb_pattern)),
      $._end_of_line
    ),

    _global_exclude: $ => seq(
      alias('global-exclude', $.keyword),
      prec.right(repeat1($._lb_pattern)),
      $._end_of_line
    ),

    _graft: $ => seq(
      alias('graft', $.keyword),
      field('dir_pattern', $._lb_pattern),
      $._end_of_line
    ),

    _prune: $ => seq(
      alias('prune', $.keyword),
      field('dir_pattern', $._lb_pattern),
      $._end_of_line
    ),

    _lb_pattern: $ => choice(
      seq($._space, $.pattern),
      seq($.linebreak, optional($.pattern))
    ),

    _space: _ => /[ \t]+/,

    _end_of_line: $ => seq(
      optional($._space),
      optional($.comment),
      /\r?\n/
    ),

    linebreak: $ => prec.left(seq(
      optional($._space),
      '\\',
      $._end_of_line,
      optional($._space)
    )),

    pattern: $ => seq(
      $._pattern,
      repeat(seq($.dir_sep, $._pattern))
    ),

    _pattern: $ => repeat1(choice(
      /[^\s\n#/?*]/,
      $.glob,
      $.escaped_char,
      $.char_sequence
    )),

    glob: _ => token(choice('?', '*', '**')),

    dir_sep: _ => '/',

    escaped_char: _ => prec(2, /\\[\#\[]/),

    char_sequence: $ => prec.left(seq(
      '[',
      optional('!'),
      repeat1(choice(
        $.char_range,
        $._seq_char,
        '-'
      )),
      ']'
    )),

    char_range: $ => prec.right(
      1, seq($._seq_char, '-', $._seq_char)
    ),

    _seq_char: _ => choice(
      /[^-\\\]#\s\n]/, /\\[-\\\[\]!#]/
    ),

    comment: _ => token.immediate(/#[^\n]*/)
  }
});
