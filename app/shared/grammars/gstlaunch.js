module.exports = grammar({
    name: 'gstlaunch',

    extras: _ => [
        /\s|\\\r?\n/
    ],

    conflicts: $ => [
        [$.simple_element],
        [$.bin, $.simple_element, $.reference]
    ],

    // https://gstreamer.freedesktop.org/documentation/tools/gst-launch.html?gi-language=c#pipeline-description
    // https://github.com/GStreamer/gstreamer/blob/07b18a6de526dcf90b4bdff0422fef1670bf3e8c/subprojects/gstreamer/gst/parse/parse.l

    rules: {
        pipeline: $ => repeat($.fragment),

        fragment: $ => sep1($.element, "!"),
        element: $ => choice(
            $.caps,
            $.bin,
            $.simple_element,
            $.reference,
        ),

        string_literal: $ => choice(
            seq('"',
                repeat(choice(
                    alias(token.immediate(prec(1, /[^\\"\n]+/)), $.string_content),
                    //$.escape_sequence,
                )),
                '"'),
            seq("'",
                repeat(choice(
                    alias(token.immediate(prec(1, /[^\\"\n]+/)), $.string_content),
                    //$.escape_sequence,
                )),
                '"'),
        ),

        bin: $ => seq(field("type", $.identifier), ".", "(", repeat($.property), repeat($.fragment), ")"),

        simple_element: $ => seq(field("type", $.identifier), repeat($.property)),
        reference: $ => seq(optional(field("element", $.identifier)), ".", sep1(field("pad", $.identifier), ",")),
        property: $ => seq(field("key", $.identifier), "=", field("value", $.value)),

        // tree-sitter-c
        identifier: _ =>
            /(\p{XID_Start}|_|\\u[0-9A-Fa-f]{4}|\\U[0-9A-Fa-f]{8})(\p{XID_Continue}|\\u[0-9A-Fa-f]{4}|\\U[0-9A-Fa-f]{8}|[-])*/,
        value: $ => choice(token.immediate(/[^\s";!,]+/), $.string_literal),


        //MIMETYPE [, PROPERTY[, PROPERTY ...]]] [; CAPS[; CAPS ...]]
        caps: $ => sep1($.cap, ";"),
        cap: $ => seq($.identifier, "/", $.identifier, optional(seq(",", sep1($.property, ",")))),

        mimetype: _ => token.immediate(/[\w-]+\/[\w-]+/),
    }
});

function sep1(rule, sep) {
    return seq(rule, repeat(seq(sep, rule)));
}
