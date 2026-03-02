# Personal Log – Karim Jassani

---

## Week-8, Entry for Feb 23 → Mar 1, 2026

---

### Connection to Previous Week

Last week completed score override funcitonality, now for this week looking into overall milestone 2 demo + presentation
---

### Pull Requests Worked On

- **[PR #740 - Validation Logic for Excluded Metrics in Project Score Override](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/740)** 
  - Added normalize_exclusions() to validate exclude_metrics against allowed metric names for the current project, trim/dedupe entries, and raise OverrideValidationError on unknown metrics. 
  - Updated override preview flow to dynamically derive valid metric names from the project’s code breakdown before computing overrides. 
  - Strengthened backend integrity by preventing invalid metric inputs from propagating into score calculations.

  - **[PR #751 - M2: System Architecture Explaination](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/751)** 
  - Added description for the updated system architecture diagram in milestone 2

  - **[PR #753 - M2: Final API Documentation](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/753)** 
  - Updated the API documentaiton for Milestone 2 ensuring consistency with swagger docs



---

### Associated Issues Completed
| Issue ID | Title | Status |
|----------|-------|--------|
| [#739](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/574) | Add validation logic for list of excluded metrics | ✅ Closed|
| [#750](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/750) | M2: System Architecture Diagram Description | ✅ Closed|
| [#752](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/752) | M2: Final API Documentation | ✅ Closed|


---

## Pull Requests Reviewed

- **[PR #710 - Fixed download for saved resumes](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/710)** 

- **[PR #723 - created the main flow api with a draft ui to test api call](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/723)** 

- **[PR #729 - Portfolio role ](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/729)** 

- **[PR #742 - Task/update readme](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/742)** 

- **[PR #743 - Task - delete project api ](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/743)** 

- **[PR #741 - Personal and Team logs for week-6,7,8.](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/741)** 


---

### Reflection

**What Went Well:**
- Overall successfully completed the milestone 2 functionalities

**What Could Be Improved:**
- All good

---

### Plan for Next Week

- Understand milestone 3 functionalities and get started