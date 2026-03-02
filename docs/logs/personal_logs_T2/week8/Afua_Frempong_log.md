# Personal Log – Afua Frempong

---

## Week-8, Entry for Feb 23 → Mar 1, 2026

### Type of Tasks Worked On
![Personal Log](<../../../docs/screenshots/Week 8 Personal_Log_T2_Afua.png>)
---


### Connection to Previous Week
In week 8 I updated documentation and did the implementation of DELETE project API endpoint. This week, we plan to finilize remaining reqs and front-end integration as we approach M2.

---
### Pull Requests Worked On
- **[PR #743 Task - delete project api ](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/743)** ✅ Merged
  - This PR uses the pre-existing utils logic that delete's project insights and implements it as a REST API endpoint.

- **[PR #742 - Task/update readme ](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/742)** ✅ Merged
  - This PR updates our main README.md file with instructions on how to upload provided test files for our project and a short description of the test files.

---

### Associated Issues Completed
| Issue ID | Title | Status |
|----------|-------|--------|
| [#585](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/757) |Update Read ME #757 | ✅ Closed |
| [#584](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/758) | DELETE Project Insights API | ✅ Closed |
---

## Work Breakdown

### Coding Tasks

#### Implemented delete project api ([PR #743](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/743))

- Key changes:

- Added DELETE /api/projects/{signature} to projects.py, reusing the existing delete_project_by_signature and get_projects utilities from delete_insights_utils.py. 

- Added q/quit/exit escape hatch at every interactive prompt (project selection, yes/no confirmation, typed confirmation) so users can cancel at any point and return to the calling menu without side effects.

- Imported delete_insights_main from app.cli.delete_insights.
- Added _open_delete_manager() helper, consistent with _open_chronology_manager() and _open_ranking_manager().
- Wired 'delete' into both the pre-upload menu and the post-analysis menu.

###  Testing & Debugging Tasks
- Tests (tests/api/test_projects.py)
- Added 3 tests for the new endpoint following the existing mock/patch pattern in the file.


---

### Reflection
**What Went Well:**
* Able to implement majority of front-end functionalities
* Lots of work and key features completed this sprint  
* Completed M2 presentation and Video

**What Could Be Improved:**
* Alignment and taks delegation nearing and during final sprint for a milestone

### Plan for Next Cycle
- Polish up our app, refactor as necessary and review M3 reqs
---