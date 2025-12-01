# Team Log week 12

**Team Name:** Team 3

**Work Performed:** 
- **Enhanced GitHub Analysis**: Implemented comprehensive commit analysis with pattern detection, technical keyword extraction, and resume generation capabilities
- **Updated Analysis Architecture**: Modified code analysis system to support new JSON structure from parsing team while maintaining backward compatibility
- **Non-Code Analysis**: Continued implementation of non-LLM and LLM analysis methods for non-code files
- **Parsing Enhancements**: Added entity extraction, dependency mapping, and improved language detection
- **CI/CD Improvements**: Implemented security scanning, automated testing pipelines, and workflow optimization
- **Git Integration**: Enhanced git history extraction and collaboration detection features
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
    * Non code pre-processing and summarization #233
    * Aggregate LLM1 Summaries into Unified Project Structure #234
    * Generate LLM2 Prompt for Non-Code Analysis #235
    * Researching Ai/non-Ai implementation for non code file analysis #186
    * Create extract project names	#265
    * Grammar loader	#282
    * Template for `file_entity_utils`	#283
    * Extract Classes	#284
    * Extract Functions	#297
    * Extract components	#298
    * Extract Metrics	#312
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
| #276, #303 | Added GitHub Analysis, Modified Analysis with New Parsed Metrics/Format   | @KarimKhalil33 |
| #251, #255, #267, #278, #300, #288, #287, #281, #280, #279  | Implemented multi-stage non-code analysis features including git metadata collection (Pt-3), user contribution verification (Pt-4), and the final classification orchestrator (Pt-5). Added offline NLP capabilities for document identification, summary generation, keyword and topic extraction, Sumy LSA important-sentence extraction, and added bullet-point generation. | @6s-1 |
| #218, #215 | Add completeness score & Word_count metrics into results for AI analysis pipeline, Ensure Analysis output & structure in sync with Non-AI Analysis Output   | @abstractafua |
| #239, #192   |  Added a dictionary map for Pygments -> Tree_sitter, Extract libraries from import statements | @dabby04     |
| #196,#212, #221, #230, #215, #245  | Added checking for non-code file via extensions,Added functionality for local directory scanning, Added missing tests for consent management and prompt input, researching non-llm/3rd party options for non-code files. | @6s-1 |
| #341, #358, #359 |  Add completeness score & Word_count metrics into results for AI analysis pipeline, Determine what analysis pipeline was used (LLM or non-LLM), Ensure Analysis output & structure in sync with Non-AI Analysis Output | @abstractafua |
|#210, #284, #283, #297,#298,| Extract File Entities, Extract Classes, Template for file_entity_utils, Extract functions, Extract components | @dabby04 |
| #294, #273, #293, #292, #274, #254 | Add Security Scan Workflow in the pipeline, Linking Non-Code File Verification Results to Code Parsing Logic, Add CI Pipeline for Automated Testing, Create the Plan for the workflow, Testing for Non Code Parsing Flow into Non-code Analysis, Integrate non code parsing flow into non code analysis | @PaintedW0lf |
| #160, #94,  #48, #113, #92, #181, #224, #301 | Git History Extraction (FR5), filter authors commits, handle empty git repo, check for collaboration in git repo, Map Changes to Files, Extract author's code commits (git), Added functionality to extract readme from git repo, Calculate PR metrics   | @kjassani    |

---

## In Progress Tasks
| Task/Issue ID | Title            | Username |
|---------------|------------------|----------|
| #305          |  Store project analysis results into db - Code | @KarimKhalil33      |
| #210 , #209          |  Extracting file entities and extracting file dependencies | @dabby04     |
| #317        |  Working on one of the last parts of non code analysis- skill extraction | @6s1      |
| #382, #381, #341, #336, #337 | Merge Non-Code & Code Analysis Results, Send Combined Analysis to project Ranker, Store results in DB, Integrate activity type contribution to AI non-code analysis, Project Retrieval | @abstractafua     |
| #312, #174       |  Extract metrics, and Parse code files (non-git)- Implementation of flow | @dabby04     |
| #215, #245          |  Researching Non-LLM/3rd party non-code file analysis methods | @6s1      |
| #236, #237         | Store Final Non-Code Analysis Results in Local Database, Call llm_client.py and Generate Insights for Non-Code Analysis| @abstractafua     |
| #164          | Integrate the overall project flow | @PaintedW0lf |

 

---

## Meeting Notes

### 18th, 21st November 2025 – Team Meeting (All members present)
- Flow clarifyign session and review.

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

* This week went well-we delegated tasks and what we will be working on for this week and possibly next week.
* This week we are ensuring that we are all aligned in order to deliver the remaining requirements for Milestone 1

## Plan for Next Cycle
* Continue with code contributions, prioritising and finalising FR1, FR3, FR2, FR4, and FR5.