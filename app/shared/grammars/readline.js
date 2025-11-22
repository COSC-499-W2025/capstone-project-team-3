const NEWLINE = /\r?\n/;
const WHITE_SPACE = /[ \t\f\v]/;
const ANYTHING = /[^\r\n]+/;
const ANYTHING_STARTING_NON_WHITESPACE = /\S[^\r\n]*/;
const ERROR_ALIAS = ($) =>
  alias(token(prec(-1, ANYTHING_STARTING_NON_WHITESPACE)), $.ERROR);

module.exports = grammar({
  name: 'readline',

  // Control whitespace explicitly
  extras: (_) => [],

  rules: {
    source: ($) => repeat($._statement),

    _statement: ($) =>
      choice(
        seq(repeat(WHITE_SPACE), $.conditional_construct, NEWLINE),
        seq(repeat(WHITE_SPACE), $.include_directive, NEWLINE),
        seq(repeat(WHITE_SPACE), $.comment, NEWLINE),
        seq(
          repeat(WHITE_SPACE),
          $.variable_setting,
          repeat(WHITE_SPACE),
          NEWLINE,
        ),
        seq(repeat(WHITE_SPACE), $.key_binding, repeat(WHITE_SPACE), NEWLINE),
        seq(repeat(WHITE_SPACE), NEWLINE),
      ),

    comment: (_) => seq(/#/, optional(ANYTHING)),

    conditional_construct: ($) =>
      seq(
        alias(/\$if/i, '$if'),
        $.test,
        NEWLINE,
        alias(repeat($._statement), $.consequence),
        optional(seq(
          repeat(WHITE_SPACE),
          alias(/\$else/i, '$else'),
          repeat(WHITE_SPACE),
          NEWLINE,
          alias(repeat($._statement), $.alternative),
        )),
        $._endif,
      ),

    _endif: (_) =>
      seq(
        repeat(WHITE_SPACE),
        alias(/\$endif/i, '$endif'),
        repeat(WHITE_SPACE),
      ),

    test: ($) =>
      seq(
        repeat1(WHITE_SPACE),
        choice(
          $._mode_test,
          $._term_test,
          $._version_test,
          $._application_test,
          $._variable_test,
        ),
        repeat(WHITE_SPACE),
      ),

    _mode_test: ($) =>
      seq(
        alias(/mode/i, 'mode'),
        '=',
        $.edit_mode_value,
      ),

    _term_test: ($) =>
      seq(
        alias(/term/i, 'term'),
        '=',
        alias(/\S+/, $.term_name),
      ),

    _version_test: ($) =>
      seq(
        alias(/version/i, 'version'),
        repeat1(WHITE_SPACE),
        choice('=', '==', '>=', '<=', '!=', '>', '<'),
        repeat1(WHITE_SPACE),
        alias(/\d+\.?\d*/, $.version_number),
      ),

    _application_test: ($) => alias(token(prec(-1, /\S+/)), $.application_name),

    _variable_test: ($) =>
      seq(
        choice(
          seq(
            $.bool_variable,
            repeat1(WHITE_SPACE),
            choice('=', '==', '!='),
            repeat(WHITE_SPACE),
            $.bool_value,
          ),
          seq(
            $.bell_variable,
            repeat1(WHITE_SPACE),
            choice('=', '==', '!='),
            repeat(WHITE_SPACE),
            $.bell_value,
          ),
          seq(
            $.string_variable,
            repeat1(WHITE_SPACE),
            choice('=', '==', '!='),
            repeat(WHITE_SPACE),
            $.string_value,
          ),
          seq(
            $.number_variable,
            repeat1(WHITE_SPACE),
            choice('=', '==', '!='),
            repeat(WHITE_SPACE),
            $.number_value,
          ),
          seq(
            $.edit_mode_variable,
            repeat1(WHITE_SPACE),
            choice('=', '==', '!='),
            repeat(WHITE_SPACE),
            $.edit_mode_value,
          ),
          seq(
            $.keymap_variable,
            repeat1(WHITE_SPACE),
            choice('=', '==', '!='),
            repeat(WHITE_SPACE),
            $.keymap_value,
          ),
        ),
      ),

    include_directive: ($) =>
      seq(
        alias(/\$include/i, '$include'),
        choice(
          repeat(WHITE_SPACE),
          seq(
            repeat1(WHITE_SPACE),
            alias(ANYTHING_STARTING_NON_WHITESPACE, $.file_path),
          ),
        ),
      ),

    variable_setting: ($) =>
      seq(
        alias(/set/i, 'set'),
        repeat1(WHITE_SPACE),
        choice(
          $._bool_assignment,
          $._bell_assignment,
          $._string_assignment,
          $._number_assignment,
          $._edit_mode_assignment,
          $._keymap_assignment,
        ),
      ),

    _bool_assignment: ($) =>
      prec.right(
        seq(
          $.bool_variable,
          choice(repeat(WHITE_SPACE), seq(repeat1(WHITE_SPACE), $.bool_value)),
        ),
      ),
    _bell_assignment: ($) =>
      prec.right(
        seq(
          $.bell_variable,
          choice(repeat(WHITE_SPACE), seq(repeat1(WHITE_SPACE), $.bell_value)),
        ),
      ),
    _string_assignment: ($) =>
      prec.right(
        seq(
          $.string_variable,
          choice(
            repeat(WHITE_SPACE),
            seq(repeat1(WHITE_SPACE), $.string_value),
          ),
        ),
      ),
    _number_assignment: ($) =>
      prec.right(
        seq(
          $.number_variable,
          choice(
            repeat(WHITE_SPACE),
            seq(repeat1(WHITE_SPACE), $.number_value),
          ),
        ),
      ),
    _edit_mode_assignment: ($) =>
      prec.right(
        seq(
          $.edit_mode_variable,
          choice(
            repeat(WHITE_SPACE),
            seq(repeat1(WHITE_SPACE), $.edit_mode_value),
          ),
        ),
      ),
    _keymap_assignment: ($) =>
      prec.right(
        seq(
          $.keymap_variable,
          choice(
            repeat(WHITE_SPACE),
            seq(repeat1(WHITE_SPACE), $.keymap_value),
          ),
        ),
      ),

    bool_value: ($) => choice('1', /on/i, /off/i, ERROR_ALIAS($)),
    bell_value: ($) => choice(/none/i, /visible/i, /audible/i, ERROR_ALIAS($)),
    string_value: (_) => ANYTHING_STARTING_NON_WHITESPACE,
    number_value: ($) => choice(/[-+]?\d+/, ERROR_ALIAS($)),
    edit_mode_value: ($) => choice(/emacs/i, /vi/i, ERROR_ALIAS($)),
    keymap_value: ($) =>
      choice(
        /(emacs(-standard|-meta|-ctlx)?|vi(-move|-command|-insert)?)/i,
        ERROR_ALIAS($),
      ),

    bool_variable: (_) =>
      choice(
        /bind-tty-special-chars/i,
        /blink-matching-paren/i,
        /colored-completion-prefix/i,
        /colored-stats/i,
        /completion-ignore-case/i,
        /completion-map-case/i,
        /convert-meta/i,
        /disable-completion/i,
        /echo-control-characters/i,
        /enable-active-region/i,
        /enable-bracketed-paste/i,
        /enable-keypad/i,
        /enable-meta-key/i,
        /expand-tilde/i,
        /history-preserve-point/i,
        /horizontal-scroll-mode/i,
        /input-meta/i,
        /mark-directories/i,
        /mark-modified-lines/i,
        /mark-symlinked-directories/i,
        /match-hidden-files/i,
        /menu-complete-display-prefix/i,
        /meta-flag/i,
        /output-meta/i,
        /page-completions/i,
        /print-completions-horizontally/i,
        /revert-all-at-newline/i,
        /show-all-if-ambiguous/i,
        /show-all-if-unmodified/i,
        /show-mode-in-prompt/i,
        /skip-completed-text/i,
        /visible-stats/i,
      ),
    bell_variable: (_) => /bell\-style/i,
    string_variable: (_) =>
      choice(
        /active-region-end-color/i,
        /active-region-start-color/i,
        /comment-begin/i,
        /emacs-mode-string/i,
        /isearch-terminators/i,
        /vi-cmd-mode-string/i,
        /vi-ins-mode-string/i,
      ),
    number_variable: (_) =>
      choice(
        /completion-display-width/i,
        /completion-prefix-display-length/i,
        /completion-query-items/i,
        /history-size/i,
        /keyseq-timeout/i,
      ),
    edit_mode_variable: (_) => /editing\-mode/i,
    keymap_variable: (_) => /keymap/i,

    key_binding: ($) =>
      seq(
        choice($.keyname, $.keyseq),
        ':',
        repeat(WHITE_SPACE),
        choice($.function_name, $.macro),
      ),

    // users can define custom function names
    function_name: (_) => /[a-zA-Z\-]+/,

    keyseq: ($) => $._double_quoted_string,

    macro: ($) => $._quoted_string,

    _double_quoted_string: ($) =>
      seq('"', repeat1(choice(/[^"\\]/, $.escape_sequence)), '"'),

    _quoted_string: ($) =>
      seq(/["']/, repeat1(choice(/[^"'\\]/, $.escape_sequence)), /["']/),

    escape_sequence: (_) =>
      /\\([abdefnrtv'"\\]|x[0-9a-fA-F]{1,2}|[0-7]{1,3}|[CM]-)/,

    keyname: ($) =>
      seq(
        repeat(seq($.symbolic_character_name, '-')),
        choice($.symbolic_character_name, $.key_literal),
      ),

    symbolic_character_name: (_) =>
      choice(
        /Control/i,
        /Meta/i,
        /Del/i,
        /Esc/i,
        /Escape/i,
        /LFD/i,
        /Newline/i,
        /Ret/i,
        /Return/i,
        /Rubout/i,
        /Space/i,
        /Spc/i,
      ),

    key_literal: (_) => /\S/,
  },
});
