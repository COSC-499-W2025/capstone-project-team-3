# Personal Log – Karim Khalil

---

## Week-7, Entry for Feb 16 → Feb 22, 2026

---

### Connection to Previous Week

After completing the static portfolio UI, I focused this week on score transparency and override handling, then started migrating the portfolio experience into the desktop frontend and added downloadable interactive portfolio export.

---

### Pull Requests Worked On

- **[PR #676 - added score breakdown & score overridden value](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/676)** ✅ Merged
  - Added score override awareness in portfolio display.
  - Added scoring methodology / breakdown section for transparency.
  - Updated logic to ensure effective score handling after rank removal.
  - Added/updated tests covering overridden score scenarios.

- **[PR #701 - started portfolio migration from static to desktop](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/701)** ✅ Merged
  - Migrated portfolio dashboard UI into Desktop frontend (React/TSX + CSS).
  - Implemented sidebar, overview cards, chart grid, project cards, and analysis sections with parity to static UI.
  - Added chart.js dependency for desktop implementation.
  - Documented that tests would be migrated in follow-up PR.

- **[PR #702 - added portfolio download option](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/702)** ✅ Merged
  - Added interactive portfolio HTML download flow.
  - Embedded current portfolio payload + chart recreation in exported file.
  - Preserved show more / show less behavior in exported interactive HTML.
  - Added regression tests for export wiring and behavior.

---

### Associated Issues Completed
| Issue ID | Title | Status |
|----------|-------|--------|
| [#706](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/706) | Score override / score transparency updates | ✅ Closed via PR #676 |
| [#705](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/705) | Start portfolio migration to desktop frontend | ✅ Closed via PR #701 |
| [#704](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/704) | Add downloadable interactive portfolio HTML | ✅ Closed via PR #702 |

---

## Work Breakdown

### Coding Tasks

- Implemented score override display behavior and scoring transparency section.
- Migrated large portions of portfolio UI from static to desktop React.
- Added interactive portfolio export generation with embedded JS/chart behavior.

### Testing & Debugging Tasks

- Added/updated tests for score override and portfolio behavior.
- Added export-specific regression tests for interactive HTML output.
- Manual validation of:
  - score breakdown rendering,
  - desktop chart behavior,
  - portfolio download output and interactions.

### Collaboration & Review Tasks

- Responded to reviewer concerns regarding score semantics and hardcoded cap visibility.
- Clarified migration scope and known deferred items (thumbnail loading in migration phase).
- Updated implementation based on review comments before merge.

### Additional Team/Class Activities

- Prepared for the live in-class presentation (demo planning, feature flow prep, and talking points).

---

### Reflection

**What Went Well:**
- Completed substantial feature progression in a single week across three merged PRs.
- Improved score transparency and user understanding of portfolio outputs.
- Successfully advanced the migration path from static to desktop UI.

**What Could Be Improved:**
- Keep test migration and feature migration closer together to reduce temporary coverage gaps.

---

### Plan for Next Week

- Finalize override display UX and role visibility on project cards.
- Continue API-driven flow migration work for analysis execution.
- Support documentation/architecture updates and class presentation follow-up.
