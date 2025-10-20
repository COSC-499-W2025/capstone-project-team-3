# Personal Log – Karim Khalil
---

## Entry for Oct 13, 2025 → Oct 19, 2025

### Type of Tasks Worked On
![Personal Log](../../../screenshots/Week%207%20Personal%20Log-%20KarimKhalil.png)

---

### Recap of Weekly Goals
- Start working on FR4: File Scanning & Indexing

---

### Features Assigned to Me
- Scan Files paying attention to exclusions and filters
- Extract & Store Metadata
- Handle Unsupported Types
- Write Metadata to local database
- Error Handling (I/O, Empty Folders, Retry)
- Test Cases

---

### Associated Project Board Tasks
| Task/Issue ID | Title       | Status     |
|---------------|-------------|------------|
| #70        | Scan Files paying attention to exclusions and filters | Completed  |
| #75       | Handle Unsupported Types | Completed  |
| #73        | Extract & Store Metadata | In Progress   |
| #76        | Write Metadata to local database | In Progress  |
| #77        | Error Handling (I/O, Empty Folders, Retry) | In Progress  |
| #78        | Test Cases | In Progress  |

---

### Progress Summary
- **Completed this week:**  
  - Created functionality to go through all files wihtin project and filter all files and documents that cannot be handled and/or user specificied documents to not include within analysis
  - Created functionality that created a hashed signature for each project using a combination of their metadata
  - Created unit tests and manual testing to ensure clean and quality code

- **In Progress this week:**  
  - Started on creating functionality to check if signature is stored in the database to flag wether system shoudl skip analysis or not.

---

### Additional Context (Optional)

The reason this issue is still in progress is because the database currently doesnt have the schema that can store the signature created for each project. Once thats implemented i will be adding the storing and checking logic. 
---

### Reflection
**What Went Well:**
* PR reviews went a lot smoother and quicker than the pervious sprint. 
* efficient communication throughout the team (only needed one meeting to discuss tasks and work priority)
* PR reviews were clean and relevant

**What Could Be Improved:**
* Although pr reviews were done more frequently, there is always space for improvement so there are less blockage and faster flow of work.
---

### Plan for Next Cycle
* Continue working on FR4 which includes:
- Extract & Store Metadata
- Write Metadata to local database
- Error Handling (I/O, Empty Folders, Retry)
- Test Cases