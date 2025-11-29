from app.utils.analysis_merger_utils import merge_analysis_results,store_results_in_db, retrieve_results_from_db

def test_merge_analysis_results():
    
    code_analysis_results = {
        "Resume_bullets": ["Built REST API", "Wrote unit tests"],
        "Metrics": {
            "languages": ["Python"],
            "technical_keywords": ["FastAPI", "pytest"],
            "code_files_changed": 5
        }
    }
    non_code_analysis_results = {
        "summary": "Project summary here.",
        "skills": {
            "technical_skills": ["SQLAlchemy"],
            "soft_skills": ["Communication"]
        },
        "Resume_bullets": ["Documented requirements"],
        "Metrics": {
            "word_count": 1000,
            "completeness_score": 0.95
        }
    }
    project_name = "Test Project"
    project_signature = "test_project_001"

    merged = merge_analysis_results(code_analysis_results, non_code_analysis_results, project_name, project_signature)

    assert "summary" in merged
    assert "skills" in merged
    assert "resume_bullets" in merged
    assert "metrics" in merged

    # Check merged skills
    assert "FastAPI" in merged["skills"]["technical_skills"]
    assert "SQLAlchemy" in merged["skills"]["technical_skills"]
    assert "Communication" in merged["skills"]["soft_skills"]

    # Check merged resume bullets
    assert "Built REST API" in merged["resume_bullets"]
    assert "Documented requirements" in merged["resume_bullets"]

    # Check merged metrics
    assert merged["metrics"]["languages"] == ["Python"]
    assert merged["metrics"]["word_count"] == 1000
    assert merged["metrics"]["completeness_score"] == 0.95
    
def test_store_and_retrieve_results_in_db():
    project_signature = "test_project_002"
    project_name = "DB Test Project"
    merged_results = {
        "summary": "DB Test Project summary.",
        "skills": {
            "technical_skills": ["Django"],
            "soft_skills": ["Teamwork"]
        },
        "resume_bullets": ["Implemented database models"],
        "metrics": {
            "languages": ["Python", "SQL"],
            "word_count": 1500,
            "completeness_score": 0.9
        }
    }

    # Store results in DB
    store_results_in_db(project_name, merged_results, project_rank=1, project_signature=project_signature)

    # Retrieve results from DB
    retrieved_results = retrieve_results_from_db(project_signature)

    assert retrieved_results["summary"] == merged_results["summary"]
    assert retrieved_results["skills"]["technical_skills"] == merged_results["skills"]["technical_skills"]
    assert retrieved_results["skills"]["soft_skills"] == merged_results["skills"]["soft_skills"]
    assert retrieved_results["resume_bullets"] == merged_results["resume_bullets"]
    assert retrieved_results["metrics"] == merged_results["metrics"]