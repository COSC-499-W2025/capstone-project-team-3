module.exports = grammar({
    name: 'nois',

    precedences: $ => [
        [$.variantList, $._statement],
        [$.methodCallOp, $.fieldAccessOp]
    ],
    conflicts: $ => [[$.identifier, $._patternExpr]],
    extras: $ => [/\s/, $.COMMENT],
    word: $ => $.NAME,
    rules: {
        // module                ::= use-stmt* statement*
        module: $ => seq(repeat($.useStatement), repeat($._statement)),
        // statement             ::= var-def | fn-def | trait-def | impl-def | type-def | return-stmt | break-stmt | expr
        _statement: $ => choice($.varDef, $.fnDef, $.traitDef, $.implDef, $.typeDef, $.returnStmt, $.breakStmt, $.expr),
        //   use-stmt            ::= PUB-KEYWORD? USE-KEYWORD use-expr
        useStatement: $ => seq(optional($.PUB_KEYWORD), $.USE_KEYWORD, $.useExpr),
        //     use-expr          ::= (NAME COLON COLON)* (use-list | NAME)
        useExpr: $ => seq(repeat(seq($.NAME, $.COLON, $.COLON)), choice($.useList, $.NAME)),
        //     use-list          ::= O-BRACE (use-expr (COMMA use-expr)*)? COMMA? C-BRACE
        useList: $ =>
            seq($.O_BRACE, optional(seq($.useExpr, repeat(seq($.COMMA, $.useExpr)))), optional($.COMMA), $.C_BRACE),
        //   var-def             ::= PUB-KEYWORD? LET-KEYWORD pattern type-annot? EQUALS expr
        varDef: $ => seq(optional($.PUB_KEYWORD), $.LET_KEYWORD, $.pattern, optional($.typeAnnot), $.EQUALS, $.expr),
        //   fn-def              ::= FN-KEYWORD NAME generics? params type-annot? block?
        fnDef: $ =>
            seq(
                optional($.PUB_KEYWORD),
                $.FN_KEYWORD,
                $.NAME,
                optional($.generics),
                $.params,
                optional($.typeAnnot),
                optional($.block)
            ),
        //     generics          ::= O-ANGLE (generic (COMMA generic)* COMMA?)? C-ANGLE
        generics: $ =>
            seq($.O_ANGLE, optional(seq($.generic, repeat(seq($.COMMA, $.generic)), optional($.COMMA))), $.C_ANGLE),
        //       generic         ::= NAME (COLON type-bounds)?
        generic: $ => seq($.NAME, optional(seq($.COLON, $.typeBounds))),
        //     params            ::= O-PAREN (param (COMMA param)*)? COMMA? C-PAREN
        params: $ =>
            seq($.O_PAREN, optional(seq($.param, repeat(seq($.COMMA, $.param)))), optional($.COMMA), $.C_PAREN),
        //       param           ::= pattern type-annot?
        param: $ => seq($.pattern, optional($.typeAnnot)),
        //   trait-def           ::= PUB-KEYWORD? TRAIT-KEYWORD NAME generics? block
        traitDef: $ => seq(optional($.PUB_KEYWORD), $.TRAIT_KEYWORD, $.NAME, optional($.generics), $.block),
        //   impl-def            ::= IMPL-KEYWORD generics? identifier impl-for? block
        implDef: $ => seq($.IMPL_KEYWORD, optional($.generics), $.identifier, optional($.implFor), $.block),
        //     impl-for          ::= FOR-KEYWORD identifier
        implFor: $ => seq($.FOR_KEYWORD, $.identifier),
        //   type-def            ::= PUB-KEYWORD? TYPE-KEYWORD NAME generics? (variant-list | variant-params)?
        typeDef: $ =>
            prec.right(
                seq(
                    optional($.PUB_KEYWORD),
                    $.TYPE_KEYWORD,
                    $.NAME,
                    optional($.generics),
                    optional(choice($.variantList, $.variantParams))
                )
            ),
        //     variant-params    ::= O-PAREN (field-def (COMMA field-def)*)? COMMA? C-PAREN
        variantParams: $ => seq($.O_PAREN, optional(seq($.fieldDef, repeat(seq($.COMMA, $.fieldDef)))), $.C_PAREN),
        //       field-def       ::= PUB-KEYWORD? NAME type-annot
        fieldDef: $ => seq(optional($.PUB_KEYWORD), $.NAME, $.typeAnnot),
        //     variant-list      ::= O-BRACE (variant (COMMA variant)* COMMA?)? C-BRACE
        variantList: $ =>
            seq($.O_BRACE, optional(seq($.variant, repeat(seq($.COMMA, $.variant)), optional($.COMMA))), $.C_BRACE),
        //       variant         ::= NAME variant-params?
        variant: $ => seq($.NAME, optional($.variantParams)),
        //   return-stmt         ::= RETURN-KEYWORD expr
        returnStmt: $ => seq($.RETURN_KEYWORD, $.expr),
        //   break-stmt          ::= BREAK-KEYWORD
        breakStmt: $ => seq($.BREAK_KEYWORD),
        //   expr                ::= sub-expr (infix-op sub-expr)*
        expr: $ => prec.right(seq($.subExpr, repeat(seq($._infixOp, $.subExpr)))),
        //     sub-expr          ::= operand postfix-op*
        subExpr: $ => prec.right(seq($._operand, repeat($._postfixOp))),
        //       operand         ::= if-expr
        //                       | if-let-expr
        //                       | while-expr
        //                       | for-expr
        //                       | match-expr
        //                       | closure-expr
        //                       | O-PAREN expr C-PAREN
        //                       | list-expr
        //                       | string
        //                       | CHAR
        //                       | number
        //                       | bool
        //                       | identifier
        _operand: $ =>
            choice(
                $.ifExpr,
                $.ifLetExpr,
                $.whileExpr,
                $.forExpr,
                $.matchExpr,
                $.closureExpr,
                seq($.O_PAREN, $.expr, $.C_PAREN),
                $.listExpr,
                $.string,
                $.CHAR,
                $.number,
                $.bool,
                $.identifier
            ),
        //     infix-op          ::= add-op | sub-op | mult-op | div-op | exp-op | mod-op | access-op | eq-op | ne-op
        //                       | ge-op | le-op | gt-op | lt-op | and-op | or-op | assign-op;
        _infixOp: $ =>
            choice(
                $.addOp,
                $.subOp,
                $.multOp,
                $.divOp,
                $.expOp,
                $.modOp,
                $.eqOp,
                $.neOp,
                $.geOp,
                $.leOp,
                $.gtOp,
                $.ltOp,
                $.andOp,
                $.orOp,
                $.assignOp
            ),
        //       add-op          ::= PLUS;
        addOp: $ => $.PLUS,
        //       sub-op          ::= MINUS;
        subOp: $ => $.MINUS,
        //       mult-op         ::= ASTERISK;
        multOp: $ => $.ASTERISK,
        //       div-op          ::= SLASH;
        divOp: $ => $.SLASH,
        //       exp-op          ::= CARET;
        expOp: $ => $.CARET,
        //       mod-op          ::= PERCENT;
        modOp: $ => $.PERCENT,
        //       eq-op           ::= EQUALS EQUALS;
        eqOp: $ => seq($.EQUALS, $.EQUALS),
        //       ne-op           ::= EXCL EQUALS;
        neOp: $ => seq($.EXCL, $.EQUALS),
        //       ge-op           ::= C-ANGLE EQUALS;
        geOp: $ => seq($.C_ANGLE, $.EQUALS),
        //       le-op           ::= O-ANGLE EQUALS;
        leOp: $ => seq($.O_ANGLE, $.EQUALS),
        //       gt-op           ::= C-ANGLE;
        gtOp: $ => $.C_ANGLE,
        //       lt-op           ::= O-ANGLE;
        ltOp: $ => $.O_ANGLE,
        //       and-op          ::= AMPERSAND AMPERSAND;
        andOp: $ => seq($.AMPERSAND, $.AMPERSAND),
        //       or-op           ::= PIPE PIPE;
        orOp: $ => seq($.PIPE, $.PIPE),
        //       assign-op       ::= EQUALS;
        assignOp: $ => $.EQUALS,
        //     postfix-op        ::= method-call-op | field-access-op | call-op | unwrap-op | bind-op | await-op
        _postfixOp: $ => choice($.methodCallOp, $.fieldAccessOp, $.callOp, $.unwrapOp, $.bindOp, $.awaitOp),
        //       method-call-op  ::= PERIOD NAME type-args? call-op
        methodCallOp: $ => seq($.PERIOD, $.NAME, optional($.typeArgs), $.callOp),
        //       field-access-op ::= PERIOD NAME
        fieldAccessOp: $ => seq($.PERIOD, $.NAME),
        //       call-op         ::= O-PAREN (arg (COMMA arg)*)? COMMA? C-PAREN
        callOp: $ => seq($.O_PAREN, optional(seq($.arg, repeat(seq($.COMMA, $.arg)))), optional($.COMMA), $.C_PAREN),
        //         arg           ::= (NAME COLON)? expr
        arg: $ => seq(optional(seq($.NAME, $.COLON)), $.expr),
        //       unwrap-op       ::= EXCL
        unwrapOp: $ => seq($.EXCL),
        //       bind-op         ::= QMARK
        bindOp: $ => seq($.QMARK),
        //       await-op        ::= PERIOD AWAIT-KEYWORD
        awaitOp: $ => seq($.PERIOD, $.AWAIT_KEYWORD),
        // identifier            ::= (NAME COLON COLON)* NAME type-args?
        identifier: $ => prec.left(seq(repeat(seq($.NAME, $.COLON, $.COLON)), $.NAME, optional($.typeArgs))),
        //   type-args           ::= O-ANGLE (type (COMMA type)* COMMA?)? C-ANGLE
        typeArgs: $ =>
            seq($.O_ANGLE, optional(seq($.type, repeat(seq($.COMMA, $.type)), optional($.COMMA))), $.C_ANGLE),
        // type                  ::= type-bounds | fn-type | hole
        type: $ => choice($.typeBounds, $.fnType, $.hole),
        //   type-bounds         ::= identifier (PLUS identifier)*
        typeBounds: $ => seq($.identifier, repeat(seq($.PLUS, $.identifier))),
        //   fn-type             ::= generics? fn-type-params type-annot
        fnType: $ => seq(optional($.generics), $.fnTypeParams, $.typeAnnot),
        //     fn-type-params    ::= PIPE (type (COMMA type)* COMMA?)? PIPE
        fnTypeParams: $ => seq($.PIPE, optional(seq($.type, repeat(seq($.COMMA, $.type)))), optional($.COMMA), $.PIPE),
        // block                 ::= O-BRACE statement* C-BRACE
        block: $ => seq($.O_BRACE, repeat($._statement), $.C_BRACE),
        // closure-expr          ::= closure-params type-annot? block
        closureExpr: $ => seq($.closureParams, optional($.typeAnnot), $.block),
        //   closure-params      ::= PIPE (param (COMMA param)*)? COMMA? PIPE
        closureParams: $ =>
            seq($.PIPE, optional(seq($.param, repeat(seq($.COMMA, $.param)))), optional($.COMMA), $.PIPE),
        // list-expr             ::= O-BRACKET (expr (COMMA expr)*)? COMMA? C-BRACKET
        listExpr: $ =>
            seq($.O_BRACKET, optional(seq($.expr, repeat(seq($.COMMA, $.expr)))), optional($.COMMA), $.C_BRACKET),
        // type-annot            ::= COLON type
        typeAnnot: $ => seq($.COLON, $.type),
        // if-expr               ::= IF-KEYWORD expr block (ELSE-KEYWORD block)?
        ifExpr: $ => seq($.IF_KEYWORD, $.expr, $.block, optional(seq($.ELSE_KEYWORD, $.block))),
        // if-let-expr           ::= IF-KEYWORD LET-KEYWORD pattern EQUALS expr block (ELSE-KEYWORD block)?
        ifLetExpr: $ =>
            seq(
                $.IF_KEYWORD,
                $.LET_KEYWORD,
                $.pattern,
                $.EQUALS,
                $.expr,
                $.block,
                optional(seq($.ELSE_KEYWORD, $.block))
            ),
        // while-expr            ::= WHILE-KEYWORD expr block
        whileExpr: $ => seq($.WHILE_KEYWORD, $.expr, $.block),
        // for-expr              ::= FOR-KEYWORD pattern IN-KEYWORD expr block
        forExpr: $ => seq($.FOR_KEYWORD, $.pattern, $.IN_KEYWORD, $.expr, $.block),
        // match-expr            ::= MATCH-KEYWORD expr match-clauses
        matchExpr: $ => seq($.MATCH_KEYWORD, $.expr, $.matchClauses),
        //   match-clauses       ::= O-BRACE match-clause* C-BRACE
        matchClauses: $ => seq($.O_BRACE, repeat($.matchClause), $.C_BRACE),
        //     match-clause      ::= patterns guard? block
        matchClause: $ => seq($.patterns, optional($.guard), $.block),
        //       patterns        ::= pattern (PIPE pattern)*
        patterns: $ => seq($.pattern, repeat(seq($.PIPE, $.pattern))),
        //       guard           ::= IF-KEYWORD expr
        guard: $ => seq($.IF_KEYWORD, $.expr),
        // pattern               ::= pattern-bind? pattern-expr
        pattern: $ => seq(optional($.patternBind), $._patternExpr),
        //   pattern-bind        ::= NAME AT
        patternBind: $ => seq($.NAME, $.AT),
        //   pattern-expr        ::= NAME | con-pattern | string | CHAR | number | bool | hole
        _patternExpr: $ => choice($.NAME, $.conPattern, $.string, $.CHAR, $.number, $.bool, $.hole),
        //     con-pattern       ::= identifier con-pattern-params
        conPattern: $ => seq($.identifier, $.conPatternParams),
        //     con-pattern-params ::= O-PAREN (field-pattern (COMMA field-pattern)*)? COMMA? C-PAREN
        conPatternParams: $ =>
            seq(
                $.O_PAREN,
                optional(seq($.fieldPattern, repeat(seq($.COMMA, $.fieldPattern)))),
                optional($.COMMA),
                $.C_PAREN
            ),
        //       field-pattern   ::= NAME (COLON pattern)?
        fieldPattern: $ => seq($.NAME, optional(seq($.COLON, $.pattern))),
        //     list-pattern      ::= O-BRACKET (pattern (COMMA pattern)*)? COMMA? C-BRACKET
        listPattern: $ =>
            seq($.O_BRACKET, optional(seq($.pattern, repeat(seq($.COMMA, $.pattern)))), optional($.COMMA), $.C_BRACKET),
        //     hole              ::= UNDERSCORE
        hole: $ => $.UNDERSCORE,
        // number                ::= MINUS? (INT | FLOAT)
        number: $ => seq(optional($.MINUS), choice($.INT, $.FLOAT)),
        // string                ::= D-QUOTE string-part* D-QUOTE
        string: $ => seq($.D_QUOTE, repeat($.stringPart), $.D_QUOTE),
        // string-part           ::= STRING | O-BRACE expr C-BRACE
        stringPart: $ => choice($.STRING, seq($.O_BRACE, $.expr, $.C_BRACE)),
        // bool                  ::= TRUE | FALSE
        bool: $ => choice($.TRUE, $.FALSE),

        USE_KEYWORD: _ => 'use',
        TYPE_KEYWORD: _ => 'type',
        TRAIT_KEYWORD: _ => 'trait',
        IF_KEYWORD: _ => 'if',
        ELSE_KEYWORD: _ => 'else',
        RETURN_KEYWORD: _ => 'return',
        BREAK_KEYWORD: _ => 'break',
        IMPL_KEYWORD: _ => 'impl',
        LET_KEYWORD: _ => 'let',
        FN_KEYWORD: _ => 'fn',
        WHILE_KEYWORD: _ => 'while',
        FOR_KEYWORD: _ => 'for',
        IN_KEYWORD: _ => 'in',
        MATCH_KEYWORD: _ => 'match',
        PUB_KEYWORD: _ => 'pub',
        AWAIT_KEYWORD: _ => 'await',

        O_PAREN: _ => '(',
        C_PAREN: _ => ')',
        O_BRACKET: _ => '[',
        C_BRACKET: _ => ']',
        O_BRACE: _ => '{',
        C_BRACE: _ => '}',
        O_ANGLE: _ => '<',
        C_ANGLE: _ => '>',
        PLUS: _ => '+',
        MINUS: _ => '-',
        ASTERISK: _ => '*',
        SLASH: _ => '/',
        CARET: _ => '^',
        PERCENT: _ => '%',
        AMPERSAND: _ => '&',
        PIPE: _ => '|',
        EXCL: _ => '!',
        QMARK: _ => '?',
        PERIOD: _ => '.',
        COLON: _ => ':',
        COMMA: _ => ',',
        EQUALS: _ => '=',
        UNDERSCORE: _ => '_',
        AT: _ => '@',
        D_QUOTE: _ => '"',

        NAME: _ => /[a-zA-Z]([a-zA-Z]|\d)*/,
        STRING: $ => prec.right(repeat1(choice(/(\\\\")/, /[^\\\n\r']/, $._ESCAPE_SEQUENCE))),
        CHAR: $ => seq("'", choice(/(\\\\')/, /[^\\\n\r"]/, $._ESCAPE_SEQUENCE), "'"),
        _ESCAPE_SEQUENCE: _ => choice(/(\\[btnvfr\\'"])/, /u[0-9a-fA-F]{4}/),
        INT: _ => /\d+/,
        FLOAT: _ => /((\d+(\.\d*)?e[+-]?\d+)|(\d+\.\d*)|(\d*\.\d+))/,
        TRUE: _ => 'true',
        FALSE: _ => 'false',

        COMMENT: _ => token(seq('//', /.*/))
    }
})
