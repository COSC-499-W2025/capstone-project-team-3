# Team Log week 13

**Team Name:** Team 3

**Work Performed:** 
- **Enhanced GitHub Analysis**: Implemented comprehensive commit analysis with pattern detection, technical keyword extraction, and resume generation capabilities
- **Updated Analysis Architecture**: Modified code analysis system to support new JSON structure from parsing team while maintaining backward compatibility
- **Non-Code Analysis**: Completed Non code analysis for both ai and non ai flows. 
- **Parsing Enhancements**: Added entity extraction, dependency mapping, and improved language detection
- **CI/CD Improvements**: Implemented security scanning, automated testing pipelines, and workflow optimization
- **Git Integration**: Enhanced git history extraction and collaboration detection features, added funcitonality to check code file, added programming language detection for git
---

## Recap of Milestone Goals

- **Features planned for this milestone:**
    * Deciding on task priorities for the next 2 weeks+
    * Consent management and User Setup in WBS (Finishing most features)
    * Project Input and Initialization in WBS (Finishing most features)
    * Code and non code analysis in WBS (starting most features)
    * Extrapolate individual contributions for a given collaboration project
    * Distinguish individual projects from collaborative projects
    * Project Ranking based on user contributions
  
- **Associated project board tasks:**
    * 227: Implement scanning flow to the project's main
    * 226: Fix analysis bugs and refactor code - Code Analysis Section
    * 228: Research and fine tune non LLM analysis - Code Analysis
    * Extract Internal Dependencies	#209
    * Added a dictionary map for Pygments -> Tree_sitter #239
    * Extract File Entities	#210
    * Extract libraries from import statements	#192
    * Added missing tests for consent management and prompt input #196
    * Added checking for non-code file via extensions (Pt-1) #212
    * Added functionality for local directory scanning (Pt-2) #221 
    * Updated directory structure for non-code analysis utils  #230 
    * Implementing non-code analysis without AI/3rd-party services #215
    * Researching methods for implementing non-code analysis without AI services #245
    * Add Security Scan Workflow in the pipeline #294
    * Linking Non-Code File Verification Results to Code Parsing Logic #273
    * Add CI Pipeline for Automated Testing #293
    * Create the Plan for the workflow #292
    * Testing for Non Code Parsing Flow into Non-code Analysis #274
    * Integrate non code parsing flow into non code analysis #254
    * Integrate the overall project flow #164
    * Added functionality to calculate PR metrics #301
    * Add git metadata collection & collaboration filtering #251
    * User identity & contribution verification (Pt-4) #255
    * Final classification orchestrator (Pt-5) #267
    * Document identification via analysis #279
    * Summary generation (offline NLP) #280
    * Extract technical keywords using KeyBERT #281
    * Generate bullet points (offline) #315
    * Research offline non-code analysis methods #245
    * Implement functionality for extracting skill information without using 3rd party services. #322
    * Allow the read me files to pass through non code file checker to help with analysis and updated tests #328
    * Added functionality for non code file non Ai analysis to output the result for all files in a project and updated NLP README. #332
    * Add completeness score and word count in output for Non Ai Non code analysis. #348
    * Added functionality to only accept zipped file paths.  #371
    * Integrate non code file checker into main flow. #372
    * Integrate contribution type frequency in the analysis pipeline. #379
    * is code file for git #320
    * language detection for git #339
    * update extract code commit content by author #356

    
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
| #239, #192   |  Added a dictionary map for Pygments -> Tree_sitter, Extract libraries from import statements | @dabby04     |
| #294, #273, #293, #292, #274, #254 | Add Security Scan Workflow in the pipeline, Linking Non-Code File Verification Results to Code Parsing Logic, Add CI Pipeline for Automated Testing, Create the Plan for the workflow, Testing for Non Code Parsing Flow into Non-code Analysis, Integrate non code parsing flow into non code analysis | @PaintedW0lf |
| #160, #94,  #48, #113, #92, #181, #224, #320, #339, #356, | Git History Extraction (FR5), filter authors commits, handle empty git repo, check for collaboration in git repo, Map Changes to Files, Extract author's code commits (git), Added functionality to extract readme from git repo, Calculate PR metrics, Function to check is_code_file inside git repo, Language Detection for git files, Update extract code commit content by author  | @kjassani    |

---

## In Progress Tasks
| Task/Issue ID | Title            | Username |
|---------------|------------------|----------|
| #305          |  Store project analysis results into db - Code | @KarimKhalil33      |
| #210 , #209          |  Extracting file entities and extracting file dependencies | @dabby04     |
| #378        |  Waiting for one remaining code review for integrating contribution frequency in analysis pipeline. | @6s1      |
| #382, #381, #341, #336, #337 | Merge Non-Code & Code Analysis Results, Send Combined Analysis to project Ranker, Store results in DB, Integrate activity type contribution to AI non-code analysis, Project Retrieval | @abstractafua |
| #164          | Integrate the overall project flow | @PaintedW0lf |
| #386 | Project Score for Project Ranking | @kjassani|

 

---

## Meeting Notes

### 26th, 29th, 30th November 2025 – Team Meeting (All members present)
- Work and Flow clarifyign session.

---

## Test Report

- **Framework used:** `pytest` and `pytest-cov`  
- **Test run date:** 9th November 2025 
- **Summary:**  
  - Total tests run:  
  - Passed:   
  - Failed:   
- **Regression Testing:**  
  - N/A  
- **Screenshot or Output:**  
  


---

## Reflection

* This week we discovered P10 and we delegated tasks and what we will be working on for this week and possibly next week...

## Plan for Next Cycle
* Continue with code contributions, prioritising and finalising FR1, FR3, FR2, FR4, and FR5.