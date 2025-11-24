from pathlib import Path
from typing import Union, List, Dict, Optional
import json 
from pygments.lexers import guess_lexer, guess_lexer_for_filename
from pygments.util import ClassNotFound
from pygount import SourceAnalysis
from tree_sitter import Parser, Node, Query
from tree_sitter_language_pack import get_language
from typing import List, Set
import importlib.resources as pkg_resources
import re

_TS_IMPORT_NODES = {}
_TS_IMPORT_REGEX={}
_TS_IMPORT_QUERIES={}
_TS_LANGUAGE_MAPPING={}

try:
    # Works even when installed as a package or run inside Docker
    with pkg_resources.files("app.shared").joinpath("treesitter_import_keywords.json").open() as f:
        _TS_IMPORT_NODES = json.load(f)
except Exception as e:
    print(f"Warning: Could not load treesitter_import_keywords.json: {e}")
    _TS_IMPORT_NODES = {}

try:
    with pkg_resources.files("app.shared").joinpath("import_patterns_regex.json").open() as f:
        _TS_IMPORT_REGEX = json.load(f)
except Exception as e:
    print(f"Warning: Could not load import_patterns_regex.json: {e}")
    _TS_IMPORT_REGEX = {}
    
try:
    with pkg_resources.files("app.shared").joinpath("library.json").open() as f:
        _TS_IMPORT_QUERIES = json.load(f)
except Exception as e:
    print(f"Warning: Could not load library.json: {e}")
    _TS_IMPORT_QUERIES = {}
    
try:
    with pkg_resources.files("app.shared").joinpath("language_mapping.json").open() as f:
        _TS_LANGUAGE_MAPPING_LOAD = json.load(f)
        _TS_LANGUAGE_MAPPING={k.strip().lower(): v for k, v in _TS_LANGUAGE_MAPPING_LOAD.items()}
except Exception as e:
    print(f"Warning: Could not load language_mapping.json: {e}")
    _TS_LANGUAGE_MAPPING = {}

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
        language= lexer.name
        language = re.split(r'\+(?=[A-Za-z])', language)[0].strip()
        language = language.split()[0]
        return language
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
        
def extract_with_treesitter_dynamic(file_content: str, ts_lang: str, language:str) -> List[str]:
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

def extract_with_regex_fallback(file_content: str, language: str) -> List[str]:
    """
    Fallback method to extract import-like statements using regex patterns
    defined for the given language.
    """
    
    config = None
    for entry in _TS_IMPORT_REGEX:
        if isinstance(entry, dict) and entry.get("language", "").lower() == language:
            config = entry
            break
        
    if not config:
        return []

    patterns = config.get("import_patterns", [])
    if not isinstance(patterns, list):
        return []

    imports = []
    lines = file_content.splitlines()

    for line in lines:
        for pattern in patterns:
            try:
                if re.search(pattern, line):
                    imports.append(line.strip())
                    break
            except re.error:
                continue  # skip malformed regex

    return imports

def map_language_for_treesitter(language: str) -> str:
    """Map detected language (from Pygments) to Tree-sitter naming."""
    if not language:
        return language
    
    lang_key = language.strip().lower()
    return _TS_LANGUAGE_MAPPING.get(lang_key, lang_key)

# ---- End of helper methods -----

def extract_imports(file_content: str, language: str) -> List[str]:
    """Extract imported modules or dependencies from the file."""
    """
    Extract imported modules or dependencies from source code using tree_sitter_languages.

    Works fully offline, detects import-like node types dynamically.
    """
    imports: List[str] = []
    # Try Tree-sitter only if the language is supported
    try:
        language = map_language_for_treesitter(language)
        ts_language = get_language(language)
        imports = extract_with_treesitter_dynamic(file_content, ts_language, language)
    except (ValueError, Exception):
        # ValueError: language not supported by tree_sitter_languages
        # Exception: any runtime error during parsing
        # In either case, we'll fall through to regex
        imports = []

    # Fallback to regex
    if not imports:
        language= language.lower()
        try:
            imports = extract_with_regex_fallback(file_content, language)
        except Exception:
            return []

    return imports

def extract_libraries(import_statements: List[str], language: str, project_names: Optional[List[str]] = None) -> List[str]:
    """
    Extract library/module names from a list of import statements.

    Returns:
        List of library/module names.
    """
    language = map_language_for_treesitter(language)
    patterns = _TS_IMPORT_QUERIES.get(language, [])
    libraries = set()

    for stmt in import_statements:
        for pattern in patterns:
            matches = re.findall(pattern, stmt)
            
            for match in matches:
                # match may be a tuple if multiple groups exist
                if isinstance(match, tuple):
                    match = next((g for g in match if g), None)
                if not match:
                    continue #if there’s no valid match, skip the rest of this loop iteration and move on to the next one.

                # Split multi-imports like "os, sys" or "os ,sys"
                parts = re.split(r"\s*,\s*", match)
                for lib in parts:
                    lib = lib.strip().strip('\'"')
                    if not lib or lib.startswith((".", "/")):
                        continue

                    # Skip libraries that belong to project_names
                    if project_names:
                        normalized_lib = lib.replace("/", ".")
                        if any(p in normalized_lib for p in project_names):
                            continue

                    normalized = normalize_library(lib, language)
                    if normalized:
                        libraries.add(normalized)


    return list(libraries)

def extract_internal_dependencies(import_statements: List[str], language: str, project_names: Optional[List[str]] = None) -> List[str]:
    """
    Extract internal/project dependencies from import statements.
    Internal = relative imports or imports starting with known project prefixes.
    For 'from ... import ...', returns fully qualified names like 'module.symbol'.
    
    Args:
        import_statements: List of raw import lines.
        language: Language name (e.g. 'python', 'javascript').
        project_names: Optional list of known project prefixes, like ['app', 'src', 'mycompany'].
    """
    language = map_language_for_treesitter(language)
    patterns = _TS_IMPORT_QUERIES.get(language, [])
    internal = set()

    for stmt in import_statements:
        for pattern in patterns:
            # Find all matches
            matches = re.findall(pattern, stmt, re.MULTILINE | re.DOTALL)
            
            for match in matches:
                module = None
                imported_names = []

                # Case 1: The regex returned a single string match (e.g., simple import like 'import os, sys')
                # Split by commas to handle multiple imports on one line
                if isinstance(match, str):
                    # If match is a simple string, split by commas (multiple imports in one line)
                    imported_names = [name.strip() for name in match.split(",") if name.strip()]
                    for name in imported_names:
                        dep = name.strip().strip('\'"')  # remove any quotes around module name
                        if dep:
                            internal.add(dep)
                            
                # Case 2: The regex returned a tuple (e.g., 'from module import name1, name2')
                elif isinstance(match, tuple):
                    if len(match) == 1:
                        # Rare case: tuple with single element, just add it as dependency
                        candidate = match[0].strip()
                        if candidate:
                            internal.add(candidate)
                    elif len(match) >= 2:
                        # Typical 'from module import name1, name2' pattern
                        module = match[0].strip()
                        raw_names = match[1].strip()

                        for part in re.split(r"\s*,\s*", raw_names):
                            name = part.strip().rstrip(",")  # handle trailing commas
                            if name and not name.startswith("*"):  # skip 'import *'
                                # Build fully qualified name: module.name
                                fq_name = f"{module}.{name}"
                                internal.add(fq_name)
    
                # Case 3: Unexpected match type (not str or tuple), skip it
                else:
                    continue

    result = set()
    for dep in internal:
        dep_clean = dep.strip('\'"') # final cleanup of quotes
        if not dep_clean:
            continue

        # Keep relative imports (starting with '.' or '/')
        if dep_clean.startswith((".", "/")):
            result.add(dep_clean)
            continue

        # Keep dependencies that match known project prefixes
        if project_names:
            normalized_dep = dep_clean.replace("/", ".")
            if any(prefix in normalized_dep for prefix in project_names):
                result.add(dep_clean)
    return list(result)

def normalize_library(lib: str, language: str) -> str:
    """
    Normalize a library/module path

    Rules:
      - Drop the last segment of a dotted path (java.util.List -> java.util)
      - Drop the last segment of slash paths except Go (lodash/array -> lodash)
      - Preserve single-segment libraries (pytest, pathlib, mongoose)
      - Ignore 'static' and similar keywords
    """

    if not lib or lib.lower() in {"static", "import", "require"}:
        return None

    #  Languages like with dot paths like Python, Java, ...
    if "." in lib:
        parts = lib.split(".")
        if len(parts) > 1:
            return ".".join(parts[:-1])
        return lib

    #  Languages with slash paths like JavaScript/TypeScript...
    if "/" in lib and not lib.startswith("."):
        parts = lib.split("/")
        if len(parts) > 1:
            # universal behavior: keep top-level package
            return parts[0]
        return lib

    #  Go special-case (keep full import path)
    if language in ("go", "golang"):
        return lib

    # Single-segment library: keep as-is
    return lib

def extract_metrics(file_path: Path, entities: Dict[str, List[Dict]]) -> Dict[str, float]:
    """
    Compute per-file metrics including class methods + free functions.
    """
    # Collect all function-like bodies
    free_funcs = entities.get("functions", [])
    class_methods = [
        m for cls in entities.get("classes", [])
        for m in cls.get("methods", [])
    ]
    all_funcs = free_funcs + class_methods

    try:
        code_lines = count_lines_of_code(file_path)
    except Exception:
        code_lines = 0
    try:
        doc_lines = count_lines_of_documentation(file_path)
    except Exception:
        doc_lines = 0

    if all_funcs:
        total_loc = sum(f.get("lines_of_code", 0) for f in all_funcs)
        avg_func_length = round(total_loc / len(all_funcs), 2)
    else:
        avg_func_length = 0.0

    total_lines = code_lines + doc_lines
    comment_ratio = round(doc_lines / total_lines, 2) if total_lines else 0.0

    return {
        "average_function_length": avg_func_length,
        "comment_ratio": comment_ratio
    }