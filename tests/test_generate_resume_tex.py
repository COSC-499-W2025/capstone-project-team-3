import pytest
from app.utils.generate_resume_tex import (
    escape_latex,
    render_skills,
    render_projects,
    render_links,
    generate_resume_tex,
)
from app.utils.latex_template import ResumeTemplate

def test_escape_latex_special_characters():
    """Tests that escape_latex escapes all LaTeX special characters."""
    text = r"& % $ # _ { } ~ ^ \\"
    escaped = escape_latex(text)

    assert r"\&" in escaped
    assert r"\%" in escaped
    assert r"\$" in escaped
    assert r"\#" in escaped
    assert r"\_" in escaped
    assert r"\{" in escaped
    assert r"\}" in escaped
    assert r"\textasciitilde{}" in escaped
    assert r"\textasciicircum{}" in escaped
    assert r"\textbackslash{}" in escaped


def test_escape_latex_unicode_normalization():
    """Tests that escape_latex normalizes Unicode punctuation to LaTeX-safe forms."""
    text = "2024 – 2025 — “quote” ’test’"
    escaped = escape_latex(text)

    assert "--" in escaped
    assert "---" in escaped
    assert "``quote''" in escaped
    assert "'test'" in escaped

def test_render_skills_basic():
    """Tests that render_skills produces LaTeX table rows for each skill category."""
    skills = {
        "Languages": ["Python", "C++"],
        "Frameworks": ["Flask", "Django"],
    }

    rendered = render_skills(skills)

    assert "Languages:" in rendered
    assert "Python, C++" in rendered
    assert "Frameworks:" in rendered
    assert "Flask, Django" in rendered
    assert r"\\" in rendered

def test_render_projects_single_project():
    """
    render_projects should render a project with title, skills, dates, and bullets.
    """
    projects = [
        {
            "title": "alpha project",
            "dates": "Jan 2024 – Jun 2024",
            "skills": "Python, Flask",
            "bullets": [
                "Built backend services",
                "Designed REST APIs",
            ],
        }
    ]

    rendered = render_projects(projects)

    assert r"\textbf{Alpha project}" in rendered
    assert "Jan 2024" in rendered
    assert r"\textbf{Skills: }" in rendered
    assert r"\item Built backend services" in rendered
    assert r"\item Designed REST APIs" in rendered


def test_render_projects_flattens_nested_bullets():
    """
    render_projects should flatten nested bullet structures.
    """
    projects = [
        {
            "title": "test",
            "dates": "",
            "skills": "",
            "bullets": [
                ["Bullet A", "Bullet B"],
                "Bullet C",
                None,
            ],
        }
    ]

    rendered = render_projects(projects)

    assert r"\item Bullet A" in rendered
    assert r"\item Bullet B" in rendered
    assert r"\item Bullet C" in rendered


def test_render_projects_empty_bullets_safe():
    """
    render_projects should safely handle missing or empty bullets.
    """
    projects = [
        {
            "title": "empty",
            "dates": "",
            "skills": "",
        }
    ]

    rendered = render_projects(projects)

    assert r"\begin{itemize}" in rendered
    assert r"\end{itemize}" in rendered

def test_render_links_multiple():
    """
    render_links should render multiple links separated by \\quad.
    """
    links = [
        {"label": "GitHub", "url": "https://github.com/test"},
        {"label": "Portfolio", "url": "https://example.com"},
    ]

    rendered = render_links(links)

    assert r"\href{https://github.com/test}{GitHub}" in rendered
    assert r"\quad" in rendered
    assert r"\href{https://example.com}{Portfolio}" in rendered


def test_render_links_empty():
    """
    render_links should return an empty string when no links are provided.
    """
    assert render_links([]) == ""

def test_generate_resume_tex_happy_path():
    """
    generate_resume_tex should populate all required LaTeX template placeholders.
    """
    resume = {
        "name": "John Doe",
        "email": "john@example.com",
        "links": [{"label": "GitHub", "url": "https://github.com/johndoe"}],
        "education": [
            {
                "school": "University X",
                "degree": "BSc Computer Science",
                "dates": "2019 – 2023",
                "gpa": "3.8",
            }
        ],
        "skills": {
            "Languages": ["Python", "SQL"],
        },
        "projects": [
            {
                "title": "project one",
                "dates": "2024",
                "skills": "Python",
                "bullets": ["Did something"],
            }
        ],
    }

    tex = generate_resume_tex(resume)

    assert "John Doe" in tex
    assert "john@example.com" in tex
    assert "University X" in tex
    assert "BSc Computer Science" in tex
    assert "GPA: 3.8" in tex
    assert r"\item Did something" in tex
    assert r"\href{https://github.com/johndoe}{GitHub}" in tex


def test_generate_resume_tex_no_gpa():
    """
    generate_resume_tex should omit GPA line when GPA is empty.
    """
    resume = {
        "name": "Jane",
        "email": "jane@example.com",
        "links": [],
        "education": [
            {
                "school": "Uni",
                "degree": "CS",
                "dates": "",
                "gpa": "",
            }
        ],
        "skills": {"Skills": []},
        "projects": [],
    }

    tex = generate_resume_tex(resume)

    assert "GPA:" not in tex


def test_generate_resume_tex_multiple_education():
    """
    generate_resume_tex should handle multiple education entries.
    """
    resume = {
        "name": "Alice Smith",
        "email": "alice@example.com",
        "links": [],
        "education": [
            {
                "school": "University A",
                "degree": "MSc Computer Science",
                "dates": "2022 – 2024",
                "gpa": "4.0",
            },
            {
                "school": "College B",
                "degree": "BSc Mathematics",
                "dates": "2018 – 2022",
                "gpa": "3.7",
            }
        ],
        "skills": {"Skills": ["Python"]},
        "projects": [],
    }

    tex = generate_resume_tex(resume)

    # Both education entries should be in the output
    assert "University A" in tex
    assert "MSc Computer Science" in tex
    assert "GPA: 4.0" in tex
    assert "College B" in tex
    assert "BSc Mathematics" in tex
    assert "GPA: 3.7" in tex
