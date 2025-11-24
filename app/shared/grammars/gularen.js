module.exports = grammar({
  name: 'gularen',

  extras: _ => ['\r'],

  rules: {
    document: $ => prec.right(repeat(choice(
      $.section,
      $.subsection,
      $.subsubsection,
      $._common_block,
    ))),

    _common_block: $ => prec.right(choice(
      $.code_block,
      $.bullet_list,
      $.numbered_list,
      $.check_list,
      $.metadata,
      $.func,
      $.admon,
      $.paragraph,
      '\n'
    )),

    section: $ => prec.right(seq(
      $.section_title,
      repeat(choice(
        $.subsection,
        $.subsubsection,
        $._common_block
      ))
    )),

    subsection: $ => prec.right(seq(
      $.subsection_title,
      repeat(choice(
        $.subsubsection,
        $._common_block
      ))
    )),

    subsubsection: $ => prec.right(seq(
      $.subsubsection_title,
      repeat(choice(
        $._common_block
      ))
    )),

    section_title: $ => prec.right(seq('>>> ', repeat1($._inline), optional('\n'))),
    subsection_title: $ => prec.right(seq('>> ', repeat1($._inline), optional('\n'))),
    subsubsection_title: $ => prec.right(seq('> ', repeat1($._inline), optional('\n'))),


    code_block: $ => choice($._code_block5, $._code_block4, $._code_block3),

    _code_block5: $ => seq(alias($.fence5, $.fence), optional(seq(choice(' !', ' '), optional($.path), $.language)), '\n', optional($.source), alias($.fence5, $.fence)),
    _code_block4: $ => seq(alias($.fence4, $.fence), optional(seq(choice(' !', ' '), optional($.path), $.language)), '\n', optional($.source), alias($.fence4, $.fence)),
    _code_block3: $ => seq(alias($.fence3, $.fence), optional(seq(choice(' !', ' '), optional($.path), $.language)), '\n', optional($.source), alias($.fence3, $.fence)),

    bullet_list: $ => prec.right(seq($.bullet, ' ', repeat1($._inline), optional('\n'))),
    numbered_list: $ => prec.right(seq($.index, ' ', repeat1($._inline), optional('\n'))),
    check_list: $ => prec.right(seq('[', choice($.x, ' '), '] ', repeat1($._inline), optional('\n'))),

    bar: _ => choice(/-{3,}/, /:-{1,}:/, /:-{2,}/, /-{2,}:/),
    pipe: _ => '|',

    admon: $ => prec.right(seq($.admon_label, choice(seq(' ', repeat1($._inline), optional('\n')), '\n'))),
    admon_label: _ => seq(choice('NOTE', 'HINT', 'IMPORTANT', 'WARNING', 'SEE', 'TIP'), '!'),

    metadata: $ => prec.right(seq('% ', $.id, ': ', $.string)),

    func: $ => prec.right(seq('% ', $.id, choice(
      optional('\n'),
      seq(' ', $.string),
      seq(' ', $.hashtable),
    ))),
    id: _ => /[a-z-]+/,
    string: _ => choice(seq('"', /[^"]+/, '"'), /[^\n]+/),
    hashtable: $ => seq('{\n', repeat1(seq(/\s+/, $.id, ': ', $.string, '\n')), '}\n'),

    bullet: _ => '-',
    index: _ => /[0-9]+\./,
    x: _ => 'x',

    fence5: _ => '`````',
    fence4: _ => '````',
    fence3: _ => '```',
    source: _ => repeat1(seq(/[^\n]*/, '\n')),
    path: _ => /[A-Za-z0-9-_\/ ]+\./,
    language: _ => /[a-z0-9-]+/,

    paragraph: $ => prec.right(seq(repeat1($._paragraph_line), optional('\n'))),
    _paragraph_line: $ => seq(repeat1($._inline), '\n'),

    _inline: $ => choice(
      $.escape,
      $.code_inline,
      $.strong_emphasis,
      $.resource,
      $.emphasis,
      $.comment,
      $.break,
      $._text
    ),

    code_inline: $ => seq($.backtick, $.source_inline, $.backtick),
    backtick: _ => '`',

    source_inline: _ => /[^`]+/,

    strong_emphasis: $ => prec.left(seq('*', $._inline, '*')),
    emphasis: $ => prec.left(seq('_', $._inline, '_')),
    resource: $ => seq('[', $.resource_link, ']', optional(seq('(', $.resource_label, ')'))),
    resource_link: _ => /[^\]]+/,
    resource_label: _ => /[^\)]+/,

    comment: _ => seq('# ', /[^\n]*/),
    break: _ => '<',
    escape: _ => /\\./,
    _text: _ => choice(/[a-zA-Z0-9\.,-]+/, /[^\n]/),
  },
});

