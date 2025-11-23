/// <reference types="tree-sitter-cli/dsl" />

module.exports = grammar({
  name: "hlsplaylist",

  rules: {
    file: ($) => repeat(seq(choice($.uri, $.comment, $.tag), $._eol)),

    _eol: (_) => /\r?\n/,
    uri: (_) => /[^#\n][^\n]*/,
    comment: (_) => choice(/#EX[^T][^\n]*/, /#E[^X][^\n]*/, /#[^E][^\n]*/),

    tag: ($) =>
      seq(
        "#",
        alias(/EXT[^\n:]*/, $.tag_name),
        optional(
          seq(
            ":",
            choice(
              // #EXT-X-KEY:<attribute-list>
              $.attribute_list,
              // #EXT-X-TARGETDURATION:<s>
              $._value,
              // #EXT-X-PLAYLIST-TYPE:<type-enum>
              $.enum,
              // #EXT-X-PROGRAM-DATE-TIME:<date-time-msec>
              $.date_time_msec,
              // #EXT-X-BYTERANGE:<n>[@<o>]
              $.range,
              // #EXTINF:<duration>,[<title>]
              seq(
                choice($.dec, $.float),
                choice(/\s+/, optional(seq(/\s+/, $.attributes))),
                ",",
                $.title
              )
            )
          )
        )
      ),

    _dec: (_) => /\d+/,
    resolution: ($) => seq($._dec, "x", $._dec),
    float: ($) =>
      choice(seq("-", $._dec), seq(optional("-"), seq($._dec, ".", $._dec))),
    dec: ($) => $._dec,
    hex: (_) => seq("0X", /[\dA-F]+/),
    string: (_) => seq('"', field("content", repeat1(/[^"]|\\"/)), '"'),
    _value: ($) => choice($.dec, $.hex, $.resolution, $.float, $.string),

    attribute_list: ($) => seq(repeat(seq($.attribute, ",")), $.attribute),
    attribute: ($) =>
      seq(alias(/[A-Za-z][A-Za-z\d-]*/, $.attribute_name), "=", $._value),

    enum: (_) => choice("VOD", "EVENT"),
    date_time_msec: (_) => /\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z?/,
    range: ($) => seq($._dec, "@", $._dec),

    attributes: ($) => seq(repeat(seq($.attribute, /\s+/)), $.attribute),
    title: (_) => repeat1(/[^\n]/),
  },
});
