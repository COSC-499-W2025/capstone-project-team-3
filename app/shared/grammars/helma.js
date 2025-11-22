module.exports = grammar({
  name: 'helma',
  rules: {
    fragment: $ => repeat(choice(
      $.macro,
      $.text
    )),

    text: $ => prec.right(repeat1(/[^<]+|</)),

    macro: $ => seq(
      '<%',
      $.macro_name,
      repeat($.macro_parameter),
      '%>'
    ),

    macro_parameter: $ => seq(
      $.parameter_key,
      token.immediate('='),
      choice(
        $.macro,
        $.parameter_value,
        $._quoted_parameter_value,
      )
    ),

    _quoted_parameter_value: $ => choice(
      seq("'", optional(alias(/[^']+/, $.parameter_value)), "'"),
      seq('"', optional(alias(/[^"]+/, $.parameter_value)), '"'),
    ),

    macro_name: $ => /[^<>"'/=%\s]+/,

    parameter_key: $ => /[^<>"'/=%\s]+/,

    parameter_value: $ => /[^<>"'=%\s]+/,

  }
});