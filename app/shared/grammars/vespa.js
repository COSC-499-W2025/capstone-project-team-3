const 
  unicodeLetter = /\p{L}/,
  unicodeDigit = /[0-9]/,
  letter = choice(unicodeLetter, '_', '-', '.'),
  newline = '\n',
  terminator = choice(newline, ';')


module.exports = grammar({
  name: 'vespa',

  extras: $ => [
    $.comment,
    /\s/
  ],

  rules: {
    schema_file: $ => repeat(choice(
      seq($.schema_declaration, optional(terminator)),
    )),

    schema_declaration: $ => seq(
        'schema',
        field('name', $.identifier),
        optional(seq(
            'inherits',
            $.identifier,
        )),
        field('body', optional($.block)),
    ),

    field_declaration: $ => seq(
        'field',
        field('name', $.identifier),
        'type',
        $.field_type,
        $.field_body,
    ),

    struct_field: $ => seq(
        'struct-field',
        field('name', $.identifier),
        $.field_body,
    ),

    summary_declaration: $ => seq(
        'summary',
        field('name', $.identifier),
        'type',
        $.field_type,
        $.field_body,
    ),

    document_summary: $ => seq(
        'document-summary',
        field('name', $.identifier),
        optional(seq(
            'inherits',
            $.identifier,
        )),
        field('body', optional($.block)),
    ),

    rank_profile: $ => seq(
        'rank-profile',
        field('name', $.identifier),
        optional(seq(
            'inherits',
            commaSep($.identifier),
        )),
        field('body', optional($.block)),
    ),

    identifier: $ => token(seq(
      letter,
      repeat(choice(letter, unicodeDigit))
    )),

    _expression: $ => choice(
        $.identifier,
        $.int_literal,
    ),

    field_type: $ => choice(
        $.array_type,
        $.weighted_set_type,
        'bool',
        'byte',
        'double',
        'float',
        'int',
        'long',
        'position',
        'predicate',
        'raw',
        'string',
        'structname',
        $.map_type,
        $.tensor_type,
        'uri',
        $.reference_type,
    ),

    reference_type: $ => seq(
      'reference',
      '<',
      $.identifier,
      '>',
    ),

    map_type: $ => seq(
      'map',
      '<',
      $.identifier,
      ',',
      $.identifier,
      '>',
    ),

    tensor_value_type: $ => choice(
        'float',
        'double',
        'int8',
        'bfloat16',
    ),

    tensor_type: $ => seq(
        'tensor',
        '<',
        $.tensor_value_type,
        '>',
        '(',
        commaSep($.tensor_dimension),
        ')',
    ),

    tensor_dimension: $ => seq(
        alias($.identifier, $.dimension_name),
        choice(
          '{}',
          seq(
            '[',
            $.int_literal,
            ']',
          ),
        ),
    ),

    weighted_set_type: $ => seq(
      'weightedset',
      '<',
      $.identifier,
      '>',
    ),

    array_type: $ => seq(
      'array',
      '<',
      $.identifier,
      '>',
    ),

    // TODO: Should rename as its shared by field, document-summary, and struct-field?
    field_body: $ => seq(
      '{',
        optional(seq(
        $.element,
        repeat(seq(terminator, $.element)),
        optional(terminator)
        )),
      '}',
    ),


    block: $ => seq(
      '{',
      optional($._statement_list),
      '}',
    ),

    element: $ => seq(
      field('name', alias($.identifier, $.element_name)),
      optional(field('argument', $.identifier)),
      choice(
        ':',
        seq(
          '{',
          optional($._statement_list),
          '}',
        ),
      ),
      field('arguments', optional($.element_arguments)),
    ),

    element_arguments: $ => seq(
      pipeSep($._expression),
    ),

    _statement_list: $ => choice(
     seq(
       $._statement,
       repeat(seq(terminator, $._statement)),
       optional(seq(
         terminator,
       )),
     ),
    ),

    _statement: $ => choice(
        $.block,
        $.field_declaration,
        $.element,
        // Document Summary
        $.document_summary,
        $.summary_declaration,
        $.struct_field,
        // Rank Profile
        $.rank_profile,
    ),

    int_literal: $ => token(seq(
      /[1-9]/,
      repeat(unicodeDigit),
    )),

    comment: $ => token(seq('#', /.*/)),
  }
});

function pipeSep(rule) {
  return seq(rule, repeat(seq('|', rule)))
}

function commaSep(rule) {
    return seq(rule, repeat(seq(',', rule)))
}
