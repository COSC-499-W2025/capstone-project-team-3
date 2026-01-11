/**
  * @file Uxn Tal Assembly grammar for tree-sitter
  * @author Amaan Qureshi <amaanq12@gmail.com>
  * @license MIT
  * @see {@link https://wiki.xxiivv.com/site/uxntal.html|official documentation}
  * @see {@link https://wiki.xxiivv.com/site/uxntal_reference.html|official opcode reference}
  * @see {@link https://compudanzas.net/uxn_tutorial.html|tutorial}
  */

/* eslint-disable arrow-parens */
/* eslint-disable camelcase */
/* eslint-disable-next-line spaced-comment */
/// <reference types="tree-sitter-cli/dsl" />
// @ts-check

module.exports = grammar({
  name: 'uxntal',

  externals: $ => [
    $.comment,
  ],

  extras: $ => [
    $.comment,
    /\s/,
  ],

  word: $ => $.identifier,

  rules: {
    program: $ => repeat(
      choice(
        $.macro,
        $.include,
        $.memory_execution,
        $.subroutine,
      ),
    ),

    memory_execution: $ => seq(
      $.absolute_pad_operation,
      repeat($._non_toplevel_statement),
    ),

    subroutine: $ => seq(
      $.label,
      repeat($._non_toplevel_statement),
    ),

    _non_toplevel_statement: $ => choice(
      $.relative_pad_operation,
      $.opcode,
      $.raw_ascii,
      $.rune,
      $.hex_literal,
      $.sublabel_reference,
      $.brackets,
      $.identifier,
      $.number,
    ),

    macro: $ => seq(
      '%',
      choice($.identifier, alias(/[\da-f*/][a-zA-Z-_\d*/]*/, $.identifier)), // why can 2* and 2/ be macro idents??
      '{',
      repeat($._non_toplevel_statement),
      '}',
    ),

    include: _ => seq('~', /[a-zA-Z_./][a-zA-Z0-9_./\-]*/),

    // ordered based on the table
    // https://wiki.xxiivv.com/site/uxntal_reference.html
    opcode: _ => choice(
      'BRK', 'INC', 'POP', 'NIP', 'SWP', 'ROT', 'DUP', 'OVR', 'EQU', 'NEQ', 'GTH', 'LTH', 'JMP', 'JCN', 'JSR', 'STH',
      'LDZ', 'STZ', 'LDR', 'STR', 'LDA', 'STA', 'DEI', 'DEO', 'ADD', 'SUB', 'MUL', 'DIV', 'AND', 'ORA', 'EOR', 'SFT',
      'JCI', 'INC2', 'POP2', 'NIP2', 'SWP2', 'ROT2', 'DUP2', 'OVR2', 'EQU2', 'NEQ2', 'GTH2', 'LTH2', 'JMP2', 'JCN2', 'JSR2', 'STH2',
      'LDZ2', 'STZ2', 'LDR2', 'STR2', 'LDA2', 'STA2', 'DEI2', 'DEO2', 'ADD2', 'SUB2', 'MUL2', 'DIV2', 'AND2', 'ORA2', 'EOR2', 'SFT2',
      'JMI', 'INCr', 'POPr', 'NIPr', 'SWPr', 'ROTr', 'DUPr', 'OVRr', 'EQUr', 'NEQr', 'GTHr', 'LTHr', 'JMPr', 'JCNr', 'JSRr', 'STHr',
      'LDZr', 'STZr', 'LDRr', 'STRr', 'LDAr', 'STAr', 'DEIr', 'DEOr', 'ADDr', 'SUBr', 'MULr', 'DIVr', 'ANDr', 'ORAr', 'EORr', 'SFTr',
      'JSI', 'INC2r', 'POP2r', 'NIP2r', 'SWP2r', 'ROT2r', 'DUP2r', 'OVR2r', 'EQU2r', 'NEQ2r', 'GTH2r', 'LTH2r', 'JMP2r', 'JCN2r', 'JSR2r', 'STH2r',
      'LDZ2r', 'STZ2r', 'LDR2r', 'STR2r', 'LDA2r', 'STA2r', 'DEI2r', 'DEO2r', 'ADD2r', 'SUB2r', 'MUL2r', 'DIV2r', 'AND2r', 'ORA2r', 'EOR2r', 'SFT2r',
      'LIT', 'INCk', 'POPk', 'NIPk', 'SWPk', 'ROTk', 'DUPk', 'OVRk', 'EQUk', 'NEQk', 'GTHk', 'LTHk', 'JMPk', 'JCNk', 'JSRk', 'STHk',
      'LDZk', 'STZk', 'LDRk', 'STRk', 'LDAk', 'STAk', 'DEIk', 'DEOk', 'ADDk', 'SUBk', 'MULk', 'DIVk', 'ANDk', 'ORAk', 'EORk', 'SFTk',
      'LIT2', 'INC2k', 'POP2k', 'NIP2k', 'SWP2k', 'ROT2k', 'DUP2k', 'OVR2k', 'EQU2k', 'NEQ2k', 'GTH2k', 'LTH2k', 'JMP2k', 'JCN2k', 'JSR2k', 'STH2k',
      'LDZ2k', 'STZ2k', 'LDR2k', 'STR2k', 'LDA2k', 'STA2k', 'DEI2k', 'DEO2k', 'ADD2k', 'SUB2k', 'MUL2k', 'DIV2k', 'AND2k', 'ORA2k', 'EOR2k', 'SFT2k',
      'LITr', 'INCkr', 'POPkr', 'NIPkr', 'SWPkr', 'ROTkr', 'DUPkr', 'OVRkr', 'EQUkr', 'NEQkr', 'GTHkr', 'LTHkr', 'JMPkr', 'JCNkr', 'JSRkr', 'STHkr',
      'LDZkr', 'STZkr', 'LDRkr', 'STRkr', 'LDAkr', 'STAkr', 'DEIkr', 'DEOkr', 'ADDkr', 'SUBkr', 'MULkr', 'DIVkr', 'ANDkr', 'ORAkr', 'EORkr', 'SFTkr',
      'LIT2r', 'INC2kr', 'POP2kr', 'NIP2kr', 'SWP2kr', 'ROT2kr', 'DUP2kr', 'OVR2kr', 'EQU2kr', 'NEQ2kr', 'GTH2kr', 'LTH2kr', 'JMP2kr', 'JCN2kr', 'JSR2kr', 'STH2kr',
      'LDZ2kr', 'STZ2kr', 'LDR2kr', 'STR2kr', 'LDA2kr', 'STA2kr', 'DEI2kr', 'DEO2kr', 'ADD2kr', 'SUB2kr', 'MUL2kr', 'DIV2kr', 'AND2kr', 'ORA2kr', 'EOR2kr', 'SFT2kr',
    ),

    // Runes
    absolute_pad_operation: $ => seq('|', $.number),

    relative_pad_operation: $ => seq('$', $.number),

    hex_literal: $ => seq('#', alias(/[\da-f]{2}|[\da-f]{4}/, $.hex_lit_value)),

    label: $ => seq('@', $.identifier),

    sublabel_reference: $ => seq(
      $.identifier,
      '/',
      $.identifier,
    ),

    rune: $ => seq(
      field('rune_start', $.rune_char),
      repeat($.rune_char),
      choice(
        $.identifier,
        alias(/[\d*/]{1,4}/, $.identifier),
        $.sublabel_reference,
      ),
    ),

    rune_char: _ => choice(
      field('relative', choice(',', '_')),
      field('zero_page', choice('.', '-')),
      field('absolute', choice(';', '=')),
      field('immediate', choice('!', '?')),
      field('sublabel', '&'),
    ),

    brackets: $ => seq(
      '[',
      repeat($._non_toplevel_statement),
      ']',
    ),

    raw_ascii: _ => seq('"', /[^\s]+/),

    number: _ => /[\da-f]{1,4}\s/,

    identifier: _ => token(prec(-1, /[0-9]?[a-zA-Z_:*/][/]*[a-zA-Z0-9_:#*\-]*/)),
  },
});
