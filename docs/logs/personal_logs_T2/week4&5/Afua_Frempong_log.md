# Personal Log – Afua Frempong

---

## Entry for Jan 27th, 2025 → Feb 8th, 2025

### Type of Tasks Worked On
![Personal Log](<../../../docs/screenshots/Week 5 Personal Log T2_Afua.png>)
---


### Connection to Previous Week
Last week I completed the implementation of edit portfolio API endpoints. This week, as we finilized front-end design decisions I took it upon myself to start the process of collecting and using additional user preference fields in our resume & portfolios. 

---
### Pull Requests Worked On
- **[PR #559 - Customize/Edit information about a portfolio showcase project (Portfolio/Edit API)#559 ](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/559)** ✅ Merged
  - This PR adds a batch edit endpoint for portfolio projects, allowing multiple projects to be updated in a single API call. The endpoint supports updating project name, summary, timestamps (created_at, last_modified), and rank values.

- **[PR #605 - Additional user info pt 1](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/605)** ✅ Merged
  - This PR implements an updated user preferences management system to include education details such as institution, degree, start_date, end_date and GPA.

---

### Associated Issues Completed
| Issue ID | Title | Status |
|----------|-------|--------|
| [#585](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/585) | Outline Eduction model for DB storage | ✅ Closed |
| [#584](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/584) | Update Existing user Preference API endpoints| ✅ Closed |
| [#604](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/604) | Create Institution API Endpoints | ✅ Closed |
| [#461](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/461) | Define Editable Portfolio Fields | ✅ Closed |
| [#462](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/462) | CBackend Model for Portfolio Customization | ✅ Closed |
| [#463](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/463) |API Endpoint: Edit Portfolio Project| ✅ Closed |

---

## Work Breakdown

### Coding Tasks

#### Added POST endpoints for Edited Portfolio generation ([PR #559](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/559))

- Key changes:
- Added /portfolio/edit POST endpoint that accepts a batch of project edits
- Implemented validation for rank values (must be between 0.0 and 1.0)
- Used a single SQL UPDATE with CASE statements for efficient batch updates
- Included error handling and database transaction rollback on failures
- Created Post Man Portfolio Testing Collection 

#### Implemented list/institution api endpoint & added backend Model to GET user Preference endpoint ([PR #485](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/485))
- Implemented Canadian Institutions API Integration `canadian_institutions_api.py` Integrated with Canada's Open Data API for post-secondary institutions
- Implemented three search modes:
- Full search with program details
- Simple search returning only institution names
- Complete institution list fetching from Education Service Routes (eduction_service.py)

- Implemented proper JSON serialization for education details in User Preferences Management (user_preferences.py)
- Implemented flexible date validation accepting both YYYY and YYYY-MM-DD formats
- Added support for multiple education entries per user
- ** USER PREFERENCE Table in Database now includes the JSON field education_details


###  Testing & Debugging Tasks
- Created `test_education_service.py` to ensure third party API is acessible/reliable
- added full coverage tests to `api/test_portfolio.py`
- Ensured downstream changes by updating tests in `api/routes/test_user_preference_api.py`, `tests/utils/user_preference_utils.py`, `tests/cli/user_preference_cli.py` 
- All changes made were withing the scope of the two aforementioned PR's.

### Collaboration & Review Tasks
- Responded & fixed code review feedback from @PaintedW0lf on PR #559 regarding DB syntax error
- Reviewed and commented on PR to determine our front-end framework PR #601
- Collaborated with team on Resume & Portfolio models
- Reviewed @ least 1 PR from every member on the Team 
- Primary Reviewer on PR #603 by @kjassani
- Received approvals on 2 PRs from team


### Issues & Blockers

**Issue Encountered:**
- Failing tests in user preference modules
- Syntax error in DB seed() function needed to be reviewed
- Merge conflicts in `api/portfolio.py`

**Resolution:**
- Fixed tests in upstreamstream user preference files
- DB error resolved & updated wuth passing tests
- A mix of both incoming and current changes were accepted in `api/portfolio.py`
---

### Reflection
**What Went Well:**
* Able to align on a front-end framework
* Lots of review and feedback the past two sprints  

**What Could Be Improved:**
* Review of pending tasks TBC before Demo #2
* Alignment on UI flow & work TBD for M2 

### Plan for Next Cycle
- Take attention of requirements and suggestions from client and in-class speakers.
- Alignment on pending M2 tasks
---