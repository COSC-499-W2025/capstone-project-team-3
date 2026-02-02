import pytest
from app.utils.analysis_merger_utils import merge_analysis_results,store_results_in_db
from app.utils.retrieve_insights_utils import get_projects_by_signatures
import json
import pytest

# Isolate DB for tests in this file to avoid touching app.sqlite3
from app.data import db as dbmod

@pytest.fixture(scope="function")
def isolated_db(tmp_path, monkeypatch):
    test_db = tmp_path / "analysis_merger.sqlite3"
    monkeypatch.setattr(dbmod, "DB_PATH", test_db)
    dbmod.init_db()
    # yield so tests can run using the isolated DB
    yield

def test_merge_analysis_results(isolated_db):
    
    code_analysis_results = {
        "Resume_bullets": ["Built REST API", "Wrote unit tests"],
        "Metrics": {
            "languages": ["Python"],
            "roles": ["FastAPI", "pytest"],
            "code_files_changed": 5
        }
    }
    non_code_analysis_results = {
        "project_summary": "Developed a scalable REST API using Python and FastAPI, enabling secure user authentication and data management. "  # ✅ Changed from "summary"
                   "Integrated SQLAlchemy for efficient database operations and implemented comprehensive unit tests with pytest. "
                   "Collaborated with cross-functional teams to document requirements and ensure project completeness, resulting in improved team communication and project delivery.",
        "skills": {
            "technical_skills": ["SQLAlchemy"],
            "soft_skills": ["Communication"]
        },
        "resume_bullets": ["Documented requirements"],
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
    assert "pytest" in merged["skills"]["technical_skills"]
    assert "Communication" in merged["skills"]["soft_skills"]

    # Check merged resume bullets
    assert "Built REST API." in merged["resume_bullets"]
    assert "Documented requirements." in merged["resume_bullets"]

    # Check merged metrics
    assert merged["metrics"]["languages"] == ["Python"]
    assert merged["metrics"]["word_count"] == 1000
    assert merged["metrics"]["completeness_score"] == 0.95
    
def test_store_and_retrieve_results_in_db(isolated_db):

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
            "languages": ['Python', 'SQL'],
            "word_count": 1500,
            "completeness_score": 0.9
        }
    }

    # Store results in DB
    store_results_in_db(project_name, merged_results, project_score=1, project_signature=project_signature)

    # Retrieve results from DB
    retrieved_results = get_projects_by_signatures(project_signature)

    assert retrieved_results["summary"] == merged_results["summary"]
 # Ensure all stored technical and soft skills are present in retrieved skills
    for tech_skill in merged_results["skills"]["technical_skills"]:
       assert tech_skill in retrieved_results["skills"]
    for soft_skill in merged_results["skills"]["soft_skills"]:
       assert soft_skill in retrieved_results["skills"]
    assert retrieved_results["resume_bullets"] == merged_results["resume_bullets"]
    assert retrieved_results["metrics"] == merged_results["metrics"]

def test_store_results_resets_override(isolated_db):
    project_signature = "test_project_override"
    project_name = "Override Reset Project"
    merged_results = {
        "summary": "Override reset summary.",
        "skills": {
            "technical_skills": ["Flask"],
            "soft_skills": ["Communication"]
        },
        "resume_bullets": ["Built API endpoints"],
        "metrics": {
            "languages": ["Python"],
            "completeness_score": 0.8
        }
    }

    store_results_in_db(project_name, merged_results, project_score=0.7, project_signature=project_signature)

    conn = dbmod.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE PROJECT SET score_overridden = 1, score_overridden_value = ? WHERE project_signature = ?",
        (0.5, project_signature)
    )
    conn.commit()

    store_results_in_db(project_name, merged_results, project_score=0.9, project_signature=project_signature)

    cursor.execute(
        "SELECT score_overridden, score_overridden_value FROM PROJECT WHERE project_signature = ?",
        (project_signature,)
    )
    row = cursor.fetchone()
    conn.close()

    assert row[0] == 0
    assert row[1] is None

def test_merge_with_empty_non_code_results():
    """Test merge_analysis_results handles empty non-code results gracefully."""
    code_analysis_results = {
        "resume_bullets": ["Built REST API"],
        "Metrics": {
            "languages": ["Python"],
            "roles": ["FastAPI"],
        }
    }
    
    # Empty non-code results
    non_code_analysis_results = {}
    
    project_name = "Test Project Empty"
    project_signature = "test_empty_001"
    
    merged = merge_analysis_results(
        code_analysis_results, 
        non_code_analysis_results, 
        project_name, 
        project_signature
    )
    
    # Should have a valid summary even with empty non-code
    assert "summary" in merged
    assert len(merged["summary"]) > 0
    assert project_name in merged["summary"] or "REST API" in merged["summary"]
    
    # Should still have code skills
    assert "FastAPI" in merged["skills"]["technical_skills"]
    assert "Python" in merged["skills"]["technical_skills"]
    
    # Should have code resume bullets
    assert len(merged["resume_bullets"]) > 0

def test_merge_with_none_inputs():
    """Test merge_analysis_results handles None inputs gracefully."""
    # None code results
    code_analysis_results = None
    non_code_analysis_results = {
        "project_summary": "Test summary",
        "skills": {"technical_skills": ["Python"], "soft_skills": ["Teamwork"]},
        "resume_bullets": ["Documented project"],
        "Metrics": {"word_count": 100}
    }
    
    project_name = "Test Project None"
    project_signature = "test_none_001"
    
    merged = merge_analysis_results(
        code_analysis_results, 
        non_code_analysis_results, 
        project_name, 
        project_signature
    )
    
    # Should generate a valid summary from non-code only
    assert "summary" in merged
    assert "Test summary" in merged["summary"]
    
    # When no code skills exist, non-code technical skills are filtered out
    # (this is expected behavior - technical skills need code context)
    # But soft skills should remain
    assert "Teamwork" in merged["skills"]["soft_skills"]
    
    # Should have non-code bullets
    assert "Documented project." in merged["resume_bullets"]

def test_merge_with_missing_project_summary_key():
    """Test that merger handles missing project_summary key in non-code results."""
    code_analysis_results = {
        "resume_bullets": ["Built API"],
        "Metrics": {"languages": ["Java"]}
    }
    
    non_code_analysis_results = {
        # Missing project_summary key
        "skills": {"technical_skills": ["Spring"], "soft_skills": []},
        "resume_bullets": ["Wrote docs"],
        "Metrics": {}
    }
    
    project_name = "Test Missing Key"
    project_signature = "test_missing_001"
    
    merged = merge_analysis_results(
        code_analysis_results, 
        non_code_analysis_results, 
        project_name, 
        project_signature
    )
    
    # Should still generate a summary
    assert "summary" in merged
    assert len(merged["summary"]) > 0
    # Summary should mention code achievements since no non-code summary
    assert "API" in merged["summary"]
