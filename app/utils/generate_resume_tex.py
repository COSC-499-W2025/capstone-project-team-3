from typing import List, Dict, Any
from datetime import datetime
import tempfile
import os
import json
import re
from jinja2 import Template
from app.utils.latex_template import ResumeTemplate

def escape_latex(text: str) -> str:
    """
    Escapes LaTeX special characters to avoid compilation issues later.
    """
    # Normalize Unicode punctuation first
    text = (text.replace("–", "--")
             .replace("—", "---")
             .replace("“", "``")
             .replace("”", "''")
             .replace("’", "'"))
    mapping = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
        "\\": r"\textbackslash{}",
    }
    return re.sub(r'[&%$#_{}~^\\]', lambda m: mapping[m.group(0)], text)


def render_summary(summary: str) -> str:
    """Return a LaTeX Professional Summary section block, or empty string if no summary."""
    if not summary or not summary.strip():
        return ""
    return (
        r"\header{Professional Summary}" + "\n"
        r"\vspace{2mm}" + "\n"
        f"{escape_latex(summary.strip())}\n"
        r"\vspace{2mm}" + "\n"
    )


def render_skills(skills: Dict[str, List[str]]) -> str:
    """Return LaTeX longtable rows for skills."""
    rows = []
    for category, items in skills.items():
        # Avoid rendering empty buckets/sections (e.g., Familiar may be empty).
        if not items:
            continue
        escaped_items = ", ".join(escape_latex(i) for i in items)
        # Match the recruiter-friendly styling used in the UI by making labels bold.
        # Put the colon inside the bold wrapper so "Proficient:" / "Familiar:" is fully bold.
        rows.append(f"\\textbf{{{escape_latex(category)}:}} & {escaped_items} \\\\")
    return "\n".join(rows)


def render_projects(projects: List[Dict]) -> str:
    """Return LaTeX blocks for projects with normalized bullet lists."""
    blocks = []
    for project in projects:
        raw_bullets = project.get("bullets", [])

        # Normalize bullets to a flat list of strings
        if isinstance(raw_bullets, str):
            s = raw_bullets.strip()
            try:
                parsed = json.loads(s)
                if isinstance(parsed, list):
                    bullet_list = parsed
                else:
                    bullet_list = [str(parsed)]
            except Exception:
                bullet_list = [s]
        elif isinstance(raw_bullets, (list, tuple, set)):
            bullet_list = list(raw_bullets)
        else:
            bullet_list = [str(raw_bullets)]

        # Flatten any nested sequences inside the list
        flat_bullets: List[str] = []
        for b in bullet_list:
            if b is None:
                continue
            if isinstance(b, (list, tuple, set)):
                flat_bullets.extend(str(x) for x in b if x is not None)
            elif isinstance(b, str) and b.strip().startswith("[") and b.strip().endswith("]"):
                try:
                    inner = json.loads(b.strip())
                    if isinstance(inner, list):
                        flat_bullets.extend(str(x) for x in inner)
                    else:
                        flat_bullets.append(str(inner))
                except Exception:
                    flat_bullets.append(b)
            else:
                flat_bullets.append(str(b))

        bullets_tex = "\n".join(
            f"\\item {escape_latex(item)}" for item in flat_bullets if str(item).strip()
        )
        # Capitalize only the first letter of the project title
        def capitalize_first(s: str) -> str:
            return s[:1].upper() + s[1:] if s else s

        title_cap = capitalize_first(project.get('title', ''))

        # Normalize skills to string (saved resumes use list, master/preview use string)
        raw_skills = project.get("skills", [])
        skills_str = ", ".join(raw_skills) if isinstance(raw_skills, (list, tuple)) else str(raw_skills)

        block = rf""" \vspace*{{3mm}}
	\textbf{{{escape_latex(title_cap)}}} \hfill {escape_latex(project['dates'])}\\
    {{\textbf{{Skills: }}\sl {escape_latex(skills_str)}}}\\[1mm]
    \begin{{itemize}}[leftmargin=2em]
{bullets_tex}
\end{{itemize}}
"""
        blocks.append(block)

    return "\n".join(blocks)

def render_links(links):
    if not links:
        return ""

    rendered = []
    for link in links:
        rendered.append(
            rf"\textbf{{\href{{{escape_latex(link['url'])}}}{{{escape_latex(link['label'])}}}}}"
        )

    return " \\quad ".join(rendered)

def render_education(education_list: List[Dict[str, Any]]) -> str:
    """Return LaTeX blocks for education entries."""
    if not education_list:
        return ""
    
    blocks = []
    for edu in education_list:
        school = escape_latex(edu.get("school", ""))
        degree = escape_latex(edu.get("degree", ""))
        dates = escape_latex(edu.get("dates", ""))
        gpa = escape_latex(str(edu.get("gpa", "")).strip())
        
        # Build GPA line if available
        gpa_line = rf"{{\sl GPA: {gpa}}}\\" if gpa else ""
        
        block = rf"""{school} \hfill {dates}\\
{degree}\\
{gpa_line}"""
        blocks.append(block.strip())
    
    return "\n\n".join(blocks)


def format_month_year(value: str) -> str:
    """
    Convert "YYYY-MM" or "YYYY-MM-01" into "Mon YYYY".
    Returns empty string for invalid inputs.
    """
    if not value:
        return ""
    try:
        # Accept YYYY-MM
        if len(value) == 7 and value[4] == "-":
            dt = datetime.fromisoformat(value + "-01")
        else:
            dt = datetime.fromisoformat(value)
        return dt.strftime("%b %Y")
    except Exception:
        return ""


def render_awards(awards: Any) -> str:
    """Return LaTeX blocks for awards/honours."""
    if not awards or not isinstance(awards, list):
        return ""

    # Filter to dict entries with at least a title.
    normalized = [
        a for a in awards
        if isinstance(a, dict) and str(a.get("title", "")).strip()
    ]
    if not normalized:
        return ""

    items_tex: List[str] = []
    for award in normalized:
        title = escape_latex(str(award.get("title", "")).strip())
        issuer_raw = str(award.get("issuer", "")).strip() if award.get("issuer") else ""
        issuer = escape_latex(issuer_raw) if issuer_raw else ""
        date_raw = str(award.get("date", "")).strip() if award.get("date") else ""
        date = escape_latex(format_month_year(date_raw)) if date_raw else ""

        details_raw = award.get("details", []) or []
        if isinstance(details_raw, str):
            details_list = [line.strip() for line in details_raw.splitlines() if line.strip()]
        elif isinstance(details_raw, list):
            details_list = [str(d).strip() for d in details_raw if str(d).strip()]
        else:
            details_list = []

        details_block = ""
        if details_list:
            details_items = "\n".join(
                rf"\item {escape_latex(d)}" for d in details_list
            )
            details_block = (
                "\n" +
                rf"\begin{{itemize}}[leftmargin=1.8em]" + "\n" +
                details_items + "\n" +
                r"\end{itemize}"
            )

        header_line = rf"\textbf{{{title}}}"
        if date:
            header_line += rf" \hfill {date}"

        issuer_line = rf"{issuer}\\" if issuer else ""

        block = rf"{header_line}\\{issuer_line}{details_block}"
        items_tex.append(block)

    awards_body = "\n\n".join(items_tex)
    return (
        r"\header{Awards \& Honours}" "\n"
        r"\vspace{2mm}" "\n"
        f"{awards_body}\n"
    )


def render_work_experience(work_experience: Any) -> str:
    """Return LaTeX blocks for work experience."""
    if not work_experience or not isinstance(work_experience, list):
        return ""

    normalized = [
        e
        for e in work_experience
        if isinstance(e, dict) and str(e.get("role", "")).strip()
    ]
    if not normalized:
        return ""

    items_tex: List[str] = []
    for entry in normalized:
        role_raw = str(entry.get("role", "")).strip()
        role = escape_latex(role_raw)

        company_raw = str(entry.get("company", "")).strip() if entry.get("company") else ""
        company = escape_latex(company_raw) if company_raw else ""

        start_raw = str(entry.get("start_date", "")).strip() if entry.get("start_date") else ""
        end_raw = str(entry.get("end_date", "")).strip() if entry.get("end_date") else ""
        start_fmt = escape_latex(format_month_year(start_raw)) if start_raw else ""
        end_fmt = escape_latex(format_month_year(end_raw)) if end_raw else ""

        date_range = ""
        if start_fmt:
            if end_fmt:
                date_range = f"{start_fmt} – {end_fmt}"
            else:
                date_range = f"{start_fmt} – Present"

        details_raw = entry.get("details", []) or []
        if isinstance(details_raw, str):
            details_list = [line.strip() for line in details_raw.splitlines() if line.strip()]
        elif isinstance(details_raw, list):
            details_list = [str(d).strip() for d in details_raw if str(d).strip()]
        else:
            details_list = []

        details_block = ""
        if details_list:
            details_items = "\n".join(rf"\item {escape_latex(d)}" for d in details_list)
            details_block = (
                "\n" + rf"\begin{{itemize}}[leftmargin=1.8em]" + "\n" +
                details_items + "\n" +
                r"\end{itemize}"
            )

        if company:
            header_text = rf"\textbf{{{company} | {role}}}"
        else:
            header_text = rf"\textbf{{{role}}}"
        header_line = header_text
        if date_range:
            header_line += rf" \hfill {date_range}"

        block = rf"{header_line}\\{details_block}"
        items_tex.append(block)

    work_body = "\n\n".join(items_tex)
    return (
        r"\header{Work Experience}" "\n"
        r"\vspace{2mm}" "\n"
        f"{work_body}\n"
        r"\vspace{1mm}" "\n"
    )
    
def generate_resume_tex(resume: Dict[str, Any]) -> str:
    """Return LaTeX resume document rendered from the resume model."""
    tex = ResumeTemplate.LATEX_TEMPLATE

    tex = tex.replace("{name}", escape_latex(resume["name"]))
    tex = tex.replace("{email}", escape_latex(resume["email"]))

    links_block = render_links(resume.get("links", []))
    tex = tex.replace("{links_block}", links_block)

    # Handle education - now supports multiple entries
    education_list = resume.get("education", [])
    if isinstance(education_list, list):
        education_block = render_education(education_list)
    else:
        # Fallback for old single-object format
        education_block = render_education([education_list])
    
    # Replace old placeholders with new education block
    tex = tex.replace("{edu_school}", "")
    tex = tex.replace("{edu_degree}", "")
    tex = tex.replace("{edu_dates}", "")
    tex = tex.replace("{edu_gpa_line}", "")
    
    # Replace with new education section
    tex = tex.replace("{education_section}", education_block)

    tex = tex.replace("{skills_table}", render_skills(resume["skills"]))
    tex = tex.replace("{summary_section}", render_summary(resume.get("personal_summary") or ""))
    tex = tex.replace("{work_experience_section}", render_work_experience(resume.get("work_experience", [])))
    tex = tex.replace("{projects}", render_projects(resume["projects"]))
    tex = tex.replace("{awards_section}", render_awards(resume.get("awards", [])))

    return tex