/// <reference types="tree-sitter-cli/dsl" />
// @ts-check

module.exports = grammar({
  name: 'llvm_mir',

  conflicts: $ => [
    [$.basic_block],
    [$.cfi_operand],
  ],

  extras: $ => [
    /[ \t]+/,
    $.comment,
    $.multiline_comment,
  ],

  rules: {
    // Optionally consume the starting character of the yaml string
    body: $ => seq(optional(/\|>/), repeat(choice($.basic_block, $._newline))),

    basic_block: $ => seq(
      $.label,
      optional(seq('(', commaSep($.attribute), ')')),
      ':',
      repeat(seq(
        optional(choice($.successors, $.liveins)),
        $._newline,
      )),
      repeat(seq(
        optional(seq(
          $.instruction,
          optional($.bundle),
        )),
        $._newline,
      )),
    ),

    _newline: $ => /\r?\n/,

    comment: $ => /;[^\n\r]*/,
    multiline_comment: $ => /\/\*([^*]|\*+[^/*])*\*+\//,

    identifier: $ => /[-a-zA-Z._][-a-zA-Z$._0-9]*/,
    mnemonic: $ => /\.[-a-zA-Z$._0-9]*/,
    label: $ => $.identifier,
    bb_ref: $ => /%bb.[-a-zA-Z$._0-9]+/,
    stack_object: $ => token(prec(1, /%(fixed-)?stack.[-a-zA-Z$._0-9]+/)),
    constant_pool_index: $ => /%const\.[-a-zA-Z$._0-9]*/,
    jump_table_index: $ => /%jump-table\.[-a-zA-Z$._0-9]*/,
    string: $ => /"[^"]*"/,
    number: $ => /-?\d+|0x[\da-fA-F]+/,
    float: $ => choice($.number, /[+-]?\d+\.\d*([Ee][+-]?\d+)?/, /[su]?0x[KMLHR]?[0-9a-fA-F]+/),
    var: $ => /%[-a-zA-Z$._0-9]+/,
    physical_register: $ => /\$[-a-zA-Z$_0-9]+/,
    immediate_type: $ => token(prec(1, /[isp]\d+/)),

    register: $ => choice($.var, $.physical_register),

    ir_block: $ => token(seq('%ir-block.', token.immediate(choice(
      /[-a-zA-Z$._][-a-zA-Z$._0-9]*/,
      /\d+/,
      /"[^"]*"/,
    )))),

    external_symbol: $ => token(seq('&', token.immediate(choice(
      /[-a-zA-Z$._][-a-zA-Z$._0-9]*/,
      /\d+/,
      /"[^"]*"/,
    )))),

    global_var: $ => token(seq('@', token.immediate(choice(
      /[-a-zA-Z$._][-a-zA-Z$._0-9]*/,
      /\d+/,
      /"[^"]*"/,
    )))),

    ir_local_var: $ => token(seq(/%(ir\.)?/, token.immediate(choice(
      /[-a-zA-Z$._][-a-zA-Z$._0-9]*/,
      /\d+/,
      /"[^"]*"/,
    )))),

    metadata_ref: $ => token(seq('!', token.immediate(choice(
      /[-a-zA-Z$._\\][-a-zA-Z$._0-9\\]*/,
      /\d+/,
      /"[^"]*"/,
    )))),

    bundle: $ => seq(
      '{',
      repeat(seq(
        optional($.instruction),
        $._newline,
      )),
      '}',
    ),

    successors: $ => seq(
      'successors',
      ':',
      commaSep(seq(
        $.bb_ref,
        optional(seq('(', $.number, ')')),
      )),
    ),

    liveins: $ => seq(
      'liveins',
      ':',
      commaSep(seq(
        $.register,
        optional(seq(
          ':',
          $.number,
        )),
      )),
    ),

    instruction: $ => seq(
      optional(seq(commaSep1($.register_operand), '=')),
      repeat($.instruction_flag),
      field('name', $.identifier),
      commaSep(choice(
        $.argument,
        seq('dbg-instr-ref', $.md_value),
      )),
      repeat(seq(
        optional(','),
        choice(
          seq('pre-instr-symbol', $.mc_symbol),
          seq('post-instr-symbol', $.mc_symbol),
          seq('heap-alloc-marker', $.metadata),
          seq('pcsections', $.metadata),
          seq('mmra', $.metadata),
          seq('cfi-type', $.number),
          seq('debug-instr-number', $.number),
          seq('debug-location', $.metadata),
        ),
      )),
      optional(','),
      // memory operands
      optional(seq('::', commaSep($.memory_operand))),
    ),

    mc_symbol: $ => seq(
      '<',
      'mcsymbol',
      choice($.string, $.identifier),
      '>',
    ),

    metadata: $ => seq(
      $.metadata_ref,
      // Can be named md or specialized md
      optional(seq(
        token.immediate('('),
        repeat($.md_value),
        ')',
      )),
    ),

    md_value: $ => choice(
      seq('!', $.string),
      $.metadata,
      'null',
      /[-a-zA-Z0-9_.$\\]+/,
      '|',
      ':',
      ',',
      '*',
      seq('{', repeat($.md_value), '}'),
      seq('(', repeat($.md_value), ')'),
      seq('[', repeat($.md_value), ']'),
      seq('<', repeat($.md_value), '>'),
    ),

    register_operand: $ => seq(
      repeat($.register_flag),
      choice(
        seq(
          $.var,
          optional(seq(':', $.registerclass)),
        ),
        seq(
          $.physical_register,
          optional(seq('.', $.subregister)),
        ),
        '_',
      ),
      optional(seq(
        '(',
        choice(
          seq('tied-def', $.number),
          $.low_level_type,
        ),
        ')',
      )),
    ),

    argument: $ => seq(
      optional(seq('target-flags', '(', commaSep1($.identifier), ')')),
      $.machine_operand,
    ),

    machine_operand: $ => seq(choice(
        $.register_operand,
        $.number,
        seq(
          $.float_keyword,
          $.float,
        ),
        $.bb_ref,
        $.stack_object,
        $.global_var,
        $.constant_pool_index,
        $.jump_table_index,
        $.external_symbol,
        $.mc_symbol,
        $.metadata,
        $.cfi_operand,
        $.block_address,
        $.intrinsic,
        $.target_index,
        $.liveout,
        $.predicate,
        $.shuffle_mask,
        $.mnemonic,
        $.custom_regmask,
        $.immediate,
        // regmask
        $.identifier,
      ),
      optional($.offset),
    ),

    subregister: $ => $.identifier,
    registerclass: $ => choice('_', $.identifier),

    primitive_type: $ => /[sp]\d*/, // scalar or pointer
    low_level_type: $ => choice(
      $.primitive_type,
      seq('<', optional(seq('vscale', 'x')), $.number, 'x', $.primitive_type, '>'),
    ),

    custom_regmask: $ => seq('CustomRegMask', '(', commaSep($.register), ')'),

    cfi_operand: $ => choice(
      seq(choice('same_value', 'def_cfa_register', 'restore', 'undefined'), $.register),
      seq(choice('offset', 'rel_offset', 'def_cfa'), $.register, ',', $.number),
      seq(choice('def_cfa_offset', 'adjust_cfa_offset'), $.number),
      seq('llvm_def_aspace_cfa', $.register, ',', $.number, ',', $.number),
      seq('register', $.register, ',', $.register),
      seq('escape', commaSep1($.number)),
      'remember_state',
      'restore_state',
      'window_save',
      'negate_ra_sign_state',
    ),

    immediate: $ => seq($.immediate_type, choice($.number, 'true', 'false')),

    predicate: $ => choice(
      seq('intpred', '(', $.intpred, ')'),
      seq('floatpred', '(', $.floatpred, ')'),
    ),

    intpred: $ => choice('eq', 'ne', 'sgt', 'sge', 'slt', 'sle', 'ugt', 'uge', 'ult', 'ule'),
    floatpred: $ => choice('false', 'oeq', 'ogt', 'oge', 'olt', 'ole', 'one', 'ord', 'uno', 'ueq', 'ugt',
          'uge', 'ult', 'ule', 'une', 'true'),

    shuffle_mask: $ => seq('shufflemask', '(', commaSep1(choice('undef', $.number)), ')'),
    liveout: $ => seq('liveout', '(', commaSep($.register), ')'),
    target_index: $ => seq('target-index', '(', $.identifier, ')'),
    block_address: $ => seq('blockaddress', '(', $.global_var, ',', $.ir_block, ')'),
    intrinsic: $ => seq('intrinsic', '(', $.global_var, ')'),

    memory_operand: $ => seq(
      '(',
      repeat($.memory_operand_flag),
      choice('load', 'store'),
      optional('store'), // for load+store
      optional($.sync_scope),
      optional($.atomic_ordering),
      optional($.atomic_ordering), // failure order
      choice(
        $.number,
        'unknown-size',
        seq('(', $.low_level_type, ')'),
      ),
      optional(seq(
        choice('on', 'from', 'into'),
        $.machine_pointer_info,
        optional($.offset),
      )),
      repeat(seq(
        ',',
        $.mem_attribute,
      )),
      ')',
    ),

    mem_attribute: $ => choice(
      seq(choice('align', 'basealign', 'addrspace'), $.number),
      seq($.metadata_ref, $.metadata),
    ),

    machine_pointer_info: $ => choice(
      $.memory_pseudo_source_value,
      $.ir_value,
    ),

    ir_value: $ => choice(
      'unknown-address',
      $.global_var,
      $.ir_local_var,
      $.escaped_ir_value,
    ),

    escaped_ir_value: $ => seq(
      '`',
      repeat($._escaped_ir_content),
      '`',
    ),

    _escaped_ir_content: $ => choice(
      $.global_var,
      $.ir_local_var,
      $.number,
      $.identifier,
      $.immediate_type,
      '*',
      ',',
      seq('{', repeat($._escaped_ir_content), '}'),
      seq('(', repeat($._escaped_ir_content), ')'),
      seq('[', repeat($._escaped_ir_content), ']'),
      seq('<', repeat($._escaped_ir_content), '>'),
    ),

    offset: $ => seq(
      choice('+', '-'),
      $.number,
    ),

    memory_pseudo_source_value: $ => choice(
      $.memory_pseudo_source_value_keyword,
      $.stack_object,
      seq('call-entry', choice($.global_var, $.external_symbol)),
      seq('custom', $.string),
    ),

    memory_pseudo_source_value_keyword: $ => choice(
      'constant-pool',
      'stack',
      'got',
      'jump-table',
    ),

    memory_operand_flag: $ => choice(
      'volatile',
      'non-temporal',
      'dereferenceable',
      'invariant',
      $.string,
    ),

    sync_scope: $ => seq(
      'syncscope',
      '(',
      $.string,
      ')',
    ),

    atomic_ordering: $ => choice(
      'unordered',
      'monotonic',
      'acquire',
      'release',
      'acq_rel',
      'seq_cst',
    ),

    register_flag: $ => choice(
      'implicit',
      'implicit-def',
      'def',
      'dead',
      'killed',
      'undef',
      'internal',
      'early-clobber',
      'debug-use',
      'renamable',
    ),

    instruction_flag: $ => choice(
      'frame-setup',
      'frame-destroy',
      'nnan',
      'ninf',
      'nsz',
      'arcp',
      'contract',
      'afn',
      'reassoc',
      'nuw',
      'nsw',
      'exact',
      'nofpexcept',
      'nomerge',
      "unpredictable",
      "noconvergent",
      'nneg',
      'disjoint',
      "nusw",
    ),

    attribute: $ => choice(
      'machine-block-address-taken',
      'landing-pad',
      'inlineasm-br-indirect-target',
      'ehfunclet-entry',
      seq('ir-block-address-taken', $.ir_block),
      seq(choice('align', 'call-frame-size'), $.number),
      seq('bb_id', $.number, optional($.number)),
      seq('bbsections', choice('Exception', 'Cold', $.number)),
      $.ir_block,
    ),

    float_keyword: $ => choice(
      'half',
      'bfloat',
      'float',
      'double',
      'x86_fp80',
      'fp128',
      'ppc_fp128',
    ),
  },
});

function commaSep(rule) {
  return optional(commaSep1(rule));
}

function commaSep1(rule) {
  return seq(rule, repeat(seq(',', rule)));
}
