# Personal Log – Shreya Saxena

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
