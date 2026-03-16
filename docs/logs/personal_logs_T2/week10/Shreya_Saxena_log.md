# Personal Log – Shreya Saxena

---

## Week-10, Entry for Mar 9 → Mar 15, 2026

### Pull Requests Worked On

- **[PR #781 - Display projects list for Data Management UI, Connect Upload to trigger scanning. (Pt-2)](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/781)** ✅ Merged
  - Display projects list on Data Management page
  - Connected Upload flow to trigger analysis after upload so projects appear in Data Management
  - Added analysis API client for desktop app
  - Projects now populate in Data Management after upload and analysis

- **[PR #801 - Added project/skill chronological editing along with project/skill display. (Pt-3)](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/801)** ✅ Merged
  - Added inline editing for project and skill dates in Data Management
  - Fixed skill source display to only show "Technical skill" or "Soft skill"
  - Updated chronological API to support non-technical skill source
  - Added chronological skill view with expandable project rows

- **[PR #821 - Added date validation handling to data management UI](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/821)** ✅ Merged
  - Added date format validation (dd-mm-yyyy only) for project and skill dates
  - Enforced last modified must be after date created
  - Added skill date range validation (skill date must be within project's created–last modified range)
  - Normalized date comparison to handle timestamps vs date-only (same-day boundary case)
  - Added error messages for invalid format, modified before created, and skill outside range
  - Added tests for all validation edge cases

---

### Associated Issues Completed

| Issue ID | Title | Status |
|----------|-------|--------|
| [#782](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/782) | Display projects list on Data Management page | ✅ Closed |
| [#783](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/783) | Connect analysis after upload so projects appear in Data Management | ✅ Closed |
| [#784](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/784) | Add analysis API client for desktop | ✅ Closed |
| [#802](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/802) | Add inline editing for project and skill dates in Data Management | ✅ Closed |
| [#803](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/803) | Fix skill source to only be "Technical skill" or "Soft skill" | ✅ Closed |
| [#804](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/804) | Fix chronological API to support non-technical skill source | ✅ Closed |
| [#805](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/805) | Add chronological skill view | ✅ Closed |
| [#824](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/824) | Add date validation for skills ensuring correct range | ✅ Closed |
| [#825](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/825) | Add date format validation for project and skills | ✅ Closed |

---

## Work Breakdown

### Coding Tasks

#### Data Management Projects List & Upload Connection (PR #781)
- Implemented projects list display on Data Management page
- Connected Upload page to analysis flow so projects populate after scan/analysis
- Added `runAnalysis` API client for desktop
- Integrated analysis runner flow with Data Management data source

#### Chronological Editing & Skill Display (PR #801)
- Added inline editable fields for project created_at and last_modified dates
- Added inline editable fields for skill dates
- Implemented dd-mm-yyyy date format display and parsing
- Fixed skill source display: "Technical skill" / "Soft skill" only
- Updated backend chronological API to accept non-technical skill source
- Added expandable project rows to show skills per project

#### Date Validation (PR #821)
- Added `parseDdMmYyyyToIso` for format validation
- Added `normalizeToDateOnly` for timestamp vs date-only comparison
- Enforced last_modified > created_at for project dates
- Enforced skill date within project date range
- Added `dateError` state and error message display
- Styled date error messages in Data Management UI

---

### Testing & Debugging Tasks

- Added DataManagementPage tests for projects list, expand skills, refresh
- Added tests for date format validation error
- Added tests for last modified before created error
- Added tests for skill date outside range error
- Added test for same-day boundary case (skill date on project created day with timestamp)
- All test suites passing

---

### Collaboration & Review Tasks

- Created PR descriptions with testing instructions
- Responded to code review feedback
- Fixed timestamp vs date-only comparison bug from review

---

### Reflection

**What Went Well:**
- Delivered full Data Management UI flow: projects list, skills view, inline editing
- Comprehensive date validation with clear error messages
- Robust handling of timestamp vs date-only comparison for same-day boundary

**What Could Be Improved:**
- Could add more UI polish (e.g. loading states for individual date saves)

---

### Plan for Next Week

- Continue Data Management enhancements as needed
- Support team with code reviews
- Explore Hub page integration and navigation flow

---
