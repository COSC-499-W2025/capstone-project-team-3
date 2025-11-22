/**
 * @file Modelica grammar for tree-sitter
 * @author Mohamad Omar Nachawati <mnachawa@gmail.com>
 * @license MIT
 */

/// <reference types="tree-sitter-cli/dsl" />
// @ts-check

const PREC = {
  LOGICAL_OR: 4,
  LOGICAL_AND: 5,
  UNARY_NEGATION: 6,
  RELATIONAL: 7,
  ADDITIVE: 8,
  ADDITIVE_UNARY: 9,
  MULTIPLICATIVE: 10,
  EXPONENTIATION: 11,
};

module.exports = grammar({
  name: 'modelica',
  extras: $ => [
    /\s/,
    $.BLOCK_COMMENT,
    $.LINE_COMMENT,
  ],
  supertypes: $ => [
    $._Argument,
    $._ClassSpecifier,
    $._Element,
    $._Equation,
    $._Expression,
    $._ImportClause,
    $._Literal,
    $._PrimaryExpression,
    $._SimpleExpression,
    $._Statement,
    $._UnsignedNumberLiteral,
  ],
  conflicts: ($) => [
    [$.EquationSection],
    [$.Name],
    [$.ElseIfEquationClause],
    [$.ElseEquationClause],
    [$.ElseWhenEquationClause],
  ],
  word: $ => $.IDENT,
  rules: {

    // A.2.1 Stored Definition – Within

    StoredDefinition: $ => seq(
      optional(field('bom', $.BOM)),
      optional(field('withinClause', $.WithinClause)),
      repeat(field('classDefinitionClause', $.ClassDefinitionClause)),
    ),

    WithinClause: $ => seq(
      'within', optional(field('packageName', $.Name)), ';',
    ),

    ClassDefinitionClause: $ => seq(
      optional(field('final', 'final')),
      field('classDefinition', $.ClassDefinition), ';',
    ),

    // A.2.2 Class Definition

    ClassDefinition: $ => seq(
      optional(field('encapsulated', 'encapsulated')),
      field('classPrefixes', $.ClassPrefixes),
      field('classSpecifier', $._ClassSpecifier),
    ),

    ClassPrefixes: $ => seq(
      optional(field('partial', 'partial')),
      choice(
        field('class', 'class'),
        field('model', 'model'),
        seq(
          optional(field('operator', 'operator')),
          field('record', 'record'),
        ),
        field('block', 'block'),
        seq(
          optional(field('expandable', 'expandable')),
          field('connector', 'connector')),
        field('type', 'type'),
        field('package', 'package'),
        seq(
          optional(
            choice(
              field('pure', 'pure'),
              field('impure', 'impure'),
            ),
          ),
          optional(field('operator', 'operator')),
          field('function', 'function'),
        ),
        field('operator', 'operator'),
      ),
    ),

    _ClassSpecifier: $ => choice(
      $.LongClassSpecifier,
      $.ShortClassSpecifier,
      $.DerClassSpecifier,
    ),

    LongClassSpecifier: $ => seq(
      choice(
        field('identifier', $.IDENT),
        seq(
          field('extends', 'extends'),
          field('identifier', $.IDENT),
          optional(field('classModification', $.ClassModification)),
        ),
      ),
      optional(field('descriptionString', $.DescriptionString)),
      optional(field('initialElementList', $.InitialElementList)),
      repeat(choice(
        field('elementList', $.ElementList),
        field('equationSection', $.EquationSection),
        field('algorithmSection', $.AlgorithmSection),
      )),
      optional(field('externalFunctionClause', $.ExternalFunctionClause)),
      optional(seq(field('annotationClause', $.AnnotationClause), ';')),
      'end', field('endIdentifier', $.IDENT),
    ),

    ShortClassSpecifier: $ => seq(
      field('identifier', $.IDENT), '=',
      choice(
        seq(
          optional(choice(field('input', 'input'), field('output', 'output'))),
          field('typeSpecifier', $.TypeSpecifier),
          optional(field('arraySubscripts', $.ArraySubscripts)),
          optional(field('classModification', $.ClassModification)),
        ),
        seq(
          field('enumeration', 'enumeration'), '(',
          optional(choice(
            commaSep1(field('enumerationLiteral', $.EnumerationLiteral)),
            field('unspecified', ':'),
          )), ')',
        ),
      ),
      optional(field('descriptionString', $.DescriptionString)),
      optional(field('annotationClause', $.AnnotationClause)),
    ),

    DerClassSpecifier: $ => seq(
      field('identifier', $.IDENT), '=', 'der', '(',
      field('typeSpecifier', $.TypeSpecifier), ',',
      commaSep1(field('input', $.IDENT)), ')',
      optional(field('descriptionString', $.DescriptionString)),
      optional(field('annotationClause', $.AnnotationClause)),
    ),

    ExternalFunctionClause: $ => seq(
      'external',
      optional(field('languageSpecification', $.LanguageSpecification)),
      optional(field('externalFunctionCall', $.ExternalFunctionCall)),
      optional(field('annotationClause', $.AnnotationClause)),
      ';',
    ),

    EnumerationLiteral: $ => seq(
      field('identifier', $.IDENT),
      optional(field('descriptionString', $.DescriptionString)),
      optional(field('annotationClause', $.AnnotationClause)),
    ),

    LanguageSpecification: $ => field('language', $.StringLiteral),

    ExternalFunctionCall: $ => seq(
      optional(seq(field('output', $.ComponentReference), '=')),
      field('functionName', $.IDENT),
      '(', optional(field('arguments', $.ExpressionList)), ')',
    ),

    InitialElementList: $ => repeat1(field('element', $._Element)),

    ElementList: $ => seq(
      choice(
        field('protected', 'protected'),
        field('public', 'public'),
      ),
      repeat(field('element', $._Element)),
    ),

    _Element: $ => choice(
      $._ImportClause,
      $.ExtendsClause,
      $.NamedElementClause,
    ),

    NamedElementClause: $ => seq(
      optional(field('redeclare', 'redeclare')),
      optional(field('final', 'final')),
      optional(field('inner', 'inner')),
      optional(field('outer', 'outer')),
      optional(field('replaceable', 'replaceable')),
      choice(
        field('classDefinition', $.ClassDefinition),
        field('componentClause', $.ComponentClause),
      ),
      optional(seq(
        field('constrainingClause', $.ConstrainingClause),
        optional(field('descriptionString', $.DescriptionString)),
        optional(field('annotationClause', $.AnnotationClause)),
      )),
      ';',
    ),

    _ImportClause: $ => choice(
      $.SimpleImportClause,
      $.CompoundImportClause,
      $.UnqualifiedImportClause,
    ),

    SimpleImportClause: $ => seq(
      'import', optional(seq(field('shortName', $.IDENT), '=')), field('packageName', $.Name),
      optional(field('descriptionString', $.DescriptionString)),
      optional(field('annotationClause', $.AnnotationClause)),
      ';',
    ),

    CompoundImportClause: $ => seq(
      'import', field('packageName', $.Name), '.', '{', commaSep1(field('importName', $.IDENT)), '}',
      optional(field('descriptionString', $.DescriptionString)),
      optional(field('annotationClause', $.AnnotationClause)),
      ';',
    ),

    UnqualifiedImportClause: $ => seq(
      'import', field('packageName', $.Name), '.', '*',
      optional(field('descriptionString', $.DescriptionString)),
      optional(field('annotationClause', $.AnnotationClause)),
      ';',
    ),

    // A.2.3 Extends

    ExtendsClause: $ => seq(
      'extends',
      field('typeSpecifier', $.TypeSpecifier),
      optional(field('classOrInheritanceModification', $.ClassOrInheritanceModification)),
      optional(field('annotationClause', $.AnnotationClause)),
      ';',
    ),

    ConstrainingClause: $ => seq(
      'constrainedby',
      field('typeSpecifier', $.TypeSpecifier),
      optional(field('classModification', $.ClassModification)),
    ),

    ClassOrInheritanceModification: $ => seq(
      '(', commaSep(field('argumentOrInheritanceModification', choice($._Argument, $.InheritanceModification))), ')',
    ),

    InheritanceModification: $ => seq(
      'break',
      choice(
        field('connectClause', $.ConnectClause),
        field('identifier', $.IDENT),
      ),
    ),

    // A.2.4 Component Clause

    ComponentClause: $ => seq(
      optional(choice(field('flow', 'flow'), field('stream', 'stream'))),
      optional(choice(field('discrete', 'discrete'), field('parameter', 'parameter'), field('constant', 'constant'))),
      optional(choice(field('input', 'input'), field('output', 'output'))),
      field('typeSpecifier', $.TypeSpecifier),
      optional(field('arraySubscripts', $.ArraySubscripts)),
      commaSep1(field('componentDeclaration', $.ComponentDeclaration)),
    ),

    ComponentDeclaration: $ => seq(
      field('declaration', $.Declaration),
      optional(field('conditionAttribute', $.ConditionAttribute)),
      optional(field('descriptionString', $.DescriptionString)),
      optional(field('annotationClause', $.AnnotationClause)),
    ),

    ConditionAttribute: $ => seq(
      'if', field('condition', $._Expression),
    ),

    Declaration: $ => seq(
      field('identifier', $.IDENT),
      optional(field('arraySubscripts', $.ArraySubscripts)),
      optional(field('modification', $.Modification)),
    ),

    // A.2.5 Modification

    Modification: $ => choice(
      seq(
        field('classModification', $.ClassModification),
        optional(seq('=', field('modificationExpression', $.ModificationExpression))),
      ),
      seq(choice('=', ':='), field('modificationExpression', $.ModificationExpression)),
    ),

    ModificationExpression: $ => choice(
      field('break', 'break'),
      field('expression', $._Expression),
    ),

    ClassModification: $ => seq(
      '(', commaSep(field('argument', $._Argument)), ')',
    ),

    _Argument: $ => choice(
      $.ElementModification,
      $.ElementReplaceable,
      $.ElementRedeclaration,
    ),

    ElementModification: $ => seq(
      optional(field('each', 'each')),
      optional(field('final', 'final')),
      field('name', $.Name),
      optional(field('modification', $.Modification)),
      optional(field('descriptionString', $.DescriptionString)),
    ),

    ElementRedeclaration: $ => seq(
      'redeclare',
      optional(field('each', 'each')),
      optional(field('final', 'final')),
      optional(field('replaceable', 'replaceable')),
      choice(
        field('shortClassDefinition', $.ShortClassDefinition),
        field('componentClause', $.ComponentClause1),
      ),
      optional(field('constrainingClause', $.ConstrainingClause)),
    ),

    ElementReplaceable: $ => seq(
      optional(field('each', 'each')),
      optional(field('final', 'final')),
      'replaceable',
      choice(
        field('shortClassDefinition', $.ShortClassDefinition),
        field('componentClause', $.ComponentClause1),
      ),
      optional(field('constrainingClause', $.ConstrainingClause)),
    ),

    ComponentClause1: $ => seq(
      optional(choice(field('flow', 'flow'), field('stream', 'stream'))),
      optional(choice(field('discrete', 'discrete'), field('parameter', 'parameter'), field('constant', 'constant'))),
      optional(choice(field('input', 'input'), field('output', 'output'))),
      field('typeSpecifier', $.TypeSpecifier),
      field('componentDeclaration', $.ComponentDeclaration1),
    ),

    ComponentDeclaration1: $ => seq(
      field('declaration', $.Declaration),
      optional(field('descriptionString', $.DescriptionString)),
      optional(field('annotationClause', $.AnnotationClause)),
    ),

    ShortClassDefinition: $ => seq(
      field('classPrefixes', $.ClassPrefixes),
      field('shortClassSpecifier', $.ShortClassSpecifier),
    ),

    // A.2.6 Equations

    EquationSection: $ => seq(
      optional(field('initial', 'initial')),
      'equation',
      repeat(field('equation', $._Equation)),
    ),

    AlgorithmSection: $ => seq(
      optional(field('initial', 'initial')),
      'algorithm',
      repeat(field('statement', $._Statement)),
    ),

    _Equation: $ => choice(
      $.SimpleEquation,
      $.IfEquation,
      $.ForEquation,
      $.ConnectEquation,
      $.WhenEquation,
      $.SpecialEquation,
    ),

    _Statement: $ => choice(
      $.SimpleAssignmentStatement,
      $.FunctionCallStatement,
      $.DestructuringAssignmentStatement,
      $.BreakStatement,
      $.ReturnStatement,
      $.IfStatement,
      $.ForStatement,
      $.WhileStatement,
      $.WhenStatement,
    ),

    IfEquation: $ => seq(
      'if', field('condition', $._Expression), 'then',
      repeat(field('equation', $._Equation)),
      repeat(field('elseIfEquationClause', $.ElseIfEquationClause)),
      optional(field('elseEquationClause', $.ElseEquationClause)),
      'end', 'if',
      optional(field('descriptionString', $.DescriptionString)),
      optional(field('annotationClause', $.AnnotationClause)),
      ';',
    ),

    ElseIfEquationClause: $ => seq(
      'elseif', field('condition', $._Expression), 'then',
      repeat(field('equation', $._Equation)),
    ),

    ElseEquationClause: $ => seq(
      'else', repeat(field('equation', $._Equation)),
    ),

    IfStatement: $ => seq(
      'if', field('condition', $._Expression), 'then',
      repeat(field('statement', $._Statement)),
      repeat(field('elseIfStatementClause', $.ElseIfStatementClause)),
      optional(field('elseStatementClause', $.ElseStatementClause)),
      'end', 'if',
      optional(field('descriptionString', $.DescriptionString)),
      optional(field('annotationClause', $.AnnotationClause)),
      ';',
    ),

    ElseIfStatementClause: $ => seq(
      'elseif', field('condition', $._Expression), 'then',
      repeat(field('statement', $._Statement)),
    ),

    ElseStatementClause: $ => seq(
      'else', repeat(field('statement', $._Statement)),
    ),

    ForEquation: $ => seq(
      'for', commaSep1(field('forIndex', $.ForIndex)), 'loop',
      repeat(field('equation', $._Equation)),
      'end', 'for',
      optional(field('descriptionString', $.DescriptionString)),
      optional(field('annotationClause', $.AnnotationClause)),
      ';',
    ),

    ForStatement: $ => seq(
      'for', commaSep1(field('forIndex', $.ForIndex)), 'loop',
      repeat(field('statement', $._Statement)),
      'end', 'for',
      optional(field('descriptionString', $.DescriptionString)),
      optional(field('annotationClause', $.AnnotationClause)),
      ';',
    ),

    ForIndex: $ => seq(
      field('identifier', $.IDENT),
      optional(seq('in', field('expression', $._Expression))),
    ),

    WhileStatement: $ => seq(
      'while', field('condition', $._Expression), 'loop',
      repeat(field('statement', $._Statement)),
      'end', 'while',
      optional(field('descriptionString', $.DescriptionString)),
      optional(field('annotationClause', $.AnnotationClause)),
      ';',
    ),

    WhenEquation: $ => seq(
      'when', field('condition', $._Expression), 'then',
      repeat(field('equation', $._Equation)),
      repeat(field('elseWhenClause', $.ElseWhenEquationClause)),
      'end', 'when',
      optional(field('descriptionString', $.DescriptionString)),
      optional(field('annotationClause', $.AnnotationClause)),
      ';',
    ),

    ElseWhenEquationClause: $ => seq(
      'elsewhen', field('condition', $._Expression), 'then',
      repeat(field('equation', $._Equation)),
    ),

    WhenStatement: $ => seq(
      'when', field('condition', $._Expression), 'then',
      repeat(field('statement', $._Statement)),
      repeat(field('elseWhenClause', $.ElseWhenStatementClause)),
      'end', 'when',
      optional(field('descriptionString', $.DescriptionString)),
      optional(field('annotationClause', $.AnnotationClause)),
      ';',
    ),

    ElseWhenStatementClause: $ => seq(
      'elsewhen', field('condition', $._Expression), 'then',
      repeat(field('statement', $._Statement)),
    ),

    ConnectEquation: $ => seq(
      field('connectClause', $.ConnectClause),
      optional(field('descriptionString', $.DescriptionString)),
      optional(field('annotationClause', $.AnnotationClause)),
      ';',
    ),

    ConnectClause: $ => seq(
      'connect', '(',
      field('componentReference1', $.ComponentReference),
      ',',
      field('componentReference2', $.ComponentReference),
      ')',
    ),

    BreakStatement: $ => seq(
      'break',
      optional(field('descriptionString', $.DescriptionString)),
      optional(field('annotationClause', $.AnnotationClause)),
      ';',
    ),

    ReturnStatement: $ => seq(
      'return',
      optional(field('descriptionString', $.DescriptionString)),
      optional(field('annotationClause', $.AnnotationClause)),
      ';',
    ),

    SimpleEquation: $ => seq(
      field('expression1', $._SimpleExpression),
      '=',
      field('expression2', $._Expression),
      optional(field('descriptionString', $.DescriptionString)),
      optional(field('annotationClause', $.AnnotationClause)),
      ';',
    ),

    SpecialEquation: $ => seq(
      field('functionReference', $.ComponentReference),
      '(', optional(field('functionArguments', $.FunctionArguments)), ')',
      optional(field('descriptionString', $.DescriptionString)),
      optional(field('annotationClause', $.AnnotationClause)),
      ';',
    ),

    SimpleAssignmentStatement: $ => seq(
      field('target', $.ComponentReference),
      ':=',
      field('expression', $._Expression),
      optional(field('descriptionString', $.DescriptionString)),
      optional(field('annotationClause', $.AnnotationClause)),
      ';',
    ),

    FunctionCallStatement: $ => seq(
      field('functionReference', $.ComponentReference),
      '(', optional(field('functionArguments', $.FunctionArguments)), ')',
      optional(field('descriptionString', $.DescriptionString)),
      optional(field('annotationClause', $.AnnotationClause)),
      ';',
    ),

    DestructuringAssignmentStatement: $ => seq(
      field('targets', $.ParenthesizedExpression),
      ':=',
      field('functionReference', $.ComponentReference),
      '(', optional(field('functionArguments', $.FunctionArguments)), ')',
      optional(field('descriptionString', $.DescriptionString)),
      optional(field('annotationClause', $.AnnotationClause)),
      ';',
    ),

    // A.2.7 Expressions

    _Expression: $ => choice(
      $.IfExpression,
      $.RangeExpression,
      $._SimpleExpression,
    ),

    IfExpression: $ => seq(
      'if', field('condition', $._Expression), 'then', field('thenExpression', $._Expression),
      repeat(field('elseIfExpressionClause', $.ElseIfExpressionClause)),
      'else', field('elseExpression', $._Expression),
    ),

    ElseIfExpressionClause: $ => seq(
      'elseif', field('condition', $._Expression), 'then', field('thenExpression', $._Expression),
    ),

    RangeExpression: $ => choice(
      seq(field('startExpression', $._SimpleExpression), ':',
        field('stepExpression', $._SimpleExpression), ':',
        field('stopExpression', $._SimpleExpression)),
      seq(field('startExpression', $._SimpleExpression), ':',
        field('stopExpression', $._SimpleExpression)),
    ),

    _SimpleExpression: $ => choice(
      $.UnaryExpression,
      $.BinaryExpression,
      $._PrimaryExpression,
    ),

    UnaryExpression: $ => choice(
      prec(PREC.UNARY_NEGATION, seq(field('operator', 'not'), field('operand', $._SimpleExpression))),
      prec(PREC.ADDITIVE_UNARY, seq(field('operator', '+'), field('operand', $._SimpleExpression))),
      prec(PREC.ADDITIVE_UNARY, seq(field('operator', '-'), field('operand', $._SimpleExpression))),
      prec(PREC.ADDITIVE_UNARY, seq(field('operator', '.+'), field('operand', $._SimpleExpression))),
      prec(PREC.ADDITIVE_UNARY, seq(field('operator', '.-'), field('operand', $._SimpleExpression))),
    ),

    BinaryExpression: $ => choice(
      prec.left(PREC.LOGICAL_OR, seq(field('operand1', $._SimpleExpression), field('operator', 'or'), field('operand2', $._SimpleExpression))),
      prec.left(PREC.LOGICAL_AND, seq(field('operand1', $._SimpleExpression), field('operator', 'and'), field('operand2', $._SimpleExpression))),
      prec.right(PREC.RELATIONAL, seq(field('operand1', $._SimpleExpression), field('operator', '<'), field('operand2', $._SimpleExpression))),
      prec.right(PREC.RELATIONAL, seq(field('operand1', $._SimpleExpression), field('operator', '<='), field('operand2', $._SimpleExpression))),
      prec.right(PREC.RELATIONAL, seq(field('operand1', $._SimpleExpression), field('operator', '>'), field('operand2', $._SimpleExpression))),
      prec.right(PREC.RELATIONAL, seq(field('operand1', $._SimpleExpression), field('operator', '>='), field('operand2', $._SimpleExpression))),
      prec.right(PREC.RELATIONAL, seq(field('operand1', $._SimpleExpression), field('operator', '=='), field('operand2', $._SimpleExpression))),
      prec.right(PREC.RELATIONAL, seq(field('operand1', $._SimpleExpression), field('operator', '<>'), field('operand2', $._SimpleExpression))),
      prec.left(PREC.ADDITIVE, seq(field('operand1', $._SimpleExpression), field('operator', '+'), field('operand2', $._SimpleExpression))),
      prec.left(PREC.ADDITIVE, seq(field('operand1', $._SimpleExpression), field('operator', '-'), field('operand2', $._SimpleExpression))),
      prec.left(PREC.ADDITIVE, seq(field('operand1', $._SimpleExpression), field('operator', '.+'), field('operand2', $._SimpleExpression))),
      prec.left(PREC.ADDITIVE, seq(field('operand1', $._SimpleExpression), field('operator', '.-'), field('operand2', $._SimpleExpression))),
      prec.left(PREC.MULTIPLICATIVE, seq(field('operand1', $._SimpleExpression), field('operator', '*'), field('operand2', $._SimpleExpression))),
      prec.left(PREC.MULTIPLICATIVE, seq(field('operand1', $._SimpleExpression), field('operator', '/'), field('operand2', $._SimpleExpression))),
      prec.left(PREC.MULTIPLICATIVE, seq(field('operand1', $._SimpleExpression), field('operator', '.*'), field('operand2', $._SimpleExpression))),
      prec.left(PREC.MULTIPLICATIVE, seq(field('operand1', $._SimpleExpression), field('operator', './'), field('operand2', $._SimpleExpression))),
      prec.right(PREC.EXPONENTIATION, seq(field('operand1', $._PrimaryExpression), field('operator', '^'), field('operand2', $._PrimaryExpression))),
      prec.right(PREC.EXPONENTIATION, seq(field('operand1', $._PrimaryExpression), field('operator', '.^'), field('operand2', $._PrimaryExpression))),
    ),

    _PrimaryExpression: $ => choice(
      $._Literal,
      $.FunctionCall,
      $.ComponentReference,
      $.ParenthesizedExpression,
      $.ArrayConcatenation,
      $.ArrayConstructor,
      $.EndExpression,
    ),

    EndExpression: $ => 'end',

    _Literal: $ => choice(
      $._UnsignedNumberLiteral,
      $.StringLiteral,
      $.LogicalLiteral,
    ),

    _UnsignedNumberLiteral: $ => choice(
      $.UnsignedIntegerLiteral,
      $.UnsignedRealLiteral,
    ),

    UnsignedIntegerLiteral: $ => $.UNSIGNED_INTEGER,

    UnsignedRealLiteral: $ => $.UNSIGNED_REAL,

    LogicalLiteral: $ => choice('false', 'true'),

    StringLiteral: $ => $.STRING,

    TypeSpecifier: $ => seq(
      optional(field('global', '.')), field('name', $.Name),
    ),

    Name: $ => commaSep1(field('part', $.IDENT), '.'),

    ComponentReference: $ => seq(
      optional(field('global', '.')),
      commaSep1(field('part', $.ComponentReferencePart), '.'),
    ),

    ComponentReferencePart: $ => seq(
      field('identifier', $.IDENT),
      optional(field('arraySubscripts', $.ArraySubscripts)),
    ),

    FunctionCall: $ => seq(
      field('functionReference', choice($.ComponentReference, 'der', 'initial', 'pure')),
      '(', optional(field('functionArguments', $.FunctionArguments)), ')',
    ),

    FunctionArguments: $ => choice(
      field('comprehensionClause', $.ComprehensionClause),
      seq(
        commaSep1(field('argument', $.FunctionArgument)),
        optional(seq(',', commaSep1(field('namedArgument', $.NamedArgument)))),
      ),
      commaSep1(field('namedArgument', $.NamedArgument)),
    ),

    ArrayConcatenation: $ => seq(
      '[', commaSep1(field('expressionList', $.ExpressionList), ';'), ']',
    ),

    ArrayConstructor: $ => seq(
      '{',
      optional(
        choice(
          field('comprehensionClause', $.ComprehensionClause),
          field('expressionList', $.ExpressionList),
        ),
      ),
      '}',
    ),

    ComprehensionClause: $ => seq(
      field('expression', $._Expression), 'for', commaSep1(field('forIndex', $.ForIndex)),
    ),

    NamedArgument: $ => seq(
      field('identifier', $.IDENT), '=', field('argument', $.FunctionArgument),
    ),

    FunctionArgument: $ => choice(
      field('functionPartialApplication', $.FunctionPartialApplication),
      field('expression', $._Expression),
    ),

    FunctionPartialApplication: $ => seq(
      'function', field('typeSpecifier', $.TypeSpecifier),
      '(', commaSep(field('namedArgument', $.NamedArgument)), ')',
    ),

    ParenthesizedExpression: $ => seq(
      '(', commaSep(optional(field('expression', $._Expression)), ','), ')',
    ),

    ExpressionList: $ => commaSep1(field('expression', $._Expression)),

    ArraySubscripts: $ => seq(
      '[', commaSep1(field('subscript', $.Subscript)), ']',
    ),

    Subscript: $ => choice(
      field('flexible', ':'),
      field('expression', $._Expression),
    ),

    DescriptionString: $ => commaSep1(field('string', $.StringLiteral), '+'),

    AnnotationClause: $ => seq(
      'annotation', field('classModification', $.ClassModification),
    ),

    // A.1 Lexical conventions

    BOM: $ => /\u00EF\u00BB\u00BF/,

    IDENT: $ => token(choice(
      seq(/[_a-zA-Z]/, repeat(choice(/[0-9]/, /[_a-zA-Z]/))),
      seq('\'', repeat(choice(
        /[_a-zA-Z]/, /[0-9]/, '!', '#', '$', '%', '&', '(', ')',
        '*', '+', ',', '-', '.', '/', ':', ';', '<', '>', '=',
        '?', '@', '[', ']', '^', '{', '}', '|', '~', ' ', '"',
        seq('\\', choice('\'', '"', '?', '\\', 'a', 'b', 'f', 'n', 'r', 't', 'v')))), '\''))),

    STRING: $ => token(seq('"', repeat(choice(/[^"\\]/,
      seq('\\', choice('\'', '"', '?', '\\', 'a', 'b', 'f', 'n', 'r', 't', 'v')))), '"')),

    UNSIGNED_INTEGER: $ => /[0-9]+/,

    UNSIGNED_REAL: $ => token(choice(
      seq(/[0-9]+/, '.', optional(/[0-9]+/)),
      seq(/[0-9]+/, optional(seq('.', optional(/[0-9]+/))), choice('e', 'E'), optional(choice('+', '-')), /[0-9]+/),
      seq('.', /[0-9]+/, optional(seq(choice('e', 'E'), optional(choice('+', '-')), /[0-9]+/))),
    )),

    // https://stackoverflow.com/questions/13014947/regex-to-match-a-c-style-multiline-comment/36328890#36328890
    BLOCK_COMMENT: $ => token(
      seq('/*', /[^*]*\*+([^/*][^*]*\*+)*/, '/'),
    ),

    LINE_COMMENT: $n => token(
      seq('//', /[^\r\n]*/),
    ),
  },
});

/**
 * Rule template to match zero or more rules delimited by a custom separator
 *
 * @param {RuleOrLiteral} rule
 * @param {RuleOrLiteral} sep
 * @return {ChoiceRule}
 */
function commaSep(rule, sep=',') {
  return optional(commaSep1(rule, sep));
}

/**
 * Rule template to match one or more rules delimited by a custom separator
 *
 * @param {RuleOrLiteral} rule
 * @param {RuleOrLiteral} sep
 * @return {SeqRule}
 */
function commaSep1(rule, sep=',') {
  return seq(rule, repeat(seq(sep, rule)));
}
