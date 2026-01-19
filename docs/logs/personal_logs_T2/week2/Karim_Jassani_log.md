# Personal Log – Karim Jassani

---

## Week-2, Entry for Jan 11 → Jan 18, 2026

![Personal Log](../../../screenshots/T2-Week2-Karim-Jassani.png)

---

### Connection to Previous Week
Building on recent work around project insights and resume generation, this week focused on exposing project through an API endpoint. Additionally, I also worked on enabling the functionality to override project ranking.


---

### Pull Requests Worked On
- **[PR #491 - GET API Project by sign ](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/491)** 
  - Added single-project retrieval by signature
  - Added Relevant test cases

---

### Associated Issues Completed
| Issue ID | Title | Status |
|----------|-------|--------|
| [#490](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/490) | API endpoint for GET /projects/{signature} | ✅ Closed |
| [#434](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/492) | Allow User to Override Project Ranking | 🔄 In Progress |

---

## Work Breakdown

### Coding Tasks

#### API endpoint for GET /projects/{signature} ([#490](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/490))
- Implemented `GET /api/projects` to list project IDs, names, and top skills
- Added `GET /api/projects/{signature}` to fetch a single project by signature
- Registered the projects router under the `/api` prefix

#### Allow User to Override Project Ranking ([#492](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/492))
- checkout branch: karim/overwrite-project-rank
- user can now re rank project for new run but not for previously performed analysis
- problem is score needs to be between 0 and 1 but they sample run shows ordinal rank is score
- score vs rank confusion needs to be resolved before this can be picked up


---

###  Testing & Debugging Tasks

- Added tests for projects list and single-project endpoints
- Tests to fetch a single project when it exists
- Test to try to fetch a signle project when it doesn't exist

---

### Collaboration & Review Tasks

- **[PR #485 - Added endpoint for GET/projects and improved resume preview for selected projects  ](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/485)** 
- **[PR #482 - added tests  ](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/482)** 
- **[PR #480 - Added POST endpoints for Resume generation and download  ](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/480)** 
- **[PR #487 - Add logs in the correct folder  ](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/487)** 

---

### Issues & Blockers

**Issue Encountered:**
- When working on functionality to allow user to override the project rank - I noticed that problem is score needs to be between 0 and 1 but they sample run shows ordinal rank is score. This needs to be resolved.


---

### Reflection

**What Went Well:**
- Had group meeting twice this week (communication strong)
- mostly decided and clear what issues need to be worked on

**What Could Be Improved:**
- More granular commits to make code review easier
- Ongoing integration on main 

---

### Plan for Next Week
- investigate score vs rank problem - discuss with teammate who worked oni it
- Work on Milestone-2 requirements.
---
