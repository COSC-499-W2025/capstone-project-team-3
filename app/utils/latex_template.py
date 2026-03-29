class ResumeTemplate:
    
    # Placeholders in LATEX_TEMPLATE are:
    # name, email, links_block, education_section,
    # skills_table, work_experience_section, projects, awards_section
    
    LATEX_TEMPLATE = r"""
    \documentclass[a4paper,11pt]{article}
    % fullpage.sty is not in BasicTeX; geometry (below) provides margins.
    \usepackage{amsmath}
    \usepackage{amssymb}
    \usepackage{textcomp}
    \usepackage[utf8]{inputenc}
    \usepackage[T1]{fontenc}
    \usepackage[hidelinks]{hyperref}
    \usepackage[left=2cm, right=2cm, top=2cm, bottom=2cm]{geometry}
    \usepackage{longtable}
    % enumitem is not in BasicTeX; approximate former:
    %   \setlist[itemize]{leftmargin=0pt, itemsep=-3pt, topsep=0pt, label=\textbullet, labelsep=0.5em}
    %   \begin{itemize}[leftmargin=1.8em] (work / awards) and [leftmargin=2em] (projects).
    \newenvironment{resumeitemize}{%
        \begin{list}{\textbullet}{%
            \setlength{\leftmargin}{1.8em}%
            \setlength{\rightmargin}{0pt}%
            \setlength{\labelwidth}{1.15em}%
            \setlength{\labelsep}{0.5em}%
            \setlength{\itemindent}{0pt}%
            \setlength{\listparindent}{0pt}%
            \setlength{\itemsep}{-3pt}%
            \setlength{\topsep}{0pt}%
            \setlength{\parsep}{0pt}%
            \setlength{\partopsep}{0pt}%
        }%
    }{\end{list}}
    \newenvironment{resumeitemizewide}{%
        \begin{list}{\textbullet}{%
            \setlength{\leftmargin}{2em}%
            \setlength{\rightmargin}{0pt}%
            \setlength{\labelwidth}{1.25em}%
            \setlength{\labelsep}{0.5em}%
            \setlength{\itemindent}{0pt}%
            \setlength{\listparindent}{0pt}%
            \setlength{\itemsep}{-3pt}%
            \setlength{\topsep}{0pt}%
            \setlength{\parsep}{0pt}%
            \setlength{\partopsep}{0pt}%
        }%
    }{\end{list}}
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
        \noindent\hrulefill \\
    }

    % Align with body text (preview uses full-width rules under headings; no negative indent).
    \newcommand{\header} [1] {
        {\noindent\vspace*{6pt} \textsc{#1}}
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
    {\Huge \scshape {{name}}}\\ % adding name of user
    \vspace{2pt}

    \vspace*{2pt}
    \href{mailto:{email}}{{{email}}}\\ % adding email of user
    {links_block} % links block (will be updated based on user info - LinkedIn, Github,...)
    \end{center}
    \vspace{1.5mm}
    {summary_section}

    \header{Education}
    \vspace{2mm}
    {education_section}
    \vspace{2mm}

    \header{Skills}
    \vspace{2mm}
    \begin{longtable}{p{4cm}p{12cm}}
    {skills_table} % skills are filled in here
    \end{longtable}
    \vspace{1mm}

    {work_experience_section}

    \header{Projects / Experience}
    \vspace{2mm}
    {projects} % projects are filled in here, includes name, skills, duration, and bullets
    \vspace{1mm}
    
    {awards_section}

    \end{document}
    """