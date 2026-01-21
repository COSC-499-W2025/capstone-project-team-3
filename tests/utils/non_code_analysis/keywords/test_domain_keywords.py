import pytest
from app.utils.non_code_analysis.keywords.domain_keywords import (
    BASE_DOMAIN_KEYWORDS,
    INDUSTRY_EXPANSIONS,
    JOB_TITLE_KEYWORDS,
    CLI_INDUSTRY_TO_DOMAIN,
    build_enhanced_keywords,
    get_mapped_industry
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


class TestGetMappedIndustry:
    """Test the get_mapped_industry function that maps CLI industries to domains."""
    
    def test_technology_maps_to_software_engineering(self):
        """Test that 'Technology' CLI industry maps to 'Software Engineering' domain."""
        assert get_mapped_industry("Technology") == "Software Engineering"
    
    def test_finance_maps_to_business(self):
        """Test that 'Finance' CLI industry maps to 'Business' domain."""
        assert get_mapped_industry("Finance") == "Business"
    
    def test_healthcare_maps_to_healthcare(self):
        """Test that 'Healthcare' CLI industry maps to 'Healthcare' domain."""
        assert get_mapped_industry("Healthcare") == "Healthcare"
    
    def test_unmapped_industry_returns_original(self):
        """Test that unmapped industries return the original value."""
        assert get_mapped_industry("Custom Industry") == "Custom Industry"
    
    def test_none_industry_returns_none(self):
        """Test that None industry returns None."""
        assert get_mapped_industry(None) == None


class TestCLIIndustryIntegration:
    """Test that CLI industry names work correctly with build_enhanced_keywords."""
    
    def test_technology_industry_expands_software_engineering_keywords(self):
        """Test that CLI 'Technology' industry expands Software Engineering keywords."""
        result = build_enhanced_keywords("Technology", None)
        se_keywords = result["Software Engineering"]
        
        # Should have base + expansion keywords
        base_count = len(BASE_DOMAIN_KEYWORDS["Software Engineering"])
        expansion_count = len(INDUSTRY_EXPANSIONS["Software Engineering"])
        assert len(se_keywords) == base_count + expansion_count
        
        # Check for both base and expansion keywords
        assert "software" in se_keywords  # base keyword
        assert "ci/cd" in se_keywords  # expansion keyword
    
    def test_technology_with_senior_engineer_combines_all(self):
        """Test that CLI 'Technology' + 'Senior Software Engineer' combines all keyword sets."""
        result = build_enhanced_keywords("Technology", "Senior Software Engineer")
        se_keywords = result["Software Engineering"]
        
        # Should have base + expansion + job title keywords
        base_count = len(BASE_DOMAIN_KEYWORDS["Software Engineering"])
        expansion_count = len(INDUSTRY_EXPANSIONS["Software Engineering"])
        job_count = len(JOB_TITLE_KEYWORDS["software engineer"])
        assert len(se_keywords) == base_count + expansion_count + job_count
        
        # Check for all three types
        assert "software" in se_keywords  # base
        assert "ci/cd" in se_keywords  # industry expansion
        assert "debugging" in se_keywords  # job title
    
    def test_all_cli_industries_map_correctly(self):
        """Test that all CLI industries in the mapping work correctly."""
        cli_industries = [
            ("Technology", "Software Engineering"),
            ("Finance", "Business"),
            ("Healthcare", "Healthcare"),
            ("Education", "Education"),
            ("Research", "Research"),
        ]
        
        for cli_industry, expected_domain in cli_industries:
            result = build_enhanced_keywords(cli_industry, None)
            assert expected_domain in result
            # Should have expanded keywords
            assert len(result[expected_domain]) > len(BASE_DOMAIN_KEYWORDS[expected_domain]) 