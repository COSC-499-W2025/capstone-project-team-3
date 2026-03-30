# Personal Log – Afua Frempong

---

## Week-11 & 12, Entry for Mar 16th → Mar 29th, 2026

### Type of Tasks Worked On
![Personal Log](<../../../docs/screenshots/Week 12 Personal_Log_T2_Afua.png>)
---


### Connection to Previous Week
In week 11 & 12 I worked on finalizing unique features for our app, updating documentation and planning/prepping for video demos and in-class presentations.

---
### Pull Requests Worked On
- **[PR #888 User pfp integration ](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/888)** ✅ Merged
  - This PR adds a **user profile picture to the app. Users can upload, change, and remove a profile photo from the User Preferences page. The picture is stored as a file in (app/data/thumbnails/) and its relative path is persisted in the USER_PREFERENCES database table.

- **[PR #889 - Dark Mode Light Mode ](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/889)** ✅ Merged
 - This PR implements a dark / light mode toggle for the entire desktop application.

- **[PR #895 - Unique Feature : Cover Letter Genarator](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/895)** ✅ Merged
  - This PR introduces the Cover Letter Generator feature, allowing users to produce tailored cover letters directly from their saved resumes.

- **[PR #901 -User Summary](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/901)** 
  - This PR integrates a Professional Summary field end-to-end across the entire application stack — from the database through the backend API, resume builder, LaTeX PDF export, and the Electron/React frontend UI.

- **[PR #948 - Cover letter ai-consent api key settings ](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/948)** 
  - This PR Integrates Gemini API key enforcement and AI consent into the Cover Letter Generator page, bringing it in line with the existing Upload page behaviour. Also tightens the resume selector on the Cover Letter Page and adds session-persistent draft saving.

---

### Associated Issues Completed
| Issue ID | Title | Status |
|----------|-------|--------|
| [#813](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/813) |User Profile - Allow users the option to upload a picture for their profile #815| ✅ Closed |
| [#834](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/586) | Request User Summary #586 | ✅ Closed |
| [#814](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/964)| Dark Mode + Light Mode Feature #964 | ✅ Closed |
| [#965](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/965) |Feature: Integrate Cover Letter Generator #965 | ✅ Closed |
| [#967](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/967) |Implement front-end Cover Letter Generator page and UI #967 | ✅ Closed |

| [#968](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/968) |Connect front-end to Cover Letter API #968 | ✅ Closed |

| [#969](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/969) |Add AI and local template generation modes #969 | ✅ Closed |

| [#970](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/970) |Enable Cover Letter PDF downloads #970 | ✅ Closed |

| [#971](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/971) |Write tests for Cover Letter Generator (API and UI) #971 | ✅ Closed |

| [#972](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/972) |Update database schema for cover letters #972 | ✅ Closed |


---

## Work Breakdown

### Coding Tasks

- ####  Implemented User Summary Addition to App [PR #901 -User Summary](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/901)** 
- Integrated Personal Summary into the project (feature implementation/integration).
- Updated front-end tests related to User Preferences (test maintenance to match UI/feature behavior).
- Applied a quick fix for resume (small bugfix / content or layout correction).
 
- #### Implemented Cover Letter Generator [PR #895 - Unique Feature : Cover Letter Genarator](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/895)** ✅ Merged
  - Backend integration for cover letter generation
- Implemented server-side wiring needed to generate cover letters (commit: “Backend integration”).
- Front-end integration for cover letter generation
- Connected the UI to the new/updated backend endpoints so users can generate cover letters from the app 
- Added cleanup/normalization steps after local generation to improve the final text quality/format 
- Refreshed/expanded API docs to reflect the new cover letter feature and integration details 
- Improved error handling for PDF downloads
- Added “graceful” handling for PDF download failures and PDF formatting tweaks
- Adjusted PDF layout/formatting for the generated cover letter output 
- Added cover letter saving functionality
- Implemented persistence so generated cover letters can be saved 
- Removed PDF file caching / Removed cached PDF behavior ( to avoid stale downloads and/or storage issues)
- Theme/UI polish (dark + light mode hover buttons)
- Updated hover button styling so it works properly in both themes 
- Updated tests and database seed data
- Adjusted automated tests and seed data to account for the new feature and flows 
- Added Gemini key settings for cover letter generation
- Added configuration support for a Gemini API key used in cover letter generation 
- CSS restructuring / cleanup and Refactored CSS organization/structure 

- #### Implemented user profile picture feature [PR #888 User pfp integration ](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/888)** ✅ Merged
  -  Database/schema update

Added a new column profile_picture_path TEXT to the USER_PREFERENCES SQLite table via a schema migration, so the app can persist where a user’s profile picture is stored.
Backend: profile picture API endpoints

Implemented endpoints to:
Upload a profile picture (POST)
Serve/retrieve a profile picture (GET)
Delete a profile picture (DELETE)
Backend: file storage + persistence

Saved uploaded images as files under app/data/thumbnails/.
Stored the relative path to the saved image in USER_PREFERENCES.profile_picture_path.
Frontend: User Preferences upload UI

Added a circular avatar component with:
Click-to-upload overlay
“Change” and “Remove” actions
Supported common image formats (PNG/JPG/WebP/GIF).
Frontend: persistence behavior

Implemented logic to fetch and display the saved profile picture on page mount, so the image persists across reloads.
Frontend: Portfolio dashboard integration

Updated the Portfolio Dashboard “profile hero card” to:
Render the profile photo if present
Otherwise fall back to the existing initials avatar.
CSS/styling alignment

Updated/added styles for the profile picture UI using existing design system variables (colors, transitions, etc.).
Regression boundary: Resume page unaffected

Ensured profile_picture_path does not get forwarded into the resume feature (i.e., no profile photo appears on resumes).
Automated tests added/updated

Added/updated frontend tests (Jest).
Added/updated backend tests (pytest), including user preferences API coverage.
Fixups during integration

Fixed a pfp_path typo.
Reverted/fixed navbar-related changes that were impacted during the integration work.

###  Testing & Debugging Tasks

- Updated automated tests to cover the new functionality
- Updated database seed data to support testing scenarios
- Debugged / fixed PDF generation & formatting issues
- Manual end-to-end integration test (local)
-  Jest suite (cd desktop && npx jest tests) to Investigate and fix any snapshot/UI regressions caused by avatar changes
- Verify conditional rendering paths are covered (pfp exists vs fallback initials)
- Backend automated test run + triage
- Pytest for seeded DB + preferences API (python -m pytest tests/test_db_seed.py tests/api/test_user_preferences_api.py -v)
- Confirmed uploaded files land in app/data/thumbnails/
- Validated the stored path is relative and is the same value used by the frontend on mount

---

### Reflection
**What Went Well:**

* Great finish to our last couple sprints we really put a lot of effort to create unique features and polish up our app's UI 
* We divided and assigned documentation tasks equally and were able to have a sucessful M3 presentation

**What Could Be Improved:**
* Finalizing our video sooner
* Weren't able to have full dry run for our in class presentation 

### Plan for Next Cycle
- In-class Project Voting and review of final App
---