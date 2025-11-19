const WHITESPACE_CHAR =
      /[\f\n\r\t, ]/;

const WHITESPACE =
      token(repeat1(WHITESPACE_CHAR));

const COMMENT =
      token(/;.*\n?/);

const DIGIT =
      /[0-9]/;

const DOUBLE =
      seq(repeat1(DIGIT),
          optional(seq(".",
                       repeat(DIGIT))),
          optional(seq(/[eE]/,
                       optional(/[+-]/),
                       repeat1(DIGIT))));

const INTEGER =
      seq(repeat1(DIGIT));

// XXX: what counts as a number appears to be a bit underspecified
const NUMBER =
      token(prec(10, seq(optional(/[+-]/),
                choice(DOUBLE,
                       INTEGER))));

const NIL =
      token('nil');

const BOOLEAN =
      token(choice('false',
                   'true'));

const STRING =
      token(seq('"',
                repeat(/[^"\\]/),
                repeat(seq("\\",
                           /./,
                           repeat(/[^"\\]/))),
                '"'));

const NAME_CHAR =
      /[^ \f\n\r\t,\[\]{}()'`~^@";]/;

const KEYWORD =
      token(seq(":",
                repeat(NAME_CHAR)));

const SYMBOL =
      token(repeat1(NAME_CHAR));

module.exports = grammar({
  name: 'mal',

  extras: $ =>
    [],

  conflicts: $ =>
    [],

  rules: {
    // THIS MUST BE FIRST -- even though this doesn't look like it matters
    source: $ =>
      repeat(choice($._form,
                    $._gap)),

    _gap: $ =>
      choice($._ws,
             $.comment),

    _ws: $ =>
      WHITESPACE,

    comment: $ =>
      COMMENT,

    _form: $ =>
      choice(// atom-ish
             $.num_lit,
             $.kwd_lit,
             $.str_lit,
             $.nil_lit,
             $.bool_lit,
             $.sym_lit,
             // basic collection-ish
             $.list_lit,
             $.map_lit,
             $.vec_lit,
             // reader macros
             $.derefing_lit,
             $.quoting_lit,
             $.syn_quoting_lit,
             $.unquote_splicing_lit,
             $.unquoting_lit),

    num_lit: $ =>
      NUMBER,

    kwd_lit: $ =>
      KEYWORD,

    str_lit: $ =>
      STRING,

    nil_lit: $ =>
      NIL,

    bool_lit: $ =>
      BOOLEAN,

    sym_lit: $ =>
      seq(repeat($._metadata_lit),
          SYMBOL),

    _metadata_lit: $ =>
      seq(field('meta', $.meta_lit),
          optional(repeat($._gap))),

    meta_lit: $ =>
      seq(field('marker', "^"),
          field('value', choice($.num_lit,
                                $.kwd_lit,
                                $.str_lit,
                                $.nil_lit,
                                $.bool_lit,
                                $.sym_lit,
                                $.list_lit,
                                $.map_lit,
                                $.vec_lit))),

    list_lit: $ =>
      seq(repeat($._metadata_lit),
          field('open', "("),
          repeat(choice(field('value', $._form),
                        $._gap)),
          field('close', ")")),

    map_lit: $ =>
      seq(repeat($._metadata_lit),
          field('open', "{"),
          repeat(choice(field('value', $._form),
                        $._gap)),
          field('close', "}")),

    vec_lit: $ =>
      seq(repeat($._metadata_lit),
          field('open', "["),
          repeat(choice(field('value', $._form),
                        $._gap)),
          field('close', "]")),

    derefing_lit: $ =>
      seq(repeat($._metadata_lit),
          field('marker', "@"),
          field('value', $._form)),

    quoting_lit: $ =>
      seq(repeat($._metadata_lit),
          field('marker', "'"),
          field('value', $._form)),

    syn_quoting_lit: $ =>
      seq(repeat($._metadata_lit),
          field('marker', "`"),
          field('value', $._form)),

    unquote_splicing_lit: $ =>
      seq(repeat($._metadata_lit),
          field('marker', "~@"),
          field('value', $._form)),

    unquoting_lit: $ =>
      seq(repeat($._metadata_lit),
          field('marker', "~"),
          field('value', $._form)),
  }
});
