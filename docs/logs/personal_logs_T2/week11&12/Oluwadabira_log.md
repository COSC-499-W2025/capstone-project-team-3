# Personal Log – Oluwadabira Omotoso

---

## Week 11 & 12, Entry for Mar 16 → Mar 29, 2026

![Personal Log](../../../screenshots/Week%2012%20Personal%20Log%20T2-%20Oluwadabira.png)

---

### Connection to Previous Week

Building from last week’s navigation and returning-user work, this stretch focused on resume feature depth (skills, new sections, sidebar polish, reordering), app configuration for AI, packaging the **Big Picture** desktop app with a PyInstaller backend sidecar and release automation, plus an architecture documentation refresh for peer testing and handoff.

---

### Pull Requests Worked On

- **[PR #863 – Grouped Skills by Expertise Level](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/863)** ✅ Merged  
  - Resume skills are returned and edited as **Proficient** and **Familiar** buckets from existing `SKILL_ANALYSIS` evidence; user edits persist on the resume; LaTeX export and the skills UI show the two groups and skip empty ones.
  - Backend, frontend, export path, and tests updated end-to-end.

- **[PR #866 – Resume Sections Base (Awards & Work Experience)](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/866)** ✅ Merged  
  - Database and API support for **RESUME_AWARDS** and **RESUME_WORK_EXPERIENCE**; resume endpoints and export formats include these sections when present; frontend types aligned.
  - Lays the foundation for the follow-on frontend and UX work.

- **[PR #868 – Add Resume Sections (Frontend)](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/868)** ✅ Merged  
  - In edit mode, **Add section** offers **Awards & Honours** and **Work experience**; users can add fields and save; ConsentPage test failure fixed.

- **[PR #871 – Resume Sidebar Upgrades](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/871)** ✅ Merged  
  - **Duplicate** and **Rename** for tailored resumes via the ⋮ menu (inline rename on tailored rows; master duplicate-only where applicable); pencil/edit works even when another résumé row was selected first.
  - Resume preview and sidebar tests updated.

- **[PR #898 – Add API key settings](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/898)** ✅ Merged  
  - Users can save, view, and clear a **Gemini** API key outside the repo (`gemini.env` under app config); server loads `GEMINI_API_KEY` on startup; Settings entry and upload warnings when AI is chosen without a key; Docker Compose mounts config for persistence; tests updated.

- **[PR #899 – Added drag and drop to new sections](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/899)** ✅ Merged  
  - Drag-and-drop reordering for **work experience** and **awards** in the resume preview (same ⋮⋮ pattern as projects); prefixed sortable IDs (`project-*`, `work-*`, `award-*`) so `@dnd-kit` IDs do not collide; save/reload keeps order.

- **[PR #945 – Updated system architecture](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/945)** ✅ Merged  
  - Updated the **system architecture** diagram and description in docs to match the current system.

- **[PR #963 – Deployment2 (desktop + PyInstaller sidecar)](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/963)** ✅ Merged  
  - **Big Picture** desktop: Electron spawns a **PyInstaller** backend sidecar; **preload/main** expose the API base URL over **IPC**; the renderer uses that origin instead of a fixed dev URL.
  - Backend: `sidecar_main` / `api_app`, resume & cover-letter routes, LaTeX/PDF helpers, `backend-sidecar.spec`, **NumPy 2.x** requirements for thinc/spaCy; CI **`release-desktop`** (macOS), artifacts, release uploads with GitHub’s **2 GiB** file cap and **`DOWNLOAD-INSTALLERS-HERE.txt`** for testers; desktop and API tests adjusted where the API origin changed.

---

### Associated Issues Completed

| Issue ID | Title | Status |
|----------|-------|--------|
| [#860](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/860) | Proficient / Familiar skill grouping | ✅ Closed by [#863](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/863) |
| [#861](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/861), [#862](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/862) | Awards & work experience sections (backend / data model) | ✅ Closed by [#866](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/866) |
| [#867](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/867) | Add resume sections in the frontend | ✅ Closed by [#868](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/868) |
| [#864](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/864) | Resume sidebar upgrades (duplicate, rename, edit) | ✅ Closed by [#871](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/871) |
| [#896](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/896) | Gemini API key handling in-app | ✅ Closed by [#898](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/898) |
| [#865](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/865) | Drag-and-drop for new resume sections | ✅ Closed by [#899](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/899) |
| [#973](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/973), [#974](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/974), [#975](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/975) | Desktop sidecar, release docs, macOS smoke-test checklist | ✅ Work delivered in [#963](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/963) (linked issues for ongoing QA / docs) |

---

## Work Breakdown

### Coding Tasks

- **Grouped skills by expertise (`#863`)**  
  - Two buckets from analysis evidence; persist edits; export and UI omit empty groups; tests on backend and desktop.

- **Awards & work experience – backend & export (`#866`)**  
  - New resume sections in the DB and API; exports include them when set; frontend types updated.

- **Awards & work experience – frontend (`#868`)**  
  - Add-section flow, section components, resume page wiring; fixed failing ConsentPage test.

- **Resume sidebar (`#871`)**  
  - Duplicate, inline rename, edit-from-non-selected row; preview/sidebar behaviour and tests.

- **Gemini API key (`#898`)**  
  - Persistence helpers, routes, env loading on startup, Settings and Upload UX, Compose volume for config, `platformdirs`; desktop and API tests.

- **Drag-and-drop for work & awards (`#899`)**  
  - Shared `SortableContext` with prefixed IDs; `handleDragEnd` routes `arrayMove` correctly; tests.

- **System architecture docs (`#945`)**  
  - Diagram and narrative brought up to date.

- **Desktop sidecar & release (`#963`)**  
  - Electron lifecycle, IPC API URL, PyInstaller spec and static bundle needs, `release-desktop` workflow, NumPy/thinc alignment, installer distribution notes.

---

### Testing & Debugging Tasks

- Ran backend tests (Docker/pytest where applicable) and `desktop` Jest for skills, sections, sidebar, API key, and DnD flows. (PRs **#863, #866, #868, #871, #898, #899**)
- Manually smoke-tested skill buckets, add-section flows, sidebar duplicate/rename, key save/clear and upload warnings, drag order then save/reload. (**#863–#899**)
- For the desktop build: smoke-tested connectivity, upload, and resume flows from **Release** / **Artifacts** as documented; verified sidecar and **`desktop-release-macos`** path when DMGs exceed release attachment limits. (**#963**)

---

### Collaboration & Review Tasks

- Iterated on reviews across resume, settings, and desktop PRs (wiring, tests, CI and packaging constraints).
- Updated architecture documentation for reviewers and testers. ([#945](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/945))
- Reviewed teammates’ PRs and left comments where useful.

---

### Issues & Blockers

**Issues Encountered:**

- **`main`** had removed **`app/static`**, which the PyInstaller spec expects; merging **`main`** into the desktop branch dropped those assets until they were restored for sidecar builds and CI.  
- GitHub’s **2 GiB** cap on a single release asset sometimes forces installers to live under **workflow Artifacts** instead of on the release page.

**Resolution:**

- Restored **`app/static`** (portfolio / analysis-runner assets) and aligned **`backend-sidecar`** CI (e.g. disk space on Linux runners) so **Build Backend Sidecar** succeeds.  
- Documented tester steps via **`DOWNLOAD-INSTALLERS-HERE.txt`** and the Actions run link. (**#963**)

---

### Reflection

**What Went Well:**

- End-to-end resume improvements (data model → UI → export) stayed cohesive across stacked PRs; desktop packaging made peer testing on a real app binary feasible.

**What Could Be Improved:**

- Earlier alignment on which files must stay in-repo for frozen builds (e.g. **`app/static`**) when **`main`** removes folders, to avoid CI surprises after merges.

---

### Plan for Next Week

- Continue peer-testing feedback and polish; watch for edge cases in packaged vs dev API origins.
- Follow up on any remaining nice-to-haves from testing (e.g. real-time updates where refresh is still manual).
