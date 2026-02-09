# Team Log Week 4

**Team Name:** Group 3 (Canvas)
**Work Performed:** Jan 26, 2026 → Feb 8, 2026

📅 **[← Go to Week 3 Team Log](week3.md)**

---

## [Personal Logs for Week 4](../personal_logs_T2/week4&5)

---

## Recap of Milestone Goals

- **Features planned for this milestone:**
  - Working on requirements for Milestone 2
  - Desktop frontend (Electron + React) integrated with Python backend (Milestone 3 start).
  
  
- **Associated project board tasks for this week:**
  - Optimization and refactoring for resume generation and download - #479
  - Update DB schema to include RESUME table - #519
  - Load/Edit Resume  - #565
  - Save Resume Edits - #566
  - Update save_resume_edits to include RESUME_SKILLS - #596
  - Create Tailored Resume - #594 
  - Setup project environment for frontend (React Native / Electron + React) - #579
  

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
| [#512, #528, #511, #498, #499] | Implement GET API calls for calling skills, chronologically and by frequency, implemented fixes for non code analysis summary, implemeted fixes for user preferences | @6s-1 | 
| [#505, #506, #522, #488] | API endpoint for user preferences, Testing of user preference API endpoint , Logic for Feature 21 and 22 for M2 ,  Investigate and fix Docker pipeline failures   | @PaintedW0lf | 
| [#460, #534] | Fix Failing tests, Troubleshoot user preference return | @abstractafua | 
| [#555, #569] | Portfolio API endpoints implementation; Portfolio Dashboard JavaScript foundation with Chart.js visualizations and advanced project rendering | @KarimKhalil33 |
| [#515, 516] | Improve Git author matching, Multi-repo Git parsing + nested repo aggregationg | @kjassani |
| [#479, #519, #565, #566, #596, #594] | Optimization and refactoring for resume generation and download; Update DB schema (RESUME table, RESUME_SKILLS); Load/Edit Resume; Save Resume Edits; Create Tailored Resume| @dabby04 |

## In Progress Tasks

| Task/Issue ID | Title            | Username |
|---------------|------------------|----------|
| [#434](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/434)           | Implement end-to-end functionality to add thumbnails per project. | @6s-1      |
| #523 | Feature 21 - M2 - Incremental information | @PaintedW0lf |
| #524 | Feature 22 - Duplicate file requirement | @PaintedW0lf |
| [#434](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/434) | Implement end-to-end functionality to add thumbnails per project. | @6s-1 |
|[#434](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/492) | Allow User to Override Project Ranking | @kjassani |
| [#459](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/459) | FR 27: Customize and save information about a portfolio showcase project | @abstractafua |
| [#579](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/597) | Setup project environment for frontend (Electron + React). PR #601 in code review. | @dabby04 |

---

## Meeting Notes



---

## Test Report

- **Framework used:** pytest  
- **Test run date:** Jan 2026  
- **Summary:**  
  - Updated test classes for Resume endpoints
  - Tested and verified Electron + React desktop frontend integration with Python backend (PR #601)
  - Added comprehensive tests for Portfolio Dashboard JavaScript functionality including Chart.js methods, data processing, and DOM manipulation
  - Validated Portfolio API endpoints with project filtering and error handling scenarios
- **Regression Testing:**  
  - All existing tests passing after resume DB schema and endpoint changes
  - New and existing resume behavior validated together across resume PRs
  - Portfolio API endpoints tested with comprehensive parameter handling and database error scenarios

---

## Reflection

- Plan to keep test classes in sync as more frontend and Milestone 3 work lands.
- Discuss more as a group any concerns or misunderstandings

--- 
## Plan for Next Cycle

* Continue work on remaining Milestone 2 features
* Start with some Milestone 3 requirements
* Monitor new API endpoints performance and usage patterns