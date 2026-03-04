# Personal Log – Afua Frempong

---

## Week-7, Entry for Feb 16 → Feb 22, 2026

### Type of Tasks Worked On

---


### Connection to Previous Week
In week 7 I completed the implementation of edit portfolio API endpoints in the front-end, displaying the user preference page and using additional user preference fields in our resume. This week, we plan to finilize front-end integration as we approach M2.

---
### Pull Requests Worked On
- **[PR #669 Education Details added to Resume ](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/699)** ✅ Merged
  - This PR integrates the education_details feature from user preferences into the resume generation and display system.

- **[PR #660 - Display User Preference Page](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/660)** ✅ Merged
  - Implemented User Preferences page with a React/TypeScript frontend and FastAPI backend integration. The page allows users to manage their profile information including personal details, background, and education history with Canadian institution autocomplete search.

- **[PR #659 - Display Front End Portfolio Edits](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/660)** ✅ Merged
  - This PR integrates the backend portfolio editing API with the frontend dashboard, enabling users to edit project details directly from the portfolio view through inline editing.

---

### Associated Issues Completed
| Issue ID | Title | Status |
|----------|-------|--------|
| [#585](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/466) | Portfolio Customization UI | ✅ Closed |
| [#584](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/464) | Load Portfolio View with Applied customizations| ✅ Closed |
| [#604](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/583) | Create Front-End View of User Profile | ✅ Closed |
| [#461](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/621) | Update existing Resume Endpoints | ✅ Closed |
---

## Work Breakdown

### Coding Tasks

#### Added Education Details to Resume ([PR #669](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/559))

- Key changes:
- Backend: Updated load_user() to fetch education_details JSON from database
- Backend: Added parse_education_details() helper to parse education JSON and format dates
- Backend: Modified build_resume_model() and load_saved_resume() to use education details with fallback to legacy fields
- Backend: Updated LaTeX generation with render_education() to support multiple education entries
- API: Removed deprecated program field from EducationDetail model

#### Display User Preference Page ([PR #660](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/485))
- Backend: app/api/routes/user_preferences.py - User preferences and institution search endpoints
- Backend: app/utils/canadian_institutions_api.py - Canadian Open Data API integration
- Backend: app/main.py - Updated router imports (removed duplicate education service router)


###  Testing & Debugging Tasks
- Created `tests/UserPreferencePage.test.tsx` to ensure front end rendering 
-  EducationSection component tests updated for array format
- All changes made were withing the scope of the two aforementioned PR's.


---

### Reflection
**What Went Well:**
* Able to implement on a front-end functionalities
* Lots of work and key features completed this sprint  

**What Could Be Improved:**
* PR Review response time has gone down this week
* Review of pending tasks TBC before Demo #2

### Plan for Next Cycle
- Prepare for M2 presentation & Video submission 
- Alignment on pending M2 tasks
---