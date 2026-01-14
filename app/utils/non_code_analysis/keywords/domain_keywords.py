"""
Domain and job-specific keyword mappings for enhanced document classification.
"""

# Base domain keywords
BASE_DOMAIN_KEYWORDS = {
    "Software Engineering": [
        "software", "code", "api", "system", "development", "application", 
        "backend", "frontend", "database"
    ],
    "Data Science": [
        "data", "analysis", "model", "dataset", "analytics", "visualization", 
        "machine learning", "statistics", "prediction"
    ],
    "Business": [
        "business", "strategy", "market", "revenue", "customer", "sales", 
        "roi", "growth", "stakeholder"
    ],
    "Healthcare": [
        "health", "medical", "patient", "treatment", "clinical", "diagnosis", 
        "care", "therapy"
    ],
    "Education": [
        "education", "learning", "curriculum", "student", "course", "teaching", 
        "training", "pedagogy"
    ],
    "Research": [
        "research", "study", "experiment", "hypothesis", "findings", "methodology", 
        "analysis", "publication"
    ],
    "Design": [
        "design", "ui", "ux", "prototype", "wireframe", "interface", 
        "user experience", "visual", "usability"
    ],
    "Project Management": [
        "project", "milestone", "deliverable", "timeline", "agile", "scrum", 
        "sprint", "planning", "coordination"
    ],
    "AI / Machine Learning": [
        "artificial intelligence", "ai", "machine learning", "model", "algorithm", 
        "neural network", "deep learning", "training"
    ],
}

# Industry-specific keyword expansions
INDUSTRY_EXPANSIONS = {
    "Software Engineering": [
        "ci/cd", "devops", "containerization", "microservices", "rest api", 
        "graphql", "deployment", "scalability"
    ],
    "Data Science": [
        "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "jupyter", 
        "data pipeline", "etl", "data cleaning"
    ],
    "Business": [
        "kpi", "metrics", "analytics", "reporting", "dashboard", 
        "business intelligence", "crm", "erp"
    ],
    "Healthcare": [
        "hipaa", "ehr", "emr", "telemedicine", "clinical trial", 
        "patient care", "medical records"
    ],
    "Education": [
        "lms", "e-learning", "mooc", "assessment", "educational technology", 
        "canvas", "moodle"
    ],
    "Research": [
        "peer review", "literature review", "data collection", 
        "statistical analysis", "survey", "methodology"
    ],
    "Design": [
        "figma", "sketch", "adobe xd", "user research", "a/b testing", 
        "accessibility", "responsive design"
    ],
    "Project Management": [
        "jira", "kanban", "gantt", "resource allocation", "risk management", 
        "stakeholder management"
    ],
    "AI / Machine Learning": [
        "nlp", "computer vision", "reinforcement learning", "feature engineering", 
        "model deployment", "mlops"
    ],
}

# Job-title-specific keywords
JOB_TITLE_KEYWORDS = {
    "software engineer": [
        "implementation", "debugging", "testing", "version control", 
        "code review", "refactoring"
    ],
    "data scientist": [
        "data cleaning", "feature selection", "model evaluation", 
        "cross-validation", "exploratory analysis"
    ],
    "product manager": [
        "roadmap", "user stories", "prioritization", "product lifecycle", 
        "sprint planning"
    ],
    "designer": [
        "mockup", "design system", "component library", "user flow", 
        "interaction design"
    ],
    "data analyst": [
        "sql", "excel", "tableau", "power bi", "reporting", "dashboard"
    ],
    "devops engineer": [
        "automation", "monitoring", "deployment", "infrastructure", 
        "ci/cd pipeline"
    ],
    "ml engineer": [
        "model deployment", "mlops", "model monitoring", 
        "hyperparameter tuning", "model optimization"
    ],
    "backend developer": [
        "api development", "database design", "server architecture", 
        "authentication"
    ],
    "frontend developer": [
        "responsive design", "component development", "state management", 
        "performance optimization"
    ],
}

# Job title to domain mapping
JOB_TO_DOMAIN = {
    "software engineer": "Software Engineering",
    "data scientist": "Data Science",
    "product manager": "Project Management",
    "designer": "Design",
    "data analyst": "Data Science",
    "devops engineer": "Software Engineering",
    "ml engineer": "AI / Machine Learning",
    "backend developer": "Software Engineering",
    "frontend developer": "Software Engineering",
}

# Job context descriptions
JOB_CONTEXT_MAP = {
    "software engineer": "with focus on development and implementation",
    "data scientist": "with emphasis on analytics and modeling",
    "product manager": "highlighting product strategy and stakeholder management",
    "designer": "showcasing design and user experience work",
    "data analyst": "with focus on data analysis and insights",
    "devops engineer": "emphasizing automation and infrastructure",
}

# ===== NEW MAPPING: CLI INDUSTRY TO DOMAIN =====
CLI_INDUSTRY_TO_DOMAIN = {
    "Technology": "Software Engineering",
    "Finance": "Business",
    "Healthcare": "Healthcare",
    "Education": "Education",
    "Research": "Research",
    "Manufacturing": "Business",
    "Retail": "Business",
    "Government": "Project Management",
    "Non-profit": "Project Management",
    "Other": None
}


def get_mapped_industry(cli_industry: str) -> str:
    """
    Helper to map CLI industry values to domain keywords.
    """
    return CLI_INDUSTRY_TO_DOMAIN.get(cli_industry, cli_industry)


def build_enhanced_keywords(user_industry: str = None, user_job_title: str = None):
    """
    Build enhanced keyword dictionary based on user preferences.
    
    Args:
        user_industry: User's target industry (CLI format like "Technology")
        user_job_title: User's job title
        
    Returns:
        Enhanced domain_keywords dict with user-specific expansions
    """
    # Start with base keywords (make a copy)
    domain_keywords = {k: list(v) for k, v in BASE_DOMAIN_KEYWORDS.items()}
    
    # Map CLI industry to domain keyword set
    mapped_industry = None
    if user_industry:
        mapped_industry = get_mapped_industry(user_industry)
    
    # Enhancement 1: Add industry-specific keywords
    if mapped_industry and mapped_industry in INDUSTRY_EXPANSIONS:
        if mapped_industry not in domain_keywords:
            domain_keywords[mapped_industry] = []
        domain_keywords[mapped_industry].extend(INDUSTRY_EXPANSIONS[mapped_industry])
    
    # Enhancement 2: Add job-title-specific keywords
    if user_job_title:
        job_title_lower = user_job_title.lower()
        
        for job_key, keywords in JOB_TITLE_KEYWORDS.items():
            if job_key in job_title_lower:
                target_domain = JOB_TO_DOMAIN.get(job_key)
                if target_domain and target_domain in domain_keywords:
                    domain_keywords[target_domain].extend(keywords)
                break
    
    return domain_keywords