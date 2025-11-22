from tree_sitter import Parser, Node, Query, Tree, Language
from tree_sitter_language_pack import get_language
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from pygments import lex
from pygments.lexers import guess_lexer_for_filename
from pygments.token import Comment, Literal
# Commented out imports below because it is used during manual testing
# from app.utils.code_analysis.grammar_loader import extract_rule_names
# from app.utils.code_analysis.parse_code_utils import detect_language,map_language_for_treesitter,extract_contents

def classify_node_types(rule_names: List[str]) -> Tuple[List[str], List[str], List[str]]:
    """
    Classify grammar rule names into class, function, and component node types
    using a hybrid strategy:
      - naive substring matching (language-agnostic)
      - accuracy filters (exclude internal patterns/types/helpers)
    """

    # Language-agnostic keyword groups
    class_keywords = ["class", "struct", "interface", "trait", "enum"]
    function_keywords = ["function", "method", "def", "lambda"]
    component_keywords = ["component", "jsx", "tsx", "element", "tag", "template", "widget"]

    class_nodes = []
    function_nodes = []
    component_nodes = []

    for rule in rule_names:
        rl = rule.lower()

        # Exclude common false positives & structural/container/helper rules
        if (
            rl.endswith("_pattern") or rl.endswith("_type") or rl.startswith("_") or
            any(bad in rl for bad in ["parameter", "argument", "attribute", "property", "identifier", "name_list", "decorator_list", "annotation_list"])
        ):
            continue

        # Class nodes
        if any(key in rl for key in class_keywords):
            class_nodes.append(rule)
            continue

        # Skip decorated wrappers from function types (they should be treated as wrappers)
        # e.g @classmethod
        if rl.startswith("decorated_"):
            continue

        # Function nodes (narrow to actual definitions, skip pure name tokens)
        if any(key in rl for key in function_keywords) and not rl.endswith("_name") and not rl.endswith("decorated_definition"):
            function_nodes.append(rule)
            continue

        # Component nodes
        if any(key in rl for key in component_keywords):
            component_nodes.append(rule)
            continue

    return class_nodes, function_nodes, component_nodes

def get_parser(file_content: str, ts_lang: str)-> Tree:
    parser = Parser()
    parser.language = ts_lang
    tree = parser.parse(file_content.encode())
    return tree

# ------ Class methods -------
# ---- Helper methods for extract_classes ----
def walk_class_nodes(node: Node, text: str, class_types: set, function_types: set, out: List[dict], file_path: Path):
    """
    DFS scan of the AST to collect class nodes.
    """
    if node.type in class_types:
        out.append(extract_single_class(node, text, function_types, file_path))

    for child in node.children:
        walk_class_nodes(child, text, class_types, function_types, out, file_path)
        
def extract_single_class(node: Node, text: str, function_types: set, file_path: Path) -> dict:
    """Extract class name + docstring + methods using provided function_types."""

    # Get class names
    class_names = extract_class_names(node, text)

    # 2. Extract docstring (Python/JS etc)
    docstring = extract_docstrings(node, text, file_path)

    # 3. Extract methods
    methods = extract_methods_from_class(node, text, function_types, file_path)

    return {
        "name": class_names[0] if class_names else None,
        "docstring": docstring[0] if docstring else None,
        "methods": methods
    }
    
def extract_class_names(node: Node, text: str) -> List[str]:
    """
    Extract ALL class names from a class node.
    """
    CLASS_IDENTIFIERS = ["identifier", "type_identifier", "name", "constant", "scoped_identifier",
                         "class_name", "type_name", "module_identifier", "namespace_identifier"]
    names = []
    for child in node.children:
        if child.type in CLASS_IDENTIFIERS:
            name = text[child.start_byte:child.end_byte]
            names.append(name)
            continue
        if getattr(child, "children", None):
                # If child is a container node like “scoped_identifier” or “qualified_name”
                # explore only one more layer
                for grand in child.children:
                    if grand.type in CLASS_IDENTIFIERS:
                        name = text[grand.start_byte:grand.end_byte]
                        names.append(name)
    return names

# -------- Helper methods for docstring extraction --------- 
def extract_doc_blocks_from_text(file_path: Path, file_content: str) -> List[str]:
    """
    Extract documentation blocks from raw source text using Pygments lexical analysis.
    """
    # Let Pygments decide an appropriate lexer for this file
    lexer = guess_lexer_for_filename(file_path.name, file_content)

    doc_blocks = []
    current = []

    # Tokenize the text with Pygments
    for tok_type, tok_value in lex(file_content, lexer):
        # Identify doc-related tokens in a language-agnostic way
        is_doc = (
            tok_type in Comment or 
            tok_type in Literal.String.Doc or
            tok_value.strip().startswith("/**") or
            tok_value.strip().startswith("///") or
            tok_value.strip().startswith("'''") or
            tok_value.strip().startswith('"""')
        )

        if is_doc:
            # Add to the current documentation block
            current.append(tok_value)
        else:
            # If we just finished a doc block, store it
            if current:
                doc_blocks.append("".join(current))
                current = []

    # If a block is still open at end-of-file, close it
    if current:
        doc_blocks.append("".join(current))

    return doc_blocks

def match_docs_to_node(node: Node, text: str, doc_blocks: List[str]) -> Optional[List[str]]:
    """
    Match documentation blocks (extracted from raw text) to a specific Tree-sitter node.
    """
    
    # TODO: might need to improve matching
    node_start = node.start_byte
    results = []

    for block in doc_blocks:
        # Find the documentation block in the raw text
        idx = text.find(block)
        if idx == -1:
            continue
        end = idx + len(block)

        # Leading documentation — comment block ends right before the node
        if end <= node_start and node_start - end < 3:  # allow whitespace
            results.append(block)

        # Inline documentation — block appears inside the node e.g Python
        if idx > node_start and idx < node.end_byte:
            results.append(block)

    return results or None

# -------- End of Helper methods of docstring extraction ---------  
def extract_docstrings(node: Node, text: str, file_path: str) -> Optional[List[str]]:
    """ Extract documentation associated with a specific Tree-sitter AST node. """
    blocks = extract_doc_blocks_from_text(file_path, text)
    docs = match_docs_to_node(node, text, blocks)
    return docs
       
# ---- End of helper methods -----
def extract_classes(root: Node, file_content: str, class_node_types: List[str], function_node_types: List[str], file_path: Path)->List[dict]:
    """
    Extract class-level entities (name, docstring, methods list).
    """
    results: List[dict] = []
    walk_class_nodes(root, file_content, set(class_node_types), set(function_node_types), results, file_path)
    # Deduplicate classes by (name, docstring) to reduce false repeats (language-agnostic heuristic)
    dedup = []
    seen = set()
    for cls in results:
        key = (cls.get("name"), cls.get("docstring"))
        if key not in seen:
            seen.add(key)
            dedup.append(cls)
    return dedup

def extract_entities(tree: Tree, file_content: str, class_node_types: List[str], function_node_types: List[str], component_node_types: List[str], file_path: Path)->Dict[str, List[dict]]:
    """
    Main entry point for extracting structured entities from a single file.
    """
    class_entities = extract_classes(tree.root_node, file_content, class_node_types, function_node_types, file_path)
    function_entities = extract_functions(tree.root_node, file_content, function_node_types, class_node_types, file_path)

    # TODO: add components extraction
    return {
        "classes": class_entities,
        "functions": function_entities,
        "components": []
    }
    
# ---------------- New helper methods for method extraction -----------------
def extract_methods_from_class(class_node: Node, text: str, function_types: set, file_path: Path) -> List[dict]:
    """
    Return list of method entity dictionaries found within the given class node.
    """
    methods: List[dict] = []
    
    CLASS_BODY_TYPES = {"class_body", "block", "suite", "member_declaration_list"}
    WRAPPER_TYPES = {"decorated_definition", "annotation", "attribute_declaration"}

    def handle_child(n: Node):
        # Direct function definition
        if n.type in function_types:
            methods.append(extract_single_method(n, text, file_path))
            return
        # Decorator/annotation wrapper: search only immediate children for function
        if n.type in WRAPPER_TYPES:
            for ch in n.children:
                if ch.type in function_types:
                    methods.append(extract_single_method(ch, text, file_path))
                    return

    # Iterate over the class's children
    for child in class_node.children: 
        # If this node represents a body block, process its inner nodes
        if child.type in CLASS_BODY_TYPES:
            for grand in child.children:
                handle_child(grand)
        else:
            # Otherwise process the node directly
            handle_child(child)

    # Deduplicate by (name, span)
    dedup: List[dict] = []
    seen = set()
    for m in methods:
        key = (m.get("name"), m.get("lines_of_code"))
        if key not in seen:
            seen.add(key)
            dedup.append(m)
    return dedup

def extract_single_method(method_node: Node, text: str, file_path: Path) -> dict:
    """Build method entity dictionary including name, params, LOC, complexity, docstring, calls."""
    
    if method_node.type == "decorated_definition": #checking that the node identified have definitions like @staticmethod
        for ch in method_node.children:
            # Common underlying function node type names across grammars
            if ch.type in {"function_definition", "method_definition", "function_declaration", "method_declaration"}:
                method_node = ch
                break
    name = extract_method_name(method_node, text)
    params = extract_method_parameters(method_node, text)
    loc = (method_node.end_point[0] - method_node.start_point[0]) + 1
    complexity = estimate_cyclomatic_complexity(method_node, text)
    docstring = extract_docstrings(method_node, text, file_path)
    calls = extract_method_calls(method_node, text)
    return {
        "name": name,
        "parameters": params,
        "lines_of_code": loc,
        "complexity": complexity,
        "docstring": docstring[0] if docstring else None,
        "calls": calls
    }

def extract_method_name(method_node: Node, text: str) -> Optional[str]:
    """Locate method/function name token among immediate or one-level nested children."""
    
    # Possible node types that can represent a method/function name across languages
    CANDIDATE_NAME_TYPES = {"identifier", "name", "function_name", "method_name", "property_identifier"}

    # Look through direct children of the method node
    for child in method_node.children:
        # If this child is a name-bearing node, return its corresponding text
        if child.type in CANDIDATE_NAME_TYPES:
            return text[child.start_byte:child.end_byte]

        # Some grammars nest the name under another wrapper node (e.g., a declarator),
        # so inspect one level deeper if needed.
        for grand in getattr(child, 'children', []):
            if grand.type in CANDIDATE_NAME_TYPES:
                return text[grand.start_byte:grand.end_byte]

    # No name token found at expected locations
    return None

def extract_method_parameters(method_node: Node, text: str) -> List[str]:
    """Collect parameter identifier tokens within recognized parameter container nodes.

    Performs recursive descent within each container; duplicates and trivial
    implicit references (self/this) are removed.
    """

    # Node types that may contain parameter declarations across different languages
    PARAM_CONTAINER_TYPES = {"parameters", "parameter_list", "formal_parameters"}

    # Node types representing parameter names or declarators
    PARAM_NAME_TYPES = {"identifier", "name", "parameter", "variable_declarator"}

    params = []

    # Recursively traverse nodes inside a parameter container and collect names
    def collect_param_names(node: Node):
        for ch in node.children:
            # If this child represents some form of parameter identifier, capture it
            if ch.type in PARAM_NAME_TYPES:
                params.append(text[ch.start_byte:ch.end_byte])
            # Continue descending to catch deeply nested declarators
            collect_param_names(ch)

    # Search immediate children of the method node for parameter containers
    for child in method_node.children:
        if child.type in PARAM_CONTAINER_TYPES:
            collect_param_names(child)
        else:
            # Some grammars nest parameter containers under wrapper nodes (e.g., declarators)
            for grand in getattr(child, 'children', []):
                if grand.type in PARAM_CONTAINER_TYPES:
                    collect_param_names(grand)

    # Cleanup: remove duplicates and ignore language-specific implicit parameters
    cleaned = []
    seen = set()
    for p in params:
        p_clean = p.strip()
        # Skip empty tokens and implicit receiver parameters
        if not p_clean or p_clean in ("self", "this"):
            continue
        # Maintain insertion order by tracking what we've already kept
        if p_clean not in seen:
            seen.add(p_clean)
            cleaned.append(p_clean)

    return cleaned

def estimate_cyclomatic_complexity(method_node: Node, text: str) -> Optional[int]:
    """Estimate cyclomatic complexity (very coarse) for a method.

    Text heuristic:
      - Start at 1 (baseline path)
      - +1 per occurrence of decision keyword: if, for, while, case, catch,
        elif, switch
      - +1 per logical operator '&&' or '||'

    Returns an integer >= 1. Replace with AST node-based counting for accuracy.
    """
    snippet = text[method_node.start_byte:method_node.end_byte]
    keywords = ["if", "for", "while", "case", "catch", "elif", "switch"]
    count = 1
    for kw in keywords:
        count += len(__import__('re').findall(rf"\b{kw}\b", snippet))
    count += snippet.count("&&") + snippet.count("||")
    return count

def extract_method_calls(method_node: Node, text: str) -> List[str]:
    """
    Extract unique method/function names invoked within a method body.
    """
     # Node types representing call expressions across various grammars
    CALL_NODE_TYPES = {"call", "call_expression", "function_call", "method_invocation"}

    # Node types that may hold the callee name itself
    NAME_NODE_TYPES = {"identifier", "name", "property_identifier"}

    calls = []

    def walk(n: Node):
        # Detect call-like nodes
        if n.type in CALL_NODE_TYPES:
            # Attempt to extract the callee from the call's first child
            if n.children:
                callee = n.children[0]

                # Direct name-based callee (e.g., identifier or simple name)
                if callee.type in NAME_NODE_TYPES:
                    calls.append(text[callee.start_byte:callee.end_byte])

                else:
                    # Nested/attribute expressions: search child nodes for the first name
                    for ch in callee.children:
                        if ch.type in NAME_NODE_TYPES:
                            calls.append(text[ch.start_byte:ch.end_byte])
                            break

        # Continue walking all descendant nodes
        for ch in n.children:
            walk(ch)

    # Begin recursive traversal from the method node
    walk(method_node)

    # Remove duplicates while preserving order
    dedup = []
    seen = set()
    for c in calls:
        c_clean = c.strip()
        # Filter obvious non-call identifiers (single char, purely numeric)
        if not c_clean or len(c_clean) == 1 or c_clean.isdigit():
            continue
        if c_clean and c_clean not in seen:
            seen.add(c_clean)
            dedup.append(c_clean)

    return dedup

# ---------------- New helper methods for free-standing function extraction -----------------
def walk_function_nodes(node: Node, text: str, function_types: set, class_types: set, in_class: bool, out: List[dict], file_path: Path):
    """Collect free-standing functions (not linked to a class)"""
    WRAPPER_TYPES = {"decorated_definition", "annotation", "attribute_declaration"}

    if not in_class:
        if node.type in WRAPPER_TYPES:
            for ch in node.children:
                if ch.type in function_types:
                    out.append(extract_single_method(ch, text, file_path))
                    return
        elif node.type in function_types:
            out.append(extract_single_method(node, text, file_path))

    # Structural fallback: if classification missed function types, detect by presence of parameter & body containers
    if not in_class and node.type not in function_types:
        PARAM_HINTS = {"parameters", "parameter_list", "formal_parameters"}
        BODY_HINTS = {"block", "suite", "body", "compound_statement"}
        has_params = any(ch.type in PARAM_HINTS for ch in node.children)
        has_body = any(ch.type in BODY_HINTS for ch in node.children)
        if has_params and has_body:
            out.append(extract_single_method(node, text, file_path))
            return

    next_in_class = in_class or (node.type in class_types)
    # Limit descent: do not descend inside function definitions
    # Do not retrieve nested functions
    if node.type in function_types:
        return
    for child in node.children:
        walk_function_nodes(child, text, function_types, class_types, next_in_class, out, file_path)

def extract_functions(root: Node, file_content: str, function_node_types: List[str], class_node_types: List[str], file_path: Path) -> List[dict]:
    """
    Extract free-standing (module-level) functions.
    Free-standing: it is not nested inside any class
    """
    results: List[dict] = []
    walk_function_nodes(root, file_content, set(function_node_types), set(class_node_types), False, results, file_path)
    return results