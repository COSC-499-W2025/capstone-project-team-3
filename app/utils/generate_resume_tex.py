from typing import List, Dict, Any
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
{{\sl {degree}}}\\
{gpa_line}"""
        blocks.append(block.strip())
    
    return "\n\n".join(blocks)
    
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
    tex = tex.replace("{projects}", render_projects(resume["projects"]))

    return tex