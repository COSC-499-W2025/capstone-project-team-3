import pytest
from app.utils.non_code_analysis.keywords.domain_keywords import (
    BASE_DOMAIN_KEYWORDS,
    INDUSTRY_EXPANSIONS,
    JOB_TITLE_KEYWORDS,
    build_enhanced_keywords,
    get_job_context
)


class TestBuildEnhancedKeywords:
    """Test the build_enhanced_keywords function with user preferences."""
    
    def test_no_preferences_returns_base_keywords(self):
        """Test that with no preferences, only base keywords are returned."""
        result = build_enhanced_keywords(None, None)
        assert len(result) == len(BASE_DOMAIN_KEYWORDS)
        for domain in BASE_DOMAIN_KEYWORDS:
            assert domain in result
            
    def test_industry_and_job_title_adds_keywords(self):
        """Test that providing both industry and job title adds all relevant keywords."""
        result = build_enhanced_keywords("Software Engineering", "Software Engineer")
        se_keywords = result["Software Engineering"]
        
        base_count = len(BASE_DOMAIN_KEYWORDS["Software Engineering"])
        expansion_count = len(INDUSTRY_EXPANSIONS["Software Engineering"])
        job_count = len(JOB_TITLE_KEYWORDS["software engineer"])
        assert len(se_keywords) == base_count + expansion_count + job_count
        
        assert "software" in se_keywords  
        assert "ci/cd" in se_keywords  
        assert "debugging" in se_keywords  
        
    def test_case_insensitive_job_title_matching(self):
        """Test that job title matching works regardless of case."""
        result1 = build_enhanced_keywords(None, "Software Engineer")
        result2 = build_enhanced_keywords(None, "software engineer")
        result3 = build_enhanced_keywords(None, "Senior Software Engineer")
        
        assert "debugging" in result1["Software Engineering"]
        assert "debugging" in result2["Software Engineering"]
        assert "debugging" in result3["Software Engineering"]
        
    def test_invalid_inputs_dont_break(self):
        """Test that invalid industry/job title don't cause errors."""
        result = build_enhanced_keywords("Invalid Industry", "Invalid Job")
        assert len(result) == len(BASE_DOMAIN_KEYWORDS)
        assert "software" in result["Software Engineering"]


class TestGetJobContext:
    """Test the get_job_context function."""
    
    def test_returns_context_for_valid_jobs(self):
        """Test that valid job titles return appropriate context strings."""
        se_context = get_job_context("Software Engineer")
        assert se_context is not None
        assert isinstance(se_context, str)
        assert "development" in se_context.lower() or "implementation" in se_context.lower()
        
        ds_context = get_job_context("Data Scientist")
        assert ds_context is not None
        assert "analytics" in ds_context.lower() or "modeling" in ds_context.lower()
        
    def test_returns_none_for_invalid_inputs(self):
        """Test that invalid/empty inputs return None."""
        assert get_job_context(None) is None
        assert get_job_context("") is None
        assert get_job_context("Invalid Job Title") is None
        
    def test_case_insensitive_partial_matching(self):
        """Test that partial and case-insensitive matching works."""
        context1 = get_job_context("Software Engineer")
        context2 = get_job_context("software engineer")
        context3 = get_job_context("Senior Software Engineer")
        
        assert context1 == context2
        assert context1 == context3 