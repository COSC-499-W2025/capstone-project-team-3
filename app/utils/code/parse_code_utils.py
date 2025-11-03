# Question: do we want a project structure too?

# Tracking TODOs:
#  "detect_language":"str" --done
#   "lines_of_code": "integer",    ---done      
#   "docstring_count": "integer", ---done
#   "imports": ["string"],                 // Third-party + standard libs //Would need language detection and extracting file content
#   "dependencies_internal": ["string"],   // Local imports within the project
#   "top_keywords": ["string"],            // Most frequent meaningful identifiers
#   "entities": { FileEntities },          // Structural elements (functions, classes, etc.)
#   "metrics": { FileMetrics },            // Per-file stats
#   "roles_detected": ["string"],          // e.g. ["training", "api"]
#   "summary_snippet": "string"            // Optional 1–2 line summary

from pathlib import Path
from typing import Union, List, Dict
import json 
from pygments.lexers import guess_lexer, guess_lexer_for_filename
from pygments.util import ClassNotFound
from pygount import SourceAnalysis
from tree_sitter import Parser, Node
from tree_sitter_language_pack import get_language, get_parser
from typing import List, Set
import importlib.resources as pkg_resources

_TS_IMPORT_NODES = {}

try:
    # Works even when installed as a package or run inside Docker
    # with pkg_resources.files("app.shared").joinpath("treesitter_import_keywords.json").open() as f:
    #     _TS_IMPORT_NODES = json.load(f)
    json_path = Path(__file__).resolve().parents[2] / "shared" / "treesitter_import_keywords.json"
    with open(json_path, "r", encoding="utf-8") as f:
        _TS_IMPORT_NODES = json.load(f)
except Exception as e:
    print(f"Warning: Could not load treesitter_import_keywords.json: {e}")
    _TS_IMPORT_NODES = {}

def detect_language(file_path: Path) -> str | None:
    """
    Detect the programming language of the given file based on filename or content.
    
    Args:
        file_path: Path to the file.

    Returns:
        Language name if detected, else None.
    """
    
    try:
        lexer = guess_lexer_for_filename(file_path.name, file_path.read_text(encoding="utf-8"))
        return lexer.name
    except ClassNotFound:
        return None

def count_lines_of_code(file_path: Path) -> int:
    """Return the number of lines of code in the given source file."""
    analysis= SourceAnalysis.from_file(str(file_path),"pygount")
    count = analysis.code_count
    return count

def count_lines_of_documentation(file_path: Path) -> int:
    """Return the number of documentation lines in the given source file."""
    analysis= SourceAnalysis.from_file(str(file_path),"pygount")
    count = analysis.documentation_count
    return count

def extract_contents(file_path: Path) -> str:
    """Extracts the contents of the given file."""
    return file_path.read_text(encoding="utf-8")

# ---- Helper methods for extract_imports ----
def collect_node_types(node: Node, seen: Set[str] | None = None) -> Set[str]:
    """Recursively collect all node types in a syntax tree."""
    if seen is None:
        seen = set()
    seen.add(node.type)
    for child in node.children:
        collect_node_types(child, seen)
    return seen

def traverse_imports(node: Node, file_content: str, import_node_types: Set[str], imports: List[str]) -> None:
    """Recursively traverse the tree to find and collect import statements."""
    if node.type in import_node_types:
        imports.append(file_content[node.start_byte:node.end_byte].strip())
    for child in node.children:
        traverse_imports(child, file_content, import_node_types, imports)
        
def _extract_with_treesitter_dynamic(file_content: str, ts_lang: str, language:str) -> List[str]:
    """
    Extract import statements from source code using a Tree-sitter parser.

    This function parses the given source code with the specified Tree-sitter language
    object (`ts_lang`) and collects import or dependency statements. 

    Note:
    - Tree-sitter Language objects from `tree_sitter_language_pack` have `name=None`.
    - The `language` string is required for looking up language-specific import node types 
    in `_TS_IMPORT_NODES`, which is why both `ts_lang` and `language` are passed.
    """

    parser = Parser()
    parser.language = ts_lang
    tree = parser.parse(file_content.encode())
    root = tree.root_node

    import_types = set(_TS_IMPORT_NODES.get(language, []))
    
    # If no mapping exists, fall back to heuristic discovery
    if not import_types:
        all_types = collect_node_types(root)
        import_types = {
            t for t in all_types
            if any(k in t.lower() for k in ("import", "use", "require", "open", "include", "load"))
        }

    # If still empty, return early
    if not import_types:
        return []

    imports: List[str] = []
    traverse_imports(root, file_content, import_types, imports)
    return imports
# ---- End of helper methods -----

def extract_imports(file_content: str, language: str) -> List[str]:
    """Extract imported modules or dependencies from the file."""
    """
    Extract imported modules or dependencies from source code using tree_sitter_languages.

    Works fully offline, detects import-like node types dynamically.
    """
    imports: List[str] = []
    language= language.lower()
    try:
        ts_language = get_language(language)
        print(ts_language)
    except ValueError:
        # Language not supported by tree_sitter_language_pack
        return imports
    
    if ts_language:
        try:
            imports = _extract_with_treesitter_dynamic(file_content, ts_language, language)
        except Exception:
            return []

    # Fallback to regex
    # if not imports:
    #     try:
    #         imports = _extract_with_regex_fallback(file_content, language)
    #     except Exception:
    #         return []

    return imports

contents=extract_contents(Path("app/utils/path_utils.py"))
language= detect_language(Path("app/utils/path_utils.py"))
print(extract_imports(contents,language))