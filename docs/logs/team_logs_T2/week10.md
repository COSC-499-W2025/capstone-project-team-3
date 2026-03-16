# Team Log Week 10

**Team Name:** Group 3 (Canvas)
**Work Performed:** Mar 9, 2026 → Mar 15, 2026

📅 **[← Go to Week 9 Team Log](week9.md)**

---

## [Personal Logs for Week 10](../personal_logs_T2/week10)

---

## Recap of Milestone Goals

- **Features planned for this milestone:**
  - Desktop frontend (Electron + React) integrated with Python backend (Milestone 3).
- **Associated project board tasks for this week:**

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


| Task/Issue ID                        | Title                                                                                                                                                                                                                                                                                                                                                                                                      | Username       |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- |
| [#628, #626, #761, #762, #765, #766] | End-to-end upload functionality for zipped files (PR #760): connect upload to backend, Remove button, drag-and-drop, UI; Base UI and API module for Data Management (PR #763)                                                                                                                                                                                                                              | @6s-1          |
| [#788, #789, #790, #793, #795, #796, #797] | Hub Page UI and Consent Page Redesign: Central Hub Page for navigation (PR #791), accessible aria-labels, comprehensive unit tests (PR #797); Consent page visual redesign with text parser for structured content (PR #792); Upload file panel integration (PR #798); Manual testing and documentation for peer testing | @PaintedW0lf   |
| [#771, #773]                         | Desktop score-override API integration, Functional Score Override management page in desktop app                                                                                                                                                                                                                                                                                                           | @kjassani      |
| [#836, #835]                         | Analysis runner setup (PR #794): desktop analysis configuration page after upload, project preload, per-project analysis type and run results; Unified one-page upload + analysis flow (PR #809): merged pages, per-project similarity actions (frontend+backend), AI consent modal + notice, tooltip guidance, post-run reset behavior, deterministic path-based override keys; also contributed to Peer Testing 2 UI task-list drafting/refinement | @KarimKhalil33 |
| [#786, #726, #810, #816, #818]       | Handle no projects for resume (PR #787): no-projects UI, snapshot-on-delete, DB migration; Add project to existing resume (PR #806): add-project modal, tests; Navigation for returning/first-time user (PR #811): consent-based redirect, error notification, WelcomePage tests; Navigation bar and ResumeBuilder/ProjectSelection (PR #819): collapsible nav, Hub home link, back button, responsiveness | @dabby04       |


## In Progress Tasks


| Task/Issue ID | Title                                                             | Username |
| ------------- | ----------------------------------------------------------------- | -------- |
| —             | Data Management UI – projects list, edit dates, skills management | @6s-1    |


---

## Meeting Notes

Discussed plans for Milestone 3 and what to wrap up for Peer testing. All notes for this meeting reflected in this [document](https://docs.google.com/document/d/1whjxm8Dyh-01K47Lic2t34O8g8vnQ7Zb3WwkUFfi3y4)

---

## Test Report

- **Framework used:** pytest (backend); Jest/React Testing Library (desktop frontend)
- **Test run date:** Mar 2026
- **Summary:**  
  - Upload page tests: auto-upload, Remove button, loading guards, ZIP validation
  - Data Management page tests
  - ConsentPage tests: 20+ unit tests covering positive and negative flows, consent/revoke UI, navigation, and error handling
  - Portfolio page tests: 32 Jest/RTL tests (loading/error states, project cards, project selection, charts, analysis section, user profile card)
  - All test suites passing

---

## Reflection

We discussed as a team to wrap up major elements for Milestone 3 going into next week. This way, we would be able to get major feedback from classmates on what elements could be improved.

---

## Plan for Next Cycle

- Updates to UI where needed
- Implementation of some nice-to-haves
- Support team with code reviews and testing

