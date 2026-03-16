# Personal Log – Afua Frempong

---

## Week-10, Entry for Mar 9 → Mar 15, 2026

### Type of Tasks Worked On
![Personal Log](<../../../docs/screenshots/Week 10 Personal_Log_T2_Afua.png>)
---


### Connection to Previous Week
In week 10 I continued to refine UI components within the user preference page and added the project deletion functionality to the front-end. 

---
### Pull Requests Worked On
- **[PR #808 Updated user preference UI ](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/808)** ✅ Merged
  - Refactored the UserPreferencePage CSS to align with the project's shared design system. 

- **[PR #807 - Project Deletion UI added to Data Management Page ](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/807)** ✅ Merged
  - This PR adds project deletion functionality to the Data Management page. Each project row now displays a red trash icon button. Clicking it opens a two-step confirmation modal. First asking the user to confirm, then requiring them to type the project name + signature prefix before the deletion is encoded and submitted to the backend DELETE /api/projects/{signature} endpoint.

- **[PR #812 - Add user settings to hub page ](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/812)** ✅ Merged
  - This PR adds a Settings card to the Hub Page that navigates to a intermediate Settings Page. The Settings Page presents two options : Profile (User Preferences) and Privacy (Consent) - as cards, similar to the existing Hub Page UI design. A back button returns the user to the Hub.

- **[PR #833 - User Preference Flow/Navigation ](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/833)** 
  - This PR updates the post-save navigation flow on the User Preference page and improves how first-time vs. returning users are distinguished.

- **[PR #817 - LinkedIn URL integrated back to front-end ](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/817)** 
  - This PR connects the LinkedIn URL field on the User Preference page to the backend, persisting it in the database and surfacing it on the generated resume.

---

### Associated Issues Completed
| Issue ID | Title | Status |
|----------|-------|--------|
| [#815](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/815) |Collect Store & Display User's LinkedIn Profile #815| ✅ In-Review |
| [#834](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/834) | Returning + First Time User Navigation for User Preference Page #834 | ✅ In-Review |
| [#814](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/814) |Update Profile UI to align with current UI #814  | ✅ Closed |
| [#799](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/799) |Front-end Deletion #799 | ✅ Closed |
| [#800](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/800) |Add settings option to hub page #800 | ✅ Closed |
---

## Work Breakdown

### Coding Tasks

#### Implemented delete project api in the front-end ([PR #743](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/743))

- Key changes:
  - Added `DELETE /api/projects/{signature}` endpoint in `app/api/routes/projects.py`, reusing existing `delete_project_by_signature` and `get_projects` utilities from `delete_insights_utils.py`. Returns 404 if project not found, 500 on unexpected failure.
  - Added `q`/`quit`/`exit` escape hatch at every interactive prompt in `app/cli/delete_insights.py` (project selection, yes/no confirmation, typed confirmation) so users can cancel cleanly without side effects.
  - Wired `delete` into both the pre-upload and post-analysis menus in `app/main.py` via a new `_open_delete_manager()` helper, consistent with existing manager patterns.
  - Added 3 API tests in `tests/api/test_projects.py` covering success (200), not found (404), and unexpected failure (500) cases.

#### - Add user settings navigation to hub page [PR #807](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/807)
- Key changes:
  - Added a new `SettingsPage.tsx` presenting two navigation cards **Profile** (→ `/userpreferencepage`) and **Privacy** (→ `/consentpage`) — styled consistently with the existing Hub Page card UI.
  - Added a **Settings** card to `HubPage.tsx` that navigates to the new Settings page.
  - I opted for an intermediate page rather than a dropdown for a more seamless User Experience and to reduce the amount of potential clutter on the main hub page.
  - Back navigation on `SettingsPage` uses `navigate(-1)` (updated after review feedback) rather than a hardcoded route, making it resilient to future route renaming.
  - Added `SettingsPage.test.tsx` covering rendering, navigation to Profile and Privacy, back button behaviour, and aria-labels; updated `HubPage.test.tsx` to reflect the new Settings card.

### Added LinkedIn URL Retreival from DB  ([PR #817](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/817)) 
- Key changes:
  - Added `linkedin TEXT` column to the `USER_PREFERENCES` table in `app/data/db.py` with a migration function that handles both the rename-from-misspelling (`linkden → linkedin`) and fresh-add cases.
  - Updated `GET /api/user-preferences` and `POST /api/user-preferences` routes in `app/api/routes/user_preferences.py` to read and write the `linkedin` field.
  - Updated `app/utils/user_preference_utils.py` (`get_latest_preferences`, `save_preferences`) to include `linkedin`.
  - Updated `app/utils/generate_resume.py` `load_user()` to SELECT `linkedin` and build a LinkedIn link entry in the resume `links` array, so the URL surfaces in the generated resume header.
  - Added `linkedin?: string | null` to the `UserPreferences` TypeScript interface in `desktop/src/api/userPreferences.ts` and wired it through `convertToFrontend` / `convertToBackend` in `UserPreferencePage.tsx`.


###  Testing & Debugging Tasks
-  Updated a failing test in SettingsPage.tests.tsx from a previous PR when navigation was expecting -1 but got \hubpage
- Updated tests/api/test_user_preferences_api.py — GET response now asserts linkden is returned at the correct position.
- Updated tests/test_generate_resume.py — fixture schema includes linkden; test_load_user asserts a LinkedIn link is present in resume.links.
- Added SettingsPage.test.tsx — covers rendering, navigation, back button, and aria-labels
- Updated HubPage.test.tsx — updated card count, replaced Profile card tests with Settings card tests
- Updated desktop/tests/UserPreferencePage.test.tsx — mock payload includes linkden: null to match the updated type.

---

### Reflection
**What Went Well:**

* Completed Peer Testing Task List
* Able to meet twice this week
* Our team has made lots of front-end progress within the app  

**What Could Be Improved:**
* Alignment on app flow (first time user vs returning user and all possible pages)

### Plan for Next Cycle
- Polish up our front-end of the app, refactor as necessary and review M3 reqs
- Implement feedback from peer testing next week. 
---