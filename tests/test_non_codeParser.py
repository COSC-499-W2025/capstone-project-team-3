#!/usr/bin/env python3
"""
Simple test for document parser.
"""
import json
import tempfile
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.utils.document_parser import parse_documents_to_json

def test():
    """Simple test."""
    # Create temp dir
    temp_dir = Path(tempfile.mkdtemp())

    # Create test file
    test_file = temp_dir / "test.txt"
    test_file.write_text("Hello world")

    # Parse
    output = temp_dir / "output.json"
    parse_documents_to_json([str(test_file)], str(output))

    # Check result
    with open(output) as f:
        data = json.load(f)

    # Verify
    assert len(data["files"]) == 1
    file_data = data["files"][0]
    assert file_data["success"] == True
    assert file_data["content"] == "Hello world"
    assert file_data["type"] == "txt"

    print("✅ Test passed!")

if __name__ == "__main__":
    test()
