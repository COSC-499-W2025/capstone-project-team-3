import os
from dotenv import load_dotenv
from app.client.llm_client import GeminiLLMClient
from app.utils.code_analysis.code_analysis_utils import analyze_github_project, analyze_parsed_project, aggregate_github_individual_metrics, generate_github_resume_summary
from app.utils.code_analysis.code_analysis_utils import infer_roles_from_file, infer_roles_from_commit_files
import logging

logging.basicConfig(level=logging.INFO,force=True)
logger = logging.getLogger(__name__)

# --- Sample parsed file data (for local analysis) ---
sample_parsed_files = [
    {
        "file_path": "frontend/src/App.js",
        "language": "javascript",
        "lines_of_code": 256,
        "imports": ["react", "axios", "./components/Chart", "./utils/helpers"],
        "functions": [
            {
                "name": "fetchData",
                "parameters": [],
                "calls": ["axios.get"],
                "lines_of_code": 18
            }
        ],
        "components": [
            {
                "name": "Dashboard",
                "props": ["user", "data"],
                "state_variables": ["loading", "chartData"],
                "hooks_used": ["useState", "useEffect"]
            }
        ],
        "metrics": {
            "average_function_length": 14,
            "comment_ratio": 0.08
        }
    }
]

# --- Sample GitHub commit data (for GitHub analysis) ---
sample_commits = [
    {
        "hash": "a7c3f2d",
        "author_name": "Karim Jassani",
        "author_email": "karim@example.com",
        "authored_datetime": "2025-10-30T12:45:32",
        "committed_datetime": "2025-10-30T12:47:05",
        "message_summary": "Initial commit: add main.py",
        "message_full": "Initial commit: add main.py\n\nSet up project structure and basic app entrypoint.",
        "is_merge": False,
        "files": [
            {
                "status": "A",
                "path_before": None,
                "path_after": "app/main.py",
                "patch": "@@ -0,0 +1,10 @@\n+def main():\n+    print('Hello, world!')\n+\n+if __name__ == '__main__':\n+    main()",
                "size_after": 84
            }
        ]
    }
]

def test_local_analysis_no_llm():
    # Test local project analysis without LLM (rule-based summary)
    summary = analyze_parsed_project(sample_parsed_files)
    logger.info("Local Analysis (no LLM):\n%s", summary)
    assert summary is not None
    assert isinstance(summary, list)

def test_local_analysis_with_llm():
    # Test local project analysis with LLM (Gemini API)
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    llm_client = GeminiLLMClient(api_key=api_key)
    summary = analyze_parsed_project(sample_parsed_files, llm_client)
    logger.info("Local Analysis (LLM):\n%s", summary)
    assert summary is not None
    assert isinstance(summary, str) or isinstance(summary, list)

def test_github_analysis_no_llm():
    # Test GitHub commit analysis without LLM (rule-based summary)
    summary = analyze_github_project(sample_commits)
    logger.info("GitHub Analysis (no LLM):\n%s", summary)
    assert summary is not None
    assert isinstance(summary, list)

def test_github_analysis_with_llm():
    # Test GitHub commit analysis with LLM (Gemini API)
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    llm_client = GeminiLLMClient(api_key=api_key)
    summary = analyze_github_project(sample_commits, llm_client)
    logger.info("GitHub Analysis (LLM):\n%s", summary)
    assert summary is not None
    assert isinstance(summary, str) or isinstance(summary, list)

def test_local_analysis_empty_input():
    # Test local analysis with empty input to ensure defaults are returned
    summary = analyze_parsed_project([])
    logger.info("Local Analysis (empty input):\n%s", summary)
    assert summary is not None
    assert isinstance(summary, list)
    # Check that all metrics are zero or empty
    assert any("0" in str(line) for line in summary)
    
def test_infer_roles_from_file_single_role():
    # Test role inference for a file with clear frontend indicators
    file = {
        "file_path": "frontend/src/App.js",
        "imports": ["react"]
    }
    roles = infer_roles_from_file(file)
    assert "frontend" in roles

def test_infer_roles_from_commit_files_multiple_roles():
    # Test role inference for commit files covering multiple roles
    files = [
        {"path_after": "frontend/src/App.js"},
        {"path_after": "docker/Dockerfile"},
        {"path_after": "data/analysis.ipynb"},
    ]
    roles = infer_roles_from_commit_files(files)
    assert "frontend" in roles
    assert "devops" in roles
    assert "data science" in roles

def test_infer_roles_no_roles():
    # Test role inference for files/commits with no relevant role indicators
    file = {
        "file_path": "docs/readme.md",
        "imports": []
    }
    roles_file = infer_roles_from_file(file)
    files_commit = [{"path_after": "docs/readme.md"}]
    roles_commit = infer_roles_from_commit_files(files_commit)
    assert len(roles_file) == 0
    assert len(roles_commit) == 0