class ResumeTemplate:
    
    # Placeholders in LATEX_TEMPLATE are:
    # name, email, links_block, education_section,
    # skills_table, projects
    
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
    {\Huge \scshape {{name}}}\\ % adding name of user
    \vspace{2pt}

    \vspace*{2pt}
    \href{mailto:{email}}{{{email}}}\\ % adding email of user
    {links_block} % links block (will be updated based on user info - LinkedIn, Github,...)
    \end{center}

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

    \header{Projects / Experience}
    \vspace{2mm}
    {projects} % projects are filled in here, includes name, skills, duration, and bullets

    \end{document}
    """