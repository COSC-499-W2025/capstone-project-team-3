module.exports = grammar({
  name: 'gemini',
  // control whitespace explicitly
  extras: $ => [],

  rules: {
    source_file: $ => repeat(seq(
      choice(
        $._space,
        $.text,
        $.link,
        seq(
          $.start_pre, 
          optional(repeat(seq($.pre, '\n'))), 
          $.end_pre,
        ),
        $.heading1,
        $.heading2,
        $.heading3,
        $.ulist,
        $.quote,
      ),
      '\n',
    )),

    /* 5.4 Core line types */

    /* 5.4.1 Text lines */
    _space: $ => repeat1(' '),
    _word: $ => /\S+/,
    text: $ => seq(optional($._space), repeat1(seq($._word, optional($._space)))),

    /* 5.4.2 Link lines */
    link: $ => seq(token(prec(1, '=>')), optional($._space), field('uri', alias($._word, $.uri)), optional(field('label', $.text))),

    /* 5.4.3 Preformatting toggle lines */
    start_pre: $ => seq(token(prec(1, '```')), field('alt', $.text), '\n'),
    end_pre: $ => '```',

    /* 5.4.4 Preformatted text lines */
    // defined separately for highlighting
    pre: $ => $.text,
    
    /* 5.5 Advanced line types */
    
    /* 5.5.1 Heading lines */
    heading1: $ => seq(token(prec(1, '#')), $.text),
    heading2: $ => seq(token(prec(1, '##')), $.text),
    heading3: $ => seq(token(prec(1, '###')), $.text),

    /* 5.5.2 Unordered list items */
    ulist: $ => seq(alias(token((prec(1, '* '))), $.indicator), $.text),

    /* 5.5.3 Quote lines */
    quote: $ => seq(alias(token(prec(1, '>')), $.indicator), $.text),
  }
});
