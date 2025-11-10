# Personal Log – Oluwadabira Omotoso

---

## Entry for Nov 3, 2025 → Nov 9, 2025

### Type of Tasks Worked On
![Personal Log](../../../screenshots/Week%2010%20Personal%20Log-%20Oluwadabira.png)

---

### Recap of Weekly Goals
- Discussed with @kjassani for the git flow and tasks for this are now assigned to him.
- Continued working on parsing logic for code files:
- - Implementation of extracting libraries in code files
- - Updated the mapping logic between the pygments library and tree_sitter
- - Researched logic for extracting file entities and working this into language-agnostic approach
- - Implementation of extracting file dependencies
---

### Features Assigned to Me
- Parsing non-code files:
- - Extract file entities
- - Extract import libraries
- - Extract internal dependencies
- - Refactor relating parsing coding files

---

### Associated Project Board Tasks
| Task/Issue ID | Title       | Status     |
|---------------|-------------|------------|
|#210| Extract File Entities| In Progress |
| #209        | Extract Internal Dependencies| In Progress  |
|#239| Added a dictionary map for Pygments -> Tree_sitter| Completed|
| #192|Extract libraries from import statements| Completed|

---

### Progress Summary
- **Completed this week:**  
    - Extract libraries from import statements
    - Refactoring for `parse_code_utils`:
        - Updated the relationship between `detect_language` and `get_language` in `parse_code_utils` (added a dictionary map mechanism)
        - Updated the `detect_language` to reflect accurate results e.g. return `C++` and update a result from pygments like `Javascript+Genshin` to just `Javascript`
    - Discussed the logic of the flow for git history extraction

- **In Progress this week:**  
    - Extract internal dependencies i.e. being able to differentiate between relative imports and libraries
    - Extract file entities
---

### Additional Context (Optional)

The implementation of the in-progress tasks took longer than I envisioned with some hiccups along the way. The research for file entities is still in progress and has not started implementation because of trying to understand how to implement this in an angostic manner.

---

### Reflection
**What Went Well:**
* We had good communication as a team and we were able to split up our work effectively.
* Code reviews have been productive, with team members providing constructive suggestions for improving each other’s code.
* Each week, this project allows me to think about my work from a design and algorithm design perspective. I am able to consider redundancy more and think about the relevancy of whatever I am implementing.

**What Could Be Improved:**
* Improve clarity around project structures and document meetings more to prevent future miscommunications.
---

### Plan for Next Cycle
* Continue work on parse coding files particularly focusing on extracting file entities.

