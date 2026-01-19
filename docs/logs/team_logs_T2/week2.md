# Team Log week 2

**Team Name:** Group 3 (Canvas)
**Work Performed:** Jan 12, 2026 → Jan 18, 2026

📅 **[← Go to Week 1 Team Log](week1.md)**

---

## Personal Logs for Week 2
- (../personla_logs_T2/week2)

---

## Recap of Milestone Goals

- **Features planned for this milestone:**
  - Complete user preference integration within main workflow
  - Continue thumbnail integration development
  - Working on requirements for Milestone 2
  - Work on API's and displaying why each project is scored higher than the other
  
- **Associated project board tasks:**
  - Integrate User Preferences within the main and local analysis workflow. #451
  - Implement end-to-end user preference integration in local non code analysis. #450
  - BugFix: DB Connection Leak Fix in user preference integration. #452
  - API/POST CONSENT MANAGER - Enable web-based consent management. #456
  - Create Automated Coverage testing in CI pipeline. #453
  - Create docker build for CI pipeline. #454
  - Fix failing tests in test_non_code_file_checker.py #468
  - Refactor code analysis part 2 - Extract user preferences and text processing #469
  - Create tests for code analysis part 1 #481
  - GET /api/projects/{signature} #490
  - Fix failing tests #460
  - Create endpoint for GET /projects	#484
  - Optimization and Refactoring for Resume generation and download	#479
  - Allow user to download tailored resume	#478
  - Add resume endpoints	#477
  - Update generate_resume.py to include project_ids in some methods	#476
  - Create endpoint for resume generation - Tailored	#475
  - Fix failing tests for `main` and `path_utils`	#473
  

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
| [#451, #450, #452] | Implement end-to-end user preference integration in local non code analysis, BugFix: DB Connection Leak Fix in user preference integration | @6s-1 | 
| [#456, #457, #453] | Privacy consent API endpoints, consent API testing , Create Automated Coverage testing in CI pipeline  | @PaintedW0lf | 
| [#460] | Fix Failing tests  | @abstractafua | 
---
| [#451, #450, #452] | Implement end-to-end user preference integration in local non code analysis, BugFix: DB Connection Leak Fix in user preference integration | @6s-1 | | [#467, #468] | Fix failing tests in test_non_code_file_checker.py | @KarimKhalil33 |
| [#470, #469] | Refactor code analysis part 2 - Extract user preferences and text processing utilities | @KarimKhalil33 |
| [#490] | API endpoint for GET /projects/{signature} | @kjassani |

## In Progress Tasks

| Task/Issue ID | Title            | Username |
|---------------|------------------|----------|
| [#434](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/434)           | Implement end-to-end functionality to add thumbnails per project. | @6s-1      |
| #454          | Create docker build for CI pipeline                                     | In progress, we are failing this currently, which may/maynot be due to pre-existing issues   |

| [#434](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/434) | Implement end-to-end functionality to add thumbnails per project. | @6s-1 |
[#434](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/492) | Allow User to Override Project Ranking | @kjassani |
| [#459](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/459) | FR 27: Customize and save information about a portfolio showcase project | @abstractafua |

---

## Meeting Notes

### Jan 16, 2026 – Team Meeting (All members present)
- Initial discussions on:
  - Progress update on Milestone 2 features
  - Planning for remaining Milestone 2 requirements

---

## Test Report

- **Framework used:** pytest  
- **Test run date:** Jan 2026  
- **Summary:**  
  - Updated test suites for user preference integration
  - Added tests for database connection management
  - Verified backward compatibility tests
- **Regression Testing:**  
  - All existing tests passing after user preference integration
- **Screenshot or Output:**  
  - TBD

---

## Reflection

* Test coverage improved with comprehensive test suites for new features
* Code refactoring approach proven successful - modular PRs easier to review
* All failing tests resolved, CI/CD pipeline now functioning properly
* Team collaboration effective with thorough code reviews and feedback

---## Plan for Next Cycle

* Monitor user preference integration in production
* Continue work on remaining Milestone 2 features
* Discuss API plans and UI details 

