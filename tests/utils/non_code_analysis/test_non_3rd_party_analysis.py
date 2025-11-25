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

def test_extract_all_skills_basic():
    content = """
    Developed a Python API using FastAPI and Docker.
    Collaborated with team members and documented requirements.
    Designed database schema for PostgreSQL.
    """
    skills = extract_all_skills(content)
    assert "Python" in skills["technical_skills"]
    assert "Docker" in skills["technical_skills"]
    assert "Postgresql" in skills["technical_skills"]
    assert "Collaboration" in skills["soft_skills"]
    assert "Database Design" in skills["soft_skills"]
    assert "Database Management" in skills["domain_expertise"]
    assert any(
    skill in skills["writing_skills"]
    for skill in ["Technical Documentation", "Specification Writing"]
)

def test_analyze_project_clean_empty_files():
    parsed_files = {"files": []}
    result = analyze_project_clean(parsed_files)
    assert result["summary"].startswith("No files were available")
    assert result["bullets"] == []
    for skill_list in result["skills"].values():
        assert skill_list == []

def test_analyze_project_clean_no_successful_files():
    parsed_files = {"files": [
        {"success": False, "content": "Some content", "path": "README.md"}
    ]}
    result = analyze_project_clean(parsed_files)
    assert result["summary"].startswith("No successfully parsed content")
    assert result["bullets"] == []
    for skill_list in result["skills"].values():
        assert skill_list == []

def test_analyze_project_clean_basic_readme():
    parsed_files = {"files": [
        {"success": True, "content": "This is a README for a Python project using FastAPI and Docker.", "path": "README.md"}
    ]}
    result = analyze_project_clean(parsed_files)
    assert "README documentation" in result["summary"]
    assert any("Python" in skill for skill in result["skills"]["technical_skills"])
    assert any("Docker" in skill for skill in result["skills"]["technical_skills"])
    assert len(result["bullets"]) > 0

def test_analyze_project_clean_multiple_files():
    parsed_files = {"files": [
        {"success": True, "content": "API endpoints for user authentication and data analysis.", "path": "api_doc.md"},
        {"success": True, "content": "System architecture and microservices design.", "path": "design.md"},
        {"success": True, "content": "Requirements: scalability, reliability, performance.", "path": "requirements.txt"},
    ]}
    result = analyze_project_clean(parsed_files)
    assert "API documentation" in result["summary"] or "system design" in result["summary"]
    assert "architecture" in result["summary"] or "requirements" in result["summary"]
    assert len(result["bullets"]) > 0
    assert isinstance(result["skills"], dict)
