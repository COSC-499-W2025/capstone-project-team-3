/* Bison Grammar Parser

   Copyright (C) 2023 BTuin.

   This file is part of tree-sitter-bison, a Bison grammar for tree-sitter.

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU Lesser General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU Lesser General Public License for more details.

   You should have received a copy of the GNU Lesser General Public License
   along with this program.  If not, see <https://www.gnu.org/licenses/>.  */



const IDENTIFIER = /(\p{XID_Start}|_|\\u[0-9A-Fa-f]{4}|\\U[0-9A-Fa-f]{8})(\p{XID_Continue}|\\u[0-9A-Fa-f]{4}|\\U[0-9A-Fa-f]{8})*/
const RESULT = IDENTIFIER
const CHAR = /[^\n']/
const NONTERMINAL = IDENTIFIER
const TERMINAL = NONTERMINAL

module.exports = grammar({
	name: 'bison',
    extras: $ => [
        /\s/,
        $.comment,
    ],

	externals: $ => [
		// undelimited_code_block manages blocks of code that don't have delimiters. It
		// needs to have a minimal understanding of the syntax to correctly find the
		// closing bracket. It cannot be done here without reimplementing every supported
		// language (C, C++, D, Java), and even then I don't think it would actually work.
		// This is why it is implemented in the external scanner.
		$.undelimited_code_block,
		$.error_sentinel
	],

	rules: {
		sections : $ =>
			seq (
				repeat(
					choice(
						$.prologue,
						seq(
							$.declaration,
							optional(';')))),
				$.grammar_rules_section),

		prologue: $ =>
			seq (
				'%{',
				optional(alias($.prologue_body, $.embedded_code)),
				'%}'),

		prologue_body: $ =>
			repeat1(
				choice(
					token(/([^%\n"]|%[^{}\n]|"([^"\\]|\\.)+")+/))),


		grammar_rules_section: $ =>
			seq(
				'%%',
				$.grammar_rules_body,
				optional(
					seq('%%',
						$.epilogue))),

		grammar_rules_body: $ =>
			repeat1(
				choice(
					$.grammar_rule,
					seq($.declaration, ';'))),

		grammar_rule: $ =>
			seq(
				alias($.grammar_rule_identifier, $.grammar_rule_declaration),
				':',
				seq(
					optional(
						choice(
							seq(optional($.action),
								alias($.directive_empty, $.directive),
								optional($.action)),
							repeat1($._component))),
					repeat(
						seq(
							'|',
							choice(
								alias($.directive_empty, $.directive),
								repeat1($._component))))),
				';'),

		_component: $ =>
			choice(
				seq(
					choice(
						$.char_literal,
						$.string_literal,
						$.grammar_rule_identifier,
					),
					optional(seq('[', IDENTIFIER, ']'))),
				alias($.directive_merge, $.directive),
				$.action,
			),

		action: $ =>
			seq(
				$.code_block
			),

		declaration: $ =>
			choice(
				$._decl_type,
				$._decl_require,
				$._decl_token,
				$._decl_nterm,
				$._decl_op_precedence,
				$._decl_initial_declaration,
				$._decl_glr_parser,
				$._decl_destructor,
				$._decl_printer,
				$._decl_expect,
				$._decl_start,
				$._decl_define,
				$._decl_code,
				$._decl_union,
				$._decl_debug,
				$._decl_header,
				$.decl_language,
				$._decl_locations,
				$._decl_name_prefix,
				$._decl_no_lines,
				$._decl_no_lines,
				$._decl_output,
				$._decl_pure_parser,
				$._decl_skeleton,
				$._decl_token_table,
				$._decl_verbose,
				$._decl_yacc,
				$._decl_initial_action,
				$._decl_parse_param,
				$._decl_param,
				$._decl_lex_param),

		_decl_type: $ =>
			seq(declarationName($, 'type'),
				optional($.type_tag),
				repeat1(
					choice(
						$.grammar_rule_identifier,
						$.char_literal,
						$.string_literal)
				),
				repeat(
					seq($.type_tag,
						repeat1(
							choice(
								$.grammar_rule_identifier,
								$.char_literal,
								$.string_literal))))),

		_decl_require: $ =>
			seq(
				declarationName($, 'require'),
				$.string_literal),

		_decl_token: $ =>
			seq(
				declarationName($, 'token'),
				optional($.type_tag),
				repeat1(
					seq(
						$.grammar_rule_identifier,
						optional($.number_literal),
						optional($.string))),
				repeat(
					seq(
						$.type_tag,
						repeat1(
							seq(
								$.grammar_rule_identifier,
								optional($.number_literal),
								optional($.string_literal)))))),

		_decl_nterm: $ =>
			seq(
				declarationName($, 'nterm'),
				optional($.type_tag),
				repeat1($.grammar_rule_identifier),
				repeat(
					seq(
						$.type_tag,
						repeat($.grammar_rule_identifier)))),

		_decl_op_precedence: $ =>
			seq(
				declarationName($,
					choice(
						'left',
						'right',
						'nonassoc',
						'precedence'
					)),
				optional($.type_tag),
				repeat1(
					seq(
						choice(
							$.grammar_rule_identifier,
							$.string_literal,
							$.char_literal),
						optional($.number_literal))
				),
				repeat(
					seq(
						$.type_tag,
						repeat1(
							seq(
								choice(
									$.grammar_rule_identifier,
									$.string_literal,
									$.char_literal),
								optional($.number_literal)))))),

		_decl_initial_declaration: $ =>
			seq(
				declarationName($, 'initial-declaration'),
				$.code_block),

		_decl_glr_parser: $ =>
			declarationName($, 'glr-parser'),

		_decl_destructor: $ =>
			seq(
				declarationName($, 'destructor'),
				$.code_block,
				repeat(
					choice(
						$.type_tag,
						seq(
							'<',
							optional('*'),
							'>'),
						$.grammar_rule_identifier))),

		_decl_printer: $ =>
			seq(
				declarationName($, 'printer'),
				$.code_block,
				repeat(
					choice(
						$.type_tag,
						seq('<',
							optional('*'),
							'>'),
						$.grammar_rule_identifier))),

		_decl_expect: $ =>
			seq(
				declarationName($,
					choice(
						'expect',
						'expect-rr')),
				token(/[0-9]+/)),

		_decl_start: $ =>
			seq(declarationName($, 'start'),
				$.grammar_rule_identifier),

		_decl_define: $ =>
			seq(
				declarationName($, 'define'),
				seq(
					IDENTIFIER,
					repeat(
						seq(
							'.',
							IDENTIFIER))),
				optional(
					choice(
						IDENTIFIER,
						seq('{',
							choice(
								IDENTIFIER,
								$.string_literal),
							'}'),
						$.string_literal))),

		_decl_code: $ =>
			seq(declarationName($, 'code'),
				optional(
					seq(
						IDENTIFIER,
						repeat(seq('-', IDENTIFIER)))),
				$.code_block
			),

		_decl_union: $ =>
			seq(declarationName($, 'union'),
				optional(IDENTIFIER),
				$.code_block),

		_decl_debug: $ =>
			declarationName($, 'debug'),

		_decl_header: $ =>
			seq(
				declarationName($, 'header'),
				optional($.string_literal)),

		decl_language: $ =>
			seq(
				declarationName($, 'language'),
				field('language', $.string_literal)),

		_decl_locations: $ =>
			declarationName($, 'locations'),

		_decl_name_prefix: $ =>
			seq(
				declarationName($, 'name-prefix'),
				$.string_literal),

		_decl_no_lines: $ =>
			declarationName($, 'no-lines'),

		_decl_output: $ =>
			seq(
				declarationName($, 'output'),
				$.string_literal),

		_decl_pure_parser: $ =>
			declarationName($, 'pure-parser'),

		_decl_skeleton: $ =>
			seq(declarationName($, 'skeleton'),
				$.string_literal),

		_decl_token_table: $ =>
			declarationName($, 'token-table'),

		_decl_verbose: $ =>
			declarationName($, 'verbose'),

		_decl_yacc: $ =>
			declarationName($, 'yacc'),

		_decl_initial_action: $ =>
			seq(
				declarationName($, 'initial-action'),
				$.code_block),

		_decl_parse_param: $ =>
			seq(
				declarationName($, 'parse-param'),
				$.code_block),

		_decl_param: $ =>
			seq(
				declarationName($, 'param'),
				$.code_block),

		_decl_lex_param: $ =>
			seq(
				declarationName($, 'lex-param'),
				$.code_block),

		directive_merge: $ =>
			seq(
				'%merge',
				'<',
				$.type,
				'>'),

		directive_empty: $ =>
			token('%empty'),

		epilogue: $ =>
			alias($.undelimited_code_block, $.embedded_code),

		string: $ =>
			choice(
				$.string_literal,
				seq('_(',
					$.string_literal,
					')')),

		string_literal: $ => seq(
			choice('L"', 'u"', 'U"', 'u8"', '"'),
			repeat(choice(
				alias(token.immediate(prec(1, /[^\\"\n]+/)), $.string_content))),
			'"'),

		// number_literal: extracted from tree-sitter-c
		number_literal: _ => {
			const separator = '\'';
			const hex = /[0-9a-fA-F]/;
			const decimal = /[0-9]/;
			const hexDigits = seq(repeat1(hex), repeat(seq(separator, repeat1(hex))));
			const decimalDigits = seq(repeat1(decimal), repeat(seq(separator, repeat1(decimal))));
			return token(seq(
				optional(/[-\+]/),
				optional(choice(/0[xX]/, /0[bB]/)),
				choice(
					seq(
						choice(
							decimalDigits,
							seq(/0[bB]/, decimalDigits),
							seq(/0[xX]/, hexDigits),
						),
						optional(seq('.', optional(hexDigits))),
					),
					seq('.', decimalDigits),
				),
				optional(seq(
					/[eEpP]/,
					optional(seq(
						optional(/[-\+]/),
						hexDigits,
					)),
				)),
				/[uUlLwWfFbBdD]*/,
			));
		},

		type_tag: $ =>
			seq(
				'<',
				$.type,
				'>'),

		type: $ =>
			seq(
				$._type_atom,
				optional(
					seq('<',
						$.type,
						'>'))),

		_type_atom: $ =>
			seq(
				IDENTIFIER,
				repeat(
					seq(optional('::'),
						IDENTIFIER)),
				optional('*')),

		grammar_rule_identifier: $ =>
			seq(
				IDENTIFIER,
				token.immediate(
					optional(
						seq(token.immediate('.'),
							choice(
								token.immediate('opt'),
								// TODO: find the actual rule for suffixes
								token.immediate('1')))))),

		code_block: $ =>
			seq('{',
				alias($.undelimited_code_block, $.embedded_code),
				'}'),

		char_literal: $ =>
			seq(
				'\'',
				optional('\\'),
				CHAR,
				'\''),

		comment: $ =>
			choice(
				seq('//', /.*/),
				seq(
					'/*',
					/[^*]*\*+([^/*][^*]*\*+)*/,
					'/')),
	}
});

function declarationName($, rule) {
	return alias(seq('%', token.immediate(rule)), $.declaration_name);
}
