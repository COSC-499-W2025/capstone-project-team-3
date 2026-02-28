# Personal Log – Shreya Saxena

---

## Week-4+5, Entry for Feb 9 26 → Feb 1, 2026

![Personal Log](../../../screenshots/Shreya_Saxena_week-4+5T2.png)

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

## Week-6, Entry for Feb 9 → Feb 15, 2026

---

### Pull Requests Worked On

- **[PR #623 - Implemented the welcome page, upload page UI with global CSS and screen responsive styling](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/623)** ✅ Merged
  - Implemented welcome page UI with modern, responsive design
  - Created base layout for upload page
  - Added global CSS for consistent UI development across the application
  - Made welcome page responsive across all screen sizes
  - Made upload page responsive across all screen sizes

- **[PR #643 - Added chronological skill/project managing to CLI, updated skill date extraction logic](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/643)** ✅ Merged
  - Implemented chronological management in CLI flow for updating skill dates
  - Implemented chronological management in CLI flow for updating project dates
  - Updated date extraction logic for chronological skills

- **[PR #653 - Thumbnail integration with Portfolio UI](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/653)** ✅ Merged
  - Implemented thumbnail upload flow in UI
  - Created GET API to serve uploaded thumbnails back to the user
  - Implemented thumbnail cache-busting for instant image upload
  - Added extension validation to ensure uploads only contain JPG, PNG, GIF, WebP, BMP

---

### Associated Issues Completed

| Issue ID | Title | Status |
|----------|-------|--------|
| [#625](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/625) | UI for welcome page | ✅ Closed |
| [#627](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/627) | Create base layout for Upload page | ✅ Closed |
| [#629](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/629) | Add global CSS for UI development | ✅ Closed |
| [#630](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/630) | Add code to make Welcome page responsive across screen sizes | ✅ Closed |
| [#631](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/631) | Update code to make Upload page responsive across screen sizes | ✅ Closed |
| [#646](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/646) | Implement Chronological Management in CLI flow for updating skill dates | ✅ Closed |
| [#647](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/647) | Implement Chronological Management in CLI flow for updating project dates | ✅ Closed |
| [#648](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/648) | Implement date extraction logic for chronological skills | ✅ Closed |
| [#581](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/581) | Implement getting the thumbnail from the user into UI flow | ✅ Closed |
| [#656](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/656) | Create GET API to serve the thumbnails uploaded back to the user | ✅ Closed |
| [#657](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/657) | Implement thumbnail cache-busting for instant image upload | ✅ Closed |
| [#658](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/658) | Implement extension validation to ensure uploads only contain JPG, PNG, GIF, WebP, BMP | ✅ Closed |

---

## Work Breakdown

### Coding Tasks

#### Welcome & Upload Page UI (PR #623)
- Designed and implemented modern, user-friendly welcome page
- Created responsive base layout for upload page with intuitive file upload interface
- Developed global CSS stylesheet for consistent UI/UX across the application
- Implemented responsive design breakpoints for all screen sizes (mobile, tablet, desktop)
- Ensured cross-browser compatibility and accessibility standards

#### Chronological CLI Integration (PR #643)
- Integrated chronological management into main CLI workflow
- Added interactive prompts for updating skill dates with validation
- Added interactive prompts for updating project dates with validation
- Enhanced date extraction logic to handle various date formats for chronological skills
- Improved user experience with clear feedback and error messages

#### Thumbnail Portfolio Integration (PR #653)
- Built complete thumbnail upload flow in portfolio UI
- Created GET API endpoint to retrieve and serve uploaded thumbnails
- Implemented aggressive cache-busting strategy for instant thumbnail updates
- Added comprehensive file extension validation (JPG, PNG, GIF, WebP, BMP)
- Handled edge cases like missing thumbnails and upload failures

---

### Testing & Debugging Tasks

- Tested welcome and upload page UI across multiple browsers (Chrome, Firefox, Safari)
- Verified responsive design on various screen sizes and devices
- Tested chronological CLI flow with edge cases (invalid dates, empty inputs)
- Validated thumbnail upload with various file types and sizes
- Tested cache-busting to ensure thumbnails update immediately
- Debugged thumbnail persistence issues in frontend
- All test suites passing for new features

---

### Collaboration & Review Tasks

- Participated in team meetings and sprint planning
- Created detailed PR descriptions with testing instructions
- Responded to code review feedback promptly
- Reviewed and tested teammates' PRs locally
- Documented new UI components and API endpoints

---

### Reflection

**What Went Well:**
- Successfully delivered 3 merged PRs with significant frontend and backend improvements
- Implemented complete responsive UI for welcome and upload pages
- Seamlessly integrated chronological management into CLI workflow
- Solved complex thumbnail caching issues for instant user feedback
- Maintained high code quality with comprehensive testing

**What Could Be Improved:**
- Could have broken down the thumbnail integration PR into smaller increments
- Better coordination with frontend team on global CSS standards
- More thorough cross-browser testing earlier in development

---

### Plan for Next Week
- Make thumbnail feature unique by adding GIF and SVG upload options
- Implement resume deletion functionality in the UI
- Continue work on Milestone-2 deliverables
- Address any feedback from merged PRs
- Support team with peer testing and code reviews

---
