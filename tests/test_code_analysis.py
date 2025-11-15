import os
from dotenv import load_dotenv
from app.client.llm_client import GeminiLLMClient
from app.utils.code_analysis.code_analysis_utils import (
    analyze_github_project, analyze_parsed_project, aggregate_github_individual_metrics, 
    generate_github_resume_summary, infer_roles_from_file, infer_roles_from_commit_files,
    extract_technical_keywords_from_parsed, extract_technical_keywords_from_github,
    analyze_code_patterns_from_parsed, analyze_github_development_patterns,
    calculate_advanced_complexity_from_parsed, aggregate_parsed_files_metrics, generate_resume_summary_from_parsed
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

# --- Enhanced Sample Data for Comprehensive Testing ---

# Complex sample for testing all new design patterns
design_pattern_files = [
    {
        "file_path": "src/factories/UserFactory.js",
        "language": "javascript",
        "lines_of_code": 120,
        "imports": ["react", "axios"],
        "functions": [
            {
                "name": "createUserFactory",
                "parameters": ["config"],
                "calls": ["buildUser", "createInstance", "makeUser"],
                "lines_of_code": 25
            },
            {
                "name": "buildUser",
                "parameters": ["data"],
                "calls": ["construct", "newUser"],
                "lines_of_code": 18
            }
        ],
        "components": [
            {
                "name": "UserObserver",
                "props": ["observable"],
                "state_variables": ["subscribers"],
                "hooks_used": ["useState", "useEffect"]
            }
        ]
    },
    {
        "file_path": "src/patterns/Observer.py",
        "language": "python",
        "lines_of_code": 200,
        "imports": ["flask", "sqlalchemy"],
        "functions": [
            {
                "name": "observer_pattern",
                "parameters": ["subject"],
                "calls": ["subscribe", "notify", "emit"],
                "lines_of_code": 30
            },
            {
                "name": "notify_subscribers",
                "parameters": ["event"],
                "calls": ["emit", "broadcast", "update"],
                "lines_of_code": 22
            },
            {
                "name": "strategy_execute",
                "parameters": ["algorithm"],
                "calls": ["process", "handle", "execute"],
                "lines_of_code": 28
            },
            {
                "name": "singleton_getInstance",
                "parameters": [],
                "calls": ["createInstance", "getinstance"],
                "lines_of_code": 15
            }
        ],
        "components": []
    },
    {
        "file_path": "src/architecture/UserController.java",
        "language": "java",
        "lines_of_code": 180,
        "imports": ["spring", "hibernate"],
        "functions": [
            {
                "name": "getUserModel",
                "parameters": ["id"],
                "calls": ["repository.find", "validateModel"],
                "lines_of_code": 20
            },
            {
                "name": "userServiceLayer",
                "parameters": ["request"],
                "calls": ["businessLayer", "dataLayer"],
                "lines_of_code": 35
            }
        ],
        "components": [
            {
                "name": "UserViewController",
                "props": ["model", "presenter"],
                "state_variables": ["viewModel"],
                "hooks_used": []
            }
        ]
    },
    {
        "file_path": "src/microservices/ApiGateway.go",
        "language": "go", 
        "lines_of_code": 150,
        "imports": ["gin", "kubernetes"],
        "functions": [
            {
                "name": "microservice_handler",
                "parameters": ["request"],
                "calls": ["apiGateway", "serviceRegistry"],
                "lines_of_code": 25
            },
            {
                "name": "rest_endpoint",
                "parameters": ["path"],
                "calls": ["get", "post", "put", "delete"],
                "lines_of_code": 40
            },
            {
                "name": "event_handler",
                "parameters": ["event"],
                "calls": ["messageQueue", "pubsub", "kafka"],
                "lines_of_code": 30
            }
        ],
        "components": []
    }
]

# Complex architectural patterns commits
architectural_commits = [
    {
        "hash": "arch001",
        "author_name": "Software Architect",
        "author_email": "arch@example.com",
        "authored_datetime": "2025-10-15T10:00:00",
        "committed_datetime": "2025-10-15T10:02:00",
        "message_summary": "implement microservices architecture with API gateway",
        "message_full": "implement microservices architecture with API gateway\n\nAdded service discovery and circuit breaker patterns",
        "is_merge": False,
        "files": [
            {"status": "A", "path_after": "services/user-service/main.py"},
            {"status": "A", "path_after": "services/auth-service/auth.py"},
            {"status": "A", "path_after": "gateway/api-gateway.js"},
            {"status": "A", "path_after": "config/kubernetes/deployment.yml"}
        ]
    },
    {
        "hash": "arch002", 
        "author_name": "Backend Developer",
        "authored_datetime": "2025-10-16T14:30:00",
        "message_summary": "refactor: implement repository pattern with layered architecture",
        "message_full": "refactor: implement repository pattern with layered architecture\n\nAdded data access layer and business logic separation",
        "files": [
            {"status": "A", "path_after": "repositories/UserRepository.java"},
            {"status": "A", "path_after": "services/UserService.java"},
            {"status": "A", "path_after": "controllers/UserController.java"},
            {"status": "M", "path_after": "models/User.java"}
        ]
    },
    {
        "hash": "arch003",
        "author_name": "Frontend Architect", 
        "authored_datetime": "2025-10-17T09:15:00",
        "message_summary": "feat: implement MVVM pattern with React and Redux",
        "message_full": "feat: implement MVVM pattern with React and Redux\n\nAdded ViewModels and state management",
        "files": [
            {"status": "A", "path_after": "viewmodels/UserViewModel.js"},
            {"status": "A", "path_after": "views/UserView.jsx"},
            {"status": "A", "path_after": "models/UserModel.js"},
            {"status": "M", "path_after": "store/userStore.js"}
        ]
    },
    {
        "hash": "arch004",
        "author_name": "DevOps Engineer",
        "authored_datetime": "2025-10-18T16:45:00", 
        "message_summary": "deploy: setup event-driven architecture with message queues",
        "message_full": "deploy: setup event-driven architecture with message queues\n\nAdded Kafka for pub/sub messaging and event streaming",
        "files": [
            {"status": "A", "path_after": "events/UserEventHandler.py"},
            {"status": "A", "path_after": "messaging/MessageQueue.js"},
            {"status": "A", "path_after": "config/kafka/producer.yml"},
            {"status": "A", "path_after": "streams/UserEventStream.java"}
        ]
    }
]

# Original samples for compatibility
complex_parsed_files = [
    {
        "file_path": "frontend/src/App.js",
        "language": "javascript",
        "lines_of_code": 256,
        "imports": ["react", "axios", "./components/Chart", "./utils/helpers", "redux", "react-router"],
        "functions": [
            {
                "name": "fetchUserData",
                "parameters": ["userId", "options"],
                "calls": ["axios.get", "validateUser", "parseResponse"],
                "lines_of_code": 18
            },
            {
                "name": "createUserFactory",
                "parameters": ["config"],
                "calls": ["buildUser", "setDefaults"],
                "lines_of_code": 25
            }
        ],
        "components": [
            {
                "name": "Dashboard",
                "props": ["user", "data", "onUpdate"],
                "state_variables": ["loading", "chartData", "error"],
                "hooks_used": ["useState", "useEffect", "useCallback"]
            }
        ],
        "metrics": {"average_function_length": 21.5, "comment_ratio": 0.12}
    },
    {
        "file_path": "backend/api/users.py",
        "language": "python", 
        "lines_of_code": 180,
        "imports": ["flask", "sqlalchemy", "jwt", "bcrypt"],
        "functions": [
            {
                "name": "create_user_observer",
                "parameters": ["user_data", "notify_callback"],
                "calls": ["validate_data", "save_to_db", "notify_subscribers"],
                "lines_of_code": 30
            }
        ],
        "components": [],
        "metrics": {"average_function_length": 30, "comment_ratio": 0.08}
    }
]

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

def test_enhanced_architectural_pattern_analysis():
    """Test architectural pattern detection from commit history"""
    print_section("🏗️  ARCHITECTURAL PATTERN ANALYSIS")
    
    # Create commits with explicit testing and documentation practices
    enhanced_commits = [
        {
            "hash": "arch001",
            "author_name": "Software Architect",
            "authored_datetime": "2025-10-15T10:00:00",
            "message_summary": "test: implement microservices architecture with comprehensive testing",
            "files": [
                {"status": "A", "path_after": "services/user-service/main.py"},
                {"status": "A", "path_after": "test/user_service_test.py"},  # Test file
            ]
        },
        {
            "hash": "arch002", 
            "author_name": "Backend Developer",
            "authored_datetime": "2025-10-16T14:30:00",
            "message_summary": "docs: add comprehensive documentation for repository pattern",
            "files": [
                {"status": "A", "path_after": "repositories/UserRepository.java"},
                {"status": "A", "path_after": "README.md"},  # Documentation
            ]
        }
    ]
    
    metrics = aggregate_github_individual_metrics(enhanced_commits)
    patterns = analyze_github_development_patterns(enhanced_commits)
    
    print_subsection("Project Evolution", patterns["project_evolution"])
    print_subsection("Code Practices", patterns["code_practices"])
    print_subsection("Detected Roles", metrics["roles"])
    
    assert len(patterns["project_evolution"]) > 0
    assert len(patterns["code_practices"]) > 0  

def test_comprehensive_technical_keyword_extraction():
    """Test expanded technical keyword extraction"""
    print_section("🔍 TECHNICAL KEYWORD EXTRACTION")
    
    # Test parsed files
    keywords_parsed = extract_technical_keywords_from_parsed(design_pattern_files)
    print_subsection("Keywords from Parsed Files", keywords_parsed[:10])
    
    # Test GitHub commits  
    keywords_github = extract_technical_keywords_from_github(architectural_commits)
    print_subsection("Keywords from GitHub Commits", keywords_github[:10])
    
    assert len(keywords_parsed) > 0
    assert len(keywords_github) > 0
    
    # Check for architectural terms
    architecture_terms = ["microservices", "architecture", "repository", "event"]
    found_terms = [term for term in architecture_terms if term in keywords_github]
    assert len(found_terms) > 0

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

def test_enhanced_resume_generation_github():
    """Test enhanced resume generation for GitHub projects"""
    print_section("📝 ENHANCED GITHUB PROJECT RESUME")
    
    metrics = aggregate_github_individual_metrics(architectural_commits)
    metrics["technical_keywords"] = extract_technical_keywords_from_github(architectural_commits)
    metrics["development_patterns"] = analyze_github_development_patterns(architectural_commits)
    
    summary = generate_github_resume_summary(metrics)
    
    print_subsection("Professional Resume Bullets", summary)
    
    assert isinstance(summary, list)
    assert len(summary) > 0
    
    summary_text = ' '.join(summary).lower()
    assert "commit" in summary_text or "implement" in summary_text

def test_framework_agnostic_component_analysis():
    """Test that component analysis works across different frameworks"""
    print_section("🔄 FRAMEWORK-AGNOSTIC ANALYSIS")
    
    # Create multi-framework sample
    multi_framework_files = [
        {
            "file_path": "src/ReactComponent.jsx",
            "language": "javascript",
            "imports": ["react"],
            "functions": [],
            "components": [
                {
                    "name": "ReactDashboard", 
                    "props": ["data"],
                    "state_variables": ["loading"],
                    "hooks_used": ["useState", "useEffect"]
                }
            ]
        },
        {
            "file_path": "src/VueComponent.vue",
            "language": "javascript", 
            "imports": ["vue"],
            "functions": [],
            "components": [
                {
                    "name": "VueDashboard",
                    "props": ["data"],
                    "state_variables": ["loading"], 
                    "hooks_used": ["onMounted", "reactive"]
                }
            ]
        },
        {
            "file_path": "src/AngularComponent.ts",
            "language": "typescript",
            "imports": ["angular"],
            "functions": [],
            "components": [
                {
                    "name": "AngularDashboard",
                    "props": ["data"],
                    "state_variables": ["loading"],
                    "hooks_used": ["ngOnInit", "ngOnDestroy"]
                }
            ]
        }
    ]
    
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
    
    # Test various role combinations
    test_files = [
        {"file_path": "frontend/react/App.tsx", "imports": ["react", "typescript"]},
        {"file_path": "backend/django/models.py", "imports": ["django", "postgresql"]},
        {"file_path": "data/analysis.ipynb", "imports": ["pandas", "numpy", "sklearn"]},
        {"file_path": "devops/kubernetes/deployment.yml", "imports": ["docker"]},
        {"file_path": "mobile/flutter/main.dart", "imports": ["flutter"]},
    ]
    
    all_roles = set()
    for file in test_files:
        roles = infer_roles_from_file(file)
        all_roles.update(roles)
        print_subsection(f"Roles for {file['file_path']}", list(roles))
    
    print_subsection("All Detected Roles", list(all_roles))
    
    assert "frontend" in all_roles
    assert "backend" in all_roles
    assert "data science" in all_roles
    assert "devops" in all_roles

def test_edge_cases_and_robustness():
    """Test edge cases and error handling"""
    print_section("🛡️  EDGE CASES & ROBUSTNESS")
    
    # Test empty inputs
    empty_patterns = analyze_code_patterns_from_parsed([])
    print_subsection("Empty Input Patterns", {k: v for k, v in empty_patterns.items() if v})
    
    # Test malformed data
    malformed_file = {"file_path": "test.py", "language": "python"}
    try:
        keywords = extract_technical_keywords_from_parsed([malformed_file])
        print_subsection("Malformed File Keywords", keywords[:5] if keywords else ["None"])
        assert isinstance(keywords, list)
    except Exception as e:
        print_subsection("Error Handling", f"Gracefully handled: {type(e).__name__}")
    
    # Test with minimal data
    minimal_commit = {"hash": "test", "author_name": "Test", "authored_datetime": "2025-01-01T10:00:00", "files": []}
    minimal_metrics = aggregate_github_individual_metrics([minimal_commit])
    print_subsection("Minimal Commit Metrics", {k: v for k, v in minimal_metrics.items() if v})

def test_full_integration_workflow():
    """Test the complete integration workflow"""
    print_section("🚀 FULL INTEGRATION WORKFLOW")
    
    print("\n" + "="*50 + " LOCAL PROJECT WORKFLOW " + "="*50)
    
    # Local project workflow
    local_summary = analyze_parsed_project(design_pattern_files)
    print_subsection("Local Project Summary", local_summary)
    
    print("\n" + "="*50 + " GITHUB PROJECT WORKFLOW " + "="*50)
    
    # GitHub project workflow  
    github_summary = analyze_github_project(architectural_commits)
    print_subsection("GitHub Project Summary", github_summary)
    
    assert isinstance(local_summary, list) and len(local_summary) > 0
    assert isinstance(github_summary, list) and len(github_summary) > 0
    
    # Verify enhanced content
    local_text = ' '.join(local_summary).lower()
    github_text = ' '.join(github_summary).lower()
    
    assert any(term in local_text for term in ["pattern", "architecture", "framework"])
    assert any(term in github_text for term in ["commit", "implement", "architecture"])

# --- Legacy Tests (Updated for Professional Output) ---

def test_local_analysis_no_llm():
    """Test local project analysis without LLM"""
    print_section("💻 LOCAL ANALYSIS (No LLM)")
    summary = analyze_parsed_project(complex_parsed_files)
    print_subsection("Generated Summary", summary)
    assert summary is not None and len(summary) > 0

def test_github_analysis_no_llm():
    """Test GitHub analysis without LLM"""
    print_section("🐙 GITHUB ANALYSIS (No LLM)")  
    sample_commits = [
        {
            "hash": "a7c3f2d",
            "author_name": "Developer", 
            "authored_datetime": "2025-10-30T12:45:32",
            "message_summary": "feat: implement user authentication",
            "files": [{"status": "A", "path_after": "auth/login.py"}]
        }
    ]
    summary = analyze_github_project(sample_commits)
    print_subsection("Generated Summary", summary)
    assert summary is not None and len(summary) > 0

def test_aggregation_functions():
    """Test metrics aggregation functions"""
    print_section("📊 METRICS AGGREGATION")
    
    parsed_metrics = aggregate_parsed_files_metrics(complex_parsed_files)
    print_subsection("Parsed File Metrics", parsed_metrics)
    
    github_metrics = aggregate_github_individual_metrics(architectural_commits)
    print_subsection("GitHub Metrics", {k: v for k, v in github_metrics.items() if k not in ['sample_messages']})
    
    assert parsed_metrics["total_files"] > 0
    assert github_metrics["total_commits"] > 0

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

def test_github_analysis_with_llm():
    """Test GitHub analysis with LLM (if API key available)"""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print_section("🤖 GITHUB ANALYSIS (With LLM)")
        llm_client = GeminiLLMClient(api_key=api_key)
        summary = analyze_github_project(architectural_commits, llm_client)
        print_subsection("LLM Generated Summary", summary)
        assert summary is not None