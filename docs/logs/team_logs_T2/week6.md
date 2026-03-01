# Team Log Week 6

**Team Name:** Group 3 (Canvas)
**Work Performed:** Feb 8, 2026 → Feb 15, 2026

📅 **[← Go to Week 4&5 Team Log](week4&5.md)**

---

## [Personal Logs for Week 6](../personal_logs_T2/week6)

---

## Recap of Milestone Goals

- **Features planned for this milestone:**
  - Working on requirements for Milestone 2
  - Desktop frontend (Electron + React) integrated with Python backend (Milestone 3 start).
  
  
- **Associated project board tasks for this week:**
  - Resume Sidebar (beginning of landing page) - #639, #642
  - Display Resume (UI) - #610
  - Resume Builder & Sidebar tests - #639
  - Create Tailored Resume (Project Selection Page) - #661
  - UI/view tailored - #607
  - Welcome page UI - #625
  - Upload page base layout - #627
  - Global CSS for UI development - #629
  - Welcome page responsive design - #630
  - Upload page responsive design - #631
  - Chronological Management CLI for skill dates - #646
  - Chronological Management CLI for project dates - #647
  - Date extraction logic for chronological skills - #648
  - Thumbnail upload flow in UI - #581
  - GET API for serving thumbnails - #656
  - Thumbnail cache-busting - #657
  - Thumbnail extension validation - #658


---

## Burnup Chart

_Accumulative view of tasks done, tasks in progress, and tasks left to do._  
Paste chart image or link here:  

Progress Burnup: https://github.com/orgs/COSC-499-W2025/projects/45/insights

Status Burnup: https://github.com/orgs/COSC-499-W2025/projects/45/insights/2

---

## Team Members

| Username (GitHub) | Student Name   |
|-------------------|----------------|
| @KarimKhalil33    | Karim Khalil   |
| @kjassani         | Karim Jassani  |
| @dabby04          | Oluwadabira Omotoso|
| @PaintedW0lf      | Vanshika Singla|
| @6s-1             | Shreya Saxena  |
| @abstractafua     | Afua Frempong  |

---

## Completed Tasks

| Task/Issue ID | Title                  | Username        |
|---------------|------------------------|-----------------|
| [#625, #627, #629, #630, #631, #646, #647, #648, #581, #656, #657, #658] | Welcome page & upload page UI with global CSS and responsive styling (PR #623); Chronological skill/project managing to CLI with updated date extraction logic (PR #643); Thumbnail integration with Portfolio UI including GET API, cache-busting, and extension validation (PR #653) | @6s-1 | 
| [#600, #635, #636, #637, #614, #615, #651, #652, #654] | User-editable threshold for incremental load (PR #634); Integrate update folder user requirement in CLI; Refactor incremental load to interactive mode; Testing for update project CLI; Testing for author key; Add author key in non-code stream bugfix; Get API endpoint for consent text for UI (PR #655); Test consent text API endpoint; Add notification CSS for popups | @PaintedW0lf | 
| [#584, #585, #604, #461, #463] | Update Existing User preference API endpoints, Outline Eduction model for DB storage, Create Institution API Endpoints, Define Editable Portfolio Fields, API Endpoint: Edit Portfolio Project, Backend Model for Portfolio Customization| @abstractafua | 
| [#632, #641, #707] | Portfolio Dashboard HTML Part 1 – base layout, sidebar/main structure, Chart.js/static wiring (PR #632); Completed interactive portfolio UI with charts/graphs, summary UX updates, and CI Docker workflow disk-space fix (PR #641); Closed portfolio UI enhancement scope for interactive graphs (#707) | @KarimKhalil33 |
| [#552, #553, #571, #572, #602, #573] | Resolve project score vs rank confusion, Rename project scan score, Add score override fields + reset on reanalysis, Implement score breakdown builder, Update Is_collaborative function, Implement override recalculation + renormalization | @kjassani |
| [#639, #642, #610, #661] | Resume Sidebar (GET /resume_names, sidebar UI, resume bullets fix); Display Resume (UI) – ResumeSections, ResumePreview, styles; Resume Builder & Sidebar frontend tests (ResumeBuilderPage, ResumeSidebar), Create Tailored Resume (Project Selection Page) | @dabby04 |

## In Progress Tasks

| Task/Issue ID | Title            | Username |
|---------------|------------------|----------|
| [#492](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/492) | Allow User to Override Project Ranking | @kjassani |
| [#574](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/574) | Wire override into API + CLI | @kjassani |
| [#607](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/607) | UI/view tailored. PR #669 | @dabby04 |

---

## Meeting Notes
https://docs.google.com/document/d/1TbeUFZQ_sNED9KTmzhB_K_Q56pP0ygIa8fMv7lOnGmo/edit?usp=sharing  
Meeting in Week 6 – add link or notes when available.  
All members present (or list attendees).  
Design discussion and M2 progress.

---

## Test Report

- **Framework used:** pytest (backend); Jest/React Testing Library (desktop frontend)
- **Test run date:** Feb 2026
- **Summary:**  
  - Updated test classes for Resume endpoints
  - Tested and verified Electron + React desktop frontend integration with Python backend (PR #601)
  - Added frontend tests for Resume Builder flow: ResumeBuilderPage (fetch on mount, sidebar list, selection, toggle), ResumeSidebar (names, onSelect, onTailorNew, empty-name fallback, toggle)
  - Added tests for Resume sections and ResumeBuilderPage display (Display Resume UI)
  - Added ProjectSelectionPage tests (loading/error states, checkboxes, Generate button state, empty state); backend projects API tests updated for `date_added`
  - Portfolio Dashboard JavaScript tests (Chart.js, data processing, DOM); Portfolio API endpoint validation
- **Regression Testing:**  
  - All existing tests passing after resume DB schema and endpoint changes
  - New and existing resume behavior validated together across resume PRs
  - Portfolio API endpoints tested with comprehensive parameter handling and database error scenarios

---

## Reflection

- Plan to keep test classes in sync as more frontend and Milestone 3 work lands.
- Discuss more as a group any concerns or misunderstandings.

--- 
## Plan for Next Cycle

* Continue work on remaining Milestone 2 features
* Start with some Milestone 3 requirements
* Monitor new API endpoints performance and usage patterns