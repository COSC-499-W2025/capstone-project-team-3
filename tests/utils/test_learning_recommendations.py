from app.utils.learning_recommendations import (
    extract_user_tag_weights,
    normalize_tag,
    recommend_courses,
    score_course_base,
)


def test_normalize_tag():
    assert normalize_tag("  Python  ") == "python"
    assert normalize_tag("Machine Learning") == "machine-learning"
    assert normalize_tag("C++") == "c++"


def test_extract_user_tag_weights_skills_and_job():
    resume = {
        "skills": {"Proficient": ["Python", "React"], "Familiar": ["SQL"]},
        "projects": [{"skills": "Docker, Kubernetes"}],
        "personal_summary": "I love building APIs with FastAPI.",
    }
    w = extract_user_tag_weights(resume, job_title="Software Engineer", industry="Technology")
    assert w["python"] >= 3.0
    assert w["react"] >= 3.0
    assert w["sql"] >= 2.0
    assert w["docker"] >= 2.5
    assert w["software"] >= 2.0
    assert w["engineer"] >= 2.0
    assert w["technology"] >= 2.0


def test_score_course_base_overlap():
    user = {"python": 3.0, "web": 2.0}
    assert score_course_base(["python", "rust"], user) == 3.0
    assert score_course_base(["python", "web"], user) == 5.0


def test_recommend_courses_starter_and_advanced_ordering():
    catalog = [
        {
            "id": "s1",
            "title": "A",
            "description": "",
            "url": "https://a",
            "thumbnail_url": "",
            "provider": "p",
            "tags": ["python"],
            "level": "starter",
            "pricing": "free",
        },
        {
            "id": "s2",
            "title": "B",
            "description": "",
            "url": "https://b",
            "thumbnail_url": "",
            "provider": "p",
            "tags": ["rust"],
            "level": "starter",
            "pricing": "free",
        },
        {
            "id": "a1",
            "title": "Adv Py",
            "description": "",
            "url": "https://c",
            "thumbnail_url": "",
            "provider": "p",
            "tags": ["python", "deep-learning"],
            "level": "advanced",
            "pricing": "free",
        },
        {
            "id": "a2",
            "title": "Adv Rust",
            "description": "",
            "url": "https://d",
            "thumbnail_url": "",
            "provider": "p",
            "tags": ["rust"],
            "level": "advanced",
            "pricing": "free",
        },
    ]
    resume = {"skills": {"Proficient": ["Python"], "Familiar": []}, "projects": [], "personal_summary": ""}
    starters, advanced = recommend_courses(
        catalog, resume, job_title="", industry="", starter_limit=5, advanced_limit=5
    )
    assert [c["id"] for c in starters] == ["s1", "s2"]
    # Top starters include python; advanced with python should rank before rust-only if tied on user tags
    assert advanced[0]["id"] == "a1"


def test_recommend_courses_falls_back_when_no_overlap():
    catalog = [
        {
            "id": "x",
            "title": "X",
            "description": "",
            "url": "https://x",
            "thumbnail_url": "",
            "provider": "p",
            "tags": ["zig"],
            "level": "starter",
            "pricing": "free",
        },
        {
            "id": "y",
            "title": "Y",
            "description": "",
            "url": "https://y",
            "thumbnail_url": "",
            "provider": "p",
            "tags": ["zig"],
            "level": "advanced",
            "pricing": "free",
        },
    ]
    resume = {"skills": {"Proficient": [], "Familiar": []}, "projects": [], "personal_summary": ""}
    starters, advanced = recommend_courses(catalog, resume, starter_limit=2, advanced_limit=2)
    assert len(starters) == 1
    assert len(advanced) == 1
