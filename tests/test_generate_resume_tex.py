import pytest
from app.utils.generate_resume_tex import (
    escape_latex,
    render_skills,
    render_projects,
    render_links,
    render_awards,
    render_work_experience,
    render_summary,
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

    assert r"\textbf{Languages:}" in rendered
    assert "Python, C++" in rendered
    assert r"\textbf{Frameworks:}" in rendered
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

    assert r"\begin{resumeitemizewide}" in rendered
    assert r"\end{resumeitemizewide}" in rendered

def test_render_links_multiple():
    """
    render_links should render multiple links separated by " | " (same as preview).
    """
    links = [
        {"label": "GitHub", "url": "https://github.com/test"},
        {"label": "Portfolio", "url": "https://example.com"},
    ]

    rendered = render_links(links)

    assert r"\href{https://github.com/test}{GitHub}" in rendered
    assert " | " in rendered
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


def test_render_awards_empty_returns_empty_string():
    assert render_awards([]) == ""
    assert render_awards(None) == ""


def test_render_awards_renders_month_year_and_details():
    awards = [
        {
            "title": "Hackathon Winner",
            "issuer": "Tech Challenge Inc.",
            "date": "2025-03",
            "details": ["Won first place", "Presented demo to judges"],
        },
    ]
    rendered = render_awards(awards)
    assert r"\header{Awards \& Honours}" in rendered
    assert r"\textbf{Hackathon Winner}" in rendered
    assert "Mar 2025" in rendered
    assert "Tech Challenge Inc." in rendered
    assert r"\item Won first place" in rendered


def test_render_work_experience_empty_returns_empty_string():
    assert render_work_experience([]) == ""
    assert render_work_experience(None) == ""


def test_render_work_experience_renders_role_company_date_and_details():
    work_experience = [
        {
            "role": "Software Engineer",
            "company": "Tech Challenge Inc.",
            "start_date": "2024-01",
            "end_date": "2024-06",
            "details": ["Built backend services", "Led collaboration efforts"],
        },
    ]
    rendered = render_work_experience(work_experience)

    assert r"\header{Work Experience}" in rendered
    # UI format: Company | Role (both bold) on same line as date
    assert r"\textbf{Tech Challenge Inc. | Software Engineer}" in rendered
    assert "Jan 2024" in rendered
    assert "Jun 2024" in rendered
    assert "Tech Challenge Inc." in rendered
    assert r"\item Built backend services" in rendered
    assert r"\item Led collaboration efforts" in rendered


def test_generate_resume_tex_renders_work_experience_section():
    resume = {
        "name": "John Doe",
        "email": "john@example.com",
        "links": [],
        "education": [],
        "skills": {"Skills": ["Python"]},
        "projects": [],
        "work_experience": [
            {
                "role": "Software Engineer",
                "company": "Tech Challenge Inc.",
                "start_date": "2024-01",
                "end_date": "2024-06",
                "details": ["Built backend services"],
            }
        ],
        "awards": [],
    }

    tex = generate_resume_tex(resume)
    assert r"\header{Work Experience}" in tex
    # UI format: Company | Role (both bold)
    assert r"\textbf{Tech Challenge Inc. | Software Engineer}" in tex
    assert "Tech Challenge Inc." in tex
    assert r"\item Built backend services" in tex


# ---------------------------------------------------------------------------
# render_summary tests
# ---------------------------------------------------------------------------

def test_render_summary_empty_string_returns_empty():
    """render_summary should return '' when given an empty string."""
    assert render_summary("") == ""


def test_render_summary_whitespace_only_returns_empty():
    """render_summary should return '' when given only whitespace."""
    assert render_summary("   ") == ""


def test_render_summary_none_returns_empty():
    """render_summary should return '' when given None (treated as falsy)."""
    assert render_summary(None) == ""  # type: ignore[arg-type]


def test_render_summary_produces_header():
    """render_summary should include the Professional Summary header."""
    rendered = render_summary("Experienced developer.")
    assert r"\header{Professional Summary}" in rendered


def test_render_summary_includes_escaped_text():
    """render_summary should include the LaTeX-escaped summary text."""
    rendered = render_summary("Experienced developer & team lead.")
    assert r"\&" in rendered  # & should be escaped
    assert "Experienced developer" in rendered


def test_render_summary_strips_leading_trailing_whitespace():
    """render_summary should strip surrounding whitespace from the summary."""
    rendered = render_summary("  Some summary.  ")
    assert "Some summary." in rendered
    # No leading/trailing spaces in the embedded text
    assert "  Some summary.  " not in rendered


def test_generate_resume_tex_includes_summary_when_present():
    """generate_resume_tex should render the Professional Summary section when personal_summary is set."""
    resume = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "links": [],
        "education": [],
        "skills": {"Languages": ["Python"]},
        "projects": [],
        "personal_summary": "Passionate engineer with 5 years of experience.",
    }

    tex = generate_resume_tex(resume)

    assert r"\header{Professional Summary}" in tex
    assert "Passionate engineer with 5 years of experience." in tex


def test_generate_resume_tex_omits_summary_when_absent():
    """generate_resume_tex should not include a Professional Summary section when personal_summary is missing."""
    resume = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "links": [],
        "education": [],
        "skills": {"Languages": ["Python"]},
        "projects": [],
    }

    tex = generate_resume_tex(resume)

    assert r"\header{Professional Summary}" not in tex


def test_generate_resume_tex_omits_summary_when_none():
    """generate_resume_tex should not include a Professional Summary section when personal_summary is None."""
    resume = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "links": [],
        "education": [],
        "skills": {"Languages": ["Python"]},
        "projects": [],
        "personal_summary": None,
    }

    tex = generate_resume_tex(resume)

    assert r"\header{Professional Summary}" not in tex
