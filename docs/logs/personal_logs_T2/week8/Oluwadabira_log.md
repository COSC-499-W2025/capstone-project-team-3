# Personal Log – Oluwadabira Omotoso

---

## Week-8, Entry for Feb 23 → Mar 1, 2026

![Personal Log](../../../screenshots/Week%205%20Personal%20Log%20T2-%20Oluwadabira.png)

**Note**: missing updated personal log image as peer eval not yet open

---

### Connection to Previous Week

Building on last week’s end‑to‑end résumé flow (preview, download, save, edit), this week I focused on polishing and extending the resume editing experience: fixing download issues for saved resumes, improving how resumes/projects are ordered, adding a way to delete projects from a saved resume, enabling drag‑and‑drop reordering of projects, and exposing a backend endpoint to add projects back to an existing resume.

---

### Pull Requests Worked On

- **[PR #710 – Fixed download for saved resumes](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/710)** ✅ Merged  
  - Fixed a bug where saved resumes were not exporting correctly by normalizing data when generating the TeX format.
  - Updated the ordering logic so master and tailored resumes are ordered by last modified date (most recent first), while still respecting user‑defined display order on tailored resumes.

- **[PR #724 – Delete projects on a resume](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/724)** ✅ Merged  
  - Added `DELETE /resume/{resumeId}/project/{projectId}` to remove a project from a saved resume without deleting the project itself.
  - Updated the Resume Builder UI so, in edit mode for saved resumes, each project shows an “×” button that prompts the user and then removes that project from the resume.

- **[PR #725 – Edit display order](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/725)** ✅ Merged  
  - Implemented drag‑and‑drop reordering of projects in the resume preview using `@dnd-kit`.
  - Persisted the new display order with the resume so users can control the project sequence for tailored resumes.

- **[PR #728 – Add projects to resume (endpoint)](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/728)** ✅ Merged  
  - Added `POST /resume/{resume_id}/projects` so users can attach additional projects from the database to an existing resume.
  - Implemented `add_projects_to_resume(resume_id, project_ids)` to skip duplicates, append new projects after the current max `display_order`, reject changes to the master resume (id=1), and handle invalid/empty inputs safely.
  - Documented how to test the endpoint with Postman (GET `/resume_names`, GET `/api/projects`, then POST with `project_ids` and verify success/error cases).

---

### Associated Issues Completed

| Issue ID | Title | Status |
|----------|-------|--------|
| [#709](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/709) | Fix for Download (saved) and Order resume by dates | ✅ Closed by [#710](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/710) |
| [#721](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/721) | Delete a project on the resume | ✅ Closed by [#724](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/724) |
| [#722](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/722) | Edit display order of projects on a resume | ✅ Closed by [#725](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/725) |
| [#727](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/727) | Add endpoint that adds project to a resume | ✅ Closed by [#728](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/728) |

---

## Work Breakdown

### Coding Tasks

- **Download fixes and ordering (`#710`)**  
  - Normalized data when generating TeX so saved resumes download correctly.
  - Updated resume ordering for master and tailored resumes so the most recently modified versions appear first.

- **Delete projects from a resume (`#724`)**  
  - Implemented backend delete logic to remove project–resume associations only.
  - Updated the Resume Builder UI to show a delete (×) button per project in edit mode for saved resumes, with a confirmation prompt and content refresh.

- **Drag‑and‑drop display order (`#725`)**  
  - Added drag handles (⋮⋮) to project headers in edit mode and wired `@dnd-kit` to reorder projects.
  - Persisted the new ordering so users’ custom sequences are reflected in the saved resume.

- **Add projects to existing resume (`#728`)**  
  - Implemented `add_projects_to_resume` and wired it to `POST /resume/{resume_id}/projects`, including validation (no changes to master resume, skip existing projects, handle empty/malformed input).
  - Ensured new projects are appended at the bottom of the resume, ordered by `last_modified` descending among the newly added ones.

---

### Testing & Debugging Tasks

- Verified that saved resumes now download correctly in both PDF/TeX formats after the normalization change, and that ordering by last modified date behaves as expected. (PR #710)
- Manually tested deleting projects from saved resumes: confirmed the project disappears from the resume view, does not affect the projects list, and that the delete button is only shown for editable saved resumes. (PR #724)
- Tested drag‑and‑drop project reordering in edit mode and confirmed the new order is persisted and used on refresh. (PR #725)
- Used Postman to exercise the new `POST /resume/{resume_id}/projects` endpoint: success cases, master‑resume rejection, not‑found resume, empty `project_ids`, duplicates, and invalid request bodies. (PR #728)
- Ran frontend tests with `npm run test` and backend tests with `pytest` (via Docker), updating or adding tests for the new download behavior, delete endpoint, drag‑and‑drop logic, and add‑projects endpoint.

---

### Collaboration & Review Tasks

- Responded to review feedback on download behavior for saved resumes and confirmed fixes via updated tests and screenshots. ([#710](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/710))
- Clarified UX expectations for deleting projects (including future improvements like showing the project name in the confirmation message) and confirmed there is a path to re‑add removed projects via the new endpoint. ([#724](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/724), [#728](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/728))
- Discussed the drag‑and‑drop interaction and shared an explanatory video so reviewers could see the behavior end‑to‑end. ([#725](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/725))

---

### Issues & Blockers

**Issues Encountered:**

- Saved resumes had edge cases in export where data shape differences caused download failures or inconsistent output.
- Deleting projects introduced UX questions about recovery and how users can add projects back after removal.
- Drag‑and‑drop reordering required careful testing to ensure it stayed in sync with backend `display_order` and did not break existing resumes.

**Resolution:**

- Normalized data for saved resumes in the export path and updated tests to lock in the fixed behavior. (PR #710)
- Implemented the add‑projects endpoint to complement delete, so users (or future UI) can recover a deleted project by re‑attaching it. (PR #728)
- Used `@dnd-kit`’s `arrayMove` plus explicit persistence of display order to keep the UI and DB aligned. (PR #725)

---

### Reflection

**What Went Well:**

- The resume editing experience is now more complete: users can download reliably, reorder projects, delete them from a resume, and (via backend APIs) add projects back.
- Pairing each UX change (delete, reorder) with solid backend support and tests made it easier for reviewers to trust the changes and merge quickly.

**What Could Be Improved:**
- The add‑projects endpoint landed as backend‑only this week; coordinating its frontend integration earlier would make the overall flow feel more polished. (Planned for future sprint)

---

### Plan for Next Week

- Wire the frontend to the add‑projects endpoint so users can recover deleted projects and enrich existing resumes directly from the UI.
- Continue refining resume UX (e.g., clearer delete confirmations with project names, better empty‑state messaging) and add tests around more edge cases in the edit/save/download flows.