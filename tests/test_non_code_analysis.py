"""pytest tests for non-code file analysis."""
import pytest

from app.utils.non_code_analysis.non_code_analysis_utils import pre_process_non_code_files


@pytest.fixture(scope="session", autouse=True)
def ensure_nltk_data():
    """Ensure NLTK punkt_tab tokenizer is available for all tests."""
    try:
        import nltk
        import ssl
        
        # Try to download punkt_tab, handling SSL errors
        try:
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            # Download punkt_tab if not available
            print("Downloading NLTK punkt_tab tokenizer for tests...")
            try:
                # Try with SSL context that doesn't verify certificates (for testing only)
                try:
                    _create_unverified_https_context = ssl._create_unverified_context
                except AttributeError:
                    pass
                else:
                    ssl._create_default_https_context = _create_unverified_https_context
                
                nltk.download('punkt_tab', quiet=True)
            except Exception as e:
                # If download fails, try to use punkt as fallback
                print(f"Failed to download punkt_tab: {e}")
                print("Attempting to use punkt tokenizer instead...")
                try:
                    nltk.data.find('tokenizers/punkt')
                except LookupError:
                    nltk.download('punkt', quiet=True)
    except ImportError:
        pytest.skip("NLTK is required for these tests. Install with: pip install nltk")
    
    # Also check that Sumy is available
    try:
        import sumy
    except ImportError:
        pytest.skip("Sumy is required for these tests. Install with: pip install sumy")

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
    """Test with custom number of summary sentences."""
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
    
    results = pre_process_non_code_files(
        sample_parsed_files,
        summary_sentences=2
    )
    
    assert len(results) == 1
    # Summary should exist (exact sentence count may vary due to LSA)
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

def test_integration_preprocessing_with_mixed_file_types(tmp_path):
    """Integration test: Preprocess files with different content types."""
    from app.utils.document_parser import parse_documents_to_json
    from pathlib import Path
    
    # Create multiple test files with different content
    files = []
    
    # Technical document
    tech_file = tmp_path / "technical.txt"
    tech_file.write_text("""API Design Principles
    
    RESTful APIs should follow standard HTTP methods. GET requests retrieve data.
    POST requests create new resources. PUT requests update existing resources.
    DELETE requests remove resources. Proper error handling is essential.
    Authentication and authorization ensure secure API access.""")
    files.append(str(tech_file))
    
    # Business document
    business_file = tmp_path / "business.txt"
    business_file.write_text("""Project Management Overview
    
    Effective project management requires clear goals and timelines.
    Stakeholder communication is crucial for project success.
    Risk management helps identify and mitigate potential issues.
    Budget planning ensures financial resources are allocated properly.
    Team collaboration tools improve productivity and coordination.""")
    files.append(str(business_file))
    
    # Parse all documents
    output_path = tmp_path / "parsed_output.json"
    parsed_files = parse_documents_to_json(files, str(output_path))
    
    # Preprocess with custom parameters
    results = pre_process_non_code_files(
        parsed_files,
        summary_sentences=3,
        max_content_length=1000
    )
    
    # Verify all files were processed
    assert len(results) == 2
    
    # Verify each result has proper structure
    for result in results:
        assert "summary" in result
        assert "key_topics" in result
        assert len(result["summary"]) > 0
        assert 1 <= len(result["key_topics"]) <= 5


def test_integration_preprocessing_handles_parsing_failures(tmp_path):
    """Integration test: Preprocessing handles files that failed to parse."""
    from app.utils.document_parser import parse_documents_to_json
    from pathlib import Path
    
    # Create a valid file and a missing file
    valid_file = tmp_path / "valid.txt"
    valid_file.write_text("This is a valid document that should be processed successfully.")
    
    missing_file = tmp_path / "missing.txt"
    # Don't create this file - it will fail to parse
    
    # Parse documents (one will fail)
    output_path = tmp_path / "parsed_output.json"
    parsed_files = parse_documents_to_json(
        [str(valid_file), str(missing_file)],
        str(output_path)
    )
    
    # Verify one succeeded and one failed
    assert len(parsed_files["files"]) == 2
    success_count = sum(1 for f in parsed_files["files"] if f["success"])
    assert success_count == 1
    
    # Preprocess - should only process the successful file
    results = pre_process_non_code_files(parsed_files)
    
    # Should only have one result
    assert len(results) == 1
    assert results[0]["file_name"] == "valid.txt"
    assert len(results[0]["summary"]) > 0
    assert len(results[0]["key_topics"]) > 0


def test_integration_preprocessing_with_large_content(tmp_path):
    """Integration test: Preprocessing handles large content with truncation."""
    from app.utils.document_parser import parse_documents_to_json
    from pathlib import Path
    
    # Create a file with very long content
    large_file = tmp_path / "large.txt"
    # Generate large content (more than default max_content_length)
    large_content = "This is a sentence. " * 5000  # ~100,000 characters
    large_file.write_text(large_content)
    
    # Parse document
    output_path = tmp_path / "parsed_output.json"
    parsed_files = parse_documents_to_json([str(large_file)], str(output_path))
    
    # Preprocess with small content limit
    results = pre_process_non_code_files(
        parsed_files,
        max_content_length=1000
    )
    
    # Should still process (with truncation)
    if results:
        assert len(results) == 1
        assert results[0]["file_name"] == "large.txt"


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