# **Features Proposal for Project** 

**Team Number**: 3  
**Team Members**: Afua Frempong 90434176,  Karim Jassani 19370717,  Karim Khalil 38485272, Oluwadabira Omotoso 84518448, Shreya Saxena 41969981, Vanshika Singla 71669675

## 1. **​​Project Scope and Usage Scenario:**

The core usage scenario involves **students, recent graduates, and working professionals** who wish to gain insights into their local project contributions and productivity. Users will run the application locally, grant consent for file access, and provide a file path to their project folder. The system will scan the folder, extract useful metadata including Git commit history (if a Git repository is provided) and generate an actionable and comprehensive dashboard. This dashboard will highlight project contributions, time spent, and skills learned, enabling users to tailor their resume for job postings and reflect on their personal productivity patterns for improvement. Our application will also analyze the content present in the files and provide the user with a summary of what they have been working on. These insights help users tailor their resumes, present their strongest work in applications, and reflect on their personal productivity and growth.

## 2. **Proposed Solution:** 

Our proposed solution is an **OS-agnostic, offline local desktop application** that acts as a powerful insights producer and work productivity tracker. Special features include **customizable dashboard** and **visualizations** of work completed within a specified scope and timeframe. Our tool offers a unique value proposition by integrating data from various local file types, scanning for code repositories, and generating tailored **professional resume summaries** based off of project work and contributions. Rather than simply displaying raw project data, our dashboard highlights the most important artifacts from the user’s directory and turns them into relevant, actionable insights.  

The clean design and intuitive interface will ensure accessibility for first-time users, while the ability to refine and export content makes it a practical tool for professionals looking to articulate their impact with precision and ease.   

We generate points that summarize key contributions and can be further refined based on user input, or exported for future reference, making the output directly usable for resumes, portfolios, or self-assessment.  

What makes our solution stand out is that we place a very high priority on accuracy. To achieve this, we carefully filter and validate relevant data, while also involving the user’s input to help identify what information truly matters. By combining automated analysis with guided user feedback, we reduce noise, focus on contextually important artifacts, and ensure that the insights presented are both precise and trustworthy. 

## 3. **Use Cases**

## UML Use Case Diagram
![UML Use Case Diagram](UML_Use_Case_Diagram_(Final).png)

## **UC1 — Provide Consent**

**Primary actor:** User  
**Description:** User reviews and grants local file-access consent required for analysis.  
**Precondition:** App launched successfully.  
**Postcondition:** Consent recorded and stored locally; OS permissions granted.  
**Main Scenario:**

1. User launches the application.  
2. System displays consent notice describing required local access and analysis scope.  
3. User accepts consent.  
4. System stores consent flag and requests OS permissions if needed.  
5. System confirms consent and permissions status. 

**Extensions:**

* 1a. **User declines consent:** System blocks analysis features; offers to exit or view privacy policy.  
* 4a. **OS permission denied:** System guides user to OS settings and retries permission check.

## **UC2 — Select Project Folder**

**Primary actor:** User  
**Description:** User provides a local folder path to analyze.  
**Precondition:** Consent granted.  
**Postcondition:** Validated folder path saved; ready for scanning.  
**Main Scenario:**

1. User chooses “Add Project Folder”.  
2. System opens native folder picker.  
3. User selects the zipped folder.  
4. System validates access and readability.  
5. System stores the path in the local project list. 

**Extensions:**

* 4a. **Inaccessible folder:** Show error with guidance; allow re-selection.  
* 4b. **Large directory warning:** Offer estimation of scan time and allow continue/cancel (Keeping user informed)  
* 4c. **Incorrect Format:** Files that are not in an accepted format will return an error to the user

## **UC3 — User Preference Selection**  

**Primary actor:** User  
**Description:** User specifies details about themselves (industry & education) before scanning.  
**Precondition:** Project folder selected  
**Postcondition:** User selections fulfilled and applied to subsequent scans.  
**Main Scenario:**

1. User selects from the drop-down the industry   
2. User selects from the drop-down the education   
3. System validates settings and saves them. 

**Extensions:**

* 1a. **Custom industry entered:** System validates free-text input (length/characters) and stores it as “Custom: \<value\>”.  
* 2b. **Custom education entered:** System validates free-text input and stores it as “Custom: \<value\>”.  
* 3a. **Profile lock (privacy settings prohibit storing prefs):** System asks to allow local-only storage or continue without saving (preferences applied for current session only).  
*  3b. **Reset to defaults:** User clicks “Reset”; System restores default industry/education and clears custom overrides.

## **UC4 — Scan & Index Files**

**Primary actor:** System (triggered by User)  
**Description:** System crawls the folder, indexes metadata, and populates the local database.  
**Precondition:** URL/folder location available.  
**Postcondition:** Store log of metadata for accessed files into local database.  
**Main Scenario:**

1. User clicks “Scan Project”.  
2. System enumerates files respecting filters/exclusions.  
3. System extracts and stores file metadata.  
4. System detects unsupported file types and marks them.  
5. System distinguishes collaborative projects from individual projects  
6. System writes indexed metadata to the local database.

**Extensions:**

* 2a. **I/O error during enumeration:** Error message; ask the user to retry.  
* 3a. Compare with the stored metadata, if data is the same- load the same dashboard.  
* 4a. File types that are not accepted will be greyed out and omitted from the scan  
* 6a. **Database write failure:** System retries; if persistent

## **UC5 — Extract Git History**

**Primary actor: System**  
**Supporting actor:** Git Repository  
**Description:** If the folder is a Git repo, extract commits, authors, diffs, and timestamps (git logs).  
**Precondition:** Scan & Index Files completed; Git analysis enabled; `.git` directory present.  
**Postcondition:** Git metadata extracted and stored for faster analytics later in case the same data is provided  
**Main Scenario:**

1. System detects `.git` and repo status.  
2. System runs read-only Git commands to fetch commit metadata and diffs.  
3. System distinguishes collaborative projects from individual projects  
4. System maps changes to files and timestamps.

 **Extensions:**

* 1a. **No Git repo found:** Skip gracefully; proceed with file-only insights.

## **UC6.1 — Analyze Non Code Content & Extract Skills**

**Primary actor:** System  
**Description:** Apply local NLP file analysis to infer topics, languages, frameworks, contributions and skills from file contents  
**Precondition:** Content scan and indexed data  
**Postcondition:** Analysis results stored per file/project.  
**Main Scenario:**

1. System accesses relevant scanned files and stored data.  
2. System runs local NLP & file analysis on non-code files  
3. Extrapolate individual contributions for given collaborative projects   
4. System aggregates topics (topics, contributions and skills) and computes analysis results.

**Extensions:**

* 2a. **Ambiguous or Sparse Content:** When file contents lack sufficient context for skill inference, the system flags the file & displays an error message.

## **UC6.2 — Analyze Code Content & Extract Skills**

**Primary actor:** System  
**Description:** Apply local NLP file analysis to infer topics, languages, frameworks, contributions and skills from file contents and stored commit messages  
**Precondition:** Content scan and indexed data  
**Postcondition:** Analysis results stored per file/project.  
**Main Scenario:**

1. System accesses relevant scanned files and stored data.  
2. System runs local NLP & file analysis   
3. Extrapolate individual contributions for given collaborative projects   
4. System aggregates topics (topics, languages, frameworks, contributions and skills) and computes analysis results.

**Extensions:**

* 2a. **Ambiguous or Sparse Content:** When code document lacks sufficient context for skill inference, the system flags the file & displays an error message.

## **UC7 — Project Ranking**

**Primary actor:** System (triggered by User)  
**Description:** Ranking importance of each project based on user contributions  
**Precondition:** UC4 (Scan) done; UC5/UC6 done or skipped; UC3 preferences available;.  
**Postcondition:** Project rank generated and saved to local database  
**Main Scenario:**

1. System retrieves project metadata and user contribution metrics from local database.  
2. System normalizes contribution scores based on user contributions gotten from code and non code metadata, skills, and git contributions.  
3. System calculates an aggregate ranking score for each project.  
4. System sorts all projects in descending order of importance.  
5. System writes the generated project ranking to the local database.

**Extensions:**

* 2a. **Insufficient input data**: mark affected visuals as empty placeholders; continue others.  
* 5a. **Database write failure:** System retries; if persistent

## **UC8 — Chronological Ordering**

**Primary actor:** System (triggered by User)  
**Description:** Producing a chronological order of projects and skills exercised  
**Precondition:** UC4 (Scan) done; UC5/UC6 done or skipped; UC3 preferences available;.  
**Postcondition:** Chronological order of projects and associated skills saved to local database.  
**Main Scenario:**

1. System retrieves project metadata and skill data from database.  
2. System extracts creation and last modified timestamps from project metadata.  
3. System associates skills with each project from UC5 or UC6  
4. System sorts all projects by:  
   * Creation date (ascending)  
   * Last modified date (descending)  
5. System writes the ordered project lists and skill associations to the local database.

**Extensions:**

* 2a. **Insufficient input data**: mark affected visuals as empty placeholders; continue others.  
* 5a. **Database write failure:** System retries; if persistent

## **UC9 — Prepare Visualization Graphics**

**Primary actor:** System (triggered by User)  
**Description:** Build chart-ready datasets (timeseries, histograms, rankings) from stored metadata/Git/analysis before dashboard render.  
**Precondition:** UC4 (Scan) done; UC5/UC6 done or skipped; UC3 preferences available.  
**Postcondition:** Visualization datasets and suggested layout saved to local database  
**Main Scenario:**

1. System loads inputs (metadata, Git, analysis, prefs/filters).  
2. System computes KPIs (commit cadence, top languages/files, time periods).  
3. System produces chart datasets with labels/units and formats.  
4. System applies accessible defaults (number/date formats, palette).

**Extensions:**

* 2a. **Insufficient input data**: mark affected visuals as empty placeholders; continue others.

## **UC10 — Generate Dashboard**

**Primary actor:** User  
**Description:** Present an interactive dashboard with contributions, time, skills, and highlights  
**Precondition:** Analysers have run successfully.  
**Postcondition:** Dashboard rendered; user can edit and save the dashboard. 

**Main Scenario:**

1. User opens the dashboard view.  
2. System loads metrics, skills, and summaries from the analyser.  
3. System loads top ranked projects.  
4. System edits charts and tables   
5. User saves a personalized view, if needed.  
6. System stores visualization data in local database. 

**Extensions:** 

* 2a. If the dashboard is unable to load, trigger the generate options till 3 times.  
* 2b. **System displays an error:** “Dashboard unable to load. Please re-run the generate dashboard"   
* 2c. **User Edits View:** User modifies the layout, changes chart types, or applies filters to the data.  
* 4a. **System displays an error:** "Failed to save. Try again or save locally." 
* 5a. **Database write failure:** System retries; 

## **UC11 — Generate Resume**

**Primary actor:** System  
**Description:** Produce tailored, evidence-backed summaries from contributions and skills; align user desired job field.  
**Precondition:** Dashboard has been generated.  
**Postcondition:** Dashboard and Resume has been generated.  
**Main Scenario:**

1. System surfaces top impacts (e.g., features delivered, performance gains) with evidence (files/commits).  
2. System drafts summary following the STAR pattern for uploaded projects and top ranked projects.  
3. User edits and accepts the generated summary.   
4. System stores resume data in local database.

**Extensions:**

* 3a. **Insufficient evidence:** System adds a placeholder for potential data points that can be added by the user.  
* 4a. **Database write failure:** System retries; 

## **UC12 — Export Reports**

**Primary actor:** User   
**Supporting actor:** Export Service  
**Description:** Export dashboard snapshots, metrics, and bullets as PDF/CSV/JSON for applications or sharing.  
**Precondition:** Content has already been produced.  
**Postcondition:** Files written to user-selected destination.  
**Main Scenario:**

1. User chooses “Export”.  
2. User selects format(s).  
3. System generates artifacts.  
4. System writes files to chosen path.  
5. System confirms export success. 

**Extensions:**

* 4a. **Write permission error:** Prompt for alternate location and retry.

## **UC13 — Manage Data & Privacy**

**Primary actor:** User  
**Description:** User reviews, clears data, revokes consent.  
**Precondition:** UC1 previously completed (consent exists) and local data may exist.  
**Postcondition:** Data retained or deleted per user choice; consent state updated.  
**Main Scenario:**

1. User opens “Privacy & Data”.  
2. System shows stored projects, database size, and consent status.  
3. User chooses to clear data and/or revoke consent.  
4. System performs requested actions and confirms.

 **Extensions:**

* 3a. **Selective delete (per project):** System deletes only chosen items.  
* 4a. **Failure to delete due to OS lock:** System retries and provides manual steps.

## **UC14 — Database & Invalidation (Metadata \+ Visuals \+ UI)**

**Primary actor:** System  
**Description:** Maintain up-to-date stored data for metadata, visuals, and dashboard state; support quick incremental refreshes and accurate removal of stale items.  
**Precondition:** Scanning/analysis and visualization preparation completed; consent present.  
**Postcondition:** Store and manifest reflect the current project state; stale items are removed; dashboard state is preserved.

**Main Scenario:**

1. Identify stored items from recent scans, analysis results, and prepared visuals.  
2. Detect what has changed since the last run.  
3. Update data that changed; keep unchanged items; remove items that no longer apply.  
4. Save current dashboard and summary  state for reuse.  
5. Record an updated summary of data contents and status.

**Extensions:**

* 1a. **Source structure changes (e.g., items renamed/moved without meaningful content change):** retain history and update references accordingly.  
* 2a. **Update is interrupted or blocked:** retry and, if needed, on next launch, resume and validate the data state.


## **UC15 — Deletion of Previous Insights**

**Primary actor:** User  
**Description:** Delete previously generated insights without deleting other related files  
**Precondition:** User has generated at least one dashboard (done at least one successful cycle from U1-U11)  
**Postcondition:** Project History is deep deleted. Confirmed through UI popup

**Main Scenario:**

1. User selects the option to delete previously generated insights from the dashboard or project settings.  
2. System prompts the user for confirmation, warning that the deletion is irreversible.  
3. User confirms the deletion request.  
4. System identifies all stored insight files associated with the selected project.  
5. System performs a deep deletion of project history and related insight data, preserving non-insight project files.  
6. System updates the database and verifies that the deleted data is no longer referenced.  
7. System displays a confirmation popup indicating successful deletion.

**Extensions:**

* 5a. **Source Structure Change:** If project folders or file paths have been renamed/moved, system updates internal references before deletion to prevent orphaned data.

4. **Requirements, Testing, Requirement Verification**

# **Tech stack**

| Component | Technology | Rationale |
| ----- | ----- | ----- |
| **Frontend / Desktop UI** | **Tauri ()** | Lightweight, cross-platform desktop framework. Produces tiny binaries, provides safe filesystem access, and integrates smoothly with modern frontend stacks. |
| **Backend / Core Logic** | **Python ()** | Widely used for data extraction, parsing, and NLP analysis. Rich ecosystem of libraries (e.g., *GitPython*) enables efficient Git history extraction and processing. |
| **Data Persistence / Cache** | **SQLite** | File-based, lightweight database ideal for offline desktop apps. Efficiently stores file metadata and analysis results, minimizing redundant computation. Implemented as a **two-part storing system** combining SQLite with content hashing for robust persistence and fast lookups. |

### **Testing Framework & CI/CD**

* ### **Backend Tests**: pytest → Simple, reliable unit/integration testing 

* ### **Frontend Tests**: Jest → Fast UI & integration testing 

* ### **CI/CD**: GitHub Actions → Automated builds, tests, deployment

| Requirement | Description of the feature, the steps involved, the complexity of it, potential difficulties | Test Cases | Who | H/M/E |
| ----- | ----- | ----- | ----- | ----- |
| **FR1. Consent Management (UC1)** | Implement the consent screen, local storage of consent status, and enforcement of access restriction until consent is granted. | Positive: User accepts consent; verify all features are unlocked. Negative: User declines consent; verify analysis features remain blocked and app can still close/exit. | Afua Frempong, Karim Khalil, Vanshika Singla | Easy (2) |
| **FR2. Folder Path Selector (UC2)** | Provide a user interface element (native picker) to select and validate a local directory path, ensuring read access is available. | Positive: Select a valid, accessible local folder; verify path is saved. Negative (Path): Input an invalid or non-existent path; verify error message is displayed. Negative (Access): Select a path with read access denied; verify error and guidance provided. | Karim Jassani, Oluwadabira Omotoso, Shreya Saxena | Medium (3) |
| **FR3. Preference Selection (UC3)** | Implement the UI for selecting industry/education from dropdowns and handling custom free-text inputs | Positive: Select a dropdown option; verify the value is saved correctly. Negative (Custom): Enter invalid characters into custom fields; verify system sanitizes or rejects the input. | Karim Khalil | Medium (3) |
| **FR4. File Scanning & Indexing (UC4)** | Implement the core file enumeration and metadata extraction logic, handling file filters, unsupported types, and writing indexed data to the local database. | Positive: Scan a small project folder; verify all expected metadata fields are present in the database. Negative (I/O): Simulate an I/O error during the scan; verify the system logs the error and allows the user to retry. Negative (I/O): if the folder is empty, the user receives a pop up message to change the url. | Shreya  Saxena | Hard (5) |
| **FR5. Git History Extraction (UC5)** | If .git present, pull commits, authors, timestamps, and map to files; store in the database. | Positive: Scan a valid Git repository; database reflects correct metadata Negative (Missing): Scan a non-Git folder; verify the Git extraction component skips gracefully without error. Negative (I/O): if the git files/folder is empty, the user receives a pop up message to load again. | Oluwadabira Omotoso | Hard (5) |
| **FR6. Content Analysis & Skill Inference (UC6s)** | Apply local NLP & Python  content analysis on file content and commit messages to infer skills, languages, frameworks, and aggregate contribution topics. | Positive: Analyze a project e.g. using Python; verify "Python" and related libraries are correctly inferred and tagged. Positive: commit messages referencing “add Kafka consumer” infers “Kafka”.  Negative (Ambiguous): Analyze files with sparse or ambiguous content; verify the system flags the file and avoids false skill attribution. Negative: ignore binary files | Vanshika Singla  | Hard (5) |
| **FR6.1. Analyze Non-Code Content & Extract Skills (UC6.1)**  | System performs local NLP and file analysis on non-code files (e.g., docs, presentations, PDFs) to infer topics, languages, frameworks, contributions, and skills. Requires scanned and indexed data. Aggregates analysis results per project. | Positive: Given rich non-code files, verify extracted topics and skills match content. Negative: Provide ambiguous or sparse text; verify file is flagged and error message appears | TBD  | Hard (5) |
| **FR6.2. Analyze Code Content & Extract Skills (UC6.2)** | System performs local NLP and code analysis to infer programming languages, frameworks, and contributions. Aggregates analysis results for each file and project. | Positive: Provide valid repo; verify languages and frameworks correctly detected. Negative: Provide empty or broken code files; verify system flags and reports insufficient context. | TBD | Hard (5) |
| **FR7. Project Ranking (UC7)** | System calculates and ranks projects based on user contributions using normalized contribution scores (from code, non-code, skills, and metadata). Stores ranking results to database. | Positive: Verify ranked project list generated in descending order and saved. Negative: Remove contribution data for a project; verify that visual placeholders appear. Negative: Simulate database write failure; confirm retry and logging occur. | TBD | Hard (5) |
| **FR8. Chronological Ordering (UC8)** | System generates chronological lists of projects and skills based on creation and modification dates. Saves ordered lists to the local database. | Positive: Verify chronological order generated correctly and saved. Negative: Missing timestamps; ensure placeholders appear, processing continues, and no crash occurs. | TBD | Medium (3) |
| **FR9. Prepare Visualization Graphics (UC9)** | Precompute chart datasets from stored metadata/Git/analysis; save datasets | Functional Testing: After a scan and analysis, run preparation; verify the visualization database is populated with the expected datasets and layout. Functional Testing (Filters): Change date/language filters and rerun preparation; verify only affected visuals recompute (others are reused). Negative Testing (I/O): Simulate a database write failure; verify the system has retried. | Karim Khalil, Shreya Saxena | Hard (5) |
| **FR10. Resume Generation (UC11)** | Implement the logic to surface evidence-backed impact statements and draft structured summaries (e.g., STAR pattern) based on user-provided field/preferences. | Positive: Generate a summary; verify it includes evidence linking a skill to a file/commit.  Negative (Insufficient Evidence): If data is too sparse, verify the system includes a placeholder instead of fabricating content. | Afua Frempong  | Hard |
| **FR11. Dashboard Generation & Edit (UC10)** | Render the interactive dashboard using analysis results and allow the user to modify the layout (add/remove widgets, filters) and save the personalized view. | Positive: Load the dashboard; verify all calculated metrics are displayed correctly.  Positive (Edit): Rearrange and remove widgets; verify the layout is saved and persists after reload.  Negative (Load): Simulate a data loading failure; verify the system retries (up to 3 times) before displaying a non-blocking error message. | Karim Jassani | Hard |
| **FR12.Export Dashboards (UC12)** | Implement functionality to generate and write export files (e.g. PDF,JPG, JSON etc) of the dashboard, summaries, and metrics to a user-selected location. | Positive: Export the dashboard as a certain file type; verify the output file is accurate and readable.  Negative (Permission): Simulate a write permission error; verify the system prompts the user to select an alternate path and retries. | Karim Khalil | Medium |
| **FR13. Data Management (UC13)** | Provide a UI to review stored project data, clear the local database (fully or selectively), and revoke consent. | Positive (Clear): Clear all database data; verify the database files are deleted and the stored project list is empty.  Negative (Failure): Simulate the OS locking the data, preventing deletion. Verify that the system: Displays the exact locked file path to the user.  Provides clear manual resolution steps (e.g., *“Please delete the file manually here: \[Path\]”*).  Internally marks the project as inactive/deleted to maintain consistency. | Shreya  Saxena | Hard |
| **FR14: Database & Invalidation (UC14)** | Persist database after metadata/analysis and visuals; support incremental rescans and precise invalidation. | Positive (Single change): Modify one file; only that file’s analysis and dependent visuals update. Positive (Rename/move): Same content; path metadata updates; history preserved. Negative (Stale items retained):File is deleted or moved outside referenced folder path; database and dashboard still reference it; stale metadata and visuals persist; dashboard shows outdated state.   | Oluwadabira Omotoso, Vanshika, Singla | Medium |
| **FR15. Deletion of Previous Insights (UC15)** | Allows users to delete previously generated insights while preserving related non-insight project files. Includes confirmation popup, irreversible warning, deep deletion of insight data, and post-deletion database verification. Must handle renamed/moved project folders safely. | Positive: Verify that insights deleted, non-insight files remain, and confirmation popup displays. Negative: Rename/move project folder before deletion; verify system updates references before deletion and avoids orphaned data. | TBD  | Medium   |
| **NFR1. Cross-Platform & Offline** | Application must be installable and executable OS-agnostically (Win/Mac/Linux) without requiring a continuous internet connection for core functions. | Test Suite: Run all functional requirements (FR1-FR10) end-to-end on Windows, macOS, and a Linux distribution. Test Case: Disconnect from the internet and verify all analysis, caching, and visualization functions operate normally. | Oluwadabira Omotoso | Medium |
| **NFR2. Data Consistency** | Extracted information and subsequent analysis results must remain consistent with the source files and stored metadata. | Test Case: Scan a project, verify the dashboard output, change one source file and rescan; verify the dashboard output reflects only the change and not new errors. | Vanshika Singla  | Medium |
| **NFR3. Usability/Intuitiveness** | The application must be intuitive for a first-time user, requiring minimal learning effort for basic navigation and core functions. | Manual Testing: Perform a usability test with three external first-time users; record time taken to complete UC2 (Select Folder) and UC9 (Generate Dashboard). | Afua Frempong, Karim Jassani | Easy |
