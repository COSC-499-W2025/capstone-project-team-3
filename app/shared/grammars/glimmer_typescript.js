"use strict";

const TypeScript = require("tree-sitter-typescript/typescript/grammar");

/**
 * A <template></template> block can exist in
 * two types of locations:
 * 1. class body
 * 2. any expression
 *
 * The contents of `<template>contents</template>`
 * are handled by tree-sitter-glimmer
 *   https://github.com/ember-tooling/tree-sitter-glimmer
 */
module.exports = grammar(TypeScript, {
  name: "glimmer_typescript",

  externals: ($, previous) => previous.concat([$.raw_text]),

  rules: {
    /**
     * TODO: add support for attributes
     *       e.g.:
     *
     *       <template trim-invisibles>
     *       <template signature:{SomeInterface}>
     *
     *       Either will require RFC
     *         https://github.com/emberjs/rfcs/
     */
    glimmer_template: ($) =>
      seq(
        field("open_tag", $.glimmer_opening_tag),
        optional($.raw_text),
        field("close_tag", $.glimmer_closing_tag),
      ),

    glimmer_opening_tag: ($) => seq("<", $.glimmer_template_tag_name, ">"),
    glimmer_closing_tag: ($) => seq("</", $.glimmer_template_tag_name, ">"),
    glimmer_template_tag_name: (_) => "template",

    /**
     * 2. Any Expression.
     * e.g.:
     *
     *   ```gts
     *   export const Foo = <template>...</template>
     *   ```
     *
     * TS: https://github.com/tree-sitter/tree-sitter-typescript/blob/master/common/define-grammar.js#L212
     * JS: https://github.com/tree-sitter/tree-sitter-javascript/blob/master/grammar.js#L479
     */
    expression: ($, previous) => {
      const choices = [
        $.glimmer_template,
        ...previous.members.filter((member) => member.name !== "_jsx_element"),
      ];

      return choice(...choices);
    },

    /**
     * This one can't be extended as nicely as Expression, because this node
     * contains a character sequence (seq)
     *
     * Most of thish is copied from upstream (TS), and only $.glimmer_template is added
     *
     * TS: https://github.com/tree-sitter/tree-sitter-typescript/blob/master/common/define-grammar.js#L419
     * JS: https://github.com/tree-sitter/tree-sitter-javascript/blob/master/grammar.js#L1150
     */
    class_body: ($) =>
      seq(
        "{",
        repeat(
          choice(
            seq(
              repeat(field("decorator", $.decorator)),
              $.method_definition,
              optional($._semicolon),
            ),
            seq(
              $.method_signature,
              choice($._function_signature_automatic_semicolon, ","),
            ),
            $.class_static_block,
            seq(
              choice(
                $.abstract_method_signature,
                $.index_signature,
                $.method_signature,
                $.public_field_definition,
              ),
              choice($._semicolon, ","),
            ),
            field("template", $.glimmer_template),
            ";",
          ),
        ),
        "}",
      ),
  },
});
