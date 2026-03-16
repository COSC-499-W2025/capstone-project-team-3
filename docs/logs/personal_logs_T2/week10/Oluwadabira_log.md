# Personal Log – Oluwadabira Omotoso

---

## Week-10, Entry for Mar 9 → Mar 15, 2026

![Personal Log](../../../screenshots/Week%2010%20Personal%20Log%20T2-%20Oluwadabira.png)

---

### Connection to Previous Week

Building from lasting week, I did not have any active coding contributions but going into this week, received feedback on what needed to be completed for peer testing. This week focused on tying up loose ends for peer testing majorly revolving around navigation and returning users.
---

### Pull Requests Worked On

- **[PR #787 – Handle no projects for resume](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/787)** ✅ Merged  
  - Handles the resume page when there are no projects in the database: sidebar hides master resume and tailored resumes, shows a notification to upload a project.
  - On the backend, when a project is deleted from the database, the project's details (name, dates, skills, bullets) are copied into the resume first, then the project is deleted, so resume content is preserved.
  - Added database migration for existing databases to support the snapshot behaviour.

- **[PR #806 – Add Project to an Existing Resume](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/806)** ✅ Merged  
  - Added an "Add project" button (visible in edit mode) that opens a modal listing projects from the database that are not already on the resume.
  - Users can select projects and add them to the current tailored resume; addressed review feedback (checkbox/row double-toggle, backend error message display in modal).

- **[PR #811 – Introduced Navigation for Returning User and First Time User](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/811)** ✅ Merged  
  - Returning users (with consent already given) are redirected to the hub page after a short delay on the welcome page; first-time users are taken to the consent page on click.
  - Restructured how the consent API is called and added an error notification design for API failures.
  - Added tests for returning user, first-time user, and API error cases.

- **[PR #819 – Updated Navigation bar and Navigation in ResumeBuilder and ProjectSelection](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/819)** ✅ Merged  
  - New navigation bar with links to key pages (collapsible).
  - ResumeBuilderPage home link now points to the Hub Page instead of the welcome page; ProjectSelectionPage responsiveness improved and a back button added.
  - Profile link updated to Settings.

---

### Associated Issues Completed

| Issue ID | Title | Status |
|----------|-------|--------|
| [#786](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/786) | Handle no projects for resume | ✅ Closed by [#787](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/787) |
| [#726](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/726) | Add project to an existing resume | ✅ Closed by [#806](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/806) |
| [#810](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/810) | Navigation for returning user and first time user | ✅ Closed by [#811](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/811) |
| [#816](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/816), [#818](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/818) | Navigation bar and ResumeBuilder/ProjectSelection updates | ✅ Closed by [#819](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/819) |

---

## Work Breakdown

### Coding Tasks

- **Handle no projects for resume (`#787`)**  
  - Frontend: resume page when there are no projects—sidebar hides master/tailored resumes, shows upload notification; tailored resume button greyed out when no projects.
  - Backend: on project delete, copy project details (name, dates, skills, bullets) into the resume first, then delete the project so resume content is preserved; added DB migration for snapshot behaviour.

- **Add project to an existing resume (`#806`)**  
  - "Add project" button in edit mode opens a modal of projects not already on the resume; users select and add them to the tailored resume.
  - Addressed review: single handler for checkbox/row (stopPropagation), and parseErrorDetail(res) to show backend error message in the modal.

- **Navigation for returning vs first-time user (`#811`)**  
  - Welcome page checks consent on mount; returning users redirect to hub after ~3s, first-time users go to consent page on click.
  - Restructured consent API usage and added error notification UI; added tests for returning user, first-time user, and API error.

- **Navigation bar and ResumeBuilder/ProjectSelection (`#819`)**  
  - New collapsible navigation bar with links to key pages; ResumeBuilder home link now goes to Hub Page; ProjectSelectionPage responsiveness and back button; Profile to Settings.

---

### Testing & Debugging Tasks

- Manual testing for no-projects resume flow: no projects landing page, sidebar behaviour, greyed-out tailor button; after deleting all projects, tailored resume kept snapshot content. (PR #787)
- Tested add-project modal: no unique projects, no existing projects, and adding a unique project; ran `npm run test` for new component/unit tests. (PR #806)
- Verified returning user redirect to hub after delay and first-time user click to consent page; confirmed error notification when consent API fails; ran WelcomePage tests. (PR #811)
- Checked navigation bar (collapsible, links), ResumeBuilder home to Hub, ProjectSelection responsiveness and back button, Profile to Settings; ran frontend tests. (PR #819)

---

### Collaboration & Review Tasks

- Addressed review on no-projects PR: added DB migration for snapshot behaviour; noted refresh/real-time updates as future improvement. ([#787](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/787))
- Addressed add-project modal review: stopPropagation on checkbox/row to avoid double-toggle, and parseErrorDetail to show backend error in modal. ([#806](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/806))
- Responded to WelcomePage test feedback (act() wrapping). ([#811](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/811))
- Reviewed some teammates PRs and provided comments where needed.

---

### Issues & Blockers

**Issues Encountered:**

- No-projects resume required DB migration for existing databases so snapshot behaviour works for tables that had the old FK.

**Resolution:**

- Added migration to drop old FK and support snapshot-on-delete. (PR #787)

---

### Reflection

**What Went Well:**

- Being able to implement good UI changes, easier to picture what changes I wanted since we had a reference to a design doc.

**What Could Be Improved:**
- Reviews of PRs during the week to not slow progress on teammate's work.

---

### Plan for Next Week
- Consider refresh/real-time updates on the no-projects resume page and other pages instead of manual refresh buttons.
- Implement feedback received from peer testing.
- Consider implement nice-to-haves.