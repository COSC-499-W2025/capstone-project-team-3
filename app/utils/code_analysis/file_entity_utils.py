# Format for this class, this will be removed once final implementation is done (Uses this to track progress)
# {
#   "classes": [
#     {
#       "name": "string", ---- done
#       "docstring": "string | null", --- done
#       "methods": [
#         {
#           "name": "string",
#           "parameters": ["string"],
#           "lines_of_code": "integer",
#           "complexity": "integer | null",
#           "docstring": "string | null",
#           "calls": ["string"]
#         }
#       ]
#     }
#   ]
# }

from tree_sitter import Parser, Node, Query, Tree, Language
from tree_sitter_language_pack import get_language
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from pygments import lex
from pygments.lexers import guess_lexer_for_filename
from pygments.token import Comment, Literal

from app.utils.code_analysis.grammar_loader import extract_rule_names
from app.utils.code_analysis.parse_code_utils import detect_language,map_language_for_treesitter,extract_contents

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

        # Exclude common false positives
        if rl.endswith("_pattern") or rl.endswith("_type") or rl.startswith("_"):
            continue

        # Class nodes
        if any(key in rl for key in class_keywords):
            class_nodes.append(rule)
            continue

        # Function nodes
        if any(key in rl for key in function_keywords):
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
def walk_class_nodes(node: Node, text: str, class_types: set, out: List[dict], file_path: Path):
    """
    DFS scan of the AST to collect class nodes.
    """
    if node.type in class_types:
        out.append(extract_single_class(node, text, file_path))

    for child in node.children:
        walk_class_nodes(child, text, class_types, out, file_path)
        
def extract_single_class(node: Node, text: str, file_path: Path) -> dict:
    """
    Extract class name + docstring + methods placeholder.
    """

    # Get class names
    class_names = extract_class_names(node, text)

    # 2. Extract docstring (Python/JS etc)
    docstring = extract_docstrings(node, text, file_path)

    # 3. Extract methods (to be implemented later)
    methods = []

    return {
        "name": class_names,
        "docstring": docstring,
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
def extract_classes(root: Node, file_content: str, class_node_types: List[str], file_path: Path)->List[dict]:
    """
    Extract class-level entities (name, docstring, methods list).
    """
    results = []
    walk_class_nodes(root, file_content, set(class_node_types), results, file_path)
    return results

def extract_entities(tree: Tree, file_content: str, class_node_types: List[str], function_node_types: List[str], component_node_types: List[str], file_path: Path)->Dict[str, List[dict]]:
    """
    Main entry point for extracting structured entities from a single file.
    """

    class_entities = extract_classes(tree.root_node, file_content, class_node_types,file_path)

    # TODO: add functions and components
    return {
        "classes": class_entities,
        "functions": [],
        "components": []
    }