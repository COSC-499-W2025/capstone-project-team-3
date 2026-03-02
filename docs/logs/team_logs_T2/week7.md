# Team Log Week 7 (READING BREAK)

**Team Name:** Group 3 (Canvas)
**Work Performed:** Feb 16, 2026 → Feb 22, 2026

📅 **[← Go to Week 6 Team Log](week6.md)**

---

## [Personal Logs for Week 7](../personal_logs_T2/week7)

---

## Recap of Milestone Goals

- **Features planned for this milestone:**
  - Working on requirements for Milestone 2
  - Desktop frontend (Electron + React) integrated with Python backend (Milestone 3 start).
- **Associated project board tasks for this week:**
  - UI/view tailored – create tailored resume preview in Resume Builder – #607
  - Design for download resume + updated export logic – #677, #678
  - Fully implemented download + header for resume – #668, #688
  - Save and loading tailored resume – #609, #689
  - Edit Resume (UI) – enable editing for tailored resumes – #608
  - API documentation for project, skills, user preferences, health, institutions – #672
  - API documentation for thumbnail, project, resume, portfolio – #673
  - Complete API endpoint documentation (Feature-36) – #671
  - End-to-end thumbnail functionality – #434
  - GIF/SVG thumbnail support (unique feature) – #682
  - Delete Resume UI implementation – #611
  - Add skills with dates in CLI – #692
  - Edit/rename skills in CLI – #694
  - Restructure chronological menu – #695
  - Complete chronological information management (Feature-23) – #547
  - Wire override into API + CLI - #574

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
| [#672, #673, #671, #434, #682, #611, #692, #694, #695, #547] | API documentation for all endpoints (PR #670, #675); GIF/SVG thumbnail support - unique feature (PR #681); Delete Resume UI implementation (PR #691); Add skills+dates, edit skill names, restructured chronological menu (PR #693) | @6s-1          |
| [#683, #684, #685, #686, #687, #708, #696, #697] | Implement Consent Page UI (PR #687); Add notification popup system; Integrate consent page with backend API; Style consent page with CSS; Add revoke consent UI (PR #698); Add endpoint documentation for consent management; Add missing endpoint documentation for resume and project | @PaintedW0lf   |
| [#584, #585, #604, #461, #463]                   | Update Existing User preference API endpoints, Outline Eduction model for DB storage, Create Institution API Endpoints, Define Editable Portfolio Fields, API Endpoint: Edit Portfolio Project, Backend Model for Portfolio Customization                                                     | @abstractafua  |
| [#676, #701, #702, #706, #705, #704]            | Added score breakdown + overridden score display transparency in portfolio (PR #676); Started portfolio migration from static to desktop React/TSX (PR #701); Added interactive portfolio HTML download/export flow with tests (PR #702); Completed related issue scopes for score transparency, desktop migration, and export functionality (#706, #705, #704); Prepared for live in-class team presentation | @KarimKhalil33 |
| [#574]             | Wire override into API + CLI  | @kjassani      |
| [#607, #677, #678, #668, #688, #609, #689, #608] | Tailored resume preview (UI); Download & export logic for resumes (backend + header UI); Save and load tailored resumes; Edit tailored resumes (Skills + Projects)                                                                                                                            | @dabby04       |


## In Progress Tasks


| Task/Issue ID                                                                | Title                                                                                                                     | Username     |
| ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | ------------ |



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

