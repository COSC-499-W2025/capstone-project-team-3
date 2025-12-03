# Mock metrics for analysis merging 
metrics = {
    "languages": ["Python", "SQL"],
    "total_files": 12,
    "total_lines": 1200,
    "functions": 34,
    "components": 8,
    "classes": 5,
    "roles": ["Backend Developer", "Database Designer"],
    "average_function_length": 18.5,
    "average_comment_ratio": 0.12,
    "code_files_changed": 7,
    "doc_files_changed": 2,
    "test_files_changed": 3,
    "authors": ["Alice", "Bob"],
    "total_commits": 45,
    "duration_days": 60,
    "files_added": 10,
    "files_modified": 15,
    "files_deleted": 2,
    "total_files_changed": 27,
}

technical_keywords = ["FastAPI", "SQLAlchemy", "pytest", "REST", "JWT"]
code_patterns = ["Repository Pattern", "Factory Pattern"]
complexity_analysis = {"cyclomatic_complexity": 3.2, "halstead": 120.5}
development_patterns = ["Agile", "CI/CD"]

resume_bullets = [
    "Developed a RESTful API using FastAPI and Python",
    "Implemented user authentication and authorization",
    "Designed and optimized database schema for performance",
    "Created unit tests and integration tests for critical components",
    "Collaborated with front-end developers to integrate APIs"
]

code_resume_bullets = [
    "Implemented RESTful endpoints for user management and authentication.",
    "Optimized SQL queries for faster data retrieval and reporting.",
    "Refactored legacy code to improve maintainability and scalability.",
    "Developed automated test suites using pytest for backend modules.",
    "Integrated third-party APIs for payment and notification services.",
    "Applied design patterns to enhance code structure and readability.",
    "Configured CI/CD pipelines for automated deployment.",
    "Monitored application performance and resolved bottlenecks.",
    "Created detailed technical documentation for backend processes.",
    "Collaborated with QA engineers to resolve critical bugs."
]

activity_type_contribution = {
    "design": 5,
    "documentation": 2,
    "other": 1
}

word_count = 2500
completeness_score = 0.92

# Code analysis results (non-git)
code_analysis_results = {
    "resume_bullets": code_resume_bullets,
    "Metrics": {
        "languages": metrics["languages"],
        "total_files": metrics["total_files"],
        "total_lines": metrics["total_lines"],
        "functions": metrics["functions"],
        "components": metrics["components"],
        "classes": metrics["classes"],
        "roles": metrics["roles"],
        "average_function_length": metrics["average_function_length"],
        "average_comment_ratio": metrics["average_comment_ratio"],
        "code_files_changed": metrics["code_files_changed"],
        "doc_files_changed": metrics["doc_files_changed"],
        "test_files_changed": metrics["test_files_changed"],
        "technical_keywords": technical_keywords,
        "code_patterns": code_patterns,
        "complexity_analysis": complexity_analysis
    }
}

# Git code analysis results
git_code_analysis_results = {
    "resume_bullets": code_resume_bullets,
    "Metrics": {
        "authors": metrics["authors"],
        "total_commits": metrics["total_commits"],
        "duration_days": metrics["duration_days"],
        "files_added": metrics["files_added"],
        "files_modified": metrics["files_modified"],
        "files_deleted": metrics["files_deleted"],
        "total_files_changed": metrics["total_files_changed"],
        "code_files_changed": metrics["code_files_changed"],
        "doc_files_changed": metrics["doc_files_changed"],
        "test_files_changed": metrics["test_files_changed"],
        "roles": metrics["roles"],
        "technical_keywords": technical_keywords,
        "development_patterns": development_patterns
    }
}

# Non-code analysis results
non_code_analysis_result = {
    "summary": "This project involved the development of a robust backend API using Python and FastAPI. "
        "The team collaborated closely to design and optimize the database schema, ensuring high performance and scalability. "
        "Comprehensive unit and integration tests were created to maintain code quality and reliability. "
        "Documentation was produced to facilitate onboarding and future maintenance. "
        "Throughout the project, agile methodologies and CI/CD pipelines were employed to streamline development and deployment. "
        "Significant contributions were made in design, documentation, and implementation, resulting in a successful and maintainable product.",
    "skills": {
        "technical_skills": ["FastAPI", "SQLAlchemy"],
        "soft_skills": ["Communication", "Collaboration"]
    },
    "resume_bullets": resume_bullets,
    "Metrics": {
        "word_count": word_count,
        "completeness_score": completeness_score,
        "activity_type_contribution": activity_type_contribution,
    }
}

project_name = "Sample Project"
project_signature = "sample_project_123"