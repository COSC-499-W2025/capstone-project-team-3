module.exports = grammar({
  name: 'fusion',

  extras: $ => [
    $._whitespace
  ],

  externals: $ => [
    $.afx_comment
  ],

  supertypes: $ => [
    $.statement,
    $.eel_expression,
    $.eel_primary_expression,
  ],

  precedences: $ => [
    [
      $.resource,
      $.fileglobbing,
      $.filepath,
    ],
    [
      'logical_and',
      'logical_or',
      'binary_releation',
      'binary_equality',
      'binary_times',
      'binary_plus',
      'ternary',
      $.eel_arrow_function,
    ],
    [
      $.eel_binary_expression,
      $.eel_arrow_function
    ]
  ],

  rules: {

    program: $ => repeat(
      choice(
        $.statement,
        $.comment,
      )
    ),

    statement: $ => choice(
      $.include_statement,
      $.namespace_declaration,
      $.property
    ),

    namespace_declaration: $ => seq(
      'namespace',
      ':',
      $.alias_namespace,
      '=',
      $.package_name
    ),

    include_statement: $ => seq(
      'include',
      ':',
      $.source_file
    ),

    property: $ => seq(
      $.path,
      choice(
        $.assignment,
        $.deletion,
        $.copy,
        $.block
      )
    ),

    path: $ => {
      const fragment = choice(
        $.string,
        $.path_part,
        $.meta_property,
        $.prototype_signature
      );

      return nested1(fragment);
    },

    block: $ => seq(
      field('start', '{'),
      field('content', repeat(
        choice(
          $.property,
          $.comment
        )
      )),
      field('end', '}')
    ),

    path_part: $ => choice('prototype', $._identifier_path),

    meta_property: $ => seq('@', $._identifier_path),

    deletion: $ => '>',

    copy: $ => seq(
      '<',
      field('source',
        choice(
          $.boolean,
          $.null,
          $.number,
          $.string,
          $.prototype_instance,
          $._copied_prototype_signature,
        )
      )
    ),

    assignment: $ => seq(
      '=',
      field('value',
        choice(
          $.boolean,
          $.null,
          $.number,
          $.string,
          $.value_dsl,
          $.prototype_instance,
          $.value_expression,
        )
      )
    ),

    value_expression: $ => seq(
      field('start', '${'),
      field('content', $.eel_expression),
      field('end', '}')
    ),

    source_file: $ => choice(
      $.resource,
      $.fileglobbing,
      $.filepath
    ),

    resource: $ => {
      const raw = prec.right(
        seq(
          'resource://',
          optional($.package_name),
          '/',
          choice(
            $.filepath,
            $.fileglobbing,
          )
        )
      );
      const quoted = seq("'", raw, "'");
      const doublequoted = seq('"', raw, '"');

      return choice(
        raw,
        quoted,
        doublequoted
      );
    },

    _filepath_fragment: $ => {
      const delimiter = '/';
      const name = choice(
        /[\w\-_]+/,
        '.',
        '..'
      );

      return seq(
        optional(delimiter),
        name
      );
    },

    filepath: $ => {
      const raw = prec.right(seq(
        repeat1($._filepath_fragment),
        '.fusion',
      ));
      const quoted = seq("'", raw, "'");
      const doublequoted = seq('"', raw, '"');

      return choice(
        raw,
        quoted,
        doublequoted
      );
    },

    fileglobbing: $ => {
      const raw = prec.right(seq(
        repeat($._filepath_fragment),
        seq(
          choice(
            '/*',
            '/**/*'
          ),
          optional(
            '.fusion',
          )
        )
      ));
      const quoted = seq("'", raw, "'");
      const doublequoted = seq('"', raw, '"');

      return choice(
        raw,
        quoted,
        doublequoted
      );
    },

    value_dsl: $ => choice(
      seq(
        field('start', 'afx`'),
        field('content', $._afx_statement),
        field('end', '`')
      ),
      seq(
        field('start', $.dsl_start),
        field('content', $.dsl_content),
        field('end', '`')
      )
    ),

    package_name: $ => $._nested_identifier_type,

    type: $ => seq(
      optional(
        seq(
          field( 'namespace', $.package_name),
          token.immediate(':')
        )
      ),
      field('name', alias($._nested_identifier_type, $.type_name))
    ),

    dsl_start: $ => /[A-Za-z0-9\.]+`/,

    dsl_content: $ => /[^`]*/,

    _copied_prototype_signature: $ => seq(
      $.prototype_signature,
      optional($.block)
    ),

    prototype_signature: $ => seq(
      'prototype',
      token.immediate('('),
      $.type,
      ')'
    ),

    prototype_instance: $ => seq(
      $.type,
      optional(
        $.block
      )
    ),

    _identifier_path: $ => {
      const wordChar = /[A-Za-z0-9_]/;

      return seq(
        wordChar,
        optional(seq(
          repeat(choice(
            wordChar,
            ':',
            '-',
          )),
          wordChar
        ))
      );
    },

    alias_namespace: $ => /[A-Za-z][A-Za-z0-9]*/,

    // Eel Expressions
    // ---------------------
    eel_expression: $ => choice(
      $.eel_primary_expression,
      $.eel_binary_expression,
      $.eel_ternary_expression,
    ),

    eel_primary_expression: $ => choice(
      $.eel_parenthesized_expression,
      $.eel_not_expression,
      $.string,
      $.number,
      $.boolean,
      $.eel_array,
      $.eel_object,
      $.eel_object_path,
      $.eel_arrow_function,
    ),

    eel_ternary_expression: $ => prec.right('ternary', seq(
      field('condition', $.eel_expression),
      '?',
      field('consequence', $.eel_expression),
      ':',
      field('alternative', $.eel_expression),
    )),

    eel_binary_expression: $ => choice(
      ...[
        ['&&', 'logical_and'],
        ['and', 'logical_and'],
        ['||', 'logical_or'],
        ['or', 'logical_or'],
        ['*', 'binary_times'],
        ['/', 'binary_times'],
        ['%', 'binary_times'],
        ['+', 'binary_plus'],
        ['-', 'binary_plus'],
        ['==', 'binary_equality'],
        ['!=', 'binary_equality'],
        ['<=', 'binary_releation'],
        ['>=', 'binary_releation'],
        ['<', 'binary_releation'],
        ['>', 'binary_releation'],
      ].map(([operator, precedence]) =>
        prec.left(precedence, seq(
          field('left', $.eel_expression),
          field('operator', operator),
          field('right', $.eel_expression)
        ))
      )
    ),

    eel_not_expression: $ => prec.left(seq(
      choice(
        '!',
        'not',
      ),
      $.eel_expression
    )),

    eel_parenthesized_expression: $ => seq(
      '(',
      $.eel_expression,
      ')'
    ),

    eel_object_path: $ => {
      const pathIdentifier = alias($._eel_identifier, $.eel_path_identifier);

      return prec.right(seq(
        choice(
          $.eel_method_call,
          pathIdentifier
        ),
        repeat(choice(
          seq(
            '.',
            choice(
              $.eel_method_call,
              pathIdentifier
            )
          ),
          $.eel_offset_access,
        ))
      ));
    },

    eel_array: $ => seq(
      field('start', '['),
      commaSep($.eel_expression),
      field('end', ']'),
    ),

    eel_object: $ => seq(
      field('start', '{'),
      commaSep($.eel_object_pair),
      field('end', '}')
    ),

    eel_object_pair: $ => seq(
      field('key', alias($._eel_identifier, $.eel_property_name)),
      ':',
      field('value', $.eel_expression)
    ),

    eel_arrow_function: $ => seq(
      field('parameters', seq(
        '(',
        field('argument', commaSep(
          alias($._eel_identifier, $.eel_parameter)
        )),
        ')',
      )),
      '=>',
      field('body', choice(
        seq('{', $.eel_expression, '}'),
        $.eel_expression
      ))
    ),

    eel_method_call: $ => seq(
      alias($._eel_identifier, $.eel_method_name),
      seq(
        '(',
        commaSep(field('parameter', $.eel_expression)),
        ')'
      ),
    ),

    eel_offset_access: $ => seq(
      '[',
      field('index', $.eel_expression),
      ']'
    ),

    _eel_identifier: $ => /[a-zA-Z_][a-zA-Z0-9_\-]*/,

    // AFX
    // -------------------
    _afx_statement: $ => prec.left(repeat1(choice(
      $.afx_comment,
      $._afx_element,
      $.afx_text,
      $._afx_expression,
    ))),

    _afx_element: $ => choice(
      $.afx_element,
      $.afx_element_self_closing
    ),

    afx_element: $ => seq(
      field('open_tag', $.afx_opening_element),
      repeat($._afx_statement),
      field('close_tag', $.afx_closing_element)
    ),

    afx_element_self_closing: $ => seq(
      '<',
      field('name', alias($._afx_element_name, $.afx_identifier)),
      repeat(field('afx_attribute', $._afx_attribute)),
      '/>'
    ),

    afx_opening_element: $ => seq(
      '<',
      field('name', alias($._afx_element_name, $.afx_identifier)),
      repeat(field('afx_attribute', $._afx_attribute)),
      '>'
    ),

    afx_closing_element: $ => seq(
      '<',
      '/',
      field('name', alias($._afx_element_name, $.afx_identifier)),
      '>'
    ),

    _afx_element_name: $ => choice(
      $._afx_identifier,
      $.afx_type,
    ),

    afx_type: $ => seq(
      field('namespace', alias($._afx_nested_identifier, $.afx_package_name)),
      token.immediate(':'),
      field('name', alias($._afx_nested_identifier, $.afx_type_name))
    ),

    _afx_attribute: $ => choice(
      $.afx_attribute,
      $._afx_expression
    ),

    afx_attribute: $ => seq(
      field('name', $._afx_attribute_name),
      optional(seq(
        '=',
        field('value', $._afx_attriute_value)
      ))
    ),

    _afx_attribute_name: $ => seq(
      choice(
        alias($._afx_identifier, $.afx_property_identifier),
        alias($._afx_meta_property_identifier, $.afx_meta_property_identifier),
      ),
      optional(seq('.', alias($._afx_nested_identifier, $.afx_property_path)))
    ),

    _afx_attriute_value: $ => choice(
      $.string,
      $._afx_expression,
    ),

    _afx_expression: $ => seq(
      '{',
      choice(
        $.eel_expression,
        $.afx_spread,
      ),
      '}',
    ),

    afx_spread: $ => seq(
      '...',
      $.eel_expression,
    ),

    afx_text: $ => /[^{}<>`]+/,

    _afx_meta_property_identifier: $ => seq('@', $._afx_identifier),

    _afx_identifier: $ => /[a-zA-Z0-9_\-]+/,

    _afx_nested_identifier: $ => nested1($._afx_identifier),


    // Primitives
    // -------------------
    number: $ => /-?\d+(\.\d+)?/,

    string: $ => choice(
      seq(
        '"',
        repeat(choice(
          /\\\\/,
          '\\"',
          /[^\"]/
        )),
        '"'
      ),
      seq(
        "'",
        repeat(choice(
          /\\\\/,
          "\\'",
          /[^\']/
        )),
        "'"
      )
    ),

    null: $ => choice('null', 'NULL'),

    boolean: $ => choice(
      'true',
      'TRUE',
      'false',
      'FALSE',
    ),

    _identifier_type: $ => /[A-Za-z0-9]+/,

    _nested_identifier_type: $ => nested1($._identifier_type),

    _whitespace: $ => /[\s\uFEFF\u2060\u200B\u00A0]/,

    comment: $ => token(
      choice(
        seq('//', /.*/),
        seq('#', /.*/),
        seq(
          '/*',
          /[^*]*\*+([^/*][^*]*\*+)*/,
          '/'
        )
      )
    ),
  }
});

function commaSep1(rule) {
  return seq(rule, repeat(seq(',', rule)));
}

function commaSep(rule) {
  return optional(commaSep1(rule));
}

function nested1(rule, delimiter='.') {
  return seq(
    rule,
    repeat(seq(
      token.immediate(delimiter),
      rule
    ))
  );
}

function nested(rule, delimiter='.') {
  return optional(nested1(rule, delimiter));
}
