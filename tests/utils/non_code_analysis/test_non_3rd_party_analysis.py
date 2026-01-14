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

def test_analyze_project_clean_no_successful_files():
    """Test with files that failed to parse."""
    parsed_files = {
        "parsed_files": [
            {"name": "file1.txt", "success": False, "error": "Parse error"},
            {"name": "file2.md", "success": False, "error": "Access denied"}
        ]
    }
    
    result = analyze_project_clean(parsed_files)
    
    assert "project_summary" in result
    assert result["project_summary"] == "No successfully parsed content was available for analysis."
    assert result["resume_bullets"] == []



def test_analyze_project_clean_basic_readme():
    """Test with single README file."""
    parsed_files = {
        "parsed_files": [
            {
                "name": "README.md",
                "path": "/project/README.md",
                "content": "# My Project\n\nThis is a test project.",
                "success": True,
                "contribution_frequency": 1
            }
        ]
    }
    
    result = analyze_project_clean(parsed_files)
    
    assert "project_summary" in result  # Changed
    assert "resume_bullets" in result   # Changed
    assert "skills" in result
    assert "Metrics" in result          # Changed
    assert isinstance(result["project_summary"], str)
    assert len(result["project_summary"]) > 0
    assert isinstance(result["resume_bullets"], list)



def test_analyze_project_clean_multiple_files():
    """Test with multiple documentation files."""
    parsed_files = {
        "parsed_files": [
            {
                "name": "README.md",
                "path": "/project/README.md",
                "content": "# Project Overview\n\nThis project does X, Y, Z.",
                "success": True,
                "contribution_frequency": 5
            },
            {
                "name": "DESIGN.md",
                "path": "/project/DESIGN.md",
                "content": "## Architecture\n\nWe use microservices with Docker.",
                "success": True,
                "contribution_frequency": 10
            }
        ]
    }
    
    result = analyze_project_clean(parsed_files)
    
    assert "project_summary" in result
    assert "resume_bullets" in result
    assert len(result["resume_bullets"]) > 0
    assert result["Metrics"]["word_count"] > 0
    assert "contribution_activity" in result["Metrics"]


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
    """Test that word count is calculated."""
    parsed_files = {
        "parsed_files": [
            {
                "name": "doc.txt",
                "path": "/project/doc.txt",
                "content": "one two three four five",
                "success": True
            }
        ]
    }
    
    result = analyze_project_clean(parsed_files)
    
    assert "Metrics" in result                    # Changed
    assert "word_count" in result["Metrics"]      # Changed
    assert result["Metrics"]["word_count"] == 5   # Changed


def test_analyze_project_clean_contribution_frequency_aggregation():
    """Test aggregation of contribution frequencies by document type."""
    parsed_files = {
        "parsed_files": [
            {
                "name": "README.md",
                "path": "/project/README.md",
                "content": "# README\n\nProject overview goes here.",
                "success": True,
                "contribution_frequency": 5
            },
            {
                "name": "DESIGN.md",
                "path": "/project/DESIGN.md",
                "content": "## System Design\n\nArchitecture description.",
                "success": True,
                "contribution_frequency": 10
            },
            {
                "name": "API.md",
                "path": "/project/docs/API.md",
                "content": "## API Documentation\n\nEndpoint list.",
                "success": True,
                "contribution_frequency": 3
            }
        ]
    }
    
    result = analyze_project_clean(parsed_files)
    
    # Check structure
    assert "Metrics" in result
    assert "contribution_activity" in result["Metrics"]
    assert "doc_type_counts" in result["Metrics"]["contribution_activity"]
    assert "doc_type_frequency" in result["Metrics"]["contribution_activity"]
    
    # Check values
    doc_counts = result["Metrics"]["contribution_activity"]["doc_type_counts"]
    doc_freq = result["Metrics"]["contribution_activity"]["doc_type_frequency"]
    
    assert "README" in doc_counts
    assert doc_counts["README"] == 1
    assert doc_freq["README"] == 5
    
    # Total of all frequencies
    total_freq = sum(doc_freq.values())
    assert total_freq == 18  # 5 + 10 + 3


def test_analyze_project_clean_default_contribution_frequency():
    """Test that contribution_frequency defaults to 1 if missing."""
    parsed_files = {
        "parsed_files": [
            {
                "name": "doc.txt",
                "path": "/project/doc.txt",
                "content": "Some content here.",
                "success": True
                # No contribution_frequency field
            }
        ]
    }
    
    result = analyze_project_clean(parsed_files)
    
    # Should have doc_type_frequency with value of 1
    doc_freq = result["Metrics"]["contribution_activity"]["doc_type_frequency"]
    assert sum(doc_freq.values()) >= 1
    
# Add this test at the end of the file

def test_analyze_project_clean_with_user_preferences_enhances_summary():
    """Test that user preferences enhance project summary with industry alignment."""
    from app.cli.user_preference_cli import UserPreferences
    
    # Create test user with Technology industry
    pref_manager = UserPreferences()
    try:
        pref_manager.store.save_preferences(
            name="Test User",
            email="test_enhanced@example.com",
            github_user="testuser",
            education="BS CS",
            industry="Technology",
            job_title="Software Engineer"
        )
        
        # Sample content with software engineering keywords
        parsed_files = {
            "parsed_files": [{
                "name": "README.md",
                "path": "/README.md",
                "content": "Software development project with architecture design using Docker and CI/CD.",
                "success": True
            }]
        }
        
        result = analyze_project_clean(parsed_files, email="test_enhanced@example.com")
        
        # Should mention alignment with Technology background
        assert "Technology background" in result["project_summary"]
        assert "Software Engineering" in result["project_summary"]
    finally:
        pref_manager.store.close()


def test_analyze_project_clean_with_senior_role_enhances_bullets():
    """Test that senior job titles get leadership language in resume bullets."""
    from app.cli.user_preference_cli import UserPreferences
    
    pref_manager = UserPreferences()
    try:
        pref_manager.store.save_preferences(
            name="Senior Dev",
            email="senior@example.com",
            github_user="seniordev",
            education="MS CS",
            industry="Technology",
            job_title="Senior Software Engineer"
        )
        
        parsed_files = {
            "parsed_files": [{
                "name": "DESIGN.md",
                "path": "/DESIGN.md",
                "content": "System architecture and design document with requirements specification.",
                "success": True
            }]
        }
        
        result = analyze_project_clean(parsed_files, email="senior@example.com")
        
        # Senior role should get "Led" instead of "Designed"
        bullets_text = " ".join(result["resume_bullets"])
        assert "Led" in bullets_text or "Analyzed and specified comprehensive" in bullets_text
    finally:
        pref_manager.store.close()


def test_analyze_project_clean_without_email_works():
    """Test that function works without email (backward compatibility)."""
    parsed_files = {
        "parsed_files": [{
            "name": "README.md",
            "path": "/README.md",
            "content": "Basic project with software development.",
            "success": True
        }]
    }
    
    # Should work without email parameter
    result = analyze_project_clean(parsed_files, email=None)
    
    assert "project_summary" in result
    assert "resume_bullets" in result
    # Should NOT mention user preferences or background
    assert "background" not in result["project_summary"]
