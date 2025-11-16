import os
from dotenv import load_dotenv
from app.client.llm_client import GeminiLLMClient
from app.utils.code_analysis.code_analysis_utils import (
    analyze_parsed_project, infer_roles_from_file,
    extract_technical_keywords_from_parsed,
    analyze_code_patterns_from_parsed,
    calculate_advanced_complexity_from_parsed, aggregate_parsed_files_metrics, generate_resume_summary_from_parsed
)
# Import test data from fixtures
from tests.fixtures.test_data import (
    design_pattern_files,
    complex_parsed_files,
    multi_framework_files,
    role_inference_test_files
)
import logging

# Configure professional logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    force=True
)
logger = logging.getLogger(__name__)

def print_section(title, content=None, separator="="):
    """Print a professional section header"""
    print(f"\n{separator * 80}")
    print(f"📊 {title}")
    print(f"{separator * 80}")
    if content:
        if isinstance(content, list):
            for i, item in enumerate(content, 1):
                print(f"  {i}. {item}")
        elif isinstance(content, dict):
            for key, value in content.items():
                print(f"  {key}: {value}")
        else:
            print(f"  {content}")
    print()

def print_subsection(title, content=None):
    """Print a subsection with clean formatting"""
    print(f"\n📋 {title}")
    print("-" * 60)
    if content:
        if isinstance(content, list):
            for item in content:
                print(f"  ✓ {item}")
        elif isinstance(content, dict):
            for key, value in content.items():
                if isinstance(value, list) and value:
                    print(f"  {key}: {', '.join(map(str, value))}")
                else:
                    print(f"  {key}: {value}")
        else:
            print(f"  {content}")


# --- Enhanced Tests with Professional Output ---

def test_enhanced_design_pattern_detection():
    """Test comprehensive design pattern detection with all new patterns"""
    print_section("🎯 ENHANCED DESIGN PATTERN DETECTION")
    
    patterns = analyze_code_patterns_from_parsed(design_pattern_files)
    
    print_subsection("Detected Design Patterns", patterns["design_patterns"])
    print_subsection("Detected Frameworks", patterns["frameworks_detected"]) 
    print_subsection("Architectural Patterns", patterns["architectural_patterns"])
    print_subsection("Development Practices", patterns["development_practices"])
    print_subsection("Technology Stack", patterns["technology_stack"])
    
    # Assertions for new patterns
    assert "Factory Pattern" in patterns["design_patterns"]
    assert "Observer Pattern" in patterns["design_patterns"] 
    assert "Strategy Pattern" in patterns["design_patterns"]
    assert "Singleton Pattern" in patterns["design_patterns"]
    
    # Architectural patterns
    assert "MVC Architecture" in patterns["architectural_patterns"]
    assert "Service-Oriented Architecture" in patterns["architectural_patterns"]
    assert "Microservices Architecture" in patterns["architectural_patterns"]
    assert "RESTful API Architecture" in patterns["architectural_patterns"]
    assert "Event-Driven Architecture" in patterns["architectural_patterns"]
    assert "Layered Architecture" in patterns["architectural_patterns"]


def test_comprehensive_technical_keyword_extraction():
    """Test expanded technical keyword extraction"""
    print_section("🔍 TECHNICAL KEYWORD EXTRACTION")
    
    # Test parsed files
    keywords_parsed = extract_technical_keywords_from_parsed(design_pattern_files)
    print_subsection("Keywords from Parsed Files", keywords_parsed[:10])
    
    assert len(keywords_parsed) > 0

def test_advanced_complexity_analysis():
    """Test advanced complexity calculation with detailed metrics"""
    print_section("📈 ADVANCED COMPLEXITY ANALYSIS")
    
    complexity = calculate_advanced_complexity_from_parsed(design_pattern_files)
    
    print_subsection("Function Complexity Scores", complexity["function_complexity"][:5])
    print_subsection("Component Complexity Scores", complexity["component_complexity"])
    print_subsection("Maintainability Factors", complexity["maintainability_factors"])
    
    assert len(complexity["function_complexity"]) > 0
    assert "average_function_complexity" in complexity["maintainability_factors"]
    assert "functions_per_file" in complexity["maintainability_factors"]

def test_enhanced_resume_generation_local():
    """Test enhanced resume generation for local projects"""
    print_section("📝 ENHANCED LOCAL PROJECT RESUME")
    
    metrics = aggregate_parsed_files_metrics(design_pattern_files)
    metrics["technical_keywords"] = extract_technical_keywords_from_parsed(design_pattern_files)
    metrics["code_patterns"] = analyze_code_patterns_from_parsed(design_pattern_files)
    metrics["complexity_analysis"] = calculate_advanced_complexity_from_parsed(design_pattern_files)
    
    summary = generate_resume_summary_from_parsed(metrics)
    
    print_subsection("Professional Resume Bullets", summary)
    
    assert isinstance(summary, list)
    assert len(summary) > 0
    
    # Check for architectural mentions
    summary_text = ' '.join(summary).lower()
    assert any(pattern in summary_text for pattern in ["pattern", "architecture", "framework"])

def test_framework_agnostic_component_analysis():
    """Test that component analysis works across different frameworks"""
    print_section("🔄 FRAMEWORK-AGNOSTIC ANALYSIS")
    patterns = analyze_code_patterns_from_parsed(multi_framework_files)
    
    print_subsection("Detected Frameworks", patterns["frameworks_detected"])
    print_subsection("Universal Development Practices", patterns["development_practices"])
    
    # Should detect multiple frameworks
    assert "React" in patterns["frameworks_detected"]
    assert "Vue.js" in patterns["frameworks_detected"] 
    assert "Angular" in patterns["frameworks_detected"]
    
    # Should have framework-agnostic practices
    practices_text = ' '.join(patterns["development_practices"]).lower()
    assert "hooks" in practices_text or "state" in practices_text

def test_role_inference_comprehensive():
    """Test comprehensive role inference across different technologies"""
    print_section("👥 COMPREHENSIVE ROLE INFERENCE")
    
    all_roles = set()
    for file in role_inference_test_files:
        roles = infer_roles_from_file(file)
        all_roles.update(roles)
        print_subsection(f"Roles for {file['file_path']}", list(roles))
    
    print_subsection("All Detected Roles", list(all_roles))
    
    assert "frontend" in all_roles
    assert "backend" in all_roles
    assert "data science" in all_roles
    assert "devops" in all_roles


def test_full_integration_workflow():
    """Test the complete integration workflow"""
    print_section("🚀 FULL INTEGRATION WORKFLOW")
    
    print("\n" + "="*50 + " LOCAL PROJECT WORKFLOW " + "="*50)
    
    # Local project workflow
    local_summary = analyze_parsed_project(design_pattern_files)
    print_subsection("Local Project Summary", local_summary)
    
    print("\n" + "="*50 + " GITHUB PROJECT WORKFLOW " + "="*50)
    
    assert isinstance(local_summary, list) and len(local_summary) > 0
    
    # Verify enhanced content
    local_text = ' '.join(local_summary).lower()
    
    assert any(term in local_text for term in ["pattern", "architecture", "framework"])


# --- Legacy Tests (Updated for Professional Output) ---

def test_local_analysis_no_llm():
    """Test local project analysis without LLM"""
    print_section("💻 LOCAL ANALYSIS (No LLM)")
    summary = analyze_parsed_project(complex_parsed_files)
    print_subsection("Generated Summary", summary)
    assert summary is not None and len(summary) > 0


def test_aggregation_functions():
    """Test metrics aggregation functions"""
    print_section("📊 METRICS AGGREGATION")
    
    parsed_metrics = aggregate_parsed_files_metrics(complex_parsed_files)
    print_subsection("Parsed File Metrics", parsed_metrics)
    
    assert parsed_metrics["total_files"] > 0

# --- Optional LLM Tests ---

def test_local_analysis_with_llm():
    """Test local analysis with LLM (if API key available)"""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print_section("🤖 LOCAL ANALYSIS (With LLM)")
        llm_client = GeminiLLMClient(api_key=api_key)
        summary = analyze_parsed_project(complex_parsed_files, llm_client)
        print_subsection("LLM Generated Summary", summary)
        assert summary is not None