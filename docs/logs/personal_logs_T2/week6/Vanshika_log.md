# Personal Log – Vanshika

---

## Week-6, Entry for Feb 9 → Feb 15, 2026

---

### Connection to Previous Week
Building on the incremental load feature and similarity detection work from previous weeks, I focused on completing the user-editable threshold feature to give user the power to choose the update. Also integrating consent management APIs for the UI, and refactoring the incremental load system to be more interactive. And adding the api endpoints for consent management.This work improved user control over project updates and enhanced the consent management flow. 

---

### Pull Requests Worked On
- **[PR #634 - Allows user to edit the threshold for incremental load](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/634)** ✅ Merged
  - Implemented user-editable threshold for incremental load
  - Integrated update project CLI with user requirements
  - Refactored incremental load from automatic to interactive mode
  - Added comprehensive testing for update project CLI
- **[PR #655 - Get API endpoint for consent Text for UI](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/655)** ✅ Merged
  - Created API endpoint for consent text retrieval
  - Added testing for consent text API endpoint
  - Implemented notification CSS for popup buttons

---

### Associated Issues Completed
| Issue ID | Title | Status | Related PRs |
|----------|-------|--------|-------------|
| [#600](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/600) | Allows user to edit the threshold for incremental load | ✅ Closed | PR #634 |
| [#635](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/635) | Integrate the update folder user requirement in CLI | ✅ Closed | PR #634 |
| [#636](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/636) | Refactor the incremental load to change to automatic to interactive | ✅ Closed | PR #634 |
| [#637](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/637) | Testing for update project CLI | ✅ Closed | PR #634 |
| [#614](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/614) | Testing for author key | ✅ Closed | - |
| [#615](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/615) | Add author key in non code stream - Bugfix part2 | ✅ Closed | PR #615 |
| [#651](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/651) | Get API endpoint for consent Text for UI | ✅ Closed | PR #655 |
| [#652](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/652) | Test the API endpoint for the consent text | ✅ Closed | PR #655 |
| [#654](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/654) | Add notification CSS for popups for buttons | ✅ Closed | PR #655 |

---

## Work Breakdown

### Coding Tasks

* **PR #634 – User-Editable Threshold:** Implemented user-editable threshold feature allowing users to customize incremental load sensitivity, integrated update project CLI with user requirements for better control, refactored incremental load from automatic to interactive mode for improved user experience.
* **PR #655 – Consent API Integration:** Created API endpoint for retrieving consent text for UI display, implemented notification CSS for popup buttons to improve user feedback, added comprehensive testing for consent text API endpoint.

---

### Testing & Debugging Tasks

* Comprehensive testing for update project CLI functionality (#637)
* Validated user-editable threshold feature across different scenarios
* Tested consent text API endpoint for proper data retrieval (#652)
* Verified interactive incremental load behavior
* Validated notification CSS implementation for various button states
* Testing for author key implementation (#614)

---

### Collaboration & Review Tasks

* Conducted code reviews for team members' PRs
* Collaborated on consent management UI/UX improvements
* Participated in discussions about incremental load user experience
* Provided feedback on frontend integration of consent APIs

---

### Issues & Blockers

**Issue Encountered:**

* Complex refactoring required to change incremental load from automatic to interactive
* Ensuring backward compatibility while adding user-editable threshold
* Coordinating consent API structure with frontend requirements

**Resolution:**

* Successfully refactored incremental load system with minimal breaking changes
* Implemented flexible threshold system that maintains default behavior while allowing customization
* Collaborated with frontend team to finalize consent API structure and notification styling

---

### Reflection

**What Went Well:**

* Successfully completed user-editable threshold feature with full CLI integration
* Created clean and well-tested consent API endpoints
* Effective refactoring of incremental load to interactive mode
* Good collaboration with frontend team on consent management

**What Could Be Improved:**

* Faster reviews on my PR, i noticed even when PR is up on a wednesday- the reviews should be happening on the weekend making it hard to implement the changes quickly
* Better initial planning for refactoring scope

---

### Plan for Next Cycle

* Continue supporting consent management UI integration
* Address any bugs or edge cases discovered in incremental load feature
* Address all the bugs for the presentation 
* Continue code reviews and team collaboration

