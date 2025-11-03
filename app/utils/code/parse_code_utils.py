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
 
# TODO: Logic for extract_imports would use tree_sitter logic (possible library: tree_sitter_languages)
def extract_imports(file_content: str, language: str) -> List[str]:
    """Extract imported modules or dependencies from the file."""
    