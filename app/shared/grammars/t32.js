/*
 * Copyright (c) 2014 Max Brunsfeld
 * SPDX-FileCopyrightText: 2014 Max Brunsfeld
 * SPDX-FileCopyrightText: 2022 Christoph Sax <c_sax@mailbox.org>
 *
 * SPDX-License-Identifier: MIT
 */

const PREC = {
  declarator: 1,
  escape_sequence: 1,
  macro_assignment: 1,
  macro_text_expansion: 1,
  option: 1,
  repeat_post_condition: 1,
  string: 1,
  logical_or: 10,
  logical_xor: 11,
  logical_and: 12,
  bitwise_or: 13,
  bitwise_xor: 14,
  bitwise_and: 15,
  equal: 16,
  relational: 17,
  add_sub: 18,
  mul_div_mod: 19,
  sizeof: 20,
  shift: 21,
  pointer: 22,
  cast: 23,
  unary: 24,
  call: 25,
  prefix_postfix: 26,
  field: 27,
  subscript: 28,
  range: 29,
}

const RE_BIN_HEX_NUMBER = [
  /0y[0-9]+/,  // Binary
  /0[xX][0-9a-fA-F]+/,  // Hexadecimal
]

const RE_QUOTED_SYMBOL_NAME = /`[^`\n]+`/
const RE_UNQUOTED_SYMBOL_NAME = /[a-zA-Z_]\w*/
const RE_MACHINE_PROG_MOD_NAME = /\w+/

const RE_FUNCTION_NAME = /[a-zA-Z_]\w*(::[a-zA-Z_]\w*)*|`[^`\n]+`/
const RE_METHOD_NAME = /[a-zA-Z_]\w*(::[a-zA-Z_]\w*)+/

module.exports = grammar({
  name: 't32',

  externals: $ => [
    $.label_identifier,
    $._and_operator_pre_hook,  // Check for presence of macros after operator
    $._decimal_number,
    $._decimal_number_pre_hook,  // Check for presence of range operator after number
    $.hll_number_literal,
    $._hll_number_literal_pre_hook,
    $.path,  // Unquoted path literals
    '&&',
    '&',
    $._ampersand_char  // Differentiate between embedded macros and ampersand in PRACTICE strings
  ],

  conflicts: $ => [
    [$.address],
    [$.argument_list, $.assignment_expression],
    [$.hll_array_declarator, $.hll_abstract_array_declarator],
    [$.hll_sized_type_specifier],
    [$.hll_type_descriptor],
    [$.if_block],
    [$.memory_space],
    [$.option_expression],
    [$.hll_option_expression],
    [$.symbol],
    [$._address_expression, $._literal],
    [$._binary_expression, $._and_expression],
    [$._command_argument, $.assignment_expression],
    [$._expression, $._function_identifier],
    [$._expression, $._address_expression],
    [$._hll_declaration_specifiers],
    [$._hll_pointer_declarator_specifier],
    [$._hll_expression, $._hll_assignment_left_expression],
    [$._hll_expression, $._hll_type_identifier],
    [$._hll_expression, $._hll_assignment_left_expression, $._hll_type_identifier],
    [$._repeat_block_pre_condition_format, $._repeat_block_post_condition_format]
  ],

  inline: $ => [
    $._hll_expression_separator,
    $._hll_number_literal,
    $._terminator,
    $._filler_line,
    $._top_level
  ],

  extras: $ => [
    $._line_continuation,
  ],

  word: $ => $.identifier,

  rules: {
    script: $ => repeat($._top_level),

    _top_level: $ => choice(
      $.block,
      $._statement,
      $._filler_line
    ),

    block: $ => prec.right(seq(
      repeat($._blank),
      seq(
        /\((&[+-]?)?/,
        $._terminator
      ),
      repeat(choice(
        $._statement,
        $._filler_line,
        $.block
      )),
      seq(
        repeat($._blank),
        ')',
        $._terminator
      ),
    )),

    _statement: $ => seq(
      repeat($._blank),
      choice(
        $.labeled_expression,
        $._non_labeled_statement
      )
    ),

    _non_labeled_statement: $ => choice(
      alias($.macro_assignment_expression, $.assignment_expression),
      $.command_expression,
      $.macro_definition,
      $.if_block,
      $.parameter_declaration,
      $.recursive_macro_expansion,
      $.repeat_block,
      $.subroutine_block,
      $.subroutine_call_expression,
      $.while_block
    ),

    _parenthesized_expression: $ => choice(
      seq(
        '(',
        $._expression,
        ')'
      ),
      seq(
        '{',
        $._expression,
        '}'
      )
    ),

    _path_expression: $ => prec.left(choice(
      $.path,
      seq(
        repeat1(seq(
          $.path,
          $.macro
        )),
        optional($.path)
      ),
      seq(
        repeat1(seq(
          $.macro,
          $.path
        )),
        optional($.macro)
      )
    )),

    labeled_expression: $ => prec.right(seq(
      $._label,
      choice(
        $._statement,
        seq(
          $._terminator,
          repeat1($._blank)
        ),
        seq(
          $._terminator,
          optional(seq(
            repeat($.comment),
            $.block
          ))
        )
      )
    )),

    subroutine_block: $ => seq(
      field('command', alias(longAndShortForm('SUBROUTINE'), $.identifier)),
      repeat1($._blank),
      field('subroutine', $.identifier),
      $._terminator,
      repeat($._filler_line),
      $.block
    ),

    if_block: $ => seq(
      choice(
        seq(
          field('command', alias($._hll_var_if_command, $.identifier)),
          repeat1($._blank),
          field('condition', $._hll_expression),
        ),
        seq(
          field('command', alias(longAndShortForm('IF'), $.identifier)),
          repeat1($._blank),
          field('condition', $._expression)
        )
      ),
      seq(
        $._terminator,
        repeat($._filler_line),
        choice(
          $._statement,
          $.block
        ),
        repeat(seq(
          repeat($._filler_line),
          repeat($._blank),
          $.elif_block,
        )),
        optional(seq(
          repeat($._filler_line),
          repeat($._blank),
          $.else_block
        ))
      )
    ),

    elif_block: $ => seq(
      field('command', alias(longAndShortForm('ELSE'), $.identifier)),
      repeat1($._blank),
      field('command', alias(longAndShortForm('IF'), $.identifier)),
      repeat1($._blank),
      field('condition', $._expression),
      seq(
        $._terminator,
        repeat($._filler_line),
        choice(
          $._statement,
          $.block
        ),
      )
    ),

    else_block: $ => seq(
      field('command', alias(
        longAndShortForm('ELSE'), $.identifier)
      ),
      seq(
        $._terminator,
        repeat($._filler_line),
        choice(
          $._statement,
          $.block,
        )
      ),
    ),

    while_block: $ => seq(
      choice(
        seq(
          field('command', alias(
            longAndShortForm('WHILE'), $.identifier)
          ),
          repeat1($._blank),
          field('condition', $._expression),
        ),
        seq(
          field('command', alias(token(seq(
            longAndShortForm('Var'),
            '.',
            longAndShortForm('WHILE')
          )), $.identifier)),
          repeat1($._blank),
          field('condition', $._hll_expression),
        )
      ),
      $._terminator,
      repeat($._filler_line),
      choice(
        $._statement,
        $.block
      )
    ),

    repeat_block: $ => choice(
      $._repeat_block_pre_condition_format,
      $._repeat_block_post_condition_format,
    ),

    _repeat_block_pre_condition_format: $ => seq(
      field('command', alias(longAndShortForm('RePeaT'), $.identifier)),
      choice(
        seq(
          repeat1($._blank),
          field('condition', $._expression),
          choice(
            $._statement,
            seq(
              $._terminator,
              repeat($._filler_line),
              choice(
                $._statement,
                $.block
              )
            )
          )
        ),
        seq(
          $._terminator,
          repeat($._filler_line),
          choice(
            $._statement,
            $.block
          ),
        )
      )
    ),

    _repeat_block_post_condition_format: $ => prec.dynamic(PREC.repeat_post_condition, seq(
      field('command', alias(longAndShortForm('RePeaT'), $.identifier)),
      choice(
        seq(
          $._terminator,
          repeat($._filler_line),
          choice(
            $._statement,
            $.block
          ),
          seq(
            repeat($._filler_line),
            field('command', alias(longAndShortForm('WHILE'), $.identifier)),
            repeat1($._blank),
            field('condition', $._expression),
            $._terminator
          )
        )
      )
    )),

    macro_assignment_expression: $ => prec.right(PREC.macro_assignment, seq(
      field('left', choice(
        $.macro,
        $.recursive_macro_expansion,
      )),
      repeat($._blank),
      field('operator', '='),
      repeat($._blank),
      field('right', $._expression),
      $._terminator
    )),

    unary_expression: $ => choice(
      $._prefix_postfix_expression,
      $._unary_expression
    ),

    _unary_expression: $ => prec.left(PREC.unary, seq(
      field('operator', choice(
        '+', '-', '~', '!'
      )),
      field('argument', $._expression)
    )),

    _prefix_postfix_expression: $ => prec.right(PREC.prefix_postfix, choice(
      seq(
        field('argument', $._expression),
        field('operator', choice('++', '--'))
      ),
      seq(
        field('operator', choice('++', '--')),
        field('argument', $._expression)
      )
    )),

    binary_expression: $ => choice(
      $._binary_expression,
      $._and_expression
    ),

    _binary_expression: $ => {
      const operators = [
        ['^^', PREC.logical_xor],
        ['||', PREC.logical_or],
        ['+', PREC.add_sub],
        ['-', PREC.add_sub],
        ['*', PREC.mul_div_mod],
        ['/', PREC.mul_div_mod],
        ['%', PREC.mul_div_mod],
        ['|', PREC.bitwise_or],
        ['^', PREC.bitwise_xor],
        ['==', PREC.relational],
        ['!=', PREC.relational],
        ['>', PREC.relational],
        ['>=', PREC.relational],
        ['<=', PREC.relational],
        ['<', PREC.relational],
        ['<<', PREC.shift],
        ['>>', PREC.shift],
        ['..', PREC.range],
        ['--', PREC.range],
        ['++', PREC.range]
      ];

      return choice(...operators.map(([op, pre]) => {
        return prec.left(pre, seq(
          field('left', $._expression),
          field('operator', op),
          field('right', $._expression)
        ))
      }));
    },

    _and_expression: $ => {
      const operators = [
        ['&&', PREC.logical_and],
        ['&', PREC.bitwise_and]
      ];

      return choice(...operators.map(([op, pre]) => {
        return prec.left(pre, seq(
          field('left', $._expression),
          $._and_operator_pre_hook,
          field('operator', op),
          field('right', $._expression)
        ))
      }));
    },

    assignment_expression: $ => prec.right(seq(
      field('left', $._expression),
      repeat($._blank),
      field('operator', '='),
      repeat($._blank),
      field('right', $._expression)
    )),

    _label: $ => seq(
      field('label', alias($.label_identifier, $.identifier)),
      ':'
    ),

    macro_definition: $ => seq(
      optional(/(::)?B::/),
      field('command', alias($.macro_definition_command, $.identifier)),
      repeat1(seq(
        repeat1($._blank),
        field('macro', $.macro)
      )),
      $._terminator
    ),

    parameter_declaration: $ => seq(
      optional(/(::)?B::/),
      choice(
        field('command', alias(longAndShortForm('PARAMETERS'), $.identifier)),
        field('command', alias(longAndShortForm('RETURNVALUES'), $.identifier)),
        seq(
          field('command', alias(longAndShortForm('ENTRY'), $.identifier)),
          optional(seq(
            repeat1($._blank),
            alias(longAndShortForm('%LINE'), $.identifier)
          ))
        )
      ),
      repeat1(seq(
        repeat1($._blank),
        field('macro', $.macro)
      )),
      $._terminator
    ),

    subroutine_call_expression: $ => seq(
      optional(/(::)?B::/),
      field('command', alias(longAndShortForm('GOSUB'), $.identifier)),
      repeat1($._blank),
      field('subroutine', $.identifier),
      optional(seq(
        repeat1($._blank),
        field('arguments', alias($._command_arguments, $.argument_list)),
      )),
      $._terminator
    ),

    macro: $ => prec.left(choice(
      seq(
        '&',
        alias($.identifier, 'name')
      ),
      seq(
        '&',
        '(',
        alias($.identifier, 'name'),
        ')'
      ),
      seq(
        '&',
        '{',
        alias($.identifier, 'name'),
        '}'
      )
    )),

    recursive_macro_expansion: $ => prec.left(seq(
      '&&',
      optional('('),
      $.identifier,
      optional(')')
    )),

    macro_text_expansion: $ => prec.right(PREC.macro_text_expansion, choice(
      seq(
        $.macro,
        repeat1(choice(
          alias($.identifier, 'fragment'),
          $.macro
        ))
      ),
      seq(
        alias($.identifier, 'fragment'),
        $.macro,
        repeat(choice(
          alias($.identifier, 'fragment'),
          $.macro
        ))
      )
    )),

    macro_definition_command: $ => choice(
      longAndShortForm('GLOBAL'),
      longAndShortForm('LOCAL'),
      longAndShortForm('PRIVATE')
    ),

    command_expression: $ => seq(
      optional(/(::)?B::/),
      choice(
        seq(
          $._var_command,
          $._terminator
        ),
        seq(
          $._host_command,
          $._terminator
        ),
        seq(
          $._other_command,
          $._terminator
        )
      )
    ),

    _host_command: $ => seq(
      field('command', alias($._host_command_with_default_format, $.identifier)),
      repeat1($._blank),
      field('arguments', alias($._host_command_argument_list_default_format, $.argument_list))
    ),

    _host_command_with_default_format: $ => seq(
      longAndShortForm('OS'),
      seq(
        '.',
        alias($.identifier, 'subcommand')
      )
    ),

    _other_command: $ => seq(
      field('command', alias($._command_identifier, $.identifier)),
      optional(seq(
        repeat1($._blank),
        field('arguments', optional(alias($._command_arguments, $.argument_list))),
      ))
    ),

    _command_identifier: $ => seq(
      alias($.identifier, 'command'),
      repeat(seq(
        '.',
        alias($.identifier, 'subcommand')
      ))
    ),

    _command_arguments: $ => seq(choice(
      seq(
        repeat(choice(
          seq(
            optional(seq(
              $._command_argument,
              repeat($._blank)
            )),
            ',',
            repeat($._blank)
          ),
          seq(
            $._command_argument,
            repeat1($._blank)
          )
        )),
        choice(
          seq(
            $._command_argument,
            optional(',')
          ),
          ','
        ),
        optional(seq(
          repeat1($._blank),
          repeat(seq(
            $.option_expression,
            repeat1($._blank)
          )),
          $.option_expression,
          repeat(seq(
            repeat1($._blank),
            choice(
              $.macro,
              $.macro_text_expansion
            )
          ))
        ))
      ),
      seq(
        repeat(seq(
          $.option_expression,
          repeat1($._blank)
        )),
        $.option_expression,
        repeat(seq(
          repeat1($._blank),
          choice(
            $.macro,
            $.macro_text_expansion
          )
        ))
      )
    )),

    _host_command_argument_list_default_format: $ => seq(
      choice(
        $.macro,
        $.string,
        repeat1(/[^ \t\r\n]/)
      ),
      repeat(seq(
        repeat1($._blank),
        choice(
          $.macro,
          $.string,
          repeat1(/[^ \t\r\n]/)
        )
      ))
    ),

    _command_argument: $ => choice(
      $._expression,
      $.format_expression
    ),

    _command_argument_separator: $ => choice(
      $._blank,
      ',',
    ),

    option_expression: $ => prec(PREC.option, seq(
      '/',
      field('option', $.identifier),
      optional(seq(
        repeat1($._blank),
        field('value', choice(
          $.binary_expression,
          $.call_expression,
          $.identifier,
          $.macro,
          $.macro_text_expansion,
          $.unary_expression,
          $._literal
        ))
      ))
    )),

    format_expression: $ => seq(
      '%',
      field('value', choice(
        $.identifier,
        $.macro,
        $.macro_text_expansion
      )),
      repeat(seq(
        '.',
        field('value', choice(
          $.identifier,
          $.macro,
          $.macro_text_expansion
        ))
      ))
    ),

    call_expression: $ => prec(PREC.call, choice(
      $._hll_var_call_expression,
      seq(
        field('function', choice(
          $._expression,
          alias($._function_identifier, $.identifier)
        )),
        field('arguments', $.argument_list)
      )
    )),

    _function_identifier: $ => seq(
      alias($.identifier, 'function'),
      repeat(seq(
        '.',
        alias($.identifier, 'subfunction')
      ))
    ),

    argument_list: $ => seq(
      '(',
      optional(seq(
        $._expression,
        repeat(seq(
          repeat($._blank),
          ',',
          repeat($._blank),
          $._expression
        ))
      )),
      ')'
    ),


    /*****************************************
     * PRACTICE commands with HLL expressions
     *****************************************/

    _var_command: $ => choice(
      $._hll_var_command,
      $._hll_var_definition_command,
      $._non_hll_var_command
    ),

    _hll_var_command: $ => choice(
      $._hll_default_format_var_command,
      $._hll_non_default_format_var_command
    ),

    _hll_default_format_var_command: $ => seq(
      field('command', alias($._hll_var_command_with_default_format, $.identifier)),
      optional(seq(
        repeat1($._blank),
        field('arguments', alias($._hll_var_command_argument_list_default_format, $.argument_list))
      ))
    ),

    _hll_non_default_format_var_command: $ => choice(
      seq(
        field('command', alias(seq(
          longAndShortForm('Var'),
          '.',
          choice(
            longAndShortForm('AddSticker'),
            longAndShortForm('EXPORT'),
            longAndShortForm('WRITE')
          )
        ), $.identifier)),
        repeat1($._blank),
        field('arguments', alias($._hll_var_command_argument_list_non_default_format, $.argument_list))
      ),
      seq(
        field('command', alias(seq(
          longAndShortForm('Var'),
          '.',
          longAndShortForm('PATtern'),
        ), $.identifier)),
        repeat1($._blank),
        field('arguments', alias($._hll_var_pattern_command_argument_list_format, $.argument_list))
      )
    ),

    _non_hll_var_command: $ => seq(
      field('command', alias($._var_command_with_non_hll_format, $.identifier)),
      optional(seq(
        repeat1($._blank),
        field('arguments', alias($._var_command_argument_list_non_hll_format, $.argument_list))
      ))
    ),

    _hll_var_definition_command: $ => seq(
      seq(
        field('command', alias($._hll_var_definition_command_expression, $.identifier)),
        seq(
          repeat1($._blank),
          field('arguments', alias($._var_definition_command_argument_list_format, $.argument_list))
        ),
        optional(seq(
          /[ \t]*=[ \t]*/,
          field('value', choice(
            $.integer,
            $.hll_char_literal,
            $.hll_string_literal,
            $.hll_number_literal
          ))
        ))
      )
    ),

    _hll_var_command_with_default_format: $ => seq(
      longAndShortForm('Var'),
      repeat(seq(
        '.',
        alias($.identifier, 'subcommand')
      ))
    ),

    _hll_var_command_with_non_default_format: $ => seq(
      longAndShortForm('Var'),
      repeat(seq(
        '.',
        choice(
          longAndShortForm('AddSticker'),
        )
      ))
    ),

    _var_command_with_non_hll_format: $ => seq(
      longAndShortForm('Var'),
      seq(
        '.',
        choice(
          longAndShortForm('Local'),
          longAndShortForm('Ref'),
          longAndShortForm('TREE')
        )
      )
    ),

    _hll_var_definition_command_expression: $ => seq(
      longAndShortForm('Var'),
      '.',
      choice(
        longAndShortForm('NEWLOCAL'),
        longAndShortForm('NEWGLOBAL')
      )
    ),

    _hll_var_if_command: $ => seq(
      longAndShortForm('Var'),
      '.',
      longAndShortForm('IF')
    ),

    _hll_var_command_argument_list_default_format: $ => seq(
      seq(
        repeat(seq(
          choice(
            $.format_expression,
            seq(
              repeat(seq(
                $._hll_expression,
                $._hll_expression_separator
              )),
              $._hll_expression
            )
          ),
          repeat1($._blank)
        )),
        choice(
          seq(
            repeat(seq(
              $._hll_expression,
              $._hll_expression_separator
            )),
            $._hll_expression
          ),
          $.format_expression
        ),
      ),
      optional(seq(
        repeat1($._blank),
        repeat(seq(
          alias($.hll_option_expression, $.option_expression),
          repeat1($._blank)
        )),
        alias($.hll_option_expression, $.option_expression)
      ))
    ),

    _hll_var_command_argument_list_non_default_format: $ => choice(
      seq(
        choice(
          $.file_handle,
          $.path,
          $.symbol,
          $.string
        ),
        repeat1($._blank),
        repeat(seq(
          choice(
            $.format_expression,
            seq(
              repeat(seq(
                $._hll_expression,
                $._hll_expression_separator
              )),
              $._hll_expression
            )
          ),
          repeat1($._blank)
        )),
        choice(
          seq(
            repeat(seq(
              $._hll_expression,
              $._hll_expression_separator
            )),
            $._hll_expression
          ),
          $.format_expression
        ),
        optional(seq(
          repeat1($._blank),
          alias($.hll_option_expression, $.option_expression)
        ))
      )
    ),

    _hll_var_pattern_command_argument_list_format: $ => choice(
      seq(
        repeat(seq(
          $.format_expression,
          repeat1($._blank)
        )),
        repeat(seq(
          $.hll_type_pattern,
          $._blank
        )),
        $.hll_type_pattern
      )
    ),

    _var_command_argument_list_non_hll_format: $ => seq(
        repeat(seq(
          choice(
            $.format_expression,
            alias($.hll_option_expression, $.option_expression)
          ),
          repeat1($._blank)
        )),
        choice(
          $.format_expression,
          alias($.hll_option_expression, $.option_expression)
        )
    ),

    _var_definition_command_argument_list_format: $ => $.hll_declaration,

    _hll_var_call_expression_function: $ => seq(
        longAndShortForm('Var'),
        '.',
        alias($.identifier, 'subfunction')
    ),

    _hll_var_call_expression: $ => seq(
      field('function', alias($._hll_var_call_expression_function, $.identifier)),
      field('arguments', alias($.hll_var_call_expression_argument_list, $.argument_list))
    ),

    hll_var_call_expression_argument_list: $ => seq(
      '(',
      $._hll_expression,
      ')'
    ),

    hll_type_pattern: $ => seq(
      repeat1(choice(
        alias($.identifier, 'type'),
        '?',
        '*'
      ))
    ),

    hll_option_expression: $ => prec(PREC.option, seq(
      '/',
      field('option', $.identifier),
      optional(seq(
        repeat1($._blank),
        field('value', choice(
          $.hll_binary_expression,
          $.hll_call_expression,
          $.hll_cast_expression,
          $.hll_char_literal,
          $.hll_conditional_expression,
          $.hll_field_expression,
          $.hll_pointer_expression,
          $.hll_sizeof_expression,
          $.hll_string_literal,
          $.hll_subscript_expression,
          $.hll_unary_expression,
          $.hll_update_expression,
          $.identifier,
          $.symbol,
          $._hll_number_literal
        ))
      ))
    )),

    //////////////////////////////////////
    //////////////////////////////////////


    /********************************
     * HLL expressions
     ********************************/

    // On top level TRACE32 does not allow to separate operators
    // by spaces from the remainder of the expression. The only
    // exception seem to be assignment opeators. However, as soon
    // as the expression is nested and enclosed in parens spaces
    // are tolerated.
    _hll_expression: $ => choice(
      $._hll_number_literal,
      $.hll_assignment_expression,
      $.hll_binary_expression,
      $.hll_conditional_expression,
      $.hll_unary_expression,
      $.hll_update_expression,
      $.hll_cast_expression,
      $.hll_pointer_expression,
      $.hll_sizeof_expression,
      $.hll_subscript_expression,
      $.hll_call_expression,
      $.hll_field_expression,
      $.hll_string_literal,
      $.hll_char_literal,
      $.hll_parenthesized_expression,
      $.identifier,
      $.symbol
    ),

    // TRACE32 does not allow any spaces between function name
    // and opening parens
    hll_call_expression: $ => prec(PREC.call, seq(
      field('function', $._hll_expression),
      field('arguments', $.hll_argument_list)
    )),

    // TRACE32 does not allow any spaces between name of the struct
    // variable and field name
    hll_field_expression: $ => seq(
      prec(PREC.field, seq(
        field('argument', $._hll_expression),
        field('operator', choice(
          '.',
          '->'
        ))
      )),
      field('field', $._hll_field_identifier)
    ),

    // TRACE32 does neither allow any spaces between array name
    // and opening bracket nor index and brackets
    hll_subscript_expression: $ => prec(PREC.subscript, seq(
      field('argument', $._hll_expression),
      '[',
      field('index', choice(
        $._hll_expression,
        $.hll_range_expression
      )),
      ']'
    )),

    // TRACE32 does not allow any spaces after the closing
    // parens
    hll_cast_expression: $ => prec(PREC.cast, seq(
      '(',
      repeat($._blank),
      field('type', $.hll_type_descriptor),
      repeat($._blank),
      ')',
      field('value', $._hll_expression)
    )),

    // TRACE32 does not allow any spaces between sizeof keyword
    // and opening parens
    hll_sizeof_expression: $ => prec.right(PREC.sizeof, seq(
      'sizeof',
      choice(
        field('value', $._hll_expression),
        seq(
          '(',
          repeat($._blank),
          field('type', $.hll_type_descriptor),
          repeat($._blank),
          ')'
        )
      )
    )),

    // TRACE32 does not allow any spaces between operator
    // and follow-up part of the expression. A standalone '*'
    // will trigger the symbol search dialog.
    hll_pointer_expression: $ => prec.left(PREC.cast, seq(
      field('operator', choice(
        '*',
        '&'
      )),
      field('argument', $._hll_expression)
    )),

    // TRACE32 does not allow any spaces between the
    // different parts of the expressions
    hll_comma_expression: $ => seq(
      field('left', $._hll_expression),
      ',',
      field('right', choice(
        $._hll_expression,
        $.hll_comma_expression
      ))
    ),

    // TRACE32 does not allow any spaces between expressions and operator
    hll_update_expression: $ => {
      const argument = field('argument', $._hll_expression)
      const operator = field('operator', choice('--', '++'))

      return prec.right(PREC.unary, choice(
        seq(
          operator,
          argument
        ),
        seq(
          argument,
          operator
        )
      ));
    },

    // TRACE32 does not allow any spaces between expression and operator
    hll_unary_expression: $ => prec.left(PREC.unary, seq(
      field('operator', choice(
        '!',
        '~',
        '-',
        '+'
      )),
      field('argument', $._hll_expression)
    )),

    // TRACE32 does not allow any spaces between expressions and operator
    // on top level.
    hll_binary_expression: $ => {
      const table = [
        ['+', PREC.add_sub],
        ['-', PREC.add_sub],
        ['*', PREC.mul_div_mod],
        ['/', PREC.mul_div_mod],
        ['%', PREC.mul_div_mod],
        ['||', PREC.logical_or],
        ['&&', PREC.logical_and],
        ['|', PREC.bitwise_or],
        ['^', PREC.bitwise_xor],
        ['&', PREC.bitwise_and],
        ['==', PREC.equal],
        ['!=', PREC.equal],
        ['>', PREC.relational],
        ['>=', PREC.relational],
        ['<=', PREC.relational],
        ['<', PREC.relational],
        ['<<', PREC.shift],
        ['>>', PREC.shift]
      ]

      return choice(...table.map(([operator, precedence]) => {
        return prec.left(precedence, seq(
          field('left', $._hll_expression),
          field('operator', operator),
          field('right', $._hll_expression)
        ))
      }));
    },

    // TRACE32 does not allow any spaces between expressions and operator
    hll_range_expression: $ => prec.left(PREC.range, seq(
        field('left', $._hll_expression),
        repeat($._blank),
        field('operator', '..'),
        repeat($._blank),
        field('right', $._hll_expression)
    )),

    hll_assignment_expression: $ => prec.right(seq(
      field('left', $._hll_assignment_left_expression),
      repeat($._blank),
      field('operator', choice(
        '=',
        '*=',
        '/=',
        '%=',
        '+=',
        '-=',
        '<<=',
        '>>=',
        '&=',
        '^=',
        '|='
      )),
      repeat($._blank),
      field('right', $._hll_expression)
    )),

    _hll_assignment_left_expression: $ => choice(
      $.identifier,
      $.hll_call_expression,
      $.hll_field_expression,
      $.hll_pointer_expression,
      $.hll_subscript_expression,
      $.hll_parenthesized_expression,
      $.symbol,
    ),

    // TRACE32 does not allow any spaces between the ternary
    // operators
    hll_conditional_expression: $ => prec.right(seq(
      field('condition', $._hll_expression),
      '?',
      field('consequence', optional(seq(
        $._hll_expression,
      ))),
      ':',
      field('alternative', $._hll_expression)
    )),

    hll_char_literal: $ => seq(
      choice('L\'', 'u\'', 'U\'', 'u8\'', '\''),
      choice(
        $.hll_escape_sequence,
        alias(/[^\n']/, $.character),
      ),
      '\''
    ),

    hll_string_literal: $ => seq(
      choice('L"', 'u"', 'U"', 'u8"', '"'),
      repeat(choice(
        prec(1, /[^\\"\n]+/),
        $.hll_escape_sequence
      )),
      '"',
    ),

    _hll_number_literal: $ => seq(
        $._hll_number_literal_pre_hook,
        $.hll_number_literal
    ),

    hll_parenthesized_expression: $ => seq(
      '(',
      repeat($._blank),
      choice(
        $._hll_expression,
        $.hll_comma_expression
      ),
      repeat($._blank),
      ')'
    ),

    hll_type_descriptor: $ => seq(
      repeat($.hll_type_qualifier),
      repeat($._blank),
      field('type', $._hll_type_specifier),
      repeat(seq(
        repeat($._blank),
        $.hll_type_qualifier
      )),
      optional(seq(
        repeat($._blank),
        field('declarator', $._hll_abstract_declarator)
      ))
    ),

    hll_type_qualifier: $ => choice(
      'const',
      'volatile'
    ),

    _hll_declaration_modifiers: $ => $.hll_type_qualifier,

    _hll_type_specifier: $ => choice(
      $._hll_type_identifier,
      $.hll_union_specifier,
      $.hll_struct_specifier,
      $.hll_enum_specifier,
      $.hll_primitive_type,
      $.hll_sized_type_specifier
    ),

    hll_struct_specifier: $ => seq(
      'struct',
      repeat1($._blank),
      field('name', $._hll_type_identifier)
    ),

    hll_union_specifier: $ => seq(
      'union',
      repeat1($._blank),
      field('name', $._hll_type_identifier)
    ),

    hll_enum_specifier: $ => seq(
      'enum',
      repeat1($._blank),
      field('name', $._hll_type_identifier)
    ),

    hll_sized_type_specifier: $ => choice(
      seq(
        repeat1(
          seq(
            choice(
            'signed',
            'unsigned',
            'long',
            'short'
            ),
            repeat1($._blank)
          )
        ),
        field('type', $._hll_type_identifier)
      ),
      seq(
        repeat(seq(
          choice(
          'signed',
          'unsigned',
          'long',
          'short'
          ),
          repeat1($._blank)
        )),
        seq(
          choice(
          'signed',
          'unsigned',
          'long',
          'short'
          )
        )
      )
    ),

    hll_primitive_type: $ => token(choice(
      'bool',
      'char',
      'int',
      'float',
      'double',
      'void',
      'size_t',
      'ssize_t',
      'intptr_t',
      'uintptr_t',
      'charptr_t',
      ...[8, 16, 32, 64].map(n => `int${n}_t`),
      ...[8, 16, 32, 64].map(n => `uint${n}_t`),
      ...[8, 16, 32, 64].map(n => `char${n}_t`)
    )),

    hll_declaration: $ => seq(
      $._hll_declaration_specifiers,
      repeat($._blank),
      field('declarator', $._hll_declarator)
    ),

    _hll_declaration_specifiers: $ => seq(
      repeat(seq(
        $._hll_declaration_modifiers,
        repeat1($._blank)
      )),
      field('type', $._hll_type_specifier),
      repeat(seq(
        repeat1($._blank),
        $._hll_declaration_modifiers
      ))
    ),

    _hll_declarator: $ => choice(
      $.hll_pointer_declarator,
      $.hll_function_declarator,
      $.hll_array_declarator,
      $.hll_parenthesized_declarator,
      $.symbol
    ),

    hll_pointer_declarator: $ => prec.right(seq(
      $._hll_pointer_declarator_specifier,
      repeat($._blank),
      field('declarator', $._hll_declarator)
    )),

    hll_function_declarator: $ => prec(PREC.declarator, seq(
      field('declarator', $._hll_declarator),
      repeat($._blank),
      field('parameters', $.hll_parameter_list)
    )),

    hll_array_declarator: $ => prec.right(PREC.declarator, seq(
      '[',
      repeat(seq(
        repeat($._blank),
        $.hll_type_qualifier
      )),
      field('size', optional(seq(
        repeat($._blank),
        choice(
          $._hll_expression,
          '*'
        )
      ))),
      repeat($._blank),
      ']',
      repeat($._blank),
      field('declarator', $._hll_declarator)
    )),

    hll_parenthesized_declarator: $ => seq(
      '(',
      repeat($._blank),
      $._hll_declarator,
      repeat($._blank),
      ')'
    ),

    _hll_pointer_declarator_specifier: $ => seq(
      '*',
      optional(seq(
        repeat($._blank),
        seq(
          repeat(seq(
            $.hll_type_qualifier,
            repeat($._blank)
          )),
          $.hll_type_qualifier
        )
      ))
    ),

    _hll_abstract_declarator: $ => choice(
      $.hll_abstract_pointer_declarator,
      $.hll_abstract_function_declarator,
      $.hll_abstract_array_declarator,
      $.hll_abstract_parenthesized_declarator
    ),

    hll_abstract_pointer_declarator: $ => prec.right(seq(
      $._hll_pointer_declarator_specifier,
      repeat($._blank),
      field('declarator', optional($._hll_abstract_declarator))
    )),

    hll_abstract_function_declarator: $ => prec(PREC.declarator, seq(
      field('declarator', $._hll_abstract_declarator),
      repeat($._blank),
      field('parameters', $.hll_parameter_list)
    )),

    hll_abstract_array_declarator: $ => prec(PREC.declarator, seq(
      field('declarator', optional(seq(
        $._hll_abstract_declarator,
        repeat($._blank)
      ))),
      '[',
      repeat(seq(
        repeat($._blank),
        $.hll_type_qualifier
      )),
      field('size', optional(seq(
        repeat($._blank),
        choice(
          $._hll_expression,
          '*'
      )))),
      repeat($._blank),
      ']'
    )),

    hll_abstract_parenthesized_declarator: $ => prec(PREC.declarator, seq(
      '(',
      repeat($._blank),
      $._hll_abstract_declarator,
      repeat($._blank),
      ')'
    )),

    hll_parameter_list: $ => seq(
      '(',
      optional(seq(
        $.hll_parameter_declaration,
        repeat(seq(
          ',',
          $.hll_parameter_declaration
        ))
      )),
      ')'
    ),

    hll_parameter_declaration: $ => seq(
      $._hll_declaration_specifiers,
      optional(field('declarator', choice(
        $._hll_declarator,
        $._hll_abstract_declarator
      )))
    ),

    hll_argument_list: $ => seq(
      '(',
      repeat($._blank),
      optional(seq(
        $._hll_expression,
        repeat($._blank),
        repeat(seq(
          ',',
          repeat($._blank),
          $._hll_expression,
          repeat($._blank),
        ))
      )),
      ')'
    ),

    hll_escape_sequence: $ => token(prec(PREC.escape_sequence, seq(
      '\\',
      choice(
        /[^xuU]/,
        /\d{2,3}/,
        /x[0-9a-fA-F]{2,}/,
        /u[0-9a-fA-F]{4}/,
        /U[0-9a-fA-F]{8}/
      )
    ))),

    _hll_type_identifier: $ => alias($.identifier, $.hll_type_identifier),
    _hll_field_identifier: $ => alias($.identifier, $.hll_field_identifier),

    _hll_expression_separator: $ => choice(
      /[ \t]*,[ \t]*/,
      /[ \t]*;[ \t]*/,
    ),

    //////////////////////////////////////
    //////////////////////////////////////


    /********************************
     * Literal types
     ********************************/

    _literal: $ => choice(
      $.address,
      $.bitmask,
      $.character,
      alias($._composed_name, $.identifier),
      $.file_handle,
      $.float,
      $.frequency,
      $.integer,
      alias($._special_command_operator, $.literal),
      $.percentage,
      $.string,
      $.symbol,
      $.time
    ),

    _address_expression: $ => choice(
      $.integer,
      $.macro,
      $.macro_text_expansion,
      alias($._address_binary_expression, $.binary_expression),
      $.call_expression,
      $._parenthesized_address_expression
    ),

    memory_space: $ => choice(
      // Machine identifier:::Memory space identifier::Memory segment identifier:
      seq(
        field('machine', $._address_expression),
        ':::',
        field('space', $._address_expression),
        '::',
        field('segment', $._address_expression),
        ':'
      ),
      seq(
        field('machine', $._address_expression),
        ':::',
        choice(
          seq(
            field('space', $._address_expression),
            '::'
          ),
          seq(
            field('segment', $._address_expression),
            ':'
          )
        )
      ),
      seq(
        field('space', $._address_expression),
        '::',
        field('segment', $._address_expression),
        ':'
      ),
      seq(
        field('machine', $._address_expression),
        ':::'
      ),
      seq(
        field('space', $._address_expression),
        '::'
      ),
      seq(
        field('segment', $._address_expression),
        ':'
      )
    ),

    access_class: $ => /[a-zA-Z][a-zA-Z0-9]*:/,

    address: $ => choice(
      seq(
        choice(
          seq(
            field('access', $.access_class),
            optional($.memory_space)
          ),
          $.memory_space
        ),
        field('location', $._address_expression)
      ),
      $.access_class
    ),

    _parenthesized_address_expression: $ => choice(
      seq(
        '(',
        $._address_expression,
        ')'
      ),
      seq(
        '{',
        $._address_expression,
        '}'
      )
    ),

    _address_binary_expression: $ => {
      const operators = [
        ['+', PREC.add_sub],
        ['-', PREC.add_sub],
        ['*', PREC.mul_div_mod],
        ['/', PREC.mul_div_mod],
        ['%', PREC.mul_div_mod],
        ['|', PREC.bitwise_or],
        ['^', PREC.bitwise_xor],
        ['..', PREC.range],
        ['--', PREC.range],
        ['++', PREC.range]
      ];

      return choice(...operators.map(([op, pre]) => {
        return prec.left(pre, seq(
          field('left', $._address_expression),
          field('operator', op),
          field('right', $._address_expression)
        ))
      }));
    },

    integer: $ => choice(
      ...RE_BIN_HEX_NUMBER,
      seq(
        $._decimal_number_pre_hook,
        $._decimal_number
      )
    ),

    float: $ => /[0-9]+\.[0-9]+(e[-+][0-9]+)?/,

    bitmask: $ => choice(
      /0y[0-9xX]+/,  // Bitmask
      /0x[0-9a-fA-FxX]+/,  // Hexmask
    ),

    string: $ => seq(
      '"',
      repeat(choice(
        /[^"&]+/,
        /""/,  // Escape sequence
        $._ampersand_char,
        $.macro,
      )),
      '"'
    ),

    character: $ => seq(
      "'",
      choice(
        /\\[^'\n]/,
        /[^\n]/,
      ),
      "'"
    ),

    _line_specifier: $ => token(choice(
      /\\[0-9]+(\\[0-9]+)?/,
      /\\[0-9]+\\[0-9]*\\[0-9]+/
    )),

    // Symbol names may omit earlier segments. After the first included segments
    // all later ones must be included. However, they may contain only the
    // separator.
    // Module names with single backslash are handled as internal C-style variables.
    // During parsing there is no way to differentiate. We reuse the token for
    // TRACE32 internal HLL variables to make the conflict obvious for the
    // generator.
    // The naming requirements for machine, program and module names are less strict
    // than those for function or method names.
    symbol: $ => choice(
      seq(
        choice(
          seq(
            '\\\\\\',
            choice(
              RE_QUOTED_SYMBOL_NAME,
              seq(
                RE_MACHINE_PROG_MOD_NAME,
                optional(choice(
                  $.macro,
                  $.macro_text_expansion
                ))
              ),
              $.macro,
              $.macro_text_expansion
            ),
            optional(seq(
              '\\\\',
              optional(choice(
                RE_QUOTED_SYMBOL_NAME,
                seq(
                  RE_MACHINE_PROG_MOD_NAME,
                  optional(choice(
                    $.macro,
                    $.macro_text_expansion
                  ))
                ),
                $.macro,
                $.macro_text_expansion
              ))
            )),
            optional(seq(
              '\\',
              optional(choice(
                RE_QUOTED_SYMBOL_NAME,
                seq(
                  RE_MACHINE_PROG_MOD_NAME,
                  optional(choice(
                    $.macro,
                    $.macro_text_expansion
                  ))
                ),
                $.macro,
                $.macro_text_expansion,
                $.string
              ))
            )),
            optional(seq(
              '\\',
              choice(
                seq(
                  RE_FUNCTION_NAME,
                  optional(choice(
                    $.macro,
                    $.macro_text_expansion
                  ))
                ),
                $.macro,
                $.macro_text_expansion
              )
            )),
            repeat(seq(
              '\\',
              choice(
                RE_QUOTED_SYMBOL_NAME,
                seq(
                  RE_UNQUOTED_SYMBOL_NAME,
                  optional(choice(
                    $.macro,
                    $.macro_text_expansion
                  ))
                ),
                $.macro,
                $.macro_text_expansion
              )
            ))
          ),
          seq(
            '\\\\',
            choice(
              RE_QUOTED_SYMBOL_NAME,
              seq(
                RE_MACHINE_PROG_MOD_NAME,
                optional(choice(
                  $.macro,
                  $.macro_text_expansion
                ))
              ),
              $.macro,
              $.macro_text_expansion
            ),
            optional(seq(
              '\\',
              optional(choice(
                RE_QUOTED_SYMBOL_NAME,
                seq(
                  RE_MACHINE_PROG_MOD_NAME,
                  optional(choice(
                    $.macro,
                    $.macro_text_expansion
                  ))
                ),
                $.macro,
                $.macro_text_expansion,
                $.string,
              ))
            )),
            optional(seq(
              '\\',
              choice(
                seq(
                  RE_FUNCTION_NAME,
                  optional(choice(
                    $.macro,
                    $.macro_text_expansion
                  ))
                ),
                $.macro,
                $.macro_text_expansion
              )
            )),
            repeat(seq(
              '\\',
              choice(
                RE_QUOTED_SYMBOL_NAME,
                seq(
                  RE_UNQUOTED_SYMBOL_NAME,
                  optional(choice(
                    $.macro,
                    $.macro_text_expansion
                  ))
                ),
                $.macro,
                $.macro_text_expansion
              ),
            ))
          ),
          seq(
            '\\',
            choice(
              RE_QUOTED_SYMBOL_NAME,
              seq(
                RE_MACHINE_PROG_MOD_NAME,
                optional(choice(
                  $.macro,
                  $.macro_text_expansion
                ))
              ),
              $.macro,
              $.macro_text_expansion,
              $.string,
            ),
            optional(seq(
              '\\',
              choice(
                seq(
                  RE_FUNCTION_NAME,
                  optional(choice(
                    $.macro,
                    $.macro_text_expansion
                  ))
                ),
                $.macro,
                $.macro_text_expansion
              )
            )),
            repeat(seq(
              '\\',
              choice(
                RE_QUOTED_SYMBOL_NAME,
                seq(
                  RE_UNQUOTED_SYMBOL_NAME,
                  optional(choice(
                    $.macro,
                    $.macro_text_expansion
                  ))
                ),
                $.macro,
                $.macro_text_expansion
              )
            ))
          ),
          seq(
            RE_QUOTED_SYMBOL_NAME,
            repeat(seq(
              '\\',
              choice(
                RE_QUOTED_SYMBOL_NAME,
                seq(
                  RE_UNQUOTED_SYMBOL_NAME,
                  optional(choice(
                    $.macro,
                    $.macro_text_expansion
                  ))
                ),
                $.macro,
                $.macro_text_expansion
              ),
            ))
          ),
        ),
        optional($._line_specifier)
      ),
      seq(
        alias($.identifier, 'function'),
        $._line_specifier
      ),
      seq(
        seq(
          RE_METHOD_NAME,
          optional(choice(
            $.macro,
            $.macro_text_expansion
          ))
        ),
        repeat(seq(
          '\\',
          choice(
            RE_QUOTED_SYMBOL_NAME,
            seq(
              RE_UNQUOTED_SYMBOL_NAME,
              optional(choice(
                $.macro,
                $.macro_text_expansion
              ))
            ),
            $.macro,
            $.macro_text_expansion
          )
        ))
      )
    ),

    _composed_name: $ => token(seq(
      /[A-Za-z][A-Za-z0-9]+/,
      repeat1(seq(
        '-',
        /[A-Za-z0-9]+/
      ))
    )),

    time: $ => /[0-9]+\.?[0-9]*[mnu]*s/,

    frequency: $ => /[0-9]+\.?[0-9]*[kKmMgG]*[hH][zZ]/,

    percentage: $ => /[0-9]+\.?[0-9]*%/,

    _special_command_operator: $ => choice(
      $._file_dialog
    ),

    _file_dialog: $ => '*',

    file_handle: $ => seq(
      '#',
      prec.right(repeat1(choice(
        /[0-9]+/,
        $.macro
      )))
    ),

    _expression: $ => choice(
      $.assignment_expression,
      $.binary_expression,
      $.call_expression,
      $.identifier,
      $.unary_expression,
      $.macro,
      $.macro_text_expansion,
      $._literal,
      $._parenthesized_expression,
      $._path_expression
    ),

    identifier: $ => /[0-9]*[A-Za-z_]\w*/,

    comment: $ => /[ \t]*(;|\/\/)(\\\r?\n|[^\n])*\n/,

    _blank_line: $ => /[ \t]*\r?\n/,

    _filler_line: $ => choice(
      $._blank_line,
      $.comment
    ),

    _terminator: $ => choice(
      $.comment,
      $._blank_line
    ),

    _line_continuation: $ => /\\\r?\n/,

    _blank: $ => /[ \t]/,
  }
})

function longAndShortForm(keyword, aliasAsWord = true) {
  // Capture short form: RePeaT -> [rR][pP][tT]
  const short = keyword
    .split('')
    .map(l => l === l.toUpperCase() ? `[${l.toLowerCase()}${l}]` : '')
    .join('')

  // Capture long form: RePeaT -> [rR][eE][pP][eE][aA][tT]
  const long = keyword
    .split('')
    .map(l => `[${l.toLowerCase()}${l.toUpperCase()}]`)
    .join('')

  let result = new RegExp([short, long].join('|'))
  if (!short || short === long) {
    result = new RegExp(long)
  }

  if (aliasAsWord) {
    result = alias(result, keyword)
  }
  return result
}
