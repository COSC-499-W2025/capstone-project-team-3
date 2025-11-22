/**
 * @file CFEngine grammar for tree-sitter
 * @author Ole Herman Schumacher Elgesem <oleherman93@gmail.com>
 * @license MIT
 */

// Regexes defined here so we can concatenate them without creating rules in the grammar;
const IDENTIFIER = /[a-zA-Z0-9_]+/;
const QUALIFIED_IDENTIFIER = /([a-zA-Z0-9_]+\:)?([a-zA-Z0-9_]+\.)?[a-zA-Z0-9_]+/;
const PROMISE_GUARD = /[a-zA-Z_]+:/;
const CLASS_EXPRESSION = /[.|&!()a-zA-Z0-9_:][\t .|&!()a-zA-Z0-9_:]*/;
const SQUOTE = /\'((\\(.|\n))|[^'\\])*\'/;
const DQUOTE = /\"((\\(.|\n))|[^"\\])*\"/;
const BQUOTE = /`[^`]*`/;
const QUOTED_STRING = RegExp('(' + SQUOTE.source + ')|(' + DQUOTE.source + ')|(' + BQUOTE.source + ')');
const CLASS_GUARD = RegExp('((' + QUOTED_STRING.source + ')|(' + CLASS_EXPRESSION.source + '))::');

/// <reference types="tree-sitter-cli/dsl" />
// @ts-check

module.exports = grammar({
  name: "cfengine",

  extras: ($) => [$.comment, $.macro, /[\s]+/],
  word: ($) => $.identifier,

  rules: {
    source_file: ($) => repeat($._block),

    _block: ($) => choice($.bundle_block, $.body_block, $.promise_block),

    body_block: ($) =>
      seq(
        $.body_block_keyword,
        alias($.identifier, $.body_block_type),
        alias($.identifier, $.body_block_name),
        optional($.parameter_list),
        $.body_block_body,
      ),
    body_block_keyword: (_) => "body",
    body_block_body: ($) =>
      seq(
        "{",
        // 0 or more promises without a class guard:
        repeat($._body_attribute),
        // 0 or more class guards with 0 or more promises inside:
        repeat($.class_guarded_body_attributes),
        "}",
      ),

    _body_attribute: ($) => seq($.attribute, ";"),

    promise_block: ($) =>
      seq(
        $.promise_block_keyword,
        alias($.identifier, $.promise_block_type),
        alias($.identifier, $.promise_block_name),
        $.promise_block_body,
      ),
    promise_block_keyword: (_) => "promise",
    promise_block_body: ($) =>
      seq(
        "{",
        // 0 or more promises without a class guard:
        repeat($._body_attribute),
        // 0 or more class guards with 0 or more promises inside:
        repeat(
          alias(
            $.class_guarded_body_attributes,
            $.class_guarded_promise_block_attributes,
          ),
        ),
        "}",
      ),

    class_guarded_body_attributes: ($) =>
      seq($.class_guard, repeat($._body_attribute)),

    bundle_block: ($) =>
      seq(
        $.bundle_block_keyword,
        alias($.identifier, $.bundle_block_type),
        alias($.identifier, $.bundle_block_name),
        optional($.parameter_list),
        $.bundle_block_body,
      ),
    bundle_block_keyword: (_) => "bundle",

    parameter_list: ($) =>
      seq(
        "(",
        optional(
          seq(
            repeat(seq(alias($.identifier, $.parameter), ",")),
            alias($.identifier, $.parameter),
            optional(","),
          ),
        ),
        ")",
      ),

    bundle_block_body: ($) => seq("{", repeat($.bundle_section), "}"),

    bundle_section: ($) =>
      seq(
        $.promise_guard,
        // 0 or more promises without a class guard:
        optional($._promises),
        // 0 or more class guards with 0 or more promises inside:
        repeat($.class_guarded_promises),
      ),

    _right_value: ($) =>
      choice(
        $.quoted_string,
        $.qualified_identifier,
        $.list,
        $.call,
        $.dollar_expression,
        $.at_expression,
      ),

    dollar_expression: ($) =>
      seq(
        alias("$", $.dollar_expression_operator),
        alias("(", $.dollar_expression_start),
        choice(
          alias($.qualified_identifier, $.dollar_expression_identifier),
          $.dollar_expression,
        ),
        alias(")", $.dollar_expression_end),
      ),
    at_expression: ($) =>
      seq(
        alias("@", $.at_expression_operator),
        alias("(", $.at_expression_start),
        alias($.qualified_identifier, $.at_expression_identifier),
        alias(")", $.at_expression_end),
      ),

    calling_identifier: ($) => choice(
      $.qualified_identifier,
      $.dollar_expression, // TODO: This is only allowed for bundles / methods calls
                           //       NOT for function or body calls
    ),
    call: ($) =>
      seq(
        $.calling_identifier,
        "(",
        optional($._value_list),
        ")",
      ),

    list: ($) => seq("{", optional($._value_list), "}"),

    // inner part of a non-empty list of values
    // such as the arguments of a function call
    // or the strings in an slist
    _value_list: ($) =>
      seq($._right_value, repeat(seq(",", $._right_value)), optional(",")),

    class_guarded_promises: ($) =>
      seq($.class_guard, optional($._promises)),

    _promises: ($) => seq($.promise, repeat(choice($.promise, $.half_promise))),

    promise: ($) =>
      seq(
        alias($.quoted_string, $.promiser),
        optional(seq("->", alias($._right_value, $.stakeholder))),
        optional($.attribute),
        repeat(seq(",", $.attribute)),
        optional(","),
        ";",
      ),

    // "Half promises" are not real, and shouldn't normally be allowed
    // in policy. However they can arise from using macros.
    // So this is sort of a hack to make the parser work better
    // when faced with macros.
    // TODO: resarch if there are better ways to handle macros
    half_promise: ($) =>
      seq($.attribute, repeat(seq(",", $.attribute)), optional(","), ";"),

    attribute: ($) =>
      seq(alias($.identifier, $.attribute_name), "=>", $._right_value),

    quoted_string: ($) => QUOTED_STRING,
    identifier: ($) => IDENTIFIER,
    qualified_identifier: ($) => QUALIFIED_IDENTIFIER,
    promise_guard: ($) => PROMISE_GUARD,
    class_guard: ($) => CLASS_GUARD,

    comment: ($) => token(seq("#", /.*/)),

    macro: ($) => token(/@(if |else|endif)[^\n]*/),
  },
});
