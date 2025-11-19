"""
Unit tests for non_3rd_party_analysis.py
Tests document classification based on filename patterns and content analysis.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.utils.non_code_analysis.non_3rd_party_analysis import (
    classify_document_type
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
    
    def test_general_documentation_fallback(self):
        """Test GENERAL_DOCUMENTATION as fallback for unmatched content"""
        content = "Some random notes about various topics."
        result = classify_document_type(content, Path("notes.txt"))
        assert result == "GENERAL_DOCUMENTATION"


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"]) 