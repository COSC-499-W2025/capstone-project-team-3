"""pytest tests for non-code file analysis."""
import pytest
from app.utils.non_code_analysis.non_code_analysis_utils import (
    pre_process_non_code_files,
    aggregate_non_code_summaries,
    get_file_type_distribution,
    get_project_name,
    get_total_files,
    get_file_names,
    get_readability_metrics,
    get_unique_key_topics,
    get_named_entities,
    create_non_code_analysis_prompt
)

# ---------- Pre-Processing Unit Tests ----------------- #
def test_pre_process_non_code_files():
    """Test basic functionality of pre_process_non_code_files with sample data."""
    sample_parsed_files = {
        "files": [
            {
                "path": "/test/sample_document.txt",
                "name": "sample_document.txt",
                "type": "txt",
                "content": "This is a sample document for testing.",
                "success": True,
                "error": "",
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


# ---------- Aggregation Unit Tests ----------------- #
def test_aggregate_non_code_summaries():
    """Test aggregation of pre-processed summaries into project metrics."""
    llm1_results = [
        {
            "file_name": "file1.pdf",
            "file_path": "/test/file1.pdf",
            "file_type": "pdf",
            "word_count": 100,
            "sentence_count": 10,
            "readability_score": 12.5,
            "summary": "This is a summary of file1.",
            "key_topics": ["Topic1", "Topic2"],
        },
        {
            "file_name": "file2.txt",
            "file_path": "/test/file2.txt",
            "file_type": "txt",
            "word_count": 200,
            "sentence_count": 20,
            "readability_score": 10.0,
            "summary": "This is a summary of file2.",
            "key_topics": ["Topic3", "Topic4"],
        },
    ]

    project_metrics = aggregate_non_code_summaries(llm1_results)

    # Assertions
    assert project_metrics is not None
    assert project_metrics["Project_Name"] == "test"
    assert project_metrics["totalFiles"] == 2
    assert project_metrics["fileNames"] == ["file1.pdf", "file2.txt"]
    assert project_metrics["averageReadabilityScore"] == pytest.approx(11.25, 0.1)
    assert set(project_metrics["uniqueKeyTopics"]) == {"Topic1", "Topic2", "Topic3", "Topic4"}
    assert project_metrics["fileTypeDistribution"] == {"pdf": 1, "txt": 1}
    assert "files" in project_metrics
    assert len(project_metrics["files"]) == 2

# ------------ PROMPT Generation Tests ----------------- #
def test_generate_prompt_structure():
    """Test prompt structure generation from aggregated metrics."""
    aggregated_metrics = {
        "Project_Name": "test_project",
        "totalFiles": 2,
        "fileTypeDistribution": {"pdf": 1, "txt": 1},
        "fileNames": ["file1.pdf", "file2.txt"],
        "averageReadabilityScore": 11.25,
        "uniqueKeyTopics": ["Topic1", "Topic2", "Topic3", "Topic4"],
        "namedEntities": ["LLM2", "2025"],
        "files": [
            {
                "file_name": "file1.pdf",
                "file_path": "/test/file1.pdf",
                "file_type": "pdf",
                "word_count": 100,
                "sentence_count": 10,
                "readability_score": 12.5,
                "summary": "This is a summary of file1.",
                "key_topics": ["Topic1", "Topic2"],
            },
            {
                "file_name": "file2.txt",
                "file_path": "/test/file2.txt",
                "file_type": "txt",
                "word_count": 200,
                "sentence_count": 20,
                "readability_score": 10.0,
                "summary": "This is a summary of file2.",
                "key_topics": ["Topic3", "Topic4"],
            },
        ],
    }

    prompt = create_non_code_analysis_prompt(aggregated_metrics)

    # Assertions
    assert prompt is not None
    assert isinstance(prompt, str)
    assert "Project Name: test_project" in prompt
    assert "Total Files: 2" in prompt
    assert "File Type Distribution:" in prompt
    assert "Average Readability Score:" in prompt
    assert "Unique Key Topics:" in prompt
    assert "Named Entities:" in prompt


def test_get_file_type_distribution():
    """Test file type distribution calculation."""
    llm1_results = [
        {"file_type": "pdf"},
        {"file_type": "txt"},
        {"file_type": "pdf"},
    ]

    distribution = get_file_type_distribution(llm1_results)

    # Assertions
    assert distribution == {"pdf": 2, "txt": 1}


def test_get_project_name():
    """Test project name extraction."""
    llm1_results = [
        {"file_path": "/test/project/file1.pdf"},
        {"file_path": "/test/project/file2.txt"},
    ]

    project_name = get_project_name(llm1_results)

    # Assertions
    assert project_name == "project"


def test_get_total_files():
    """Test total file count."""
    llm1_results = [
        {"file_name": "file1.pdf"},
        {"file_name": "file2.txt"},
    ]

    total_files = get_total_files(llm1_results)

    # Assertions
    assert total_files == 2


def test_get_file_names():
    """Test file name extraction."""
    llm1_results = [
        {"file_name": "file1.pdf"},
        {"file_name": "file2.txt"},
    ]

    file_names = get_file_names(llm1_results)

    # Assertions
    assert file_names == ["file1.pdf", "file2.txt"]


def test_get_readability_metrics():
    """Test average readability score calculation."""
    llm1_results = [
        {"readability_score": 12.5},
        {"readability_score": 10.0},
    ]

    avg_readability = get_readability_metrics(llm1_results)

    # Assertions
    assert avg_readability == pytest.approx(11.25, 0.1)


def test_get_unique_key_topics():
    """Test unique key topics extraction."""
    llm1_results = [
        {"key_topics": ["Topic1", "Topic2"]},
        {"key_topics": ["Topic2", "Topic3"]},
    ]

    unique_topics = get_unique_key_topics(llm1_results)

    # Assertions
    assert set(unique_topics) == {"Topic1", "Topic2", "Topic3"}


def test_get_named_entities():
    """Test named entity extraction."""
    llm1_results = [
        {"summary": "Team 3 is working on a project with LLM2 in 2025."},
        {"summary": "The project involves AI and machine learning."},
    ]

    named_entities = get_named_entities(llm1_results)

    # Assertions

    assert "LLM2" in named_entities
    assert "2025" in named_entities


# ---------- Integration Tests ----------------- #
def test_pipeline_integration():
    """Test the full pipeline from pre-processing to aggregation."""
    sample_parsed_files = {
        "files": [
            {
                "path": "/test/sample_document.txt",
                "name": "sample_document.txt",
                "type": "txt",
                "content": "This is a sample document for testing.",
                "success": True,
                "error": "",
            }
        ]
    }

    # Run pipeline
    llm1_results = pre_process_non_code_files(sample_parsed_files)
    project_metrics = aggregate_non_code_summaries(llm1_results)

    # Assertions
    assert project_metrics is not None
    assert project_metrics["totalFiles"] == 1
    assert project_metrics["fileTypeDistribution"] == {"txt": 1}


# ---------- Run Tests Directly ----------------- #
if __name__ == "__main__":
    pytest.main()