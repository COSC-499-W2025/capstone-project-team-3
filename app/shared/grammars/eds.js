module.exports = grammar({
  name: "eds",
  rules: {
    source_file: ($) => repeat(choice($.section, $.comment)),
    section: ($) => seq("[", $.section_name, "]", repeat($.statement)),
    section_name: ($) => /[^\r\n\[\]]+/,

    key: ($) => /[^\r\n\[\]=]+/,
    value: ($) => /[^\r\n\[\]]+/,
    statement: ($) => seq($.key, "=", $.value),

    comment: ($) => /;.*/,
  },
});
