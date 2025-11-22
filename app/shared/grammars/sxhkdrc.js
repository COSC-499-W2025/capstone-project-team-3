// official grammar referrence
// https://github.com/baskerville/sxhkd/blob/master/doc/sxhkd.1.asciidoc#configuration

let regex_keysym = /[A-Za-z0-9_]+/
let regext_range_digit = /[A-Za-z0-9]/

module.exports = grammar({
  name: 'sxhkdrc',

  extras: $ => [
    $.comment,
    /\s/,
  ],

  rules: {
    source_file: $ => repeat($._definition),

    _definition: $ => choice(
      $.binding,
    ),

    binding: $ => seq(
      $.hotkey,
      '\n',
      /\s+/,
      optional($.command_sync_prefix),
      $.command,
      '\n'
    ),

    hotkey: $ => seq(
      repeat(seq(
        $._hotkey,
        '\\\n'
      )),
      $._hotkey,
    ),
    _hotkey: $ => repeat1(choice(
      $.modifier,
      $.operator,
      $.punctuation,
      $.attribute,
      $.delimiter,
      $.keysym,
      $.range,
    )),

    modifier: _ => choice(
      'super',
      'hyper',
      'meta',
      'alt',
      'control',
      'ctrl',
      'shift',
      'mode_switch',
      'lock',
      'mod1',
      'mod2',
      'mod3',
      'mod4',
      'mod5',
      'any',
    ),
    operator: _ => '+',
    attribute: _ => choice('@', '~'),
    punctuation: _ => choice('{', ',', '}'),
    delimiter: _ => choice(';', ':'),
    command_sync_prefix: _ => ';',
    keysym: _ => regex_keysym,
    range: _ => token(seq(regext_range_digit, '-', regext_range_digit)),
    comment: _ => token(prec(-10, /#.*/)),

    command: _ => seq(
      repeat(/[^;].*\\\n\s+/),
      /[^;].*/,
    ),
  }
});
