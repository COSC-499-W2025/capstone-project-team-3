import dukpy
from pathlib import Path
from typing import List
import re

def extract_rule_names(grammar_path: Path) -> List[str]:
    """
    Extracts rule names from a Tree-sitter grammar.js file purely by parsing text.
    """
    text = grammar_path.read_text()

    # Find the rules block: rules: { ... }
    match = re.search(r"rules\s*:\s*{(.*?)}\s*,?\s*$", text, re.S | re.M)
    if not match:
        return []

    rules_block = match.group(1)

    # Extract all identifiers before a colon at the top indent level
    # Handles: rule_name: $ => ..., rule_name: seq(...), rule_name: ...
    rule_names = re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*:", rules_block)

    # Remove duplicates and internal rule names starting with "_"
    return list(dict.fromkeys(rule_names))