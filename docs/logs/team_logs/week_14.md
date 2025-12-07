# Team Log week 14

**Team Name:** Team 3

**Work Performed:**  Dec 1, 2025 → Dec 7, 2025


---

## Recap of Milestone Goals

- **Features planned for this milestone:**
    * Complete integration into main (seeing the whole flow of project)
  
- **Associated project board tasks:**
    * Fix retrieval of resume bullets #415
    * Includes resolving time stamp error during extraction, some errors in main integration #409
    * Updated git info to contain username #413
    * Fixed integration tests #406
    * Implement the flow for parsing local code files + refactoring main #398
    
---

## Burnup Chart

_Accumulative view of tasks done, tasks in progress, and tasks left to do._  
Paste chart image or link here:

Progress Burnup: https://github.com/orgs/COSC-499-W2025/projects/45/insights

Status Burnup: https://github.com/orgs/COSC-499-W2025/projects/45/insights/2

---

## Team Members

| Username (GitHub) | Student Name   |
|-------------------|----------------|
| @KarimKhalil33    | Karim Khalil   |
| @kjassani         | Karim Jassani  |
| @dabby04          | Oluwadabira Omotoso|
| @PaintedW0lf      | Vanshika Singla|
| @6s-1             | Shreya Saxena  |
| @abstractafua     | Afua Frempong  |

---

## Completed Tasks

| Task/Issue ID | Title                  | Username        |
|---------------|------------------------|-----------------|
| #335, #331, #327, #369 | Comprehensive Project Analysis Workflow, Project Timestamp Storage, Analysis Output Format Standardization, Test Hot Fixes | @KarimKhalil33 |
| #372, #371, #348, #332, #328, #322  | Implemented fucntionality to only accpet zipped files, added skill extraction in analysis pipeline, added completeness score and word count, added non code file checker into main flow(integration) allowed readme files to pass through from non code file checker. | @6s-1 |
| #341, #358, #359 |  Add completeness score & Word_count metrics into results for AI analysis pipeline, Determine what analysis pipeline was used (LLM or non-LLM), Ensure Analysis output & structure in sync with Non-AI Analysis Output | @abstractafua |
| #351, #366, #352, #368, #344, #342, #365, #367 | Add Contribution Frequency Tracking for Non-Code Files, Implement Efficient Git Commit Counting, Comprehensive testing for Git parsing, Integrate parsing in main, Special parsing for git non-code files to extract individual contribution, Separate README.md from other md files, README as non-collaborative for non-code (bug fix), Update Non-Code Parser Tests for New Signature | @PaintedW0lf |
| #415, #409, #413, #406, #398  |  Fix retrieval of resume bullets, Includes resolving time stamp error during extraction, some errors in main integration, Updated git info to contain username, Fixed integration tests, Implement the flow for parsing local code files + refactoring main | @dabby04     |
| #160, #94,  #48, #113, #92, #181, #224, #320, #339, #356, | Git History Extraction (FR5), filter authors commits, handle empty git repo, check for collaboration in git repo, Map Changes to Files, Extract author's code commits (git), Added functionality to extract readme from git repo, Calculate PR metrics, Function to check is_code_file inside git repo, Language Detection for git files, Update extract code commit content by author  | @kjassani    |

---

## In Progress Tasks

## In Progress Tasks
| Task/Issue ID | Title            | Username |
|---------------|------------------|----------|
| #305          |  Store project analysis results into db - Code | @KarimKhalil33      |
| #378        |  Waiting for one remaining code review for integrating contribution frequency in analysis pipeline. | @6s1      |
| #382, #381, #341, #336, #337 | Merge Non-Code & Code Analysis Results, Send Combined Analysis to project Ranker, Store results in DB, Integrate activity type contribution to AI non-code analysis, Project Retrieval | @abstractafua |
| #386 | Project Score for Project Ranking | @kjassani|


---

## Meeting Notes

### Dec 1st 2025 – Team Meeting (All members present)
- Discuss remaining requirements

---

## Test Report

- **Framework used:** `pytest` and `pytest-cov`  
- **Test run date:** 7th December 2025 
- **Summary:**  
  - Total tests run:  403
  - Passed:   380
  - Failed:  23 
- **Regression Testing:**  
  - N/A  
- **Screenshot or Output:**  
  


---

## Reflection

* We worked as a team to wrap up requirements for Milestone 1

## Plan for Next Cycle
* Continue with code contributions, prioritising and finalising FR1, FR3, FR2, FR4, and FR5.