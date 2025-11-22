module.exports = grammar({
  name: "facility",

  rules: {
    source_file: ($) => $._definition,

    _definition: ($) =>
      seq(repeat(choice($.comment, $.doc_comment, $.attribute)), $.service),

    service_block: ($) => seq("{", repeat($._service_item), "}"),

    service: ($) =>
      seq(
        "service",
        field("service_name", $.identifier),
        choice($.service_block, seq(";", repeat($._service_item))),
        repeat($.remarks),
      ),

    _service_item: ($) =>
      choice(
        $.error_set,
        $.dto,
        $.enum,
        $.external_dto,
        $.external_enum,
        $.method,
        $.comment,
      ),

    values_block: ($) =>
      seq(
        "{",
        repeat(
          choice(
            $.comment,
            $.doc_comment,
            seq(repeat($.attribute), $.identifier, ","),
          ),
        ),
        "}",
      ),

    error_set: ($) =>
      seq(
        repeat($.attribute),
        "errors",
        field("name", $.identifier),
        $.values_block,
      ),

    dto: ($) =>
      seq(
        repeat($.attribute),
        "data",
        field("name", $.identifier),
        $.field_list,
      ),

    enum: ($) =>
      seq(
        repeat($.attribute),
        "enum",
        field("name", $.identifier),
        $.values_block,
      ),

    external_dto: ($) =>
      seq(
        repeat($.attribute),
        "extern",
        "data",
        field("name", $.identifier),
        ";",
      ),

    external_enum: ($) =>
      seq(
        repeat($.attribute),
        "extern",
        "enum",
        field("name", $.identifier),
        ";",
      ),

    method: ($) =>
      seq(
        repeat($.attribute),
        choice("method", "event"),
        field("name", $.identifier),
        $.field_list,
        ":",
        $.field_list,
      ),

    _attribute_property: ($) =>
      choice(
        "validate",
        "obsolete",
        "required",
        seq(
          choice(
            "validate",
            "obsolete",
            "http",
            "info",
            "csharp",
            "js",
            "proto",
          ),
          $._parameter_list,
        ),
      ),

    attribute: ($) =>
      seq(
        "[",
        $._attribute_property,
        repeat(seq(",", $._attribute_property)),
        "]",
      ),

    parameter: ($) =>
      seq(
        field("name", $.identifier),
        ":",
        choice(
          $.string_literal,
          $.number_literal,
          $.range,
          seq($.identifier, repeat(seq(".", $.identifier))),
        ),
      ),

    _parameter_list: ($) =>
      seq(
        "(",
        choice(
          optional($.parameter),
          seq($.parameter, repeat(seq(",", $.parameter))),
        ),
        ")",
      ),

    range: ($) => seq($.number_literal, "..", optional($.number_literal)),

    template_type: ($) =>
      seq(
        choice("map", "nullable", "result"),
        "<",
        choice($.template_type, $.list_type, $.required_type, $.type),
        ">",
      ),
    list_type: ($) => seq(choice($.type, $.template_type), "[]"),
    required_type: ($) => seq($.type, "!"),

    type: ($) =>
      seq(
        choice(
          "string",
          "datetime",
          "boolean",
          "double",
          "float",
          "int32",
          "int64",
          "decimal",
          "bytes",
          "object",
          "error",
          field("name", $.identifier),
        ),
      ),

    field_list: ($) =>
      seq("{", repeat(choice($.field, $.comment, $.doc_comment)), "}"),

    field: ($) =>
      seq(
        repeat($.attribute),
        field("name", $.identifier),
        ":",
        choice($.template_type, $.list_type, $.required_type, $.type),
        ";",
      ),

    doc_comment: ($) => seq("///", /.*/),
    comment: ($) => seq("//", /.*/),

    identifier: ($) => /[a-zA-Z_][a-zA-Z_0-9]*/,

    string_literal: ($) => /".*"/,

    number_literal: ($) => /[0-9]+/,

    remarks: ($) => seq("#", repeat(/.+/)),
  },
});
