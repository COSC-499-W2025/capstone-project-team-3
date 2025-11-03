# Team Log week 9

**Team Name:** Team 3

**Work Performed:** Oct 27, 2025 → Nov 2, 2025

---

## Recap of Milestone Goals

- **Features planned for this milestone:**
    * Deciding on task priorities for the next 2 weeks+
    * Consent management and User Setup in WBS (starting most features)
    * Project Input and Initialization in WBS (starting most features)
    * Code and non code analysis in WBS (starting most features)
    
  
- **Associated project board tasks:**
    * Test Cases #99
    * Privacy-based Restrictions #98
    * Dropdown UI for Industry & Education #96
    * Validate Directory Read Access #79
    * Enforce Access Restriction Until Consent is given #82
    * Handle Invalid or Inaccessible Paths #81
    * Store Consent Status Locally #80
    * Implement Consent Screen UI #74
    * Zipped file path will be typed in #72
    * Extract & Store Metadata #73
    * Native Folder Picker Integration #71
    * Folder Path Selector #46
    * Consent & User Management #30
    * Consent Model + Storage Layer #29
    * Test Cases #78
    * Error Handling (I/O, Empty Folders, Retry) #77
    * Write Metadata to local database #76
    * Handle Unsupported Types #75
    * Extract Commit Metadata #91
    * Git History Extraction #89
    * Test Cases (Positive/Negative) #87
    * Consent Management #88
    * FR4: File Scanning & Indexing #69
    * Scan Files paying attention to exclusions and filters #70
    * check zip file #48
    * Project Extraction Logic #152
    * Project Identification from ZIPs #153
    * Read the Number of Projects Uploaded by the User #139
    * Methods that return list should be plural named #132
    * Fixed no tests ran result in Docker Env #133
    * Fix Docker environment interactivity issue #145
    * Identify collaborative projects #160
    * Handle Empty git repo #94
    * Test Cases #86
    * Implement User Flow for inputting file path #185
    * Researching LLM/non-LLM implementation for non code file analysis #186


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
| #70, #75 | Scan Files paying attention to exclusions and filters, Handle Unsupported Types | @KarimKhalil33 |
| #79, #81, #83, #86, #139, #153, #86, #183, #186 | Folder Path Selector (FR2)-achieved 100% test coverage, Implemented User file path input in cli, researching llm/non-llm options for non-code files. | @6s-1 |
| #135, #136          | Expand Db Schema and Add steps to Read.ME, Seed Data with test data    | @abstractafua |
| #91, #113, #133, #132       | Extract Commit Metadata, Fixed no tests ran result in Docker Env, Methods that return list should be plural     | @dabby04     |
| #164, #165, #170, #186  | Decide project & CLI flow; design reusable utils; integrate overall flow, Implement Consent Manager flow and testing , Parse function for non-code files and testing the functioning, Researching LLM/non-LLM implementation for non code file analysis | @PaintedW0lf     |
| #160, #94,  #48, #113    | Git History Extraction (FR5), filter authors commits, handle empty git repo, check for collaboration in git repo    | @kjassani    |

---

## In Progress Tasks

| Task/Issue ID | Title            | Username |
|---------------|------------------|----------|
| #145          |  Fix Docker environment interactivity issue  | @dabby04      |
| #186          |  Researching LLM/Non-LLM non-code file analysis methods | @6s1      |
| #73, #76, #77, #78 | Extract & Store Metadata, Write Metadata to local database, Error Handling, Test Cases | @KarimKhalil33 |
| #115         | Absolute path for target Dockerr  | @kjassani     |
| #85         | FR3: User Preference Selection #85  | @abstractafua     |

---

## Meeting Notes

### 24th October 2025 – Team Meeting (All members present)
- Assignment of tasks 
- Discuss what everyone is working on
- Clarified what should be stored in the schema for project info and consent

---

## Test Report

- **Framework used:** `pytest` and `pytest-cov`  
- **Test run date:** 26 October 2025 
- **Summary:**  
  - Total tests run:  70
  - Passed:   69
  - Failed:   1
- **Regression Testing:**  
  - N/A  
- **Screenshot or Output:**  
  
<img width="649" height="405" alt="t2" src="https://github.com/user-attachments/assets/99c8ef04-a8b7-4c41-ad7e-10c098776c27" />

<img width="948" height="294" alt="t1" src="https://github.com/user-attachments/assets/69f57ab6-c553-4813-84d8-fd01ce0039d6" />


---

## Reflection

* This week went well- we delegated tasks and what we will be working on for this week and possibly next week...

## Plan for Next Cycle
* Continue with code contributions, prioritising and finalising FR1, FR3, FR2, FR4, and FR5.
