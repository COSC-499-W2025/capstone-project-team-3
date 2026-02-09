# Personal Log – Shreya Saxena

---

## Week-3, Entry for Jan 26 → Feb 8, 2026

![Personal Log](../../../screenshots/Shreya_Saxena_week-3T2.png)

---

### Pull Requests Worked On
- **[PR #546 - Feature 23: Edit/Update Project Duration Dates & Base Utils for Chronological Results](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/546)** ✅ Merged
  - Added CLI tool to view and edit project dates from analyzed projects
  - Created new DB utility manager for SQLite connection and operations
  - Implemented interactive CLI for listing projects and validating dates
  - Added comprehensive test coverage with temp SQLite DB testing
  - 558 lines of new code with complete scaffolding for reliability

- **[PR #550 - Feature 26: POST API Endpoint for Adding Thumbnail for Project](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/550)** ✅ Merged
  - Created POST API endpoint to handle file path input to database
  - Added thumbnail support for projects

- **[PR #577 - Feature 28: Endpoint for Deleting Edited Resumes](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/577)** ✅ Merged
  - Added endpoint for edited resume deletion
  - Implemented proper cleanup and validation

- **[PR #589 - Feature 23: Chronological Information Managing for Skills Date](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/589)** ✅ Merged
  - Updated database to contain chronological skills
  - Updated Chronological manager to produce editable output
  - Updated Chronological utils to accept editing of dates for skills

---

### Associated Issues Completed
| Issue ID | Title | Status |
|----------|-------|--------|
| [#548](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/548) | Create base chronological information managing utils file | ✅ Closed |
| [#549](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/549) | Create chronological information managing for editing/updating project date | ✅ Closed |
| [#551](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/551) | Create POST API endpoint to get the file path input to db | ✅ Closed |
| [#578](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/578) | Add endpoint for edited resume deletion | ✅ Closed |
| [#590](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/590) | Update database to contain chronological skills | ✅ Closed |
| [#591](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/591) | Update Chronological manager to produce editable output for user | ✅ Closed |
| [#592](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/592) | Update Chronological utils to accept editing of dates for skills | ✅ Closed |

---

## Work Breakdown

### Coding Tasks

#### Chronological Project Dates CLI Tool (Feature 23 - Part 1)
- Created interactive CLI tool to view and edit project dates from analyzed projects
- Implemented new DB utility manager for SQLite connection and operations
- Added project listing with date prompting and validation
- Built confirmation workflow for updates with error handling
- Created comprehensive test suite with temp SQLite DB for reliability
- Total 558 lines including complete scaffolding and test coverage

#### Thumbnail API Endpoint (Feature 26)
- Implemented POST API endpoint for adding project thumbnails
- Added file path input handling to database
- Integrated thumbnail support with existing project structure

#### Resume Deletion Endpoint (Feature 28)
- Created endpoint for deleting edited resumes
- Implemented proper cleanup and validation logic
- Added error handling for deletion operations

#### Chronological Skills Management (Feature 23 - Part 2)
- Updated database schema to contain chronological skills data
- Enhanced Chronological manager to produce editable output for users
- Extended Chronological utils to accept editing of dates for skills
- Integrated skills date management with existing chronological tools

---

###  Testing & Debugging Tasks

- Created comprehensive test suites for all new features
- Developed comprehensive test suite for chronological project dates CLI tool using temp SQLite DB
- Tested project date updates, ordering, input normalization, and connection closing
- Verified thumbnail POST endpoint with various file path inputs
- Tested resume deletion endpoint for proper cleanup and error handling
- Created test coverage for chronological skills date management functionality
- Test coverage includes: response structure validation, edge cases, and error handling
- All tests passing for chronological tools and new endpoints
- Tested all PRs reviewed for teammates by locally running their code on my system

---

### Collaboration & Review Tasks

- Presented my individual figma design in team meeting
- Documented API endpoints with clear parameter descriptions
- Responded to code review feedback 
- Reviewed and commented on teammates' PRs
- Created detailed PR descriptions with testing instructions

---

### Reflection

**What Went Well:**
- Successfully delivered 4 merged PRs with comprehensive functionality
- Implemented complete Feature 23 (chronological editing) across projects and skills
- Built robust CLI tool with 558 lines including full test coverage
- Added thumbnail and resume deletion endpoints with proper validation
- Maintained backward compatibility in all changes
- All test suites passing with comprehensive coverage

**What Could Be Improved:**
- Could have broken down Feature 23 into smaller incremental PRs for easier review
- Better time estimation for complex features like the CLI tool

---

### Plan for Next Week
- Integrate chronological CLI tools with main application workflow
- Continue work on Milestone-2 requirements
- Monitor new endpoints (thumbnail, resume deletion) in production
- Address any feedback from merged PRs
- Support team with peer testing and code reviews
---
