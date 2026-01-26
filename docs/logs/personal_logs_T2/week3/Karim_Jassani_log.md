# Personal Log – Karim Jassani

---

## Week-2, Entry for Jan 11 → Jan 18, 2026

![Personal Log](../../../screenshots/T2-Week3-Karim-Jassani.png)


---

### Pull Requests Worked On
- **[PR #535 - Multi-repo Git parsing + nested repo aggregationg](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/535)** 


- **[PR #539 - Improve Git author matching](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/539)** 
---

### Associated Issues Completed
| Issue ID | Title 
|----------|-------
| [#516](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/516) | Test & Review Commit Contribution |
| [#515](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/515) | Troubleshoot git detect |

---

## Work Breakdown

### Coding Tasks


#### **[PR #539 - Improve Git author matching](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/539)** 
  - Unified GitHub noreply emails and real emails under a single author identity
  - Added normalization helpers to support multiple identifiers per author
  - Implemented parsing for GitHub noreply emails by extracting username component
  - Updated git parsing flow to pass multiple identifiers instead of a single email
  - Fixed project ranking logic to correctly sort floating-point scores
  - Updated tests to reflect identifier list usage
  - Closes: #516




#### **[PR #535 - Multi-repo Git parsing + nested repo aggregationg](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/535)** 
- Added support for parsing multiple repositories in a single analysis run
- Grouped input files by repository root instead of assuming a single repo
- Ensured nested repositories are detected and analyzed correctly
- Expanded test coverage for nested paths, invalid inputs, and non-repo files

---
### Other Tasks
- Script for peer testing
- Task List for peer testing
- Google forms survery for peer testing
---

###  Testing & Debugging Tasks

- Added tests for nested repo aggregation, repo root resolution, and invalid JSON handling  
- Validated author-matching behavior across real and noreply identifiers  
- Confirmed rank sorting behavior on float values  


---

### Collaboration & Review Tasks

- **[PR #537 - Completed fix for encoding issue on certain content extraction](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/537)**
- **[PR #532 - Fixed test data stored in db](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/532)**
- **[PR #527 - Updated and fixed non code analysis summary along with milestone-1 feedback](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/527)**
- **[PR #540 - Vanshika logs w3](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/540)**


---

### Reflection

**What Went Well:**
- Unified author identities to avoid split contributions  
- Improved accuracy and reliability of git-based analysis  
- Expanded test coverage for nested repo and parsing edge cases  

**What Could Be Improved:**
- Earlier detection of multi-identifier impacts on downstream metrics  
- More proactive coordination on review timelines  
- 
---

### Plan for Next Week
- There were very higher priority features, hence, I had to postpone working on allowing user to re-rank projects so I can pick it up next week.
