# git code:
{
  "Resume_bullets": [
    "Contributed 47 commits adding 3,247 lines of code in Python, JavaScript over 23 days of active development",
    "Implemented changes in 15 code files across Python, JavaScript projects, with 8 new files created and 12 existing files enhanced",
    "Demonstrated expertise in: testing, api, flask, react, components, utils",
    "Applied best practices: Test-Driven Development, Code Refactoring, Documentation-Focused",
    "Led development in: Python Development, JavaScript/Frontend Development",
    "Emphasized code quality through testing (5 test files) and documentation (3 docs)"
  ],
  "Metrics": {
    "authors": ["john_doe", "jane_smith"],
    "total_commits": 47,
    "duration_days": 23,
    "files_added": 8,
    "files_modified": 12,
    "files_deleted": 2,
    "total_files_changed": 18,
    "code_files_changed": 15,
    "doc_files_changed": 3,
    "test_files_changed": 5,
    "languages": ["Python", "JavaScript", "TypeScript", "CSS"],
    "total_lines": 3247,
    "roles": ["backend", "frontend", "testing"],
    "technical_keywords": [
      "api", "authentication", "components", "database", "docker", 
      "flask", "javascript", "models", "react", "routes", 
      "testing", "utils", "validation", "webpack"
    ],
    "development_patterns": {
      "development_workflow": ["feature_based", "git_flow"],
      "collaboration_patterns": ["pull_requests", "code_reviews"],
      "code_practices": ["Test-Driven Development", "Code Refactoring", "Documentation-Focused"],
      "project_evolution": ["Python Development", "JavaScript/Frontend Development"]
    }
  }
}
# code non git:
{
  "Resume_bullets": [
    "Developed a comprehensive 4,523-line codebase across 23 files using Python, JavaScript, TypeScript",
    "Demonstrated expertise in key technologies: react, components, hooks, api, models, utils, testing, express",
    "Built solutions using React, Flask frameworks",
    "Implemented software design patterns: Observer Pattern, Factory Pattern, Repository Pattern",
    "Applied modern development practices: RESTful API Architecture, Service-Oriented Architecture, React Hooks/Lifecycle (8 types), Component State Management",
    "Maintained excellent code quality with high maintainability score and well-structured functions",
    "Followed best practices with low-complexity, maintainable code structure",
    "Architected modular solution with 45 functions, 12 classes and 8 components",
    "Maintained low complexity across all functions and components",
    "Integrated 15 external libraries and dependencies for enhanced functionality",
    "Designed modular architecture with 8 internal dependencies promoting code reusability"
  ],
  "Metrics": {
    "languages": ["Python", "JavaScript", "TypeScript"],
    "total_files": 23,
    "total_lines": 4523,
    "functions": 45,
    "components": 8,
    "classes": 12,
    "roles": ["backend", "frontend", "database"],
    "average_function_length": 18.7,
    "average_comment_ratio": 0.15,
    "code_files_changed": 20,
    "doc_files_changed": 2,
    "test_files_changed": 6,
    "technical_keywords": [
      "api", "authentication", "components", "database", "hooks", 
      "models", "react", "routes", "services", "testing", 
      "utils", "validation", "express", "middleware", "async"
    ],
    "code_patterns": {
      "frameworks_detected": ["React", "Flask", "Express.js"],
      "design_patterns": ["Observer Pattern", "Factory Pattern", "Repository Pattern"],
      "architectural_patterns": ["RESTful API Architecture", "Service-Oriented Architecture", "MVC Architecture"],
      "development_practices": [
        "React Hooks/Lifecycle (8 types)",
        "Component State Management", 
        "Component Props/Data Flow (8 components)"
      ],
      "technology_stack": ["Python", "JavaScript", "TypeScript"]
    },
    "complexity_analysis": {
      "function_complexity": [12, 8, 45, 23, 15, 9, 34, 18, 7, 29],
      "component_complexity": [8, 12, 6, 15, 10, 7, 9, 11],
      "class_complexity": [25, 34, 18, 42, 28, 16, 31, 22, 19, 27, 33, 21],
      "maintainability_score": {
        "overall_score": 82.3,
        "average_complexity": 19.8,
        "total_code_units": 65,
        "complexity_distribution": {
          "low_complexity": 48,
          "medium_complexity": 15,
          "high_complexity": 2
        },
        "quality_indicators": {
          "functions_per_file": 2.83,
          "avg_lines_per_unit": 69.6,
          "complexity_trend": "good"
        }
      },
      "complexity_breakdown": {
        "functions": {
          "count": 45,
          "avg_complexity": 18.4,
          "high_complexity": 1
        },
        "classes": {
          "count": 12,
          "avg_complexity": 26.3,
          "high_complexity": 1
        },
        "components": {
          "count": 8,
          "avg_complexity": 9.8,
          "high_complexity": 0
        }
      }
    }
  }
}
from typing import Dict, Any

def _norm_with_cap(value: float, cap: float) -> float:
    """Simple 0–1 normalization with an upper cap."""
    if cap <= 0:
        return 0.0
    if value <= 0:
        return 0.0
    return min(value / cap, 1.0)

def _compute_git_code_score(git_code_metrics: Dict[str, Any]) -> float:
    """
    Compute a code score (0–1) for a Git-based project using weighted components.

    Weights (sum to 1.0):
      1. total_commits         → 30%
      2. duration_days         → 30%
      3. files_added           → 9%
      4. files_deleted         → 3%
      5. files_modified        → 14%
      6. code_files_changed    → 9%
      7. test_files_changed    → 5%
    """

    # Extract raw values (default to 0 if missing)
    total_commits      = git_code_metrics.get("total_commits", 0)
    duration_days      = git_code_metrics.get("duration_days", 0)
    files_added        = git_code_metrics.get("files_added", 0)
    files_deleted      = git_code_metrics.get("files_deleted", 0)
    files_modified     = git_code_metrics.get("files_modified", 0)
    code_files_changed = git_code_metrics.get("code_files_changed", 0)
    test_files_changed = git_code_metrics.get("test_files_changed", 0)

    # Caps: "excellent" levels for a final-year undergrad project
    commits_cap              = 50.0
    duration_cap             = 30.0
    files_added_cap          = 10.0
    files_deleted_cap        = 10.0
    files_modified_cap       = 25.0
    code_files_changed_cap   = 20.0
    test_files_changed_cap   = 8.0

    # Normalize each component to [0, 1]
    s_commits      = _norm_with_cap(total_commits,      commits_cap)
    s_duration     = _norm_with_cap(duration_days,      duration_cap)
    s_added        = _norm_with_cap(files_added,        files_added_cap)
    s_deleted      = _norm_with_cap(files_deleted,      files_deleted_cap)
    s_modified     = _norm_with_cap(files_modified,     files_modified_cap)
    s_code_files   = _norm_with_cap(code_files_changed, code_files_changed_cap)
    s_test_files   = _norm_with_cap(test_files_changed, test_files_changed_cap)

    # Apply weights (sum to 1.0)
    code_score = (
        0.30 * s_commits +
        0.30 * s_duration +
        0.09 * s_added +
        0.03 * s_deleted +
        0.14 * s_modified +
        0.09 * s_code_files +
        0.05 * s_test_files
    )

    return code_score

def _compute_non_code_score(non_code_metrics: Dict[str, Any]) -> float:
    """
    Compute a non-code score from completeness_score.
    Expected range: [0, 1].
    If completeness_score is out of this range, clamp it.
    """

    completeness = non_code_metrics.get("completeness_score", 0.0)

    # If someone accidentally passes 0–100, convert to 0–1
    if completeness > 1.0:
        completeness /= 100.0

    # Clamp to valid range
    completeness = max(0.0, min(completeness, 1.0))

    return completeness

def _compute_non_git_code_score(non_git_code_metrics: Dict[str, Any]) -> float:
    """
    Compute a code contribution score (0–1) for a non-Git project.
    Uses structural + complexity-based metrics.
    Higher complexity = higher contribution.
    """

    # Extract raw values
    total_files          = non_git_code_metrics.get("total_files", 0)
    total_lines          = non_git_code_metrics.get("total_lines", 0)
    code_files_changed   = non_git_code_metrics.get("code_files_changed", 0)
    test_files_changed   = non_git_code_metrics.get("test_files_changed", 0)

    maint = non_git_code_metrics["complexity_analysis"]["maintainability_score"]
    overall_score      = maint.get("overall_score", 0)
    average_complexity = maint.get("average_complexity", 0)

    # Caps
    total_files_cap        = 40
    total_lines_cap        = 5000
    code_files_changed_cap = 30
    test_files_changed_cap = 10
    overall_score_cap      = 100
    average_complexity_cap = 30

    # Normalize using shared function
    s_files        = _norm_with_cap(total_files, total_files_cap)
    s_lines        = _norm_with_cap(total_lines, total_lines_cap)
    s_code_files   = _norm_with_cap(code_files_changed, code_files_changed_cap)
    s_test_files   = _norm_with_cap(test_files_changed, test_files_changed_cap)
    s_overall      = _norm_with_cap(overall_score, overall_score_cap)
    s_complexity   = _norm_with_cap(average_complexity, average_complexity_cap)

    # Weights (sum to 1.0)
    score = (
        0.15 * s_files +
        0.20 * s_lines +
        0.20 * s_code_files +
        0.10 * s_test_files +
        0.20 * s_overall +
        0.15 * s_complexity
    )

    return score



def compute_contribution_percentages_single_project(
    code_metrics: Dict[str, Any],
    git_code_metrics: Dict[str, Any],
    non_code_metrics: Dict[str, Any],
) -> Dict[str, float]:
    """
    Compute percentage of code vs non-code contribution for a project.
    
    Inputs:
        code_metrics     - dict containing "total_lines" OR empty
        git_code_metrics - dict containing "total_lines" OR empty
        non_code_metrics - dict containing "word_count"
    """

    # Choose code lines from whichever source is not empty
    if code_metrics and code_metrics.get("total_lines", 0) > 0:
        code_lines = code_metrics.get("total_lines", 0)
    else:
        code_lines = git_code_metrics.get("total_lines", 0)

    # Extract word count
    total_words = non_code_metrics.get("word_count", 0)

    # Convert documentation words → code line equivalents
    words_per_code_line = 7.0
    doc_line_equiv = total_words / words_per_code_line if words_per_code_line > 0 else total_words

    total = code_lines + doc_line_equiv

    if total == 0:
        return {
            "code_percentage": 0.0,
            "non_code_percentage": 0.0
        }

    return {
        "code_percentage": code_lines / total,
        "non_code_percentage": doc_line_equiv / total
    }


