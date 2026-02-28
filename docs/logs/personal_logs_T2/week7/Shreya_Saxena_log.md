# Personal Log – Shreya Saxena

## Week-7, Entry for Feb 16 → Feb 22, 2026

---

### Pull Requests Worked On

- **[PR #670 - Feature-36: Added API documentation for overall project (Pt-1)](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/670)** ✅ Merged
  - Added comprehensive endpoint documentation for projects, skills, user preferences, health, and institutions
  - Documented request/response formats, parameters, and error codes
  - Created clear examples with JSON and JavaScript code samples

- **[PR #675 - Feature-36: Added API documentation for overall project (Pt-2)](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/675)** ✅ Merged
  - Completed API documentation for thumbnails, portfolio, and resume endpoints
  - Added documentation for all 30+ API endpoints in the system
  - Included JavaScript usage examples and quick reference guide
  - Finalized complete API documentation for Milestone 2

- **[PR #681 - Thumbnail unique feature: Added support for GIF/SVG while uploading thumbnail](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/681)** ✅ Merged
  - Implemented unique feature allowing GIF and SVG thumbnails for creative flexibility
  - Updated backend validation to accept image/gif and image/svg+xml formats
  - Modified frontend to allow SVG/GIF selection in file upload dialogs
  - Added comprehensive tests for new file format support
  - Completed end-to-end thumbnail functionality (Feature-26)

- **[PR #691 - Added API client functions and event handlers for deletion of saved resumes](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/691)** ✅ Merged
  - Implemented frontend delete functionality for saved resumes
  - Created API client function to call DELETE /resume/{id} endpoint
  - Added delete button with confirmation dialog in Resume Sidebar
  - Updated state management to refresh resume list after deletion
  - Ensured Master Resume cannot be deleted (safety feature)

- **[PR #693 - Added option to let user add skill+date, edit skill names, restructured chronological menu](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/693)** ✅ Merged
  - Implemented add skills with dates via CLI
  - Added skill name editing/renaming functionality with database persistence
  - Restructured "Chronological Manager" into intuitive "Corrections Menu"
  - Separated concerns: [1] Project dates, [2] Skills dates, [3] Manage skills
  - Added comprehensive tests for all new CLI features
  - Completed Feature-23: chronological information management

---

### Associated Issues Completed

| Issue ID | Title | Status |
|----------|-------|--------|
| [#672](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/672) | Add Endpoint documentation for project, skills, user preferences, health and institutions | ✅ Closed |
| [#673](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/673) | Add endpoint documentation for thumbnail, project, resume and portfolio | ✅ Closed |
| [#671](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/671) | M2 Feature-36 Add clear documentation for all of the API endpoints | ✅ Closed |
| [#434](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/434) | M2 Feature-26: Implement end-to-end functionality to add thumbnails per project | ✅ Closed |
| [#682](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/682) | Unique feature: Add GIF/SVG as thumbnail for creative flexibility for the user | ✅ Closed |
| [#611](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/611) | Delete Resume (UI) | ✅ Closed |
| [#692](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/692) | Implement add skills section in CLI | ✅ Closed |
| [#694](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/694) | Implement allowing the users to edit skills in CLI | ✅ Closed |
| [#695](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/695) | Restructure chronological menu to separate concerns for skill editing and chronological editing | ✅ Closed |
| [#547](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/547) | M2 Feature-23: Allow users to update chronological information in CLI | ✅ Closed |

---

## Work Breakdown

### Coding Tasks

#### API Documentation (Feature-36, PR #670 & #675)
- Documented all 30+ API endpoints with clear descriptions
- Created comprehensive request/response examples for each endpoint
- Added JavaScript code samples for common use cases
- Documented query parameters, headers, and error responses
- Created Quick Reference guide for developer convenience
- Organized documentation by functional areas (Projects, Skills, Resume, Portfolio, etc.)

#### GIF/SVG Thumbnail Support (PR #681)
- Extended backend validation to accept GIF and SVG image formats
- Updated allowed_types list in POST endpoint: `["image/jpeg", "image/jpg", "image/png", "image/gif", "image/svg+xml", "image/webp"]`
- Modified frontend file input to explicitly accept new formats
- Created unit tests for SVG and GIF upload validation
- Verified cache-busting works with new file types
- Completed unique feature implementation for creative portfolio thumbnails

#### Resume Deletion UI (PR #691)
- Implemented `deleteResume(id)` API client function in TypeScript
- Added delete button to `ResumeSidebar` component (appears only for non-master resumes)
- Created confirmation dialog before deletion (`window.confirm`)
- Implemented `handleDeleteResume` in `ResumeBuilderPage` with state updates
- Added logic to refresh resume list and adjust active selection after deletion
- Added frontend unit tests for delete functionality

#### Chronological CLI Enhancements (PR #693)
- Renamed menu from "PROJECT CHRONOLOGICAL MANAGER" to "PROJECT CORRECTIONS MENU"
- Split `_manage_project_skills` into two focused methods:
  - `_manage_skill_dates()`: Update dates only (menu option [2])
  - `_manage_skills()`: Add, remove, rename skills (menu option [3])
- Implemented `_add_skill()` with date prompts and validation
- Created `_edit_skill_name()` with database persistence via `update_skill_name()`
- Added comprehensive input validation and error handling
- Updated all CLI prompts for consistency across main.py

---

### Testing & Debugging Tasks

- Added unit tests for SVG and GIF thumbnail uploads (`test_upload_svg_thumbnail`, `test_upload_gif_thumbnail`)
- Verified cache headers in thumbnail GET endpoint tests
- Created frontend tests for `deleteResume` API client function
- Added CLI tests for add skill functionality (`test_add_skill_with_cli`, validation tests)
- Created CLI tests for skill name editing (`test_edit_skill_name`, preservation tests)
- Updated tests to reflect new chronological menu structure
- All 33 tests passing for chronological manager and utilities
- Verified API documentation accuracy against actual codebase

---

### Collaboration & Review Tasks

- Created comprehensive API documentation for entire team and external developers
- Participated in reading break planning and Milestone 2 wrap-up discussions
- Responded to code review feedback across all PRs
- Reviewed and tested teammates' PRs locally
- Created detailed PR descriptions with testing instructions for all 5 PRs
- Updated documentation with clear examples and usage patterns

---

### Reflection

**What Went Well:**
- Successfully delivered 5 merged PRs completing multiple Milestone 2 features
- Completed Feature-23 (chronological management) with comprehensive CLI enhancements
- Completed Feature-26 (thumbnails) with unique GIF/SVG support
- Completed Feature-36 (API documentation) covering all 30+ endpoints
- Implemented resume deletion UI connecting frontend to backend seamlessly
- All features include thorough testing and validation
- Strong code quality maintained across all PRs

**What Could Be Improved:**
- API documentation could have been done earlier to help team integration
- Could have coordinated better with frontend team on resume deletion UI patterns
- Better time management during reading break to balance workload

---

### Plan for Next Week
- Begin Milestone 3 requirements and planning
- Monitor all newly merged features for any production issues
- Continue peer reviews and support team with testing
- Address any feedback from Milestone 2 feature delivery
- Prepare for final Milestone 2 presentation and demo

---
