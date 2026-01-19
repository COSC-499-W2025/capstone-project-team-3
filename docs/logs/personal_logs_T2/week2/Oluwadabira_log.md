# Personal Log – Oluwadabira Omotoso

---

## Week-2, Entry for Jan 11 → Jan 18, 2026

![Personal Log](../../../screenshots/Week%202%20Personal%20Log%20T2-%20Oluwadabira.png)

---

### Connection to Previous Week
Building on my work from last week, I made improvements to the endpoints for generating and downloading a resume, allowing two options: master resume or tailored resume. This buildup, also included adding other endpoints and updating previous tests.

---

### Pull Requests Worked On
- **[PR #474 - Fixed failing tests in main and path_utils](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/474)** ✅ Merged
  - This PR resolves failing tests in `tests/test_main.py and tests/test_path_utils.py`.
- **[PR #480 - Added POST endpoints for Resume generation and download](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/480)** ✅ Merged
  - Updated methods in generate_resume.py: the methods updated are load_projects and build_resume_model
  - Added POST endpoints in api/routes/resume.py for resume generation and exporting to .tex and .pdf
  - Added and updated their related test classes.
- **[PR #485 - Added endpoint for GET/projects and improved resume preview for selected projects](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/485)** ✅ Merged
  - Added API endpoint for GET /projects in `api/routes/projects.py`
  - Made updates to the GET /resume endpoint to access one when no project_signatures are provided (master resume) and one when signatures are provided (tailored resume)

---

### Associated Issues Completed
| Issue ID | Title | Status |
|----------|-------|--------|
| [#476](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/476) | Update generate_resume.py to include project_ids in some methods | ✅ Closed |
| [#477](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/477) | Add resume endpoints| ✅ Closed |
| [#481](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/481) | Create tests for code analysis part 1 | ✅ Closed |
| [#473](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/473) | Fix failing tests for main and path_utils | ✅ Closed |
| [#475](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/475) | Create endpoint for resume generation - Tailored | ✅ Closed |
| [#478](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/478) | Allow user to download tailored resume | ✅ Closed |
| [#484](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/484) | Create endpoint for GET /projects | ✅ Closed |

---

## Work Breakdown

### Coding Tasks

#### Test Fixes ([PR #474 - Fixed failing tests in main and path_utils](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/474))
- Fixed 3 failing tests in main.py.
- Fixed 1 failing test in path_utils.

#### Added POST endpoints for Resume generation and download ([PR #480](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/480))
- Updated methods in generate_resume.py: the methods updated are load_projects and build_resume_model. The reason for this is so that the use can generate a resume based on selected projects.
- Added POST endpoints in api/routes/resume.py:
- - POST /resume/generate: it is used to generate a resume that only includes the selected projects.
- - POST /resume/export/tex and POST /resume/export/pdf: This is such that the user can export their filtered projects to a resume in .tex format or in a .pdf format.
- Added and updated test cases to show that this is change is effective and produces expected results.

#### Added endpoint for GET/projects and improved resume preview for selected projects ([PR #485](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/485))
- Added to CLI or UI to show use case of downloading tailored resume.
- Created endpoint for GET /projects
- Added and updated test cases to show that this is change is effective and produces expected results.

---

###  Testing & Debugging Tasks

- Added comprehensive tests in `test_generate_resume.py`
- Added comprehensive tests in `tests/api/test_resume.py`
- Resolved failing tests in `tests/test_main.py` and `tests/test_path_utils.py`
- Added and made updates to these test classes: `test_main.py`, `test_resume.py`, `test_resume_cli.py`, and `test_projects.py`. This is relating to post methods, generating links with file signatures.


---

### Collaboration & Review Tasks

- Responded to code review feedback from @PaintedW0lf on PR #474 regarding improved assertion
- Responded and address comments from @KarimKhalil33 and @kjassani on PR #480
- Collaborated with team on understanding of endpoints
- Documented changes and updated tests for clarity
- Received approvals from multiple team members
- Reviewed and commented on teammates PRs

---

### Issues & Blockers

**Issue Encountered:**
- Some failing tests in main which were restricting a good test environment
- 

**Resolution:**
- Fixed tests that were restricting environment.

---

### Reflection

**What Went Well:**
- Successful implementation of API endpoints in resume and projects.
- I was able to understand why a POST request was needed for one of the endpoints.
- Created comprehensive test coverage for all new functionality

**What Could Be Improved:**
- Better optimization of code to reduce redundancy and future refactoring.

---

### Plan for Next Week
- Continue contributing to Milestone-2 requirements (API's & UI)
- Optimize and refactoring for resume endpoints.
---
