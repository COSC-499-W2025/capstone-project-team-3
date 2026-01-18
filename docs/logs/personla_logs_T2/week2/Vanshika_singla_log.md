# Personal Log – Vanshika Singla

---
## Entry for Week 2, Jan 12 - Jan 18

### Type of Tasks Worked On
- Implemented API endpoints for privacy consent management
- Added automated tests for consent API endpoints
- Created Docker Build workflow for CI/CD validation
- Created Test Coverage workflow for quality assurance
- Updated CI/CD documentation

---

### Recap of Weekly Goals
✅ Implement privacy consent API endpoints — Completed
✅ Add automated tests for consent functionality — Completed
✅ Create Docker Build workflow — Completed
✅ Create Test Coverage workflow — Completed
✅ Update workflow documentation — Completed

---

### Features Assigned to Me
#456: API/POST CONSENT MANAGER - Enable web-based consent management
#457: Testing for consent-API - Automated tests for consent endpoints
#453: Create Automated Coverage testing in CI pipeline
#454: Create docker build for CI pipeline

---

### Associated Project Board Tasks
| Task/Issue ID | Title                                                                   | Status     |
|---------------|-------------------------------------------------------------------------|------------|
| #456          | API/POST CONSENT MANAGER                                                | Closed     |
| #457          | Testing for consent-API                                                 | Closed     |
| #453          | Create Automated Coverage testing in CI pipeline                        | Its done, but not merged yet     |
| #454          | Create docker build for CI pipeline                                     | In progress, we are failing this currently, which may/maynot be due to pre-existing issues   |

---

### Issue Descriptions

**#456 – API/POST CONSENT MANAGER**

Added three API endpoints to enable web-based privacy consent management:
- POST /api/privacy-consent - Submit user consent decision (accept/decline)
- GET /api/privacy-consent - Check if user has given consent
- DELETE /api/privacy-consent - Revoke user consent

Previously, consent only worked via CLI terminal prompts. These endpoints enable building a web frontend where users can submit consent through forms, check their consent status, and revoke consent from settings pages.

Implementation reuses existing consent_utils.py functions (record_consent, has_consent, revoke_consent) and the existing CONSENT table in SQLite database, mirroring CLI functionality from ConsentManager class.

**#457 – Testing for consent-API**

Added comprehensive automated tests for consent API endpoints:
- test_submit_consent_accept() - Verify accepting consent returns success
- test_submit_consent_decline() - Verify declining consent returns success
- test_get_consent_status() - Verify consent status check returns correct fields
- test_revoke_consent() - Verify consent revocation works

**#453 – Create Automated Coverage testing in CI pipeline**

Created coverage.yml workflow that generates detailed test coverage reports on every PR and push to main/master. This helps identify untested code paths and maintain code quality standards across the project.

**#454 – Create docker build for CI pipeline**

Created docker.yml workflow that validates Docker images build successfully on every PR and push to main/master. This prevents deployment failures due to Docker configuration issues and ensures the application can be containerized correctly before merging changes.

Both workflows complement the existing CI pipeline and security scans to provide comprehensive automated testing and validation. and this is helping us alot to work on the tests that are failing currently

---

### Progress Summary
- **Completed this week:**
Successfully implemented privacy consent API endpoints with full test coverage, enabling web-based consent management. Created two essential CI/CD workflows (Docker Build and Test Coverage) that automate quality assurance and deployment validation. Updated workflow documentation in .github/workflows/README.md.

---

### Reflection
**What Went Well:**
- Successfully reused existing consent utilities for API implementation
- Comprehensive test coverage for all consent endpoints
- Workflows follow GitHub Actions best practices


**What Could Be Improved:**
- Fixing of tests can be the priority while are still figuring out the requirmeents and work load is little manageble

---

### Plan for Next Cycle
- Monitor new workflows in production to ensure stability
- Address any issues that arise from Docker or coverage workflows
- My CI/CD pipeline can see the wrong tests that are existing in the project, so i have discussed with the team and we will picking up failed files and fix them as well. 
- work on api endpoint for user preference 
- Start planing for 21 Point in the Milestone2 if time allows 
