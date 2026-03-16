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
  - Display projects list on Data Management page – #782
  - Connect analysis after upload so projects appear in Data Management – #783
  - Add analysis API client for desktop – #784
  - Add inline editing for project and skill dates in Data Management – #802
  - Fix skill source to only be "Technical skill" or "Soft skill" – #803
  - Fix chronological API to support non-technical skill source – #804
  - Add chronological skill view – #805
  - Add date validation for skills ensuring correct range – #824
  - Add date format validation for project and skills – #825

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


| Task/Issue ID                                    | Title                                                                                                                                                         | Username       |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- |
| [#782, #783, #784]                               | Display projects list for Data Management UI, Connect Upload to trigger scanning (PR #781): projects list, analysis API client, upload→analysis flow           | @6s-1          |
| [#802, #803, #804, #805]                         | Project/skill chronological editing and display (PR #801): inline editing for dates, skill source display, chronological API support, skill view                | @6s-1          |
| [#821, #824, #825]                               | Date validation for Data Management UI (PR #821): dd-mm-yyyy format, modified>created, skill date range, timestamp normalization, error messages             | @6s-1          |


## In Progress Tasks


| Task/Issue ID                                                                | Title                                                                                                                     | Username     |
| ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | ------------ |
| —                                                                           | *Add in-progress tasks here*                                                                                              | —            |


---

## Meeting Notes

*Add meeting notes for Week 10*

---

## Test Report

- **Framework used:** pytest (backend); Jest/React Testing Library (desktop frontend)
- **Test run date:** Mar 2026
- **Summary:**  
  - Data Management page tests: projects list, expand skills, refresh, delete flow
  - Date validation tests: invalid format, last modified before created, skill outside range, same-day boundary (timestamp vs date-only)
  - All test suites passing

---

## Reflection

*Add team reflection for Week 10*

---

## Plan for Next Cycle

- Continue Data Management and desktop integration work
- Support team with code reviews and testing
