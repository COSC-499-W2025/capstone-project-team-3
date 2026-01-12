import pytest
from app.utils.non_code_analysis.keywords.domain_keywords import (
    BASE_DOMAIN_KEYWORDS,
    INDUSTRY_EXPANSIONS,
    JOB_TITLE_KEYWORDS,
    build_enhanced_keywords
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