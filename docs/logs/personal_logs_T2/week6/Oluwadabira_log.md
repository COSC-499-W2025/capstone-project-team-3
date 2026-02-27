# Personal Log – Oluwadabira Omotoso

---

## Week-6, Entry for Feb 9 → Feb 15, 2026

---

### Connection to Previous Week

Building on the previous weeks, I continued the resume feature work: backend (DB schema, save/load/tailored resume endpoints) and the frontend. This week I focused on the resume UI flow—sidebar, display view, project selection for tailored resumes—and added tests for the Resume Builder and sidebar.

---

### Pull Requests Worked On

- **[PR #638 - Resume Sidebar (beginning of landing page)](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/638)** ✅ Merged
  - Introduced the Resume UI with a collapsible sidebar listing resumes (from `GET /resume_names`), selection to load master or saved resume, API client (`getResumes()`, `buildResume()`, `getResumeById()`), and resume bullets fix. Backend tests added.
- **[PR #640 - Added tests and fixed console error](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/640)** ✅ Merged
  - Added frontend tests for Resume Builder flow: `ResumeBuilderPage.test.tsx` (fetch on mount, sidebar list, selection, toggle) and `ResumeSidebar.test.tsx` (title, names, onSelect, active class, onTailorNew, empty-name fallback, toggle, icon buttons). Closes #639.
- **[PR #649 - Display Resume (UI)](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/649)** ✅ Merged
  - Introduced the resume display view: `ResumeSections` folder with section components, `ResumePreview.tsx`, `ResumeBuilderPage.tsx` as entry point, and CSS moved to styles folder. Tests added for resume sections and builder page.
- **[PR #662 - Create Tailored Resume (Project Selection Page)](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/662)** ✅ Merged
  - Project Selection Page for tailored resume: backend projects API includes `date_added`, frontend `projects.ts` API, `ProjectSelectionPage.tsx` with table and checkboxes, “Generate Resume” button, and Resume Builder “Tailor New Resume” to project selection. Closes #661.
- **[PR #669 - UI/view tailored](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/669)** Code Review
  - UI for viewing tailored resume. Closes #607.

---

### Associated Issues Completed
| Issue ID | Title | Status |
|----------|-------|--------|
| [#639](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/639) | Resume Sidebar / Resume Builder tests | ✅ Closed |
| [#642](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/642) | (Resume sidebar related) | ✅ Closed |
| [#610](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/610) | Display Resume (UI) | ✅ Closed |
| [#661](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/661) | Create Tailored Resume – Project Selection Page | ✅ Closed |
| [#607](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/607) | UI/view tailored | In Review (PR #669 draft) |

---

## Work Breakdown

### Coding Tasks

* **PR #638 – Resume Sidebar:** Resume Builder page with collapsible sidebar, `GET /resume_names`, API client and TypeScript types, `ResumeManager.css` / `ResumeSidebar.css`, SVG assets, resume bullets JSON fix. Backend tests added.
* **PR #640 – Tests and console fix:** `ResumeBuilderPage.test.tsx` and `ResumeSidebar.test.tsx` for fetch, sidebar list, selection, Tailor New button, active class, empty-name fallback, toggle, and icon behavior.
* **PR #649 – Display Resume (UI):** `ResumeSections` components, `ResumePreview.tsx`, `ResumeBuilderPage.tsx` as resume entry point, CSS moved to styles folder. Tests for resume sections and builder page.
* **PR #662 – Create Tailored Resume (Project Selection Page):** Backend `date_added` in projects API, `desktop/src/api/projects.ts`, `ProjectSelectionPage.tsx` (table, checkboxes, Generate Resume), navigation from “Tailor New Resume” to project selection. Tests for project selection page and backend.
* **PR #669 – UI/view tailored:** Work in progress on UI for viewing tailored resume.

---

### Testing & Debugging Tasks

* Added and updated backend tests for `GET /resume_names` and resume flow. (PR #638)
* Added `ResumeBuilderPage.test.tsx` and `ResumeSidebar.test.tsx` for Resume Builder and sidebar behavior. (PR #640)
* Added tests for resume sections and ResumeBuilderPage display. (PR #649)
* Removed broken CDN link in CSS per review (PR #649); added `ProjectSelectionPage.test.tsx` and updated projects backend tests. (PR #662)
* Manual testing of sidebar, resume display, and project selection flow across PRs.

---

### Collaboration & Review Tasks

* Reviewed and iterated on PRs with team members to address some feature implementation.
* Participated in code reviews, including feedback and revisions for the some PRs such as create tailored resume.
* Went through Milestone 2 and review designs made by team.

---

### Issues & Blockers

**Issue Encountered:**

* Large PRs (e.g. #638, #649) made review slower; reviewers suggested a note on PR length for TAs.

**Resolution:**

* Merged PR #649 after addressing feedback; continued with remaining features and remained open to follow-up changes.

---

### Reflection

**What Went Well:**

* Shipped the resume UI flow end-to-end: sidebar (PR #638), display view (PR #649), and project selection for tailored resume (PR #662), with tests.
* Got positive review feedback on test coverage, sidebar UX, and flow (e.g. Project Selection → Resume Builder → Tailor New).
* Multiple PRs merged this week, advancing Milestone 2.

**What Could Be Improved:**

* Keep PRs smaller where possible and add a short “PR length” note for reviewers/TAs to avoid mark reduction.
* Double-check external links (e.g. CDN) and run a quick UI pass before opening PRs.

---

### Plan for Next Week

* Get PR #662 (Project Selection Page) through review and merged.
* Complete and open PR #669 (UI/view tailored) for review.
* Continue Milestone 2 and 3 contributions; align resume model with updated user_preferences where needed.