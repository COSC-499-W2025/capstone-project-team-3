import json
import os
import urllib.request

JSON_FILE = "tree-sitter-parsers.json"
OUTPUT_DIR = "grammars"

# Ensure grammars directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load JSON file
with open(JSON_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

for language, entries in data.items():
    for entry in entries:
        if entry.get("grammar.json") is True or entry.get("grammar.js") is True:
            repo_url = entry["url"]

            # Build grammar.js raw file URL
            # Works for GitHub repos
            # Example:
            #   https://github.com/user/repo → https://github.com/user/repo/raw/HEAD/grammar.js
            grammar_url = repo_url.rstrip("/") + "/raw/HEAD/grammar.js"

            output_path = os.path.join(OUTPUT_DIR, f"{language}.js")

            print(f"Downloading grammar.js for {language} ...")

            try:
                urllib.request.urlretrieve(grammar_url, output_path)
                print(f"→ Saved to {output_path}")
            except Exception as e:
                print(f"Failed to download {grammar_url}: {e}")


# Some languages failed when implementing this script, had to download some of them manually
# Failed languages: [
#     "apex", "asciidoc", "asciidoc_inline", "blueprint", "csv", "dtd", "ebnf",
#     "fsharp", "fsharp_signature", "fusion", "gemini", "markdown",
#     "markdown_inline", "ocaml", "ocaml_interface", "ocaml_type",
#     "php", "php_only", "problog", "psv", "smali", "soql", "sosl", "sflog",
#     "superhtml", "tsv", "tsx", "typescript", "v", "ziggy", "ziggy_schema",
#     "wast", "wat", "wing", "xml" 
# ]