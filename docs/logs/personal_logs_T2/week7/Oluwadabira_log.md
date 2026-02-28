# Personal Log – Oluwadabira Omotoso

---

## Week-7, Entry for Feb 16 → Feb 22, 2026

---

### Connection to Previous Week

Building on the earlier work for the Resume Builder (sidebar, base display, and tailored preview flow), this week I focused on completing the end‑to‑end résumé experience: downloading resumes in multiple formats, saving and loading tailored resumes, and enabling in‑place editing of skills and projects. I also refined the backend export logic and error handling so the frontend flows are robust and match our API contracts.

---

### Pull Requests Worked On

- **[PR #679 – Design for download resume + updated export logic](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/679)** ✅ Merged  
  - Added the initial Resume Builder header with a Download button (dropdown for “Download as PDF” / “Download as TeX”), wired to new GET export endpoints that support `resume_id` or `project_ids` and return blobs for browser download. 
  - Updated backend export logic to handle master, saved, and preview resumes in a single endpoint and return a 400 when both `resume_id` and `project_ids` are provided.  
- **[PR #680 – Fully implemented download + header for resume](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/680)** ✅ Merged  
  - Completed the download flow and header UI, including save button placement and behavior. 
  - Tightened the `ResumeFilter` schema (name now required with `min_length=1`), removed redundant manual validations, and updated tests.  
- **[PR #669 – UI/view tailored](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/669)** ✅ Merged  
  - Wired the Project Selection page to the Resume Builder so that selecting projects and clicking “Generate Resume” opens a preview tailored resume. 
  - Added “Preview Resume (Unsaved)” into the sidebar and ensured switching to a saved resume exits preview correctly.  
- **[PR #690 – Save and Loading tailored resume](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/690)** ✅ Merged  
  - Implemented the core logic for saving a tailored resume from preview to a persisted version, then loading it from the sidebar. This included generating default resume names, wiring the Save button to the backend, and updating tests so the save/load behavior is covered.  
- **[PR #700 – Edit Resume](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/700)** ✅ Merged  
  - Added editing support for tailored resumes directly in the Resume Builder. The Edit button is shown only for saved tailored resumes (not master or preview). Users can edit the Skills and Projects sections, including project dates via a date picker, and changes persist when saved.

---

### Associated Issues Completed

| Issue ID | Title | Status |
|----------|-------|--------|
| [#607](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/607) | Create Tailored Resume (UI) | ✅ Closed by [#669](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/669) |
| [#677](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/677) | Update backend logic to handle edited/saved resumes | ✅ Closed by [#679](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/679) |
| [#678](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/678) | Add frontend design, format, and style (download) | ✅ Closed by [#679](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/679) |
| [#668](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/668) | Export Resume (UI) | ✅ Closed by [#680](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/680) |
| [#688](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/688) | Modal + frontend design for save button | ✅ Closed by [#680](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/680) |
| [#609](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/609) | Save Resume Edits (UI) | ✅ Closed by [#690](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/690) |
| [#689](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/689) | Load tailored resume after save | ✅ Closed by [#690](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/690) |
| [#608](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/608) | Load/Edit Resume (UI) | ✅ Closed by [#700](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/700) |

---

## Work Breakdown

### Coding Tasks

- **Download & header flow (`#679`, `#680`)**  
  - Added a header with a Download button (PDF/TeX) and updated export endpoints to handle master, preview, and saved resumes with correct validation.

- **Tailored resume preview (`#669`)**  
  - Wired Project Selection to Resume Builder so selected projects show as a “Preview Resume (Unsaved)” that disappears when a saved or master resume is chosen.

- **Save & load tailored resumes (`#690`)**  
  - Implemented saving of tailored resumes so they appear in the sidebar with a name and can be reloaded from the resume list.

- **Edit tailored resumes (`#700`)**  
  - Enabled editing of Skills and Projects for tailored resumes only, with an Edit button that is hidden for the master and preview resumes.

---

### Testing & Debugging Tasks

* Manually tested download behavior (PDF/TeX) for master, preview, and saved resumes using `docker compose up --build` and `npm run dev`. (PRs #679, #680)
* Verified tailored preview mode from the Project Selection page and switching back to master/saved resumes. (PR #669)
* Tested saving tailored resumes, confirming they appear in the sidebar and reload correctly, including the default random names. (PR #690)
* Tested the Edit button for tailored resumes (Skills and Projects sections) and confirmed changes persist when saved; checked that master and preview resumes cannot be edited. (PR #700)
* Ran backend tests with `pytest` and frontend tests with `npm run test`, updating tests for export error codes and resume name validation. (PRs #679, #680)

---

### Collaboration & Review Tasks

- Responded to reviewer questions about:
  - Error behavior for supplying both `resume_id` and `project_ids` to export endpoints, and adjusted logic to return 400 with clear semantics ([#679](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/679)).  
  - Proper status codes for missing resumes vs server failures (404 `ResumeNotFoundError` vs 500 `ResumeServiceError`) in export routes ([#679](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/679)).  
  - UX details around save vs edit buttons, random name generation, and when saved names should show up in the sidebar ([#680](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/680), [#690](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/690)).  
  - Whether project dates should always be present and how that affects the edited resume UX ([#700](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/700)).  
- Incorporated feedback and iterated quickly so PRs could be merged into Milestone 2.

---

### Issues & Blockers

**Issues Encountered:**

- Getting the export endpoints to correctly handle master vs saved vs preview resumes (and return the right status codes) required careful coordination between backend logic and frontend defensive checks.
- The save and edit flows introduced UX edge cases (e.g., when to show the Save button vs Edit icon, how random names should behave, and when edits should persist to the sidebar).

**Resolution:**

- Solved export behavior into the GET endpoints, added 400s for invalid parameter combinations, and distinguished 404 vs 500 errors based on exception type, as suggested in reviews.  
- Clearly separated responsibilities between the Save button (persisting a version) and the Edit button (modifying fields before persisting).

---

### Reflection

**What Went Well:**

- The résumé flow is now much more complete: users can pick projects, preview a tailored resume, download it (PDF/TeX), save it, reload it, and edit it—all within the Resume Builder.

**What Could Be Improved:**

- The review of PRs much closer to when it was published. The lack of reviews slows down the continuous implementation that might be planned.

---

### Plan for Next Week

- Continue to add endpoints for resume and other aspects of the project that might be missing.