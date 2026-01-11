from typing import List, Dict
import tempfile
import os
import json
from jinja2 import Template

LATEX_TEMPLATE = r"""
\documentclass[a4paper]{article}
\usepackage{fullpage}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{textcomp}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[hidelinks]{hyperref}
\usepackage[left=2cm, right=2cm, top=2cm]{geometry}
\usepackage{longtable}
\usepackage{enumitem}
% Align itemize bullets with left margin and tighten spacing
\setlist[itemize]{leftmargin=0pt, itemsep= -3pt, topsep=0pt, label=\textbullet, labelsep=0.5em}
\textheight=10in
\pagestyle{empty}
\raggedright

\def\bull{\vrule height 0.8ex width .7ex depth -.1ex }

\newcommand{\area} [2] {
    \vspace*{-9pt}
    \begin{verse}
        \textbf{#1}   #2
    \end{verse}
}

\newcommand{\lineunder} {
    \vspace*{-8pt} \\
    \hspace*{-18pt} \hrulefill \\
}

\newcommand{\header} [1] {
    {\hspace*{-18pt}\vspace*{6pt} \textsc{#1}}
    \vspace*{-6pt} \lineunder
}
\newcommand{\employer} [3] {
    { \textbf{#1} (#2)\\ \underline{\textbf{\emph{#3}}}\\  }
}

\newcommand{\contact} [3] {
    \vspace*{-10pt}
    \begin{center}
        {\Huge \scshape {#1}}\\
        #2 \\ #3
    \end{center}
    \vspace*{-8pt}
}

\newenvironment{achievements}{
    \begin{list}
        {$\bullet$}{\topsep 0pt \itemsep -2pt}}{\vspace*{4pt}
    \end{list}
}

\newcommand{\schoolwithcourses} [4] {
    \textbf{#1} #2 $\bullet$ #3\\
    #4 \\
    \vspace*{5pt}
}

\newcommand{\school} [4] {
    \textbf{#1} #2 $\bullet$ #3\\
    #4 \\
}
        
\begin{document}
\vspace*{-40pt}

\vspace*{-2pt}
\begin{center}
{\Huge \scshape {{name}}}\\
\vspace{2pt}

\vspace*{2pt}
\href{mailto:{email}}{{{email}}}\\
{links_block}
\end{center}

\header{Education}
\vspace{2mm}
\textbf{{edu_school}}\\
{edu_degree} \hfill {edu_dates}\\
{edu_gpa_line}
\vspace{2mm}

\header{Skills}
\vspace{2mm}
\begin{longtable}{p{4cm}p{12cm}}
{skills_table}
\end{longtable}
\vspace{1mm}

\header{Projects / Experience}
\vspace{2mm}
{projects}

\end{document}
"""

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
    rows = []
    for category, items in skills.items():
        escaped_items = ", ".join(escape_latex(i) for i in items)
        rows.append(f"{escape_latex(category)}: & {escaped_items} \\\\")
    return "\n".join(rows)


def render_projects(projects: List[Dict]) -> str:
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
    
def generate_resume_tex(resume):
    tex = LATEX_TEMPLATE

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