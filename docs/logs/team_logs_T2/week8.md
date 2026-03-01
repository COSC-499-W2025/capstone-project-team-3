# Team Log Week 8

**Team Name:** Group 3 (Canvas)
**Work Performed:** Feb 23, 2026 → Mar 1, 2026

📅 **[← Go to Week 7 Team Log](week7.md)**

---

## [Personal Logs for Week 8](../personal_logs_T2/week8)

---

## Recap of Milestone Goals

- **Features planned for this milestone:**
  - Working on requirements for Milestone 2
  - Desktop frontend (Electron + React) integrated with Python backend (Milestone 3 start).
- **Associated project board tasks for this week:**
  - Fix for Download (saved) and Order resume by dates – #709
  - Delete a project on the resume – #721
  - Edit display order of projects on a resume – #722
  - Add endpoint that adds project to a resume – #727
  - Update resume deletion UI to include dropdown – #712
  - API endpoints to list and retrieve chronological projects – #715
  - API endpoint to update project dates – #716
  - API endpoints to list and add skills for a project – #717
  - API endpoints to update skill date and name – #718
  - API endpoint to delete a skill – #719
  - Complete API Endpoints for Chronological Management – #720

---

## Burnup Chart

*Accumulative view of tasks done, tasks in progress, and tasks left to do.*  
Paste chart image or link here:  

Progress Burnup: [https://github.com/orgs/COSC-499-W2025/projects/45/insights](https://github.com/orgs/COSC-499-W2025/projects/45/insights)

Status Burnup: [https://github.com/orgs/COSC-499-W2025/projects/45/insights/2](https://github.com/orgs/COSC-499-W2025/projects/45/insights/2)

---

## Team Members


| Username (GitHub) | Student Name        |
| ----------------- | ------------------- |
| @KarimKhalil33    | Karim Khalil        |
| @kjassani         | Karim Jassani       |
| @dabby04          | Oluwadabira Omotoso |
| @PaintedW0lf      | Vanshika Singla     |
| @6s-1             | Shreya Saxena       |
| @abstractafua     | Afua Frempong       |


---

## Completed Tasks


| Task/Issue ID                                    | Title                                                                                                                                                                                                                                                                                         | Username       |
| ------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- |
| [#712, #715, #716, #717, #718, #719, #720]       | Enhanced resume deletion UI with dropdown (PR #711); Added comprehensive API endpoints for chronological management - projects list/retrieve, update dates, skills CRUD operations (PR #714); Created Figma UI design for chronological management; Recorded M2 presentation video covering Features 23, 24, 26, 33 | @6s-1          |
| [#731, #732]       | Refactor non-code pdf, readme, text parsing to full parse for collaborative files (PR #733); Fix analysis of collaborative non-code files not happening | @PaintedW0lf   |
| [#584, #585, #604, #461, #463]                   | Update Existing User preference API endpoints, Outline Eduction model for DB storage, Create Institution API Endpoints, Define Editable Portfolio Fields, API Endpoint: Edit Portfolio Project, Backend Model for Portfolio Customization                                                     | @abstractafua  |
| [#745, #746, #747, #748, #734]                  | Completed project score overrides in portfolio (PR #713); Added API-driven main analysis flow and draft runner UI for migration testing (PR #723); Displayed portfolio role tags on project cards (PR #729); Fixed score editing, removed Functions/Classes from GitHub cards, and fixed thumbnail rendering in interactive HTML export (PR #744); Assisted with updated system architecture review/support (PR #734); Prepared portfolio video demo, presented live with team, and provided peer presentation feedback | @KarimKhalil33 |
| [#552, #553, #571, #572, #602, #573]             | Resolve project score vs rank confusion, Rename project scan score, Add score override fields + reset on reanalysis, Implement score breakdown builder, Update Is_collaborative function, Implement override recalculation + renormalization                                                  | @kjassani      |
| [#709, #721, #722, #727]                   | Fix download for saved resumes and resume ordering; Delete projects from a saved resume; Drag-and-drop project ordering for resumes; Add backend endpoint to attach projects to an existing resume | @dabby04       |


## In Progress Tasks


| Task/Issue ID                                                                | Title                                                                                                                     | Username     |
| ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | ------------ |
| [#735](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/735) | Add testing for consent management in desktop/Test                                                                    | @PaintedW0lf |
| [#492](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/492) | Allow User to Override Project Ranking                                                                                    | @kjassani    |
| [#574](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/574) | Wire override into API + CLI                                                                                              | @kjassani    |


---

## Meeting Notes

No meeting this week (reading break)

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
- We need to improve the immediate reviews of PRs.

---

## Plan for Next Cycle

- Continue work on remaining Milestone 2 features
- Start with some Milestone 3 requirements
- Monitor new API endpoints performance and usage patterns

