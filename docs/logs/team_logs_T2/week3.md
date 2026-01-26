# Team Log week 3

**Team Name:** Group 3 (Canvas)
**Work Performed:** Jan 19, 2026 → Jan 25, 2026

📅 **[← Go to Week 2 Team Log](week2.md)**

---

## [Personal Logs for Week 3](../personal_logs_T2/week3)

---

## Recap of Milestone Goals

- **Features planned for this milestone:**
  - Working on requirements for Milestone 2
  - Working on implementing API calls to get skills
  - Working on implementing summary fix for Non Code Analysis
  - Working on fixing Milestone-1 feedback
  - Implementing portfolio generation API endpoints
  - Fixing encoding issues for file parsing with special characters
  - Peer Testing Preparation
  
- **Associated project board tasks for this week:**
  - Non Code Analysis Troubleshooting #512
  - Troubleshoot user preferences error #528
  - Add GET API Endpoint for retrieving skills in chronological order. #511
  - Add GET API Endpoint for retrieving all skills. #498
  - Add GET API End point for retrieving frequency sorted skills. #499  
  - Portfolio generation POST API endpoint #508
  - Fix failing test with hardcoded year #503
  - Encoding error when parsing files with special characters #536  - Added Missing Import for Project – #495
  - Updates to CI/CD Workflow – #502
  - Fixed Resume Bullets & Suppressed Terminal Warnings – #526
  - Fixed Test Data Stored in Database – #532
  - Optimized PDF Compilation & Removed Redundancy – #531
  - Fix Failing tests - #460
  - User Preference Return Troubleshoot - #513

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
| [#467, #468] | Fix failing tests in test_non_code_file_checker.py | @KarimKhalil33 |
| [#470, #469] | Refactor code analysis part 2 - Extract user preferences and text processing utilities | @KarimKhalil33 |
| [#490] | API endpoint for GET /projects/{signature} | @kjassani |
| #484, #517, #530 | Create endpoint for GET /projects, Fix Missing Resume Bullets, Test data being stored in main database | @dabby04 |


## In Progress Tasks

| Task/Issue ID | Title            | Username |
|---------------|------------------|----------|
| [#434](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/434)           | Implement end-to-end functionality to add thumbnails per project. | @6s-1      |
| #523 | Feature 21 - M2 - Incremental information | @PaintedW0lf |
| #524 | Feature 22 - Duplicate file requirement | @PaintedW0lf |
| [#434](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/434) | Implement end-to-end functionality to add thumbnails per project. | @6s-1 |
|[#434](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/492) | Allow User to Override Project Ranking | @kjassani |
| [#459](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/459) | FR 27: Customize and save information about a portfolio showcase project | @abstractafua |
| [#479](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/479)|Optimization and Refactoring for Resume generation and download|@dabby04|

---

## Meeting Notes

### Jan 22, 2026 – Team Meeting (All members present)
- Initial discussions on:
  - Figma design for UI
  - Planning for remaining Milestone 2 requirements
  - Portfolio display design demo by @KarimKhalil33
  - Preparation for upcoming peer testing sessions

---

## Test Report

- **Framework used:** pytest  
- **Test run date:** Jan 2026  
- **Summary:**  
  - Updated test suites for user preference integration
  - Added tests for database connection management
  - Added comprehensive encoding test suite (4 new test cases)
  - Added portfolio generation API test coverage (4 test cases)
  - Fixed hardcoded year test to prevent future failures
  - Verified backward compatibility tests
- **Regression Testing:**  
  - All existing tests passing after user preference integration
  - All encoding fixes verified with comprehensive test coverage
- **Screenshot or Output:**  
  - TBD

---

## Reflection

* Test coverage improved with comprehensive test suites for new features including encoding and portfolio generation
* Code refactoring approach proven successful - modular PRs easier to review
* All failing tests resolved, CI/CD pipeline now functioning properly
* Critical encoding issues resolved proactively before affecting production
* Portfolio generation API successfully implemented with flexible project selection
* Team collaboration effective with thorough code reviews and feedback

--- 
## Plan for Next Cycle
* Continue work on remaining Milestone 2 features
* Conduct peer testing sessions and document findings
* Monitor new API endpoints performance and usage patterns


