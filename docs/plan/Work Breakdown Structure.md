# Work Breakdown Structure
**Note:** 
* **\* items will be worked on in further milestones and are not worked on in current milestone.**  
* **Task Assignment and further details shown in the [Requirements Verification table in Project Proposal](Project%20Proposal.md#4-requirements-testing-requirement-verification).**

## 1. **Consent and User Setup**

   1. ### **FR1: Consent Management (UC1)**

      1. Determine content on Consent Form

      2. Implement Consent Screen UI \*

      3. Store Consent Status Locally

      4. Enforce Access Restriction Until Consent is given

      5. Handle Consent Decline & OS Permission Denial

      6. Test Cases (Positive/Negative)

   2. ### **FR3: User Preference Selection (UC3)\***

      1. Dropdown UI for Industry & Education

      2. Free-text Input for Custom Entries

      3. Validation & Local Storage

      4. Privacy-based Restrictions (Session-only Preferences)

      5. Test Cases

## 2. **Project Input & Initialization**

   1. ### **FR2: Folder Path Selector (UC2)**

      1. Native Folder Picker Integration

         a. Milestone 1: Zipped file path will be typed in

         b. Further milestones will use UI for upload feature\*

      2. Validate Directory Read Access

      3. Handle Invalid or Inaccessible Paths

      4. Handle Large Directory/Incorrect Format Warnings

      5. Test Cases

   2. ### **FR4: File Scanning & Indexing (UC4)**

      1. Scan Files paying attention to exclusions and filters

      2. Extract & Store Metadata

      3. Handle Unsupported Types

      4. Write Metadata to local database

      5. Error Handling (I/O, Empty Folders, Retry)

      6. Test Cases

   3. ### **FR5: Git History Extraction (UC5)**

      1. Detect .git Folder

      2. Extract Commit Metadata

      3. Map Changes to Files

      4. Store Git Data in local database

      5. Handle Missing or Empty Git Repos

      6. Test Cases

## 3. **Skill & Contribution Analysis**

   1. ### **FR6.1: Non-Code Content Analysis (UC6.1)**

      1. Parse Non-Code Text based Files (PDF, DOC, TXT, etc.)

      2. Aggregate Project-Level Results

      3. Handle Sparse/Ambiguous Content

      4. Test Cases

   2. ### **FR6.2: Code Content Analysis (UC6.2)**

      1. Parse Code Projects (Multiple Languages)

      2. NLP for Skill/Framework Extraction

      3. Aggregate Analysis Per File/Project

      4. Handle Broken or Empty Code Files

      5. Test Cases

   3. ### **FR6: Overall Content Analysis & Skill Inference (UC6s)**

      1. Merge Code \+ Non-Code Results

      2. Exclude Binary Files

      3. Store Inferred Skills & Contributions

      4. Error/Edge Case Handling

      5. Test Cases

## 4. **Post-Processing: Ranking, Chronological Ordering, and Visualization Metrics**

   1. ### **FR7: Project Ranking (UC7)**

      1. Aggregate Score Calculation

      2. Normalize Across Metadata \+ Git \+ Analysis

      3. Store Ranked List in Local Database

      4. Handle Missing Data

      5. Test Cases

   2. ### **FR8: Chronological Ordering (UC8)**

      1. Sort by Creation and Modification Dates

      2. Associate Skills to Project Timeframe

      3. Store Ordered Lists

      4. Test Cases

   3. ### **FR9: Prepare Visualization Graphics (UC9)\***

      1. Compute Visual Datasets from Database

      2. Generate KPIs & Charts

      3. Filter Support for Visuals

      4. Test Cases

## 5. **User-Facing Summaries & Dashboards**

   1. ### **FR11: Dashboard Generation & Edit (UC10)\***

      1. Load Dashboard with Visualized Data

      2. Support Layout Editing (Widgets, Filters)

      3. Save Personalized View

      4. Retry on Load/Save Failure

      5. Test Cases

   2. ### **FR10: Resume Generation (UC11)\***

      1. STAR-Based Resume Templates

      2. Link Summaries to Evidence (files, commits)

      3. Handle Insufficient Evidence with Placeholders

      4. Store Summary Output

      5. Test Cases

   3. ### **FR12: Export Dashboards (UC12)\***

      1. Generate PDF/JSON/JPG types

      2. Handle Write Permissions & Retry

      3. Test Cases

## 6. **Data Management & Maintenance**

   1. ### **FR13: Data Management (UC13)**

      1. UI for Viewing Stored Items, Consent, and Projects Generated\*

      2. Clear All/Selected Data

      3. Revoke Consent

      4. Handle OS Lock Failures with Manual Resolution

         a. Show steps for deletion manually

      5. Test Cases

   2. ### **FR14: Database & Invalidation (UC14)\***

      1. Detect Changed, Deleted, Renamed Items

      2. Update, Invalidate, and Remove Data Intelligently

      3. Preserve Dashboard State

      4. Test Cases

   3. ### **FR15: Deletion of Previous Insights (UC15)**

      1. Deep Delete Selected Project History\*

      2. Post-Deletion Confirmation

      3. Test Cases

## 7. **Non-Functional Requirements (NFRs)**

   1. ### **NFR1: Cross-Platform & Offline Compatibility**

      1. Build Platform-Agnostic Installer

      2. Ensure Offline Mode for Core Features

      3. Run Functional Tests Across OSes

   2. ### **NFR2: Data Consistency**

      1. Ensure Updates Reflect Only Real Changes

      2. Prevent New Errors from Stable Inputs

   3. ### **NFR3: Usability/Intuitiveness**

      1. Usability Test for First-Time Users

      2. Measure Time to Complete Key Tasks

      3. Incorporate Feedback for Improvements