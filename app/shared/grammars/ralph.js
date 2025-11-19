const PREC = {
  call: 15,
  field: 14,
  unary: 12,
  multiplicative: 10,
  additive: 9,
  shift: 8,
  bitand: 7,
  bitxor: 6,
  bitor: 5,
  comparative: 4,
  and: 3,
  or: 2
};

//TODO: not used yet
const USING_ANNOTATIONS = {
  usePreapprovedAssetsKey: 'preapprovedAssets',
  useContractAssetsKey: 'assetsInContract',
  useCheckExternalCallerKey: 'checkExternalCaller',
  useUpdateFieldsKey: 'updateFields',
  useMethodIndexKey: 'methodIndex'
};

const primitiveTypes = ['Bool', 'I256', 'U256', 'ByteVec', 'Address'];

module.exports = grammar({

  name: 'ralph',

  conflicts: $ => [
  ],

  extras: $ => [
    /\s/,
    $.line_comment
  ],

  rules: {
    source_file: $ => repeat(
      choice(
        $._statement,
        $.tx_script,
        $.asset_script,
        $.contract,
        $.interface,
        $.struct
      )),

    line_comment: $ => seq(/\/\/.*/),

    tx_script: $ => seq(
      repeat($.annotation),
      'TxScript',
      $.type_identifier,
      optional($.args_def),
      '{',
      repeat($._statement),
      repeat($.func),
      '}'
    ),

    asset_script: $ => seq(
      'AssetScript',
      $.type_identifier,
      optional($.args_def),
      '{',
      repeat($.func),
      '}',
    ),

    contract: $ => seq(
      repeat($.annotation),
      optional('Abstract'),
      'Contract',
      $.type_identifier,
      $.args_def,
      optional($.contract_extending),
      optional($.interface_implementing),
      '{',
      repeat(choice($.map_def, $.event_def, $.constant_var_def, $.enum_def, $.func)),
      '}'
    ),

    interface: $ => seq(
      repeat($.annotation),
      'Interface',
      $.type_identifier,
      optional($.interface_extends),
      '{',
      repeat($.event_def),
      repeat($.func),
      '}'
    ),

    struct: $ => seq(
      'struct',
      $.type_identifier,
      '{',
      sepBy($.struct_field, ','),
      '}'
    ),

    mutable: $ => 'mut',

    struct_field: $ => seq(
      optional($.mutable),
      $.identifier,
      ':',
      $._type
    ),

    annotation: $ => seq(
      '@',
      $.identifier,
      optional($._annotation_fields)
    ),

    _annotation_fields: $ => seq(
      '(',
      sepBy1($.annotation_field, ','),
      ')'
    ),

    args_def: $ => seq(
      '(',
      sepBy($.arg_def, ','),
      ')'
    ),

    annotation_field: $ => seq(
      $.identifier,
      '=',
      choice($._const_expr, $.identifier)
    ),

    arg_def: $ => seq(
      optional($.annotation),
      optional($.mutable),
      $.identifier,
      ':',
      choice($._type, $.array_type),
    ),

    map_def: $ => seq(
      'mapping',
      '[',
      field('key_type', $.type_identifier),
      ',',
      field('value_type', $.type_identifier),
      ']',
      $.identifier
    ),

    event_def: $ => seq(
      'event',
      $.type_identifier,
      '(',
      sepBy($.event_field, ','),
      ')'
    ),

    event_field: $ => seq(
      $.identifier,
      ':',
      field('namedType', $.type_identifier)
    ),

    constant_var_def: $ => seq(
      'const',
      $.type_identifier,
      '=',
      choice($._const_expr, $.stringLiteral)
    ),

    enum_field: $ => seq(
      $.type_identifier,
      '=',
      choice($._const_expr, $.stringLiteral)
    ),

    enum_fields: $ => seq(
      '{',
      repeat($.enum_field),
      '}'
    ),

    enum_def: $ => seq(
      'enum',
      $.type_identifier,
      $.enum_fields
    ),

    func: $ => seq(
      repeat($.annotation),
      optional('pub'),
      'fn',
      $.func_id,
      $.args_def,
      $.return_type,
      optional(seq('{', repeat($._statement), '}'))
    ),

    // interface_func: $ => seq(
    //   repeat($.annotation),
    //   optional('pub'),
    //   'fn',
    //   $.func_id,
    //   $.args_def,
    //   $.return_type,
    // ),

    return_type: $ => choice(
      $.simple_return_type,
      $.bracket_return_type
    ),

    simple_return_type: $ => seq(
      '->',
      $._type
    ),

    bracket_return_type: $ => seq(
      '->',
      '(',
      sepBy($._type, ','),
      ')'
    ),

    inheritance_fields: $ => seq(
      '(',
      sepBy($.identifier, ','),
      ')'
    ),

    contract_extending: $ => seq(
      choice('extends', 'embeds'),
      sepBy1(seq(
        $.type_identifier,
        $.inheritance_fields
      ), ',')
    ),

    interface_implementing: $ => seq(
      'implements',
      sepBy1(field('interface_inheritance', $.type_identifier), ',')
    ),

    interface_extends: $ => seq(
      'extends',
      sepBy1(field('interface_inheritance', $.type_identifier), ',')
    ),


    identifier: $ => prec(1, /[a-z][a-zA-Z0-9]*/),

    func_id: $ => seq(
      $.identifier,
      optional('!')
    ),

    type_identifier: $ => prec(1, /[A-Z][A-Za-z0-9]*/),

    hex_num: $ => seq(
      '0x',
      /[0-9a-fA-F]*/
    ),

    integer: $ => seq(
      /[0-9_]+/,
      optional(seq(
        '.',
        /[0-9_]+/,
      )),
      optional(seq(
        'e',
        optional('-'),
        /[0-9]+/,
      )),
      optional(field('alph', 'alph'))
    ),

    _number: $ => choice(
      $.hex_num,
      $.integer
    ),

    array_type: $ => seq(
      '[',
      $._type,
      ';',
      $._number,
      ']'
    ),

    _type: $ => choice(
      $.type_identifier,
      alias(choice(...primitiveTypes), $.primitive_type),
    ),

    typed_num: $ => seq(
      optional('-'),
      $._number,
      optional(choice('i', 'u')),
    ),

    bool: $ => choice('true', 'false'),

    bytes: $ => seq(
      '#',
      /['0-9a-zA-Z']*/
    ),

    address: $ => seq(
      '@',
      /['0-9a-zA-Z']*/
    ),

    _const_expr: $ => choice(
      $.typed_num,
      $.bool,
      $.bytes,
      $.address
    ),

    stringLiteral: $ => seq(
      'b`',
      /[^`]*/,
      '`'
    ),

    alph_token_id: $ => 'ALPH',

    enum_field_selector: $ => prec(PREC.field, seq(
      $.type_identifier,
      '.',
      $.type_identifier
    )),

    struct_constructor_field: $ => seq(
      seq($.identifier, ':', $._expr)
    ),

    struct_constructor_fields: $ => seq(
      '{',
      optional($.struct_constructor_field),
      repeat(seq(',', $.struct_constructor_field)),
      '}'
    ),
    struct_constructor: $ => seq(
      $.type_identifier,
      $.struct_constructor_fields,
    ),

    paren_expr: $ => seq(
      '(',
      $._expr,
      ')'
    ),

    array_expr: $ => choice(
      $._create_array1,
      $._create_array2
    ),

    _create_array1: $ => seq(
      '[',
      $._expr,
      repeat(seq(',', $._expr)),
      ']'
    ),

    _create_array2: $ => seq(
      '[',
      $._expr,
      ';',
      $._number,
      ']'
    ),

    ifBranchExpr: $ => prec.right(seq(
      'if',
      '(',
      $._expr,
      ')',
      $._expr
    )),

    else_if_branch_expr: $ => prec(2, seq(
      'else',
      $.ifBranchExpr
    )),

    else_branch_expr: $ => prec.right(seq(
      'else',
      $._expr
    )),

    if_else_expr: $ => prec.right(3, choice(
      seq(
        $.ifBranchExpr,
        repeat($.else_if_branch_expr),
        optional($.else_branch_expr)
      )
    )),

    _statement: $ => choice(
      $.let_declaration,
      $.assign,
      $.debug,
      //$.funcCall,
      $.call_expression,
      $.if_else_stmt,
      $.while_stmt,
      $.for_loop_stmt,
      $.return_stmt,
      $.emit_event
    ),

    named_var: $ => seq(
      optional($.mutable),
      $.identifier
    ),

    anonymous_var: $ => '_',

    var_declaration: $ => choice($.named_var, $.anonymous_var),

    _var_declarations: $ => choice(
      $.var_declaration,
      seq('(', sepBy1($.var_declaration, ','), ')')
    ),

    let_declaration: $ => seq(
      'let',
      $._var_declarations,
      '=',
      field('let_value', $._expr)
    ),

    block: $ => seq(
      '{',
      repeat($._statement),
      '}'
    ),

    assignment_target: $ => seq(
      $.identifier,
      repeat(choice(seq('.', $.identifier), $.index_selector))
    ),

    assign: $ => seq(
      sepBy1($.assignment_target, ','),
      '=',
      $._expr
    ),

    debug: $ => seq('emit', 'Debug', '(', '`', '${', $._expr, '}', '`', ')'),

    // funcCall: $ => prec(PREC.call,seq(
    //   optional(seq($.type_identifier, '.')),
    //   $._callAbs
    // )),

    contract_conv: $ => prec(PREC.call, seq(
      field('contract_type', $.type_identifier),
      '(',
      field('address', $._expr),
      ')'
    )),

    ident_selector: $ => seq(
      '.',
      $.identifier
    ),

    _data_selector: $ => choice(
      $.ident_selector,
      $.index_selector
    ),

    load_field_by_selectors: $ => prec(PREC.field, seq(
      choice($.identifier, $.type_identifier),
      repeat1($._data_selector)
    )),

    //TODO FIXME
    // Tests doesn't pass simple case: a.r
    // mess up with call Abs
    // structFieldSelector: $ => prec(PREC.call,seq(
    //   $._atom,
    //   '.',
    //     $.identifier
    // )),

    call_expression: $ => prec(PREC.call, choice(
      seq(
        choice($.call_expression, $.contract_conv, $.identifier),
        repeat1(seq('.', $._callAbs))
      ),
      seq(
        optional(seq($.type_identifier, '.')),
        $._callAbs,
      ))),

    _callAbs: $ => prec(PREC.call, seq(
      $.func_id,
      optional($.approve_assets),
      $.arguments
    )),

    arguments: $ => choice(
      seq('(', ')'),
      seq('(', sepBy1($._expr, ','), ')'),
    ),

    if_branch_stmt: $ => seq(
      'if',
      '(',
      $._expr,
      ')',
      $.block
    ),

    else_if_branch_stmt: $ => seq(
      'else',
      $.if_branch_stmt
    ),

    else_branch_stmt: $ => seq(
      'else',
      $.block
    ),

    if_else_stmt: $ => seq(
      $.if_branch_stmt,
      repeat($.else_if_branch_stmt),
      optional($.else_branch_stmt)
    ),

    while_stmt: $ => seq(
      'while',
      '(',
      $._expr,
      ')',
      $.block,
    ),

    for_loop_stmt: $ => seq('for', '(', optional($._statement), ';', $._expr, ';', optional($._statement), ')', $.block),

    return_stmt: $ => choice(
      seq('return', sepBy1($._expr, ',')),
      prec(-1, 'return'),
    ),

    emit_event: $ => seq(
      'emit',
      $.type_identifier,
      '(',
      sepBy($._expr, ','),
      ')'
    ),

    token_amount: $ => seq(
      $._expr, ':', $._expr
    ),

    amount_list: $ => sepBy1($.token_amount, ','),

    approve_asset_per_address: $ => seq(
      $._expr,
      '->',
      $.amount_list
    ),

    approve_assets: $ => seq(
      '{',
      sepBy1($.approve_asset_per_address, ';'),
      optional(';'),
      '}'
    ),

    index_selector: $ => seq(
      '[',
      $._expr,
      ']'
    ),

    _expr: $ => choice(
      $.unary_expr,
      $.binary_expr,
      $.array_element,
      $.load_field_by_selectors,
      $._atom,
    ),

    unary_expr: $ => prec(PREC.unary, seq(
      $.op_not,
      $._expr
    )),

    array_element: $ => prec(PREC.field, seq(
      $._atom,
      repeat1(
        $.index_selector
      )
    )),

    _atom: $ => choice(
      $.identifier,
      $.type_identifier,
      $._const_expr,
      $.stringLiteral,
      $.alph_token_id,
      $.call_expression,
      $.contract_conv,
      $.enum_field_selector,
      $.struct_constructor,
      $.paren_expr,
      $.array_expr,
      $.if_else_expr
    ),

    binary_expr: $ => {
      const table = [
        [PREC.additive, $.op_byte_vec_add],
        [PREC.additive, $.op_add],
        [PREC.additive, $.op_sub],
        [PREC.multiplicative, $.op_mul],
        [PREC.multiplicative, $.op_div],
        [PREC.multiplicative, $.op_exp],
        [PREC.multiplicative, $.op_mod_exp],
        [PREC.multiplicative, $.op_mod],
        [PREC.multiplicative, $.op_mod_add],
        [PREC.multiplicative, $.op_mod_sub],
        [PREC.multiplicative, $.op_mod_mul],
        [PREC.shift, $.op_shl],
        [PREC.shift, $.op_shr],
        [PREC.bitand, $.op_bit_and],
        [PREC.bitxor, $.op_xor],
        [PREC.bitor, $.op_bit_or],
        [PREC.comparative, $.op_eq],
        [PREC.comparative, $.op_ne],
        [PREC.comparative, $.op_lt],
        [PREC.comparative, $.op_le],
        [PREC.comparative, $.op_gt],
        [PREC.comparative, $.op_ge],
        [PREC.and, $.op_and],
        [PREC.or, $.op_or],
      ];

      return choice(...table.map(([precedence, operator]) => prec.left(precedence, seq(
        field('left', $._expr),
        field('operator', operator),
        field('right', $._expr),
      ))));
    },

    op_byte_vec_add: $ => '++',
    op_add: $ => '+',
    op_sub: $ => '-',
    op_mul: $ => '*',
    op_exp: $ => '**',
    op_mod_exp: $ => '|**|',
    op_div: $ => '/',
    op_mod: $ => '%',
    op_mod_add: $ => '⊕',
    op_mod_sub: $ => '⊖',
    op_mod_mul: $ => '⊗',
    op_shl: $ => '<<',
    op_shr: $ => '>>',
    op_bit_and: $ => '&',
    op_xor: $ => '^',
    op_bit_or: $ => '|',
    op_eq: $ => '==',
    op_ne: $ => '!=',
    op_lt: $ => '<',
    op_le: $ => '<=',
    op_gt: $ => '>',
    op_ge: $ => '>=',
    op_and: $ => '&&',
    op_or: $ => '||',
    op_not: $ => '!',
  }
});

function sepBy(elementRule, delimiter) {
  return seq(
    optional(elementRule),
    repeat(seq(delimiter, elementRule))
  );
}

function sepBy1(elementRule, delimiter) {
  return seq(
    elementRule,
    repeat(seq(delimiter, elementRule))
  );
}
