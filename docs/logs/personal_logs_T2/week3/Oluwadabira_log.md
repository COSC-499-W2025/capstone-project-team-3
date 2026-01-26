# Personal Log – Oluwadabira Omotoso

---

## Week-2, Entry for Jan 19 → Jan 25, 2026

![Personal Log](../../../screenshots/Week%203%20Personal%20Log%20T2-%20Oluwadabira.png)

---

### Connection to Previous Week
Connecting to the previous work, I made updates to the resume class for faster download on `.pdf` and removed redundancy. From our previous sprint, we ran into issues with testing and some results were being skipped.

---

### Pull Requests Worked On
- **[PR #495 - Added missing import for project](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/495)** ✅ Merged
  - This PR resolves a quick fix on a missing project import for the get API endpoint.
- **[PR #502 - Made updates to CI/CD flow](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/502)** ✅ Merged
  - Fixes the issue of having more failing tests in the actions pipeline compared what we see in our system.
- **[PR #526 - Fixed resume bullets and suppressed warnings shown on terminal](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/526)** ✅ Merged
  - Fixes the issue of retrieving resume bullets.
  - Made changes to the Dockerfile to suppress warnings that are printed in our terminal when launching the app.
  - Test classes updated
- **[PR #532 - Fixed test data stored in db](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/532)** ✅ Merged
  - Makes sure the mock is stored in a temporary mocked database instead of the original database.
- **[PR #531 - Optimised compilation for PDF download and removed redundancy](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/531)** Code Review
  - Faster compile pdf which introduces a caching mechanism.
  - Reduced redundancy in various endpoints by creating new helper methods: `get_resume_tex` and `escape_tex_for_html`.
  - Updated the HTTPException to account for more area codes

---

### Associated Issues Completed
| Issue ID | Title | Status |
|----------|-------|--------|
| [#484](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/484) | Create endpoint for GET /projects | ✅ Closed |
| [#517](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/517) | Fix Missing Resume Bullets | ✅ Closed |
| [#530](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/530) | Test data being stored in main database | ✅ Closed |
| [#479](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/479) | Optimization and Refactoring for Resume generation and download | ✅ In Progress |

---

## Work Breakdown

### Coding Tasks

* Fixed missing imports affecting the GET /projects API endpoint. (PR #495)
* Updated CI/CD workflow to align local test results with GitHub Actions outcomes. (PR #502)
* Resolved resume bullet retrieval issues and refactored related logic. (PR #526)
* Optimized PDF resume generation by introducing caching to reduce compile time. (PR #531)
* Reduced redundancy across endpoints by adding shared helper methods (`get_resume_tex`, `escape_tex_for_html`). (PR #531)
* Improved error handling by expanding HTTPException coverage for additional area codes. (PR #531)
* Updated Dockerfile to suppress non-critical startup warnings. (PR #526)

---

### Testing & Debugging Tasks

* Investigated discrepancies between local test runs and CI pipeline failures. (PR #502)
* Updated and stabilized test classes affected by resume bullet fixes. (PR #526)
* Ensured mock data is written to a temporary mocked database rather than the main database. (PR #532)
* Verified PDF generation and download behavior after optimization changes. (PR #531)

---

### Collaboration & Review Tasks

* Reviewed and iterated on PRs with team members to address CI and testing concerns.
* Participated in code reviews, including feedback and revisions for the PDF optimization PR.
* Went through Milestone 1 feedback and current production issues with the team.

---

### Issues & Blockers

**Issue Encountered:**

* Tests behaving differently in the CI environment compared to local development.
* Resume-related data being unintentionally stored in the main database during testing.

**Resolution:**

* Updated the CI/CD configuration and test setup to ensure consistency across environments.
* Refactored test mocks to use a temporary mocked database, preventing pollution of the main database.

---

### Reflection

**What Went Well:**

* Successfully resolved multiple backend and testing issues within the sprint.
* CI pipeline reliability improved, reducing false negatives in test runs.
* PDF resume generation performance improved through caching and refactoring.

**What Could Be Improved:**

* Earlier validation of CI behavior could have reduced debugging time later in the sprint.
* More comprehensive test isolation from the start would help prevent database-related issues.

---

### Plan for Next Week

* Continue with milestone 2 contributions.
