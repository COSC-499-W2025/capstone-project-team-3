# Data Flow Diagrams (Level 0 & Level 1)

## View the diagrams (interactive)

For a zoomable, editable view in draw.io (diagrams.net), open:

**[Productivity Dashboard DFD — diagrams.net](https://app.diagrams.net/#G10cYCpvFpWB_LUyqjNVTxVPAnlgEQ53dM#%7B%22pageId%22%3A%22CjHqhK4MZXdRkchG9Wa0%22%7D)**

The Google Drive–backed diagram may show multiple pages (e.g. Level 0 and Level 1).

## Static copies in this repository

These PNGs match the current Level 0 (context) and Level 1 diagrams:

### Level 0 — context diagram

![DFD Level 0 (context)](../screenshots/DFD_level0.png)

### Level 1 — system decomposition

![DFD Level 1](../screenshots/DFD_level1.png)

### Legend

<img src="../screenshots/Legend.png" width="200" alt="DFD legend: entity, process, data store, data flow">

---

## How the diagrams evolved

### Level 0 (context)

The **older** Level 0 mainly showed:

- User  
- Productivity Dashboard / System  
- Local File System  
- Export Storage  

The **newer** Level 0 expands context substantially. It adds:

- **Canadian Institution API** — external institutional data (e.g. for preferences or lookups).  
- **Google Gemini API** — external AI for analysis and generation.  
- **Project Cache** — internal persistent store for project-related data.

That change matters because the system is no longer modeled as “read files → produce exports” only. The context diagram now reflects **real dependencies**: external services for recommendations and AI-assisted features, and **internal cached project state**. The diagram is a more accurate picture of how the dashboard actually operates.

### Level 1 (major decomposition)

The **older** Level 1 already included processes such as:

- Folder Selection & Session Configuration  
- Consent & Preferences  
- Data and Cache Management  
- Scanning and Indexing Files  
- Extracting Metadata  
- Comparing Metadata  
- Parse Content  
- Extracting Git History / Metadata  
- Visualization Generation  
- Content Analysis & Skill Inference  
- Portfolio  
- Resume  
- Exporter  
- Project Cache  

The **newer** Level 1 **keeps** those and adds capabilities that extend the product from **analysis** into **recommendation, scoring, and job-application support**.

**Google Gemini API (explicit at Level 1)**  
Gemini appears as an external entity feeding **Content Analysis & Skill Inferences**. That makes LLM-backed behavior part of the formal model instead of leaving it implicit: downstream analysis and generation depend on that service.

**Learning recommendations**  
A **Learning Recommendations** process (learning recommender) is a major addition. The system is not only **descriptive** (analyze past work, generate documents) but also **prescriptive** (suggest what to learn or improve). It is fed from parsed content and related signals and contributes recommendations toward user-facing outputs—an extra intelligence layer. The diagram also shows ties to institutional data (e.g. **Canadian Institution API**) where relevant to preferences or context.

**Project scoring**  
**Project Scoring Configuration** formalizes a **scoring** path: the portfolio is not only a static generated artifact; the system computes an evaluation of projects (from metadata, content, and inferred signals). That moves the platform from “organizer + generator” toward **evaluator**.

**Job match score**  
**Job Match Score** is new scope: the system compares portfolio/resume/project information against **job-oriented criteria** (e.g. user-supplied job description) and produces a match score. Processed data is used not only to store and present projects but to **assess fit with opportunities**—a more career- and application-oriented DFD.

**Cover letter generation**  
**Cover Letter Generation** adds another application artifact beyond portfolio and resume, reusing structured profile and project information for **tailored application content**. Together with job match, this is a strong signal that the product evolved from a **project dashboard** toward **broader career tooling**.

**Resume in the workflow**  
In the older Level 1, **Resume** was largely an output next to **Portfolio**. In the newer diagram, **Resume** is more integrated into the right-hand workflow as an input to **Job Match Score** and **Cover Letter Generation**—it is not only an endpoint but **fuel for downstream intelligent processes**.

**Richer output / decision-support side**  
The right side grows from roughly *Portfolio → Resume → Exporter → Export Storage* to include **Project Scoring Configuration**, **Job Match Score**, and **Cover Letter Generation** before export. Outputs now include **evaluations**, **matching scores**, and **generated application content**, not only documents and visual summaries.

**Separation of analysis vs. decision support**  
Previously, ingestion, parsing, and skill inference led mostly to presentation and export. The new processes (**Learning Recommendations**, **Job Match Score**, **Cover Letter Generation**, explicit **Gemini**) show **reasoning and personalization** on top of analysis—closer to an **assistant-like** platform than a pure file-processing dashboard.

---

## Description of the system flow

When the user starts the application, they see **Consent and Preferences**. If consent is declined or revoked, stored data is removed. With consent, the user can select a **zipped project folder** from the **local file system**; the archive is unpacked, **scanned**, and **indexed**. Extracted **metadata** is compared with **Project Cache** (and related stored metadata).

If metadata matches existing analyzed work, the system can **skip re-analysis** and refresh dashboard, portfolio, and resume views as appropriate. If not, new metadata is persisted and processing continues:

1. **Timeline and productivity** — timelines and metrics feed **visualization** and reporting.  
2. **Git** — when present, commit history supports insights, contributions, timelines, and skill-related signals for the resume and portfolio.  
3. **Content parsing** — code and non-code files are parsed to support contribution narrative and **content analysis / skill inference** (with **Google Gemini** where used for summaries and inferences).

**Visualization** and **content analysis** produce graphs, reflections, **STAR-style project summaries**, and role/skill signals integrated into **Portfolio** and **Resume**. **Learning recommendations** use saved profile, resume-aligned signals, and curated resources (and institutional context where applicable) to suggest next learning steps. **Project scoring** updates how projects are ranked and presented.

The user can **edit** portfolio and resume content. **Job match** and **cover letter** flows take **resume (and related) content** plus a **job description** to produce scores and drafts. An **Exporter** writes **PDF**, **PNG**, or **JSON** to **export storage**. Users can also clear or manage stored data via the app’s data/cache flows.
