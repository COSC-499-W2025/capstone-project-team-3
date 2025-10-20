# Personal Log – Vanshika Singla

---

## Entry for Oct 13, 2025 → Oct 19, 2025

### Type of Tasks Worked On
![Personal Log](../../../screenshots/Vanshika_Week7.png)


### Type of Tasks Worked On
- Backend development (ConsentManager — Python)
- Command-line UX/UI (Consent CLI — interactive prompts, detailed info)
- Documentation updates and fixes (DFD image paths, README links)
- Testing & code review (manual tests, PR reviews, test planning)
- Project coordination (issue tracking, task assignments)

---

### Recap of Weekly Goals
- Implement and merge local consent management (ConsentManager) — completed and merged (PR #104)
- Add standardized consent messaging and privacy information (consent_text.py) — completed
- Build an interactive Consent CLI to prompt users and show detailed privacy info (consent_cli.py) — implemented, PR opened (PR #105)
- Fix documentation (DFD image paths, README updates) — completed and merged (PR #63)
- Add Docker configuration for consistent development environment (Dockerfile, docker-compose) — completed and merged (PR #36)
- Review related PRs and plan next steps: unit tests for ConsentManager, revoke-consent flow, and database integration for user input (issues #100, #84, #82)

---

### Features Assigned to Me
- #30: Consent and user management
- #88: Consent Management

---

### Associated Project Board Tasks
| Task/Issue ID | Title                                            | Status     |
|-------------- |--------------------------------------------------|------------|
| #68           | Determine content on Consent Form                 | Closed     |
| #80           | Store Consent Status Locally                      | Closed     |
| #100          | Save the user input in database for consent       |            |
| #88           | Enforce Access Restriction Until Consent is given | Closed     |
| #87           | Test Cases (Positive/Negative)                    | Closed     |
| #84           | Handle Consent Decline & OS Permission Denial     | In review  |

---

### Progress Summary
- **Completed this week:**
  - Implemented `ConsentManager` to store and read consent status ([PR #104] — merged)
  - Added standardized consent messaging and privacy information (`consent_text.py`) ([PR #104])
  - Created an interactive Consent CLI (`consent_cli.py`) with options to view detailed privacy info ([PR #105] — open)
  - Opened PR #105 to integrate the CLI with ConsentManager and consent_text (in review/in progress)
  - Fixed DFD documentation image paths so diagrams render correctly ([PR #63] — merged)
  - Added and/or reviewed Docker configuration and compose files for development ([PR #36] — merged)
  - Reviewed related PRs / provided feedback (Docker coverage, git-folder detection, and other team PRs)

- **In Progress this week:**
  - Follow-ups for handling consent revocation and OS permission denial flows (issues #84, #82)

---

### Additional Context (Optional)

This week’s work focused on adding a robust local consent-management foundation plus a CLI UX for prompting users about consent and displaying privacy details. The `ConsentManager` persists status to the user’s local environment; `consent_text` centralizes messaging so the same text is used everywhere; the Consent CLI provides a clear interactive experience (accept/decline/more info). Documentation fixes (DFD) and Docker setup were also completed and merged, improving developer onboarding and environment parity.

---

### Reflection
**What Went Well:**
- Completed core consent-management pieces and shipped the ConsentManager (merged) ahead of schedule
- Added creativity in the consent form by adding more features for increased transparency
- Clear separation of concerns: consent data, messaging, and UI split into separate modules
- Documentation and Docker improvements merged, improving developer experience
- Actively participated in code reviews and testing across environments
- Implemented responsive and user-friendly UX through ConsentManager and CLI
- Team communication has been effective for integration planning

**What Could Be Improved:**
- Add more unit/automated tests (especially for ConsentManager file read/write edge cases)
- Add explicit handling for consent revocation flows and OS permission-denied scenarios
- Improve in-code documentation/comments for some utility functions

---

### Plan for Next Cycle
- Refactor the CLI if needed to have a centralized CLI for consent management
- Add more unit tests (especially for ConsentManager file read/write edge cases)
- Add explicit handling for consent revocation flows
- Connect repository selection/profile features (if applicable) with backend endpoints
- Take on new features and start building on them
- Continue participating in code reviews and helping team members
