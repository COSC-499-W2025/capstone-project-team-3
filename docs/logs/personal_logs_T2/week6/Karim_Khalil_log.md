# Personal Log – Karim Khalil

---

## Week-6, Entry for Feb 9 → Feb 15, 2026

---

### Connection to Previous Week

Building on my earlier portfolio backend and API work, this week I focused on building the portfolio UI shell and then completing the interactive dashboard visuals in static HTML/JS so the team could validate the end-to-end dashboard experience.

---

### Pull Requests Worked On

- **[PR #632 - completed part 1 of portfolio html](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/632)** ✅ Merged
  - Added the base Portfolio Dashboard HTML layout and styling.
  - Implemented sidebar project selection + main dashboard structure.
  - Wired Chart.js and existing `/api/static/portfolio.js` into the page.
  - Added manual reproduction URL in PR discussion (`http://localhost:8000/api/portfolio-dashboard`).

- **[PR #641 - completed portfolio UI](https://github.com/COSC-499-W2025/capstone-project-team-3/pull/641)** ✅ Merged
  - Added interactive portfolio charts and graph sections.
  - Fixed Docker workflow disk-space issue in CI by adding cleanup commands in workflow YAML.
  - Updated summary data source and UI rendering details based on review feedback.
  - Added show more / show less behavior for long project summaries.
  - Improved chart readability (including y-axis details).

---

### Associated Issues Completed
| Issue ID | Title | Status |
|----------|-------|--------|
| [#707](https://github.com/COSC-499-W2025/capstone-project-team-3/issues/707) | Portfolio UI enhancements / interactive graphs | ✅ Closed via PR #641 |

---

## Work Breakdown

### Coding Tasks

- Built initial portfolio dashboard page structure (sidebar + main content + overview section).
- Implemented interactive graph rendering and portfolio visual sections.
- Updated summary presentation behavior and truncation UX controls.
- Added CI workflow disk cleanup changes to unblock Docker build failures.

### Testing & Debugging Tasks

- Manual browser testing of portfolio dashboard route:
  - `http://localhost:8000/api/portfolio-dashboard`
- Verified chart rendering, responsiveness, summary toggles, and populated table/graph states.
- Re-ran checks after CI workflow updates to confirm Docker build passed.

### Collaboration & Review Tasks

- Addressed review feedback from teammates on:
  - reproducibility/test URL,
  - summary data display,
  - top skills/table population,
  - long-summary handling.
- Shared screenshots and follow-up clarifications during PR review.

---

### Reflection

**What Went Well:**
- Delivered portfolio UI in phased PRs while keeping momentum.
- Quickly resolved CI Docker disk-space failure.
- Incorporated reviewer suggestions effectively (summary UX + data display refinements).

**What Could Be Improved:**
- Add tighter scope notes for phased UI PRs to reduce confusion about what is intentionally deferred.
- Include final visual screenshots earlier in the review cycle.

---

### Plan for Next Week

- Add score transparency and override display improvements in portfolio.
- Begin migration from static portfolio UI into desktop React app.
- Add downloadable interactive portfolio output support.
