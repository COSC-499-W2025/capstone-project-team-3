from typing import List, Dict, Any
import tempfile
import os
import json
from jinja2 import Template
from app.utils.latex_template import ResumeTemplate

def escape_latex(text: str) -> str:
    """
    Escapes LaTeX special characters to avoid compilation issues later.
    """
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
        # Normalize Unicode dashes/quotes to LaTeX-friendly forms
        "–": "--",   # en dash
        "—": "---",  # em dash
        "“": "``",
        "”": "''",
        "’": "'",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def render_skills(skills: Dict[str, List[str]]) -> str:
    """Return LaTeX longtable rows for skills."""
    rows = []
    for category, items in skills.items():
        escaped_items = ", ".join(escape_latex(i) for i in items)
        rows.append(f"{escape_latex(category)}: & {escaped_items} \\\\")
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

        block = rf""" \vspace*{{3mm}}
	\textbf{{{escape_latex(title_cap)}}} \hfill {escape_latex(project['dates'])}\\
    {{\textbf{{Skills: }}\sl {escape_latex(project['skills'])}}}\\[1mm]
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
    
def generate_resume_tex(resume: Dict[str, Any]) -> str:
    """Return LaTeX resume document rendered from the resume model."""
    tex = ResumeTemplate.LATEX_TEMPLATE

    tex = tex.replace("{name}", escape_latex(resume["name"]))
    tex = tex.replace("{email}", escape_latex(resume["email"]))

    links_block = render_links(resume.get("links", []))
    tex = tex.replace("{links_block}", links_block)

    tex = tex.replace("{edu_school}", escape_latex(resume["education"]["school"]))
    tex = tex.replace("{edu_degree}", escape_latex(resume["education"]["degree"]))
    tex = tex.replace("{edu_dates}", escape_latex(resume["education"]["dates"]))
    gpa_val = escape_latex(str(resume.get("education", {}).get("gpa", "")).strip())
    edu_gpa_line = rf"{{\sl GPA: {gpa_val}}}\\" if gpa_val else ""
    tex = tex.replace("{edu_gpa_line}", edu_gpa_line)

    tex = tex.replace("{skills_table}", render_skills(resume["skills"]))
    tex = tex.replace("{projects}", render_projects(resume["projects"]))

    return tex