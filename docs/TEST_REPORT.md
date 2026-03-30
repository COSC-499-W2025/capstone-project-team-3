# Test Report

## Project Insights — Testing Documentation

---

## Table of Contents

1. [Overview](#overview)
2. [Testing Frameworks and Tools](#testing-frameworks-and-tools)
3. [Test Configuration](#test-configuration)
4. [Test File Inventory](#test-file-inventory)
   - [Backend Tests (Python)](#backend-tests-python)
   - [Frontend Tests (TypeScript/React)](#frontend-tests-typescriptreact)
   - [Test Fixtures and Mocks](#test-fixtures-and-mocks)
5. [Test Strategies](#test-strategies)
6. [How to Run Tests](#how-to-run-tests)
7. [CI/CD Integration](#cicd-integration)
8. [Test Coverage Map](#test-coverage-map)
9. [Known Limitations and Exclusions](#known-limitations-and-exclusions)
10. [Test Files to Use for Demo](tests/files/test_data)

---

## Overview

Project Insights is a full-stack desktop application for analyzing GitHub/local projects, generating resumes, and building portfolios. It consists of a Python/FastAPI backend and a TypeScript/React frontend running in Electron. The system uses pytest for backend testing and Jest for frontend testing, with a total of **85 test files** covering unit, component, API, integration, and CLI testing.

| Metric | Value |
|--------|-------|
| Total test files | 85 |
| Backend test files | 63 |
| Frontend test files | 20 |
| Mock/fixture files | 2 |
| Test frameworks | 2 (pytest, Jest) |
| Test strategies | 5 (unit, component, API, integration, CLI) |


## Testing Frameworks and Tools

### Backend (Python)

| Tool | Version | Purpose |
|------|---------|---------|
| pytest | 8.4.2 | Test runner |
| pytest-cov | 7.0.0 | Code coverage reporting |
| pytest-asyncio | 1.2.0 | Async test support for FastAPI |
| pytest-mock | >=3.12.0 | Mock fixtures |
| unittest.mock | built-in | Patching and MagicMock |
| coverage | 7.10.6 | Coverage measurement |

### Frontend (TypeScript/React)

| Tool | Version | Purpose |
|------|---------|---------|
| Jest | 30.2.0 | Test runner |
| ts-jest | 29.4.6 | TypeScript transform |
| jest-environment-jsdom | 30.2.0 | DOM simulation |
| @testing-library/react | 16.3.2 | Component testing |
| @testing-library/jest-dom | 4.2.4 | Custom DOM matchers |
| @testing-library/user-event | 14.6.1 | User interaction simulation |

---

## Test Configuration

### pytest Configuration (`pytest.ini`)

```ini
[pytest]
pythonpath = .
addopts = --ignore=tests/test_cli.py --ignore=tests/test_code_analysis.py --ignore=tests/test_non_code_analysis.py
```

- Sets the Python path to the project root so imports resolve correctly.
- Three test files are excluded due to import errors (see [Known Limitations](#known-limitations-and-exclusions)).

### Jest Configuration (`desktop/jest.config.js`)

- Preset: `ts-jest`
- Environment: `jsdom`
- Test match pattern: `<rootDir>/tests/**/*.test.(ts|tsx)`
- CSS and image files are mocked via `styleMock.js`.
- API config is mocked via `tests/__mocks__/config/api.ts`.
- Setup file: `jest.setup.ts` (imports `@testing-library/jest-dom`, polyfills `TextEncoder`/`TextDecoder`).

### API Route Test Fixtures (`tests/api/routes/conftest.py`)

- Forces all async tests to use the `asyncio` backend (not `trio`).

### Shared Test Fixtures (`tests/fixtures/test_data.py`)

- Provides sample project data structures (design pattern files, architecture patterns, entity definitions) used across multiple test modules.

---

## Test File Inventory

### Backend Tests (Python)

The 61 backend test files are organized into four directories mirroring the application structure.

#### Root-Level Tests (`tests/`)

| # | File | Module Under Test |
|---|------|-------------------|
| 1 | `test_access_checker.py` | `app.utils.access_checker` |
| 2 | `test_collaborative_parsing.py` | `app.utils.code_analysis.collaborative_parsing` |
| 3 | `test_consent_manager.py` | `app.manager.consent_manager` |
| 4 | `test_db_seed.py` | `app.data.db_seed` |
| 5 | `test_final_verification.py` | End-to-end verification flows |
| 6 | `test_generate_resume.py` | `app.utils.generate_resume` |
| 7 | `test_generate_resume_tex.py` | `app.utils.generate_resume_tex` |
| 8 | `test_git_code_parsing.py` | `app.cli.git_code_parsing` |
| 9 | `test_git_utils.py` | `app.utils.git_utils` |
| 10 | `test_individual_work_parsing.py` | `app.utils.code_analysis.individual_work_parsing` |
| 11 | `test_main.py` | `app.main` |
| 12 | `test_non_codeParser.py` | `app.utils.non_code_parsing` |
| 13 | `test_path_utils.py` | `app.utils.path_utils` |
| 14 | `test_project_input.py` | `app.cli.project_input` |
| 15 | `test_project_score.py` | `app.utils.project_score` |
| 16 | `test_readme_correct.py` | `app.utils.readme_correct` |
| 17 | `test_revoke_consent.py` | `app.manager.revoke_consent` |
| 18 | `test_similarity_confirmation.py` | `app.utils.similarity_confirmation` |
| 19 | `test_text_processing.py` | `app.utils.code_analysis.text_processing` |
| 20 | `test_user_preferences.py` | `app.utils.user_preferences` |

#### API Tests (`tests/api/`)

| # | File | Route Under Test |
|---|------|------------------|
| 21 | `test_analysis_api.py` | `/api/analysis` |
| 22 | `test_cover_letter.py` | `/api/cover-letter` |
| 23 | `test_gemini_settings_api.py` | `/api/gemini-settings` |
| 24 | `test_get_upload_id.py` | `/api/get-upload-id` |
| 25 | `test_portfolio.py` | `/api/portfolio` |
| 26 | `test_privacy_consent.py` | `/api/privacy-consent` |
| 27 | `test_projects.py` | `/api/projects` |
| 28 | `test_resume.py` | `/api/resume` |
| 29 | `test_upload_page.py` | `/api/upload` |
| 30 | `test_user_preferences_api.py` | `/api/user-preferences` |

#### API Route Tests (`tests/api/routes/`)

| # | File | Route Under Test |
|---|------|------------------|
| 31 | `test_ats.py` | `/api/ats` |
| 32 | `test_chronological.py` | `/api/chronological` |
| 33 | `test_education_service.py` | `/api/education` |
| 34 | `test_post_thumbnail.py` | `/api/thumbnail` |
| 35 | `test_skills.py` | `/api/skills` |
| 36 | `conftest.py` | Shared async fixture |

#### CLI Tests (`tests/cli/`)

| # | File | Module Under Test |
|---|------|-------------------|
| 37 | `test_chronological_manager.py` | `app.cli.chronological_manager` |
| 38 | `test_delete_insights.py` | `app.cli.delete_insights` |
| 39 | `test_file_input.py` | `app.cli.file_input` |
| 40 | `test_project_score_override_cli.py` | `app.cli.project_score_override` |
| 41 | `test_resume_cli.py` | `app.cli.resume_cli` |
| 42 | `test_user_preference_cli.py` | `app.cli.user_preference_cli` |

#### Utility Tests (`tests/utils/`)

| # | File | Module Under Test |
|---|------|-------------------|
| 43 | `test_analysis_merger.py` | `app.utils.analysis_merger` |
| 44 | `test_analysis_merger_utils.py` | `app.utils.analysis_merger_utils` |
| 45 | `test_chronological_utils.py` | `app.utils.chronological_utils` |
| 46 | `test_clean_up.py` | `app.utils.clean_up` |
| 47 | `test_delete_insights_utils.py` | `app.utils.delete_insights_utils` |
| 48 | `test_project_extractor.py` | `app.utils.project_extractor` |
| 49 | `test_retrieve_insights.py` | `app.utils.retrieve_insights` |
| 50 | `test_score_override_utils.py` | `app.utils.score_override_utils` |
| 51 | `test_thumbnail_utils.py` | `app.utils.thumbnail_utils` |
| 52 | `test_user_preferences.py` | `app.utils.user_preferences` |
| 53 | `test_analysis_clear_utils.py` | `app.utils.analysis_clear_utils` |
| 54 | `test_learning_recommendations.py` | `app.utils.learning_recommendations` |

#### Code Analysis Tests (`tests/utils/code_analysis/`)

| # | File | Module Under Test |
|---|------|-------------------|
| 55 | `test_extract_components.py` | `app.utils.code_analysis.extract_components` |
| 56 | `test_file_entity_utils.py` | `app.utils.code_analysis.file_entity_utils` |
| 57 | `test_grammar_loader.py` | `app.utils.code_analysis.grammar_loader` |
| 58 | `test_parse_code_utils.py` | `app.utils.code_analysis.parse_code_utils` |

#### Non-Code Analysis Tests (`tests/utils/non_code_analysis/`)

| # | File | Module Under Test |
|---|------|-------------------|
| 59 | `test_non_3rd_party_analysis.py` | `app.utils.non_code_analysis.non_3rd_party_analysis` |
| 60 | `test_non_code_file_checker.py` | `app.utils.non_code_analysis.non_code_file_checker` |
| 61 | `keywords/test_domain_keywords.py` | `app.utils.non_code_analysis.keywords.domain_keywords` |

---

### Frontend Tests (TypeScript/React)

The 20 frontend test files cover all major page components, shared context, and the primary API client module.

#### Page Component Tests (`desktop/tests/`)

| # | File | Component Under Test |
|---|------|----------------------|
| 1 | `ATSScoringPage.test.tsx` | `src/pages/ATSScoringPage` |
| 2 | `ConsentPage.test.tsx` | `src/pages/ConsentPage` |
| 3 | `CoverLetterPage.test.tsx` | `src/pages/CoverLetterPage` |
| 4 | `DataManagementPage.test.tsx` | `src/pages/DataManagementPage` |
| 5 | `HubPage.test.tsx` | `src/pages/HubPage` |
| 6 | `NavBar.test.tsx` | `src/NavBar` |
| 7 | `PortfolioPage.test.tsx` | `src/pages/PortfolioPage` |
| 8 | `ProjectSelectionPage.test.tsx` | `src/pages/ProjectSelectionPage` |
| 9 | `ResumeBuilderPage.test.tsx` | `src/pages/ResumeBuilderPage` |
| 10 | `ResumePreview.test.tsx` | `src/components/ResumePreview` |
| 11 | `ResumeSections.test.tsx` | `src/components/ResumeSections` |
| 12 | `ResumeSidebar.test.tsx` | `src/components/ResumeSidebar` |
| 13 | `ScoreOverridePage.test.tsx` | `src/pages/ScoreOverridePage` |
| 14 | `SettingsPage.test.tsx` | `src/pages/SettingsPage` |
| 15 | `TemplatePage.test.tsx` | `src/pages/TemplatePage` |
| 16 | `UploadPage.test.tsx` | `src/pages/UploadPage` |
| 17 | `UserPreferencePage.test.tsx` | `src/pages/UserPreferencePage` |
| 18 | `WelcomePage.test.tsx` | `src/pages/WelcomePage` |

#### Context Tests

| # | File | Module Under Test |
|---|------|-------------------|
| 19 | `ThemeContext.test.tsx` | `src/context/ThemeContext` |

#### API Module Tests

| # | File | Module Under Test |
|---|------|-------------------|
| 20 | `projectsApi.test.ts` | `src/api/projects` |

---

### Test Fixtures and Mocks

| File | Purpose |
|------|---------|
| `tests/fixtures/test_data.py` | Sample project structures (design patterns, architecture patterns, entity definitions) used across backend tests |
| `tests/fixtures/__init__.py` | Makes fixtures importable as a package |
| `desktop/tests/__mocks__/styleMock.js` | Mocks CSS and image imports for Jest |
| `desktop/tests/__mocks__/config/api.ts` | Mocks the frontend API base URL configuration |
| `tests/api/routes/conftest.py` | Forces async tests to use asyncio backend |

---

## Test Strategies

### 1. Unit Testing (Primary Strategy)

The majority of tests are **unit tests** that isolate individual functions and modules using mocking.

**Backend pattern:**
- `unittest.mock.patch` and `MagicMock` to replace external dependencies
- `tmp_path` fixtures to isolate SQLite database operations
- `monkeypatch` to override module-level constants and functions

```python
# Example: tests/test_main.py
@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    from app.data import db as dbmod
    test_db = tmp_path / "test_main.sqlite3"
    monkeypatch.setattr(dbmod, "DB_PATH", test_db)
    dbmod.init_db()
    yield
```

**Frontend pattern:**
- `jest.mock()` to mock API modules and external dependencies
- `@testing-library/react` for rendering components in isolation
- `jest.fn()` for spy functions and controlled return values

```typescript
// Example: desktop/tests/UploadPage.test.tsx
jest.mock("../src/api/upload");
jest.mock("../src/api/geminiKey", () => ({
  getGeminiKeyStatus: jest.fn().mockResolvedValue({ configured: true, valid: true }),
}));
```

### 2. Component Testing

React component tests verify rendering, user interactions, and state changes using `@testing-library/react` and `@testing-library/user-event`.

**Areas covered:**
- All 17 page components
- Shared UI components (NavBar, ResumePreview, ResumeSections, ResumeSidebar)
- React context providers (ThemeContext)

**What is verified:**
- Correct rendering of text and elements
- User interactions (clicks, form inputs, file uploads)
- Conditional rendering based on state
- Navigation behavior via `react-router-dom`

### 3. API / Route Testing

FastAPI routes are tested with mocked service layers to verify HTTP request/response handling.

**Areas covered:**
- 15 API route test files covering upload, analysis, resume, portfolio, ATS scoring, cover letter, skills, chronological ordering, education, thumbnails, user preferences, privacy consent, Gemini settings, and projects.

**What is verified:**
- Correct HTTP status codes
- Request validation and error handling
- Response body structure and content
- Edge cases (missing fields, invalid data, duplicate uploads)

### 4. Integration Testing

Integration-style tests in `test_main.py` (35+ tests) verify multi-step flows where multiple modules interact.

**Flows covered:**
- Full CLI analysis loop (file input -> scan -> parse -> analyze -> store)
- Resume generation pipeline (data retrieval -> formatting -> LaTeX output)
- Consent management flow (grant -> enforce -> revoke)
- Scan flow with similarity detection and re-analysis

### 5. CLI Testing

Command-line interface modules are tested by mocking `builtins.input` and `sys.argv` to simulate user interactions.

**Modules covered:**
- File input and project selection
- Resume generation CLI
- User preference management
- Project score override
- Chronological ordering manager
- Delete insights

---

## How to Run Tests

### Backend Tests

```bash
# Run all backend tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=term-missing

# Run a specific test file
pytest tests/test_main.py

# Run tests matching a keyword
pytest -k "resume"

# Generate HTML coverage report
pytest --cov=app --cov-report=html
# Open htmlcov/index.html in a browser
```

### Frontend Tests

```bash
# Navigate to the desktop directory
cd desktop

# Run all frontend tests
npm run test

```

### Run All Tests

```bash
# Backend
pytest --cov=app --cov-report=term-missing

# Frontend (separate terminal)
cd desktop && npm run test
```

---

## CI/CD Integration

### GitHub Actions Workflows

#### `ci.yml` — Main CI Pipeline

| Step | Action |
|------|--------|
| Trigger | Push or PR to `main`/`master` |
| Python version | 3.11 |
| Install | `pip install -r requirements.txt` |
| Server | Starts FastAPI via `uvicorn app.main:app` in background |
| Test command | `pytest --cov=app --cov-report=term-missing --cov-report=html` |
| Artifacts | Uploads `htmlcov/` as build artifact |

**Note:** The CI pipeline runs backend tests only. Frontend Jest tests must be run manually.

#### `docker.yml` — Docker Build Validation

- Builds the Docker image for `linux/amd64`
- Validates `docker compose config`

#### `security.yml` — Dependency Security Scan

- Runs `safety check` on `requirements.txt`
- Triggers on PR, push, and weekly schedule (Sundays)

---

## Test Coverage 

### Backend Coverage Report (896 Test Cases Passing)

 Run `docker compose server pytest --cov=app --cov-report=html:/app/htmlcov` 

 This will run your tests and create a detailed **HTML report** inside the `/app/htmlcov` folder.

To view the coverage report:

1. Open the `htmlcov/index.html` file in a web browser.
2. You’ll see a visual overview showing which lines of code are tested (highlighted in green) and which are not (highlighted in red). 

| Application Area | Test Files | Strategy |
|------------------|------------|----------|
| Main entry point (`app/main.py`) | `test_main.py` | Unit + Integration |
| API routes (15 endpoints) | `tests/api/test_*.py` (10 files) | API/Route |
| API route handlers (5 routes) | `tests/api/routes/test_*.py` (5 files) | API/Route |
| CLI modules (6 modules) | `tests/cli/test_*.py` (6 files) | CLI |
| Core utilities (10 modules) | `tests/utils/test_*.py` (10 files) | Unit |
| Code analysis (4 modules) | `tests/utils/code_analysis/test_*.py` (4 files) | Unit |
| Non-code analysis (3 modules) | `tests/utils/non_code_analysis/test_*.py` (3 files) | Unit |
| Resume generation | `test_generate_resume.py`, `test_generate_resume_tex.py` | Unit |
| Git operations | `test_git_utils.py`, `test_git_code_parsing.py` | Unit |
| Consent management | `test_consent_manager.py`, `test_revoke_consent.py` | Unit |
| Database seeding | `test_db_seed.py` | Unit |
| Text/NLP processing | `test_text_processing.py` | Unit |
| Similarity detection | `test_similarity_confirmation.py` | Unit |
| Project scoring | `test_project_score.py` | Unit |

### Frontend Coverage Report (455 Tests Passing)

[desktop/coverage/Frontend_Coverage_03292026.png]

To run : 
 `cd desktop && npm run test:coverage`

 This will run your tests and create a detailed **HTML report** inside the `/desktop/coverage` folder.

| Application Area | Test Files | Strategy |
|------------------|------------|----------|
| All page components (17 pages) | `desktop/tests/*.test.tsx` (17 files) | Component |
| Shared UI components | `ResumePreview.test.tsx`, `ResumeSections.test.tsx`, `ResumeSidebar.test.tsx` | Component |
| Theme context | `ThemeContext.test.tsx` | Unit |
| Projects API client | `projectsApi.test.ts` | Unit |



---
