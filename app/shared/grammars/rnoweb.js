const sepBy1 = (rule, sep) => seq(rule, repeat(seq(sep, rule)));

module.exports = grammar({
    name: 'rnoweb',

    externals: $ => [
        $._latex_word,
        $.command_name,
        $._renv_sig_beg,
        $._renv_sig_end,
        $.renv_content,
    ],

    rules: {
        source_file: $ =>
            repeat(
                choice(
                    $.latex,
                    $.rchunk,
                    $.rinline,
                )
            ),

        rchunk: $ =>
            seq(
                $._renv_sig_beg,
                optional($.renv_sig_options),
                $._renv_sig_end,
                optional($.renv_content),
                '@'
            ),

        rinline: $ =>
            seq(
                field("Sexpr", $.command_name),
                "{",
                optional(alias(/[^}]+/, $.renv_content)),
                '}',
            ),

        renv_sig_options: $ =>
            choice(
                field("options", $._renv_options),
                seq(
                    field("label", alias($.renv_key, $.renv_label)),
                    optional(seq(",", field("options", $._renv_options)))
                ),
            ),

        _renv_options: $ =>
            sepBy1(choice(
                $.renv_key_pair,
                prec(2, $._renv_engine)
            ), ","),

        _renv_engine: $ =>
            seq(
                "engine",
                "=",
                alias($.renv_engine_val, $.renv_engine)
            ),

        renv_engine_val: $ =>
            choice(
                seq(
                    "\"",
                    field("engine", $.renv_engine_key),
                    "\""
                ),
                seq(
                    "'",
                    field("engine", $.renv_engine_key),
                    "'"
                )
            ),

        renv_key_pair: $ =>
            seq(
                field("key", $.renv_key),
                /=[ ]*/,
                field("value", $.renv_val)
            ),

        renv_engine_key: $ =>
            /[a-zA-Z]+[a-zA-Z0-9]*/,

        renv_key: $ =>
            /[a-zA-Z_]+[a-zA-Z0-9_.]*/,

        renv_val: $ =>
            /[^,>]+/,

        latex: $ =>
            prec.right(repeat1(
                $._latex_word,
            )),
    },
});
