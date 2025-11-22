// Reference : https://github.com/kwanghoon/sbparser
// Our SmallBasic Parser works well for samples sb files in the directory.

module.exports = grammar({
    name: "smallbasic",

    // Processing blank characters or annotation-related symbols
    // \s : Processing blank characters(Space/Tab/CR/NewLine/VerticalTab)
    // \p{Zs} : Unicode blank character processing
    // \uFEFF : Show Byte Order
    // \u2028 : Line Separator
    // \u2029 : Paragraph Separator
    // \u2060 : Word Joiner
    extras: $ => [
      $.Comment,
      /[\s\t\p{Zs}\uFEFF\u2028\u2029\u2060\u200B]/
    ],
  
    rules: {
      // Non-Terminal Symbols
      Start: $ => repeat($.Prog),

      Prog: $ => $.MoreThanOneStmt, // Considerations : Directly Prog -> Stmt

      MoreThanOneStmt: $ => $.Stmt,

      // /[Ss][Tt][Ee][Pp]/ means that the spelling in brackets is case-insensitive.
      // STEP == step
      OptStep: $ => seq(/[Ss][Tt][Ee][Pp]/, $.Expr),

      Stmt: $ => choice(
        $.ExprStatement,
        seq(/[Ww][Hh][Ii][Ll][Ee]/, $.Expr, repeat($.CRStmtCRs), /[Ee][Nn][Dd][Ww][Hh][Ii][Ll][Ee]/),
        seq($.ID, ":"),
        seq(/[Gg][Oo][Tt][Oo]/, $.ID),
        seq(/[Ff][Oo][Rr]/, $.ID, "=", $.Expr, /[Tt][Oo]/, $.Expr, optional($.OptStep), repeat($.CRStmtCRs), /[Ee][Nn][Dd][Ff][Oo][Rr]/),
        seq(/[Ss][Uu][Bb]/, $.ID, $.CRStmtCRs, /[Ee][Nn][Dd][Ss][Uu][Bb]/),
        seq(/[Ii][Ff]/, $.Expr, /[Tt][Hh][Ee][Nn]/, repeat($.CRStmtCRs), $.MoreThanZeroElseIf)
      ),
      
      MoreThanZeroElseIf: $ => choice(
        $.OptionalElse,
        seq(/[Ee][Ll][Ss][Ee][Ii][Ff]/, $.Expr, /[Tt][Hh][Ee][Nn]/, repeat($.CRStmtCRs), $.MoreThanZeroElseIf)
      ),

      OptionalElse: $ => choice(
        // ignoreCase("EndIf") type : string => regExp 
        // Below Consideration : When expressed in a form that can be seen in AST
        // $.EndIf ... EndIf : _ => /[Ee][Nn][Dd][Ii][Ff]/ 
        /[Ee][Nn][Dd][Ii][Ff]/,
        seq(/[Ee][Ll][Ss][Ee]/, $.CRStmtCRs, /[Ee][Nn][Dd][Ii][Ff]/)
      ),

      ExprStatement: $ => choice(
        seq($.ID, "=", $.Expr),
        seq($.ID, ".", $.ID, "=", $.Expr),
        seq($.ID, ".", $.ID, "(", optional($.Exprs), ")"), // ID.ID() case without parameters -> optional func use
        seq($.ID, "(", ")"),
        seq($.ID, $.Idxs, "=", $.Expr)
      ),

      CRStmtCRs: $ => seq($.CR, repeat($.TheRest)),

      TheRest: $ => seq($.Stmt, $.CR),
      
      // choice(seq(), seq($.Expr, ",", $.MoreThanOneExpr)) - (X)
      // The rule `Exprs` matches the empty string. -> Not allowed by tree-sitter
      // Therefore, it should be written as below.
      Exprs: $ => $.MoreThanOneExpr,

      MoreThanOneExpr: $ => choice(
        $.Expr,
        seq($.Expr, ",", $.MoreThanOneExpr)
      ),

      Expr: $ => $.CondExpr,

      CondExpr: $ => $.OrExpr,

      OrExpr: $ => choice(
        seq($.OrExpr, /[Oo][Rr]/, $.AndExpr),
        $.AndExpr
      ),

      AndExpr: $ => choice(
        seq($.AndExpr, /[Aa][Nn][Dd]/, $.EqNeqExpr),
        $.EqNeqExpr
      ),

      EqNeqExpr: $ => choice(
        seq($.EqNeqExpr, "=", $.CompExpr),
        seq($.EqNeqExpr, "<>", $.CompExpr),
        $.CompExpr
      ),

      CompExpr: $ => choice(
        seq($.CompExpr, "<", $.AdditiveExpr),
        seq($.CompExpr, "<=", $.AdditiveExpr),
        seq($.CompExpr, ">", $.AdditiveExpr),
        seq($.CompExpr, ">=", $.AdditiveExpr),
        $.AdditiveExpr
      ),

      AdditiveExpr: $ => choice(
        seq($.AdditiveExpr, "+", $.MultiplicativeExpr),
        seq($.AdditiveExpr, "-", $.MultiplicativeExpr),
        $.MultiplicativeExpr
      ),

      MultiplicativeExpr: $ => choice(
        seq($.MultiplicativeExpr, "*", $.UnaryExpr),
        seq($.MultiplicativeExpr, "/", $.UnaryExpr),
        $.UnaryExpr,
      ),

      UnaryExpr: $ => choice(
        seq("-", $.Primary),
        $.Primary
      ),

      Primary: $ => choice(
        $.NUM,
        $.STR,
        seq("(", $.Expr, ")"),
        $.ID,
        seq($.ID, ".", $.ID),
        seq($.ID, ".", $.ID, "(", optional($.Exprs), ")"),
        seq($.ID, $.Idxs)
      ),

      Idxs: $ => choice(
        seq("[", $.Expr, "]"),
        seq("[", $.Expr, "]", $.Idxs)
      ),

      // Terminal Symbols
      // Identifier & String & Number & CarriageReturn & Comment
      ID: _ => /[_a-zA-Z][_a-zA-Z0-9]*/,

      STR: _ => /\"[^\"]*\"/,

      NUM: _ => /([0-9]*[.])?[0-9]+/,

      CR: _ => choice(/\r\n/, /\n/),

      Comment: _ => token(seq(/\'/, /.*/))
    }
  });