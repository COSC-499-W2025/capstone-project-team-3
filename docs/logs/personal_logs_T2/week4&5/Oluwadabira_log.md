# Personal Log – Oluwadabira Omotoso

---

## Week-2, Entry for Jan 26 → Feb 8, 2026

![Personal Log](../../../screenshots/Week%205%20Personal%20Log%20T2-%20Oluwadabira.png)

---

### Connection to Previous Week
Connecting to the previous works, I have been making updates to the resume feature; making changes specifically to optimization, updated DB schema, stronger API endpoints, and starting baseline for frontend

---

### Pull Requests Worked On
- **[PR #558 - Added DB schema for resume versions](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/558)** ✅ Merged
  - This PR updates our database to include the new storage for a résumé after edits has been made for them and associating a name and id to a resume.
  - Test classes updated
- **[PR #567 -Updated DB_SCHEMA with table of skills and unique key](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/567)** ✅ Merged
  - This PR adds one more table in the dp.py for the resume. I added RESUME_SKILLS which handles the section for edited general skills in the resume.
  - Test classes updated
- **[PR #576 - Save resume edits](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/576)** ✅ Merged
  - Added a new endpoint POST /resume/{id}/edit so users can save edits to their resumes.
  - Test classes updated
- **[PR #568 - Load Edited Resume](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/568)** ✅ Merged
  - This PR introduces the endpoint for loading an edited resume (GET /resume/{id}).
  - Test classes updated
- **[PR #595 - Create tailored resume](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/595)** ✅ Merged
  - This PR adds to the existing feature of creating a tailored resume.
  - Test classes updated
- **[PR #601 - Integrated UI with current Python Environment](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/601)** Code Review
  - This PR introduces a fully functional desktop frontend for our Python backend using Electron + React.

---

### Associated Issues Completed
| Issue ID | Title | Status |
|----------|-------|--------|
| [#479](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/479) | Optimization and Refactoring for Resume generation and download | ✅ Closed |
| [#519](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/519) | Update DB Schema to include RESUME Table | ✅ Closed |
| [#565](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/565) | Load/Edit Resume | ✅ Closed |
| [#566](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/566) | Save Resume Edits | ✅ Closed |
| [#596](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/596) | Update save_resume_edits to include RESUME_SKILLS | ✅ Closed |
| [#594](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/594) | Create Tailored Resume | ✅ Closed |
| [#579](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/597) | Setup Project Environment to include React Native for Frontend | ✅ In Progress |

---

## Work Breakdown

### Coding Tasks

* **PR #558 – Added DB schema for resume versions:** Updated the database to include storage for a résumé after edits, with name and id association. Test classes updated.
* **PR #567 – Updated DB_SCHEMA with table of skills and unique key:** Added the RESUME_SKILLS table in dp.py to handle the section for edited general skills in the resume. Test classes updated.
* **PR #576 – Save resume edits:** Added the endpoint POST /resume/{id}/edit so users can save edits to their resumes. Test classes updated.
* **PR #568 – Load Edited Resume:** Introduced the endpoint for loading an edited resume (GET /resume/{id}). Test classes updated.
* **PR #595 – Create tailored resume:** Extended the existing feature for creating a tailored resume. Test classes updated.
* **PR #601 – Integrated UI with current Python Environment:** Introduced a fully functional desktop frontend for the Python backend using Electron + React. (Code Review)

---

### Testing & Debugging Tasks

* Updated test classes for the new resume version storage and DB schema. (PR #558)
* Updated test classes for the RESUME_SKILLS table and unique key. (PR #567)
* Updated test classes for the save resume edits endpoint (POST /resume/{id}/edit). (PR #576)
* Updated test classes for the load edited resume endpoint (GET /resume/{id}). (PR #568)
* Updated test classes for the create tailored resume feature. (PR #595)
* Tested and verified the Electron + React desktop frontend integration with the Python backend. (PR #601)

---

### Collaboration & Review Tasks

* Reviewed and iterated on PRs with team members to address some feature implementation.
* Participated in code reviews, including feedback and revisions for the some PRs such as create tailored resume.
* Went through Milestone 2 and review designs made by team.

---

### Issues & Blockers

**Issue Encountered:**

* Slower reviews on PR stretched out improving future works quickly.
* Had some issues with ensuring the new endpoints for the resume align with the old one.

**Resolution:**

* Broke resume work into focused PRs (schema, save, load, tailored resume, UI) and responded to review feedback promptly so merged work could unblock the next PR and keep velocity up.
* Aligned new resume endpoints with existing patterns by implementing GET /resume/{id} and POST /resume/{id}/edit (PRs #568, #576) to match the current API style, and updated test classes across PRs #558, #567, #576, #568, and #595 to validate that new and existing resume behavior work together.

---

### Reflection

**What Went Well:**

* Completed majority of the resume work for milestone 2 and was able to troubleshoot network errors.
* Being able to start the frontend to visualize our project.
 
**What Could Be Improved:**

* Better communication within the team; too much miscommunication slows down progress on both ends; clarify use cases and what is considered and edge case.

---

### Plan for Next Week

* Continue with milestone 2 and 3 contributions. 
