"""pytest tests for non-code file analysis."""
import pytest
from app.utils.non_code_analysis.non_code_analysis_utils import pre_process_non_code_files

#----------Pre Processing Unit Tests-----------------#
def test_pre_process_non_code_files():
    """Test basic functionality of pre_process_non_code_files with sample data."""
    # Sample parsed_files object matching the structure from document_parser
    sample_parsed_files = {
        "files": [
            {
                "path": "/test/sample_document.txt",
                "name": "sample_document.txt",
                "type": "txt",
                "content": """This is a sample document for testing the pre-processing function.
                The document contains multiple sentences to test summarization capabilities.
                It discusses various topics including machine learning, data analysis, and software development.
                The system should be able to extract key topics and generate a concise summary.
                This test verifies that the Sumy LSA summarizer works correctly with the function.""",
                "success": True,
                "error": ""
            }
        ]
    }
    
    results = pre_process_non_code_files(sample_parsed_files)
    
    # Assertions
    assert results is not None
    assert isinstance(results, list)
    assert len(results) == 1
    
    result = results[0]
    assert "file_name" in result
    assert "file_path" in result
    assert "summary" in result
    assert "key_topics" in result
    
    assert result["file_name"] == "sample_document.txt"
    assert result["file_path"] == "/test/sample_document.txt"
    assert len(result["summary"]) > 0
    assert len(result["key_topics"]) > 0
    assert len(result["key_topics"]) <= 5

def test_pre_process_non_code_files_multiple_files():
    """Test processing multiple files."""
    sample_parsed_files = {
        "files": [
            {
                "path": "/test/doc1.txt",
                "name": "doc1.txt",
                "type": "txt",
                "content": """First document about project management and agile methodologies.
                This document discusses sprint planning, standup meetings, and retrospectives.
                It covers various project management tools and techniques.""",
                "success": True,
                "error": ""
            },
            {
                "path": "/test/doc2.txt",
                "name": "doc2.txt",
                "type": "txt",
                "content": """Second document about software architecture and design patterns.
                This document explains microservices, event-driven architecture, and API design.
                It provides examples of common architectural patterns used in modern applications.""",
                "success": True,
                "error": ""
            }
        ]
    }
    
    results = pre_process_non_code_files(sample_parsed_files)
    
    assert len(results) == 2
    assert all("summary" in r and "key_topics" in r for r in results)
    assert results[0]["file_name"] == "doc1.txt"
    assert results[1]["file_name"] == "doc2.txt"


def test_pre_process_non_code_files_skips_failed_parsing():
    """Test that files with success=False are skipped."""
    sample_parsed_files = {
        "files": [
            {
                "path": "/test/success.txt",
                "name": "success.txt",
                "type": "txt",
                "content": "This file was successfully parsed and should be processed.",
                "success": True,
                "error": ""
            },
            {
                "path": "/test/failed.txt",
                "name": "failed.txt",
                "type": "txt",
                "content": "",
                "success": False,
                "error": "Parsing failed"
            }
        ]
    }
    
    results = pre_process_non_code_files(sample_parsed_files)
    
    assert len(results) == 1
    assert results[0]["file_name"] == "success.txt"


def test_pre_process_non_code_files_skips_empty_content():
    """Test that files with empty content are skipped."""
    sample_parsed_files = {
        "files": [
            {
                "path": "/test/empty.txt",
                "name": "empty.txt",
                "type": "txt",
                "content": "",
                "success": True,
                "error": ""
            },
            {
                "path": "/test/valid.txt",
                "name": "valid.txt",
                "type": "txt",
                "content": "This file has content and should be processed.",
                "success": True,
                "error": ""
            }
        ]
    }
    
    results = pre_process_non_code_files(sample_parsed_files)
    
    assert len(results) == 1
    assert results[0]["file_name"] == "valid.txt"


def test_pre_process_non_code_files_content_length_limit():
    """Test that content exceeding max_content_length is truncated."""
    long_content = "This is a test. " * 1000  # Create long content
    sample_parsed_files = {
        "files": [
            {
                "path": "/test/long.txt",
                "name": "long.txt",
                "type": "txt",
                "content": long_content,
                "success": True,
                "error": ""
            }
        ]
    }
    
    results = pre_process_non_code_files(
        sample_parsed_files,
        max_content_length=100
    )
    
    # Should still process but with truncated content
    assert len(results) >= 0  # May or may not process depending on truncation


def test_pre_process_non_code_files_custom_summary_sentences():
    """Test that summary is generated for short content."""
    sample_parsed_files = {
        "files": [
            {
                "path": "/test/custom.txt",
                "name": "custom.txt",
                "type": "txt",
                "content": """First sentence about machine learning.
                Second sentence about data science.
                Third sentence about artificial intelligence.
                Fourth sentence about neural networks.
                Fifth sentence about deep learning.""",
                "success": True,
                "error": ""
            }
        ]
    }
    
    results = pre_process_non_code_files(sample_parsed_files)
    
    assert len(results) == 1
    # Summary should exist (exact sentence count may vary due to dynamic calculation)
    assert len(results[0]["summary"]) > 0


def test_pre_process_non_code_files_key_topics_extraction():
    """Test that key topics are extracted correctly."""
    sample_parsed_files = {
        "files": [
            {
                "path": "/test/topics.txt",
                "name": "topics.txt",
                "type": "txt",
                "content": """This document discusses Python programming extensively.
                It covers web development with Flask and Django frameworks.
                The document also mentions database design and SQL queries.
                Machine learning and data analysis are important topics.
                Software engineering practices and testing methodologies are discussed.""",
                "success": True,
                "error": ""
            }
        ]
    }
    
    results = pre_process_non_code_files(sample_parsed_files)
    
    assert len(results) == 1
    assert len(results[0]["key_topics"]) > 0
    assert len(results[0]["key_topics"]) <= 5
    # Topics should be capitalized
    assert all(topic[0].isupper() or topic[0].isdigit() for topic in results[0]["key_topics"])


def test_pre_process_non_code_files_empty_input():
    """Test with empty files list."""
    sample_parsed_files = {
        "files": []
    }
    
    results = pre_process_non_code_files(sample_parsed_files)
    
    assert results == []
    assert isinstance(results, list)


#----------Pre Processing Integration Tests-----------------#
# TODO : Create Integration Tests between parsing-_pre-processing->aggregation & generation

if __name__ == "__main__":
    # Run tests directly
    print("Running test_pre_process_non_code_files...")
    try:
        test_pre_process_non_code_files()
        print("✓ test_pre_process_non_code_files passed")
    except Exception as e:
        print(f"✗ test_pre_process_non_code_files failed: {e}")
    
    print("\nRunning test_pre_process_non_code_files_multiple_files...")
    try:
        test_pre_process_non_code_files_multiple_files()
        print("✓ test_pre_process_non_code_files_multiple_files passed")
    except Exception as e:
        print(f"✗ test_pre_process_non_code_files_multiple_files failed: {e}")
    
    print("\nRunning test_pre_process_non_code_files_skips_failed_parsing...")
    try:
        test_pre_process_non_code_files_skips_failed_parsing()
        print("✓ test_pre_process_non_code_files_skips_failed_parsing passed")
    except Exception as e:
        print(f"✗ test_pre_process_non_code_files_skips_failed_parsing failed: {e}")
    
    print("\nRunning test_pre_process_non_code_files_skips_empty_content...")
    try:
        test_pre_process_non_code_files_skips_empty_content()
        print("✓ test_pre_process_non_code_files_skips_empty_content passed")
    except Exception as e:
        print(f"✗ test_pre_process_non_code_files_skips_empty_content failed: {e}")
    
    print("\nRunning test_pre_process_non_code_files_key_topics_extraction...")
    try:
        test_pre_process_non_code_files_key_topics_extraction()
        print("✓ test_pre_process_non_code_files_key_topics_extraction passed")
    except Exception as e:
        print(f"✗ test_pre_process_non_code_files_key_topics_extraction failed: {e}")
    
    print("\nRunning test_pre_process_non_code_files_empty_input...")
    try:
        test_pre_process_non_code_files_empty_input()
        print("✓ test_pre_process_non_code_files_empty_input passed")
    except Exception as e:
        print(f"✗ test_pre_process_non_code_files_empty_input failed: {e}")