"""
Unit tests for non_3rd_party_analysis.py
Tests document classification based on filename patterns and content analysis.
"""
import re
import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.utils.non_code_analysis.non_3rd_party_analysis import (
    classify_document_type,
    extract_contribution_bullets,
    extract_all_skills,
    calculate_completeness_score,
    analyze_project_clean
)


class TestClassifyDocumentType:
    """Essential test suite for document type classification"""
    
    def test_readme_by_filename(self):
        """Test README classification by filename"""
        content = "This is a project overview with installation instructions."
        result = classify_document_type(content, Path("README.md"))
        assert result == "README"
    
    def test_api_documentation_by_content(self):
        """Test API_DOCUMENTATION classification by content (needs 3+ 'api' mentions)"""
        content = """
        # User API
        GET /api/users - Retrieve all users
        POST /api/users - Create user
        The API uses REST principles.
        """
        result = classify_document_type(content, Path("documentation.md"))
        assert result == "API_DOCUMENTATION"
    
    def test_design_document_by_content(self):
        """Test DESIGN_DOCUMENT classification (needs both 'design' and 'architecture')"""
        content = """
        # System Design Document
        
        ## Architecture Overview
        The system uses microservices architecture.
        Components are designed for scalability.
        """
        result = classify_document_type(content, Path("system_doc.md"))
        assert result == "DESIGN_DOCUMENT"
    
    def test_requirements_document_by_content(self):
        """Test REQUIREMENTS_DOCUMENT (needs both 'requirements' and 'specification')"""
        content = """
        # Requirements Specification
        
        ## Functional Requirements
        1. User authentication
        2. Data validation
        """
        result = classify_document_type(content, Path("specs.md"))
        assert result == "REQUIREMENTS_DOCUMENT"
    
    def test_tutorial_by_content(self):
        """Test TUTORIAL classification"""
        content = """
        # Python Tutorial
        This tutorial will guide you through building a web app.
        Follow these step-by-step instructions.
        """
        result = classify_document_type(content, Path("learning.md"))
        assert result == "TUTORIAL"
    
    def test_installation_guide_by_content(self):
        """Test INSTALLATION_GUIDE classification"""
        content = """
        # Installation Guide
        ## Setup Instructions
        1. Install Python 3.8+
        2. Getting started with the application
        """
        result = classify_document_type(content, Path("guide.md"))
        assert result == "INSTALLATION_GUIDE"
    
    def test_meeting_notes_by_filename(self):
        """Test MEETING_NOTES classification by filename"""
        content = "Attendees: John, Jane. Discussion: Project timeline."
        result = classify_document_type(content, Path("meeting_notes.md"))
        assert result == "MEETING_NOTES"
    
    def test_proposal_by_content(self):
        """Test PROPOSAL classification"""
        content = """
        # Project Proposal
        We propose using modern technologies.
        Our strategy is agile development.
        """
        result = classify_document_type(content, Path("project.md"))
        assert result == "PROPOSAL"
    
    def test_filename_overrides_content(self):
        """Test that filename patterns have priority over content"""
        # Content suggests API doc, but filename says README
        content = "API documentation with endpoints. API design guide. API reference."
        result = classify_document_type(content, Path("README.md"))
        assert result == "README"  # Filename wins
 
def test_extract_contribution_bullets_api():
    content = "Developed a RESTful API using FastAPI and PostgreSQL. Implemented JWT authentication for secure endpoints."
    doc_type = "API_DOCUMENTATION"
    metrics = {"word_count": len(content.split()), "heading_count": 1, "code_snippet_count": 0}
    bullets = extract_contribution_bullets(content, doc_type, metrics)
    assert any("Created structured API documentation outlining endpoints and request/response behavior." in b for b in bullets)
    assert any("Fastapi" in b and "Postgresql" in b for b in bullets)
    for b in bullets:
        assert not re.search(r"\s+\d+\s*\.*$", b)

def test_extract_contribution_bullets_proposal():
    content = "Proposed a cloud migration strategy for legacy systems. Designed scalable architecture using AWS services."
    doc_type = "PROPOSAL"
    metrics = {"word_count": len(content.split()), "heading_count": 1, "code_snippet_count": 0}
    bullets = extract_contribution_bullets(content, doc_type, metrics)
    assert any(
        "Developed project proposal outlining objectives, approach, and expected outcomes" in b or
        "Produced organized documentation explaining concepts and implementation details." in b
        for b in bullets
    )
    assert any("AWS" in b for b in bullets)
    for b in bullets:
        assert not re.search(r"\s+\d+\s*\.*$", b)

def test_extract_contribution_bullets_readme():
    content = "This project uses Python and Docker. Setup instructions are provided."
    doc_type = "README"
    metrics = {"word_count": len(content.split()), "heading_count": 1, "code_snippet_count": 0}
    bullets = extract_contribution_bullets(content, doc_type, metrics)
    assert any("Authored a complete README including setup, usage, and project structure." in b for b in bullets)
    assert any("Python" in b and "Docker" in b for b in bullets)
    for b in bullets:
        assert not re.search(r"\s+\d+\s*\.*$", b)

def test_analyze_project_clean_empty_files():
    parsed_files = {"files": []}
    result = analyze_project_clean(parsed_files)
    assert result["summary"].startswith("No files were available")
    assert result["bullets"] == []
    assert result["doc_type_counts"] == {}
    assert result["doc_type_frequency"] == {}
    for skill_list in result["skills"].values():
        assert skill_list == []

def test_analyze_project_clean_no_successful_files():
    parsed_files = {"files": [
        {"success": False, "content": "Some content", "path": "README.md"}
    ]}
    result = analyze_project_clean(parsed_files)
    assert result["summary"].startswith("No successfully parsed content")
    assert result["bullets"] == []
    assert result["doc_type_counts"] == {}
    assert result["doc_type_frequency"] == {}
    for skill_list in result["skills"].values():
        assert skill_list == []

def test_analyze_project_clean_basic_readme():
    parsed_files = {"files": [
        {"success": True, "content": "This is a README for a Python project using FastAPI and Docker.", "path": "README.md", "contribution_frequency": 1}
    ]}
    result = analyze_project_clean(parsed_files)
    assert "README documentation" in result["summary"]
    assert any("Python" in skill for skill in result["skills"]["technical_skills"])
    assert any("Docker" in skill for skill in result["skills"]["technical_skills"])
    assert len(result["bullets"]) > 0
    assert result["doc_type_counts"]["README"] == 1
    assert result["doc_type_frequency"]["README"] == 1
    assert len(result["files_by_doc_type"]) == 1

def test_analyze_project_clean_multiple_files():
    parsed_files = {"files": [
        {"success": True, "content": "API endpoints for user authentication and data analysis.", "path": "api_doc.md", "contribution_frequency": 3},
        {"success": True, "content": "System architecture and microservices design.", "path": "design.md", "contribution_frequency": 5},
        {"success": True, "content": "Requirements: scalability, reliability, performance.", "path": "requirements.txt", "contribution_frequency": 2},
    ]}
    result = analyze_project_clean(parsed_files)
    assert "API documentation" in result["summary"] or "system design" in result["summary"]
    assert "architecture" in result["summary"] or "requirements" in result["summary"]
    assert len(result["bullets"]) > 0
    assert isinstance(result["skills"], dict)
    assert len(result["doc_type_counts"]) > 0
    assert len(result["doc_type_frequency"]) > 0
    assert len(result["files_by_doc_type"]) == 3

def test_completeness_score_design_document():
    # Simulate a design document with key sections
    content = """
    System Architecture: The platform uses a microservice architecture.
    Component Design: Each module is independently deployable.
    Flow Diagram: See attached diagrams for data flow.
    Rationale: Chosen for scalability and maintainability.
    Pattern: Uses the Observer and Factory patterns.
    """
    doc_type = "DESIGN_DOCUMENT"
    score = calculate_completeness_score(content, doc_type)
    # Should be high since all key sections are present
    assert score >= 80

def test_completeness_score_empty_content():
    content = ""
    doc_type = "README"
    score = calculate_completeness_score(content, doc_type)
    assert score == 0

def test_completeness_score_partial_readme():
    content = "Introduction: This project is awesome. Install: Use pip install."
    doc_type = "README"
    score = calculate_completeness_score(content, doc_type)
    # Should be non-zero but less than 100
    assert 0 < score < 100
    
def test_analyze_project_clean_returns_word_count():
    parsed_files = {"files": [
        {
            "success": True,
            "content": "This is a README file with several words for testing.",
            "path": "README.md",
            "contribution_frequency": 1
        }
    ]}

    result = analyze_project_clean(parsed_files)
    expected_word_count = len("This is a README file with several words for testing.".split())

    # TOP-LEVEL word_count, not nested inside metrics
    assert "word_count" in result
    assert result["word_count"] == expected_word_count

def test_analyze_project_clean_contribution_frequency_aggregation():
    """Test that contribution frequency is properly aggregated by document type"""
    parsed_files = {"files": [
        {
            "success": True,
            "content": "This is a README for Python project.",
            "path": "README.md",
            "name": "README.md",
            "contribution_frequency": 3
        },
        {
            "success": True,
            "content": "API endpoints for users. GET /api/users and POST /api/users. API documentation.",
            "path": "api_docs.md",
            "name": "api_docs.md",
            "contribution_frequency": 5
        },
        {
            "success": True,
            "content": "Another README with setup instructions.",
            "path": "docs/README.md",
            "name": "README.md",
            "contribution_frequency": 2
        }
    ]}

    result = analyze_project_clean(parsed_files)
    
    # Test doc_type_counts (number of files per type)
    assert "doc_type_counts" in result
    assert result["doc_type_counts"]["README"] == 2  # Two README files
    assert result["doc_type_counts"]["API_DOCUMENTATION"] == 1  # One API doc
    
    # Test doc_type_frequency (sum of contribution frequencies per type)
    assert "doc_type_frequency" in result
    assert result["doc_type_frequency"]["README"] == 5  # 3 + 2
    assert result["doc_type_frequency"]["API_DOCUMENTATION"] == 5  # 5
    
    # Test files_by_doc_type structure
    assert "files_by_doc_type" in result
    assert len(result["files_by_doc_type"]) == 3
    
    # Verify each file entry has required fields
    for file_entry in result["files_by_doc_type"]:
        assert "file_name" in file_entry
        assert "file_path" in file_entry
        assert "doc_type" in file_entry
        assert "contribution_frequency" in file_entry
    
    # Verify specific file entries
    readme_entries = [f for f in result["files_by_doc_type"] if f["doc_type"] == "README"]
    assert len(readme_entries) == 2
    assert sum(f["contribution_frequency"] for f in readme_entries) == 5
    
    api_entries = [f for f in result["files_by_doc_type"] if f["doc_type"] == "API_DOCUMENTATION"]
    assert len(api_entries) == 1
    assert api_entries[0]["contribution_frequency"] == 5

def test_analyze_project_clean_default_contribution_frequency():
    """Test that files without contribution_frequency default to 1"""
    parsed_files = {"files": [
        {
            "success": True,
            "content": "This is a README without contribution frequency specified.",
            "path": "README.md",
            "name": "README.md"
            # No contribution_frequency field
        }
    ]}

    result = analyze_project_clean(parsed_files)
    
    assert result["doc_type_frequency"]["README"] == 1
    assert result["files_by_doc_type"][0]["contribution_frequency"] == 1
    