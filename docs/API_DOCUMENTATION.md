# API Documentation

**Server:** `http://localhost:8000` (development)

---

## Overview

This document explains all API endpoints in Project Insights. 

**Note:** Full frontend URLs available once complete UI is deployed.

---

## Response Codes

| Code | Meaning |
|------|---------|
| `200` | ✅ Success |
| `201` | ✅ Created |
| `204` | ✅ No content |
| `404` | ❌ Not found |
| `400` | ❌ Bad request |
| `409` | ❌ Conflict |
| `422` | ❌ Validation/processing error |
| `500` | ❌ Server error |

---

## Endpoints

### 1. Health Check

**What it does:** Checks if server is running.

**URL:** `GET /health`

**Response:**
```json
{"status": "ok"}
```

---

### 2. Get All Projects

**What it does:** Lists all analyzed projects.

**URL:** `GET /api/projects`

**Response:**
```json
[
  {
    "id": "abc123",
    "name": "My Project",
    "score": 0.85,
    "score_original": 0.85,
    "score_overridden": false,
    "score_overridden_value": null,
    "score_override_exclusions": [],
    "skills": ["Python", "FastAPI", "Docker"],
    "date_added": "2024-01-15T10:00:00Z"
  }
]
```

**Fields:**
- `id` - Unique identifier
- `name` - Project name
- `score` - Quality score (0-1)
- `score_original` - Original computed score before overrides
- `score_overridden` - Whether an override is currently active
- `score_overridden_value` - Persisted override score value (if any)
- `score_override_exclusions` - Metrics excluded by override
- `skills` - Top 5 skills
- `date_added` - Analysis date

---

### 3. Get All Skills

**What it does:** Lists all skills across projects.

**URL:** `GET /api/skills`

**Response:**
```json
[
  {
    "skill": "Python",
    "frequency": 5,
    "source": "code"
  }
]
```

**Fields:**
- `skill` - Technology name
- `frequency` - Usage count
- `source` - Skill source label (for example: `code`, `non-code`, `technical`, `soft`)

---

### 4. Get Top Skills

**What it does:** Returns most-used skills.

**URL:** `GET /api/skills/frequent`

**Parameters:**
- `limit` - Number of results (default: 10, max: 50)

**Example:** `GET /api/skills/frequent?limit=10`

**Response:**
```json
[
  {
    "skill": "Python",
    "frequency": 8,
    "source": "code"
  },
  {
    "skill": "JavaScript",
    "frequency": 5,
    "source": "code"
  }
]
```

---

### 5. Get Recent Skills

**What it does:** Lists recently used skills.

**URL:** `GET /api/skills/chronological`

**Parameters:**
- `limit` - Number of results (default: 10, max: 50)

**Example:** `GET /api/skills/chronological?limit=10`

**Response:**
```json
[
  {
    "skill": "React",
    "latest_use": "2024-02-10T15:30:00Z",
    "source": "code",
    "frequency": 3
  }
]
```

---

### 6. Get User Preferences

**What it does:** Returns user profile information.

**URL:** `GET /api/user-preferences`

**Response:**
```json
{
  "name": "Your Name",
  "email": "you@example.com",
  "github_user": "yourusername",
  "education": "Computer Science",
  "industry": "Software",
  "job_title": "Software Engineer",
  "education_details": "[{\"institution\":\"Your University\",\"degree\":\"BS Computer Science\",\"start_date\":\"2020-09-01\",\"end_date\":\"2024-05-01\",\"gpa\":3.8}]"
}
```

---

### 7. Search Schools

**What it does:** Searches educational institutions.

**URL:** `GET /api/institutions/search`

**Parameters:**
- `q` - Search term (optional, default: empty string)
- `limit` - Results count (default: 50, range: 1-200)
- `simple` - `true` for institution name list, `false` for full institution + program data

**Example:** `GET /api/institutions/search?q=california&limit=5&simple=true`

**Response:**
```json
{
  "status": "ok",
  "count": 1,
  "institutions": [
    {
      "name": "University of Toronto"
    }
  ]
}
```

---

### 8. List All Schools

**What it does:** Returns all schools in database.

**URL:** `GET /api/institutions/list`

**Response:**
```json
{
  "status": "ok",
  "count": 250,
  "institutions": ["University A", "University B"]
}
```

---

### 9. Get Portfolio Data

**What it does:** Returns complete portfolio with all project analytics and graphs.

**URL:** `GET /api/portfolio`

**Optional:** Filter specific projects: `/api/portfolio?project_ids=proj1,proj2`

**Response:**
```json
{
  "user": {
    "name": "Your Name",
    "email": "you@example.com",
    "links": [{"label": "GitHub", "url": "https://github.com/yourusername"}],
    "education": "Computer Science",
    "job_title": "Software Engineer",
    "education_details": "[{\"institution\":\"Your University\",\"degree\":\"BS Computer Science\",\"start_date\":\"2020-09-01\",\"end_date\":\"2024-05-01\",\"gpa\":3.8}]"
  },
  "overview": {
    "total_projects": 10,
    "avg_score": 0.82,
    "total_skills": 45,
    "total_languages": 8,
    "total_lines": 50000
  },
  "projects": [...],
  "skills_timeline": [{"skill": "Python", "first_used": "2024-01-15", "year": 2024}],
  "project_type_analysis": {
    "github": {"count": 6, "stats": {"avg_score": 0.87}},
    "local": {"count": 4, "stats": {"avg_score": 0.74}}
  },
  "graphs": {
    "language_distribution": {"Python": 5, "JavaScript": 3},
    "complexity_distribution": {...},
    "score_distribution": {...},
    "monthly_activity": {...},
    "top_skills": {...}
  },
  "metadata": {
    "generated_at": "2026-03-02T16:00:00",
    "total_projects": 10,
    "filtered": false,
    "project_ids": []
  }
}
```

**Notes:**
- `user.github_user` is used to build `user.links`, but is not returned as a separate field.
- `project_type_analysis.github.stats` and `project_type_analysis.local.stats` can include additional overview fields (for example `total_projects`, `total_skills`, `total_languages`, `total_lines`) plus type-specific fields like `avg_commits` (GitHub) or `avg_completeness` (Local).

---

### 10. View Portfolio Dashboard

**What it does:** Opens interactive HTML dashboard with charts and project cards.

**URL:** `GET /api/portfolio-dashboard`

**Response:** Full HTML page with interactive visualizations.

**Features:**
- Project cards with thumbnails
- Language distribution charts
- Complexity and score charts
- Project selection sidebar
- Statistics overview

---

### 11. Edit Portfolio Projects 

**What it does:** Updates one to many projects in a single request.

**URL:** `POST /api/portfolio/edit`

**Request:**
```json
{
  "edits": [
    {
      "project_signature": "sig1",
      "project_name": "New Name",
      "project_summary": "New summary",
      "created_at": "2024-01-15",
      "last_modified": "2024-06-10",
      "score_overridden_value": 0.8
    }
  ]
}
```

**Supported fields:** `project_name`, `project_summary`, `created_at`, `last_modified`, `score_overridden_value` (0.0-1.0)

**Response:**
```json
{
  "status": "ok",
  "projects_updated": ["sig1"],
  "count": 1
}
```

---

### 12. Upload Project Thumbnail

**What it does:** Uploads an image for a project.

**URL:** `POST /api/portfolio/project/thumbnail`

**Content-Type:** `multipart/form-data`

**Form Data:**
- `project_id` - Project identifier (required)
- `image` - Image file (required)

**Rules:**
- Image only (JPEG, JPG, PNG, GIF, SVG, WebP)
- Replaces existing thumbnail

**Response:**
```json
{
  "success": true,
  "thumbnail_path": "data/thumbnails/abc123.jpg",
  "thumbnail_url": "/api/portfolio/project/thumbnail/abc123"
}
```

**Errors:**
- `400` - Not an image file

---

### 13. Get Project Thumbnail

**What it does:** Returns the thumbnail image file.

**URL:** `GET /api/portfolio/project/thumbnail/{project_id}`

**Response:** Image file (JPG, PNG, etc.)

**Headers:** Includes no-cache headers to prevent caching.

**Error:** `404` if thumbnail doesn't exist.

---

### 14. Upload File Page

**What it does:** Shows HTML page for uploading project ZIP files.

**URL:** `GET /upload-file`

**Response:** HTML page with file upload form.

---

### 15. Upload Projects ZIP

**What it does:** Uploads a ZIP file and returns an `upload_id` for later analysis endpoints.

**URL:** `POST /upload-file`

**Content-Type:** `multipart/form-data`

**Form Data:**
- `file` - ZIP file with project folders

**Response:**
```json
{
  "status": "ok",
  "upload_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Error behavior:** If file is missing or not `.zip`, endpoint returns an HTML response with status `400`.

---

### 16. Update User Preferences

**What it does:** Updates your personal information and settings.

**URL:** `POST /api/user-preferences`

**Request:**
```json
{
  "name": "Your Name",
  "email": "you@example.com",
  "github_user": "yourusername",
  "education": "Computer Science",
  "industry": "Software",
  "job_title": "Senior Engineer",
  "education_details": [
    {
      "institution": "Your University",
      "degree": "BS Computer Science",
      "start_date": "2020-09-01",
      "end_date": "2024-05-01",
      "gpa": 3.8
    }
  ]
}
```

**Response:**
```json
{
  "status": "ok",
  "message": "User preferences saved successfully"
}
```

---

### 17. Get Resume (Master or Filtered)

**What it does:** Returns resume data (master or filtered by projects).

**URL:** `GET /resume`

**Parameters:**
- `project_ids` - Optional repeated query parameter (default: master resume)

**Example:** `GET /resume?project_ids=proj1&project_ids=proj2`

**Response:**
```json
{
  "name": "John User",
  "email": "john@example.com",
  "links": [
    {
      "label": "GitHub",
      "url": "https://github.com/johnuser"
    }
  ],
  "education": [
    {
      "school": "Test University",
      "degree": "BSc Computer Science",
      "dates": "Sep 2020 – May 2024",
      "gpa": "3.8"
    }
  ],
  "skills": {
    "Skills": ["Python", "FastAPI", "SQL"]
  },
  "projects": [
    {
      "title": "Project One",
      "dates": "Jan 2024 – Mar 2024",
      "skills": "Python, FastAPI, SQL",
      "bullets": ["Built REST API", "Improved test coverage"]
    }
  ]
}
```

**Error:** `500` if resume model generation fails.

---

### 18. Export Resume as PDF (GET)

**What it does:** Downloads resume as PDF file.

**URL:** `GET /resume/export/pdf`

**Parameters:**
- `project_ids` - Optional repeated query parameter
- `resume_id` - Optional saved resume ID

**Examples:**
- `GET /resume/export/pdf?project_ids=proj1&project_ids=proj2`
- `GET /resume/export/pdf?resume_id=2`

**Response:** PDF file download.

**Note:** Provide either `project_ids` or `resume_id`, not both.

**Errors:**
- `400` - Both `project_ids` and `resume_id` were provided
- `404` - `resume_id` not found
- `422` - LaTeX compilation failed
- `500` - Resume generation failed or `pdflatex` is unavailable
- `504` - LaTeX compilation timed out

---

### 19. Export Resume as LaTeX (GET)

**What it does:** Downloads resume as LaTeX (.tex) file.

**URL:** `GET /resume/export/tex`

**Parameters:**
- `project_ids` - Optional repeated query parameter
- `resume_id` - Optional saved resume ID

**Examples:**
- `GET /resume/export/tex?project_ids=proj1&project_ids=proj2`
- `GET /resume/export/tex?resume_id=2`

**Response:** .tex file download.

**Note:** LaTeX can be edited and compiled to PDF.
**Note:** Provide either `project_ids` or `resume_id`, not both.

**Errors:**
- `400` - Both `project_ids` and `resume_id` were provided
- `404` - `resume_id` not found
- `500` - Resume generation failed

---

### 20. Delete Resume

**What it does:** Deletes a saved resume (cannot delete Master Resume).

**URL:** `DELETE /resume/{resume_id}`

**Response:**
```json
{
  "success": true,
  "message": "Resume 2 deleted successfully",
  "deleted_resume_id": 2
}
```

**Errors:**
- `400` - Trying to delete Master Resume (`resume_id=1`)
- `404` - Resume doesn't exist
- `500` - Deletion failed unexpectedly


---

### 21. Create Tailored Resume

**What it does:** Creates a new resume with selected projects.

**URL:** `POST /resume`

**Request:**
```json
{
  "name": "Software Engineer Resume",
  "project_ids": ["proj1", "proj2", "proj3"]
}
```

**Response:**
```json
{
  "resume_id": 2,
  "message": "Resume created successfully"
}
```

**Errors:**
- `422` - Missing required fields (such as `name` or `project_ids`)
- `409` - Persistence error
- `500` - Resume service failed

---

### 22. Get Saved Resume

**What it does:** Loads a previously saved resume by ID.

**URL:** `GET /resume/{resume_id}`

**Response:**
```json
{
  "name": "John User",
  "email": "john@example.com",
  "links": [
    {
      "label": "GitHub",
      "url": "https://github.com/johnuser"
    }
  ],
  "education": [
    {
      "school": "Test University",
      "degree": "BSc Computer Science",
      "dates": "Sep 2020 – May 2024",
      "gpa": "3.8"
    }
  ],
  "skills": {
    "Skills": ["Python", "FastAPI", "SQL"]
  },
  "projects": [
    {
      "project_id": "proj1",
      "title": "Project One",
      "dates": "Jan 2024 – Mar 2024",
      "skills": ["Python", "FastAPI", "SQL"],
      "bullets": ["Built REST API", "Improved test coverage"]
    }
  ]
}
```

**Error:** `404` if resume not found.
**Error:** `500` if loading the saved resume fails.

---

### 23. List All Resumes

**What it does:** Returns all saved resumes for sidebar display.

**URL:** `GET /resume_names`

**Response:**
```json
{
  "resumes": [
    {"id": 1, "name": "Master Resume", "is_master": true},
    {"id": 2, "name": "Software Engineer Resume", "is_master": false}
  ]
}
```

**Error:** `500` if listing resumes fails.

---

### 24. Save Edited Resume

**What it does:** Saves edits to an existing resume.

**URL:** `POST /resume/{id}/edit`

**Request:**
```json
{
  "skills": ["Python", "FastAPI", "SQL"],
  "projects": [
    {
      "project_id": "proj1",
      "project_name": "Project One (Edited)",
      "start_date": "2024-01-01",
      "end_date": "2024-03-31",
      "skills": ["Python", "FastAPI"],
      "bullets": ["Led API design", "Added integration tests"],
      "display_order": 1
    }
  ]
}
```

**Response:**
```json
{
  "status": "ok",
  "message": "Resume edits saved"
}
```

**Errors:**
- `404` - Resume not found
- `409` - Persistence error
- `500` - Resume service failed

---

### 25. Get Project by Signature

**What it does:** Returns detailed information for a specific project.

**URL:** `GET /api/projects/{signature}`

**Response:**
```json
{
  "id": "abc123",
  "name": "My Project",
  "score": 0.85,
  "score_original": 0.85,
  "score_overridden": false,
  "score_overridden_value": null,
  "score_override_exclusions": [],
  "skills": ["Python", "FastAPI", "Docker"]
}
```

**Error:** `404` if project not found.

---

### 26. Delete Project

**What it does:** Permanently deletes all stored insights for a project identified by its signature.

**URL:** `DELETE /api/projects/{signature}`

**URL Parameters:**
- `signature` — The unique project signature (visible on the project card or via `GET /api/projects`)

**Response:**
```json
{
  "status": "ok",
  "message": "Project 'My Project' deleted successfully",
  "project_signature": "abc123"
}
```

**Notes:**
- Deletion is permanent and cannot be undone.
- All associated data (skills, scores, resume bullets) linked to the project is removed via cascading database constraints.

---

### 27. Get Project Score Breakdown

**What it does:** Returns the score components and weighting details for one project.

**URL:** `GET /api/projects/{signature}/score-breakdown`

**Response:**
```json
{
  "project_signature": "abc123",
  "name": "My Project",
  "score": 0.82,
  "score_original": 0.82,
  "score_overridden": false,
  "score_overridden_value": null,
  "exclude_metrics": [],
  "breakdown": {
    "code": {
      "type": "git",
      "metrics": {
        "total_commits": {
          "raw": 30,
          "cap": 50,
          "normalized": 0.6,
          "weight": 0.3,
          "contribution": 0.18
        }
      },
      "subtotal": 0.76
    },
    "non_code": {
      "metrics": {
        "completeness_score": {
          "raw": 0.9,
          "cap": 1.0,
          "normalized": 0.9,
          "weight": 1.0,
          "contribution": 0.9
        }
      },
      "subtotal": 0.9
    },
    "blend": {
      "code_percentage": 0.8,
      "non_code_percentage": 0.2,
      "code_lines": 2500,
      "doc_word_count": 700,
      "doc_line_equiv": 100.0,
      "words_per_code_line": 7.0
    },
    "final_score": 0.82
  }
}
```

**Error:** `404` if project not found.

---

### 28. Preview Project Override

**What it does:** Previews score override impact without saving changes.

**URL:** `POST /api/projects/{signature}/score-override/preview`

**Request:**
```json
{
  "exclude_metrics": ["total_lines", "test_files_changed"]
}
```

**Response:**
```json
{
  "project_signature": "abc123",
  "name": "My Project",
  "exclude_metrics": ["total_lines"],
  "current_score": 0.82,
  "score_original": 0.82,
  "preview_score": 0.88,
  "breakdown": {
    "code": {
      "type": "git",
      "metrics": {},
      "subtotal": 0.8
    },
    "non_code": {
      "metrics": {},
      "subtotal": 0.9
    },
    "blend": {
      "code_percentage": 0.8,
      "non_code_percentage": 0.2,
      "code_lines": 2500,
      "doc_word_count": 700,
      "doc_line_equiv": 100.0,
      "words_per_code_line": 7.0
    },
    "final_score": 0.88
  }
}
```

---

### 29. Apply Project Override

**What it does:** Applies and persists a score override for the selected project.

**URL:** `POST /api/projects/{signature}/score-override`

**Request:**
```json
{
  "exclude_metrics": ["total_lines", "test_files_changed"]
}
```

**Response:**
```json
{
  "project_signature": "abc123",
  "name": "My Project",
  "exclude_metrics": ["total_lines"],
  "score": 0.88,
  "score_original": 0.82,
  "score_overridden": true,
  "score_overridden_value": 0.88,
  "breakdown": {
    "code": {
      "type": "git",
      "metrics": {},
      "subtotal": 0.8
    },
    "non_code": {
      "metrics": {},
      "subtotal": 0.9
    },
    "blend": {
      "code_percentage": 0.8,
      "non_code_percentage": 0.2,
      "code_lines": 2500,
      "doc_word_count": 700,
      "doc_line_equiv": 100.0,
      "words_per_code_line": 7.0
    },
    "final_score": 0.88
  }
}
```

---

### 30. Clear Project Override

**What it does:** Removes previously applied score overrides and restores default scoring behavior.

**URL:** `POST /api/projects/{signature}/score-override/clear`

**Response:**
```json
{
  "project_signature": "abc123",
  "name": "My Project",
  "exclude_metrics": [],
  "score": 0.82,
  "score_original": 0.82,
  "score_overridden": false,
  "score_overridden_value": null
}
```

---

### 31. Record Privacy Consent

**What it does:** Records user consent decision for privacy.

**URL:** `POST /api/privacy-consent`

**Request:**
```json
{
  "accepted": true
}
```

**Response:**
```json
{
  "status": "ok",
  "message": "Consent recorded successfully"
}
```

---

### 32. Get Privacy Consent Status

**What it does:** Checks if user has given consent.

**URL:** `GET /api/privacy-consent`

**Response:**
```json
{
  "has_consent": true,
  "timestamp": "2024-01-15T10:00:00Z"
}
```

---

### 33. Revoke Privacy Consent

**What it does:** Revokes user consent.

**URL:** `DELETE /api/privacy-consent`

**Response:**
```json
{
  "status": "ok",
  "message": "Consent revoked successfully"
}
```

---

### 34. Get Privacy Consent Text

**What it does:** Returns privacy consent text for display.

**URL:** `GET /api/privacy-consent/text`

**Response:**
```json
{
  "consent_message": "...",
  "detailed_info": "...",
  "granted_message": "...",
  "declined_message": "...",
  "already_provided_message": "..."
}
```

---

### 35. Resolve Upload Status

**What it does:** Returns status and path if uploaded ZIP exists.

**URL:** `GET /api/resolve-upload/{upload_id}`

**Response:**
```json
{
  "status": "pending"
}
```

**Response (found):**
```json
{
  "status": "ok",
  "path": "app/uploads/abc123.zip"
}
```

---

### 36. List Upload Projects

**What it does:** Lists projects discovered inside an uploaded ZIP before running analysis.

**URL:** `GET /api/analysis/uploads/{upload_id}/projects`

**Response:**
```json
{
  "status": "ok",
  "upload_id": "upload_abc123",
  "total_projects": 3,
  "projects": [
    {"name": "project-a", "path": "/tmp/extracted/project-a"}
  ]
}
```

---

### 37. Run Analysis For Upload

**What it does:** Runs analysis across projects for a previously uploaded ZIP.

**URL:** `POST /api/analysis/run`

**Request:**
```json
{
  "upload_id": "upload_abc123",
  "default_analysis_type": "local",
  "project_analysis_types": {},
  "similarity_action": "create_new",
  "cleanup_zip": false,
  "cleanup_extracted": false
}
```

**Response:**
```json
{
  "status": "ok",
  "upload_id": "upload_abc123",
  "total_projects": 3,
  "analyzed_projects": 3,
  "skipped_projects": 0,
  "failed_projects": 0,
  "results": [
    {
      "project_name": "project-a",
      "project_path": "/tmp/extracted/project-a",
      "project_signature": "abc123",
      "requested_analysis_type": "local",
      "effective_analysis_type": "local",
      "status": "analyzed",
      "reason": null
    }
  ],
  "cleanup": null
}
```

---

### 38. Get Chronological Projects

**What it does:** Lists all projects with chronological date fields for review.

**URL:** `GET /api/chronological/projects`

**Response:** Array of projects with `created_at` and `last_modified`.

---

### 39. Get Chronological Project

**What it does:** Returns chronological details for one project by signature.

**URL:** `GET /api/chronological/projects/{signature}`

**Response:** Project object with date information.

**Error:** `404` if project not found.

---

### 40. Update Project Dates

**What it does:** Updates `created_at` and `last_modified` for a project.

**URL:** `PATCH /api/chronological/projects/{signature}/dates`

**Request:**
```json
{
  "created_at": "2024-01-15",
  "last_modified": "2024-06-10"
}
```

**Response:** Updated project object.

---

### 41. Get Project Chronological Skills

**What it does:** Lists a project's skills ordered chronologically.

**URL:** `GET /api/chronological/projects/{signature}/skills`

**Response:** Array of skills with `id`, `skill`, `source`, and `date`.

---

### 42. Add Skill To Project

**What it does:** Adds a dated skill entry to a project.

**URL:** `POST /api/chronological/projects/{signature}/skills`

**Status:** `201 Created`

**Request:**
```json
{
  "skill": "FastAPI",
  "source": "code",
  "date": "2024-02-01"
}
```

**Response:**
```json
{
  "message": "Skill added",
  "skill": "FastAPI",
  "source": "code",
  "date": "2024-02-01"
}
```

---

### 43. Update Skill Date

**What it does:** Updates the date for a specific skill entry.

**URL:** `PATCH /api/chronological/skills/{skill_id}/date`

**Request:**
```json
{
  "date": "2024-03-01"
}
```

**Response:**
```json
{
  "id": 12,
  "skill": "FastAPI",
  "source": "code",
  "date": "2024-03-01"
}
```

---

### 44. Update Skill Name

**What it does:** Renames an existing skill entry.

**URL:** `PATCH /api/chronological/skills/{skill_id}/name`

**Request:**
```json
{
  "skill": "Python"
}
```

**Response:**
```json
{
  "id": 12,
  "skill": "Python",
  "source": "code",
  "date": "2024-02-01"
}
```

---

### 45. Delete Skill

**What it does:** Deletes a skill entry by ID.

**URL:** `DELETE /api/chronological/skills/{skill_id}`

**Response:** `204 No Content`

---

### 46. Add Projects To Resume

**What it does:** Adds selected projects to an existing saved resume.

**URL:** `POST /resume/{resume_id}/projects`

**Request:**
```json
{
  "project_ids": ["proj1", "proj2"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Projects added to resume 2",
  "resume_id": 2
}
```

**Errors:**
- `400` - Cannot add projects to Master Resume (`resume_id=1`)
- `404` - Resume not found
- `409` - Invalid project IDs or persistence conflict
- `500` - Resume service failed

---

### 47. Delete Project From Resume

**What it does:** Removes one project association from a resume.

**URL:** `DELETE /resume/{resume_id}/project/{project_id}`

**Response:**
```json
{
  "success": true,
  "message": "Project proj1 removed from resume 2",
  "resume_id": 2,
  "project_id": "proj1"
}
```

**Errors:**
- `404` - Resume not found
- `500` - Resume service failed

---

### 48. Portfolio JavaScript

**What it does:** Serves the JavaScript bundle for the portfolio dashboard page.

**URL:** `GET /api/static/portfolio.js`

**Response:** JavaScript file (`application/javascript`).

---

### 49. Read Root

**What it does:** Returns a basic welcome payload for the API root.

**URL:** `GET /`

**Response:**
```json
{
  "message": "Welcome to the Project Insights!!"
}
```

### Using JavaScript

```javascript
const API_BASE = 'http://localhost:8000';

// Get all projects
fetch(`${API_BASE}/api/projects`)
  .then(res => res.json())
  .then(data => console.log(data));

// Get portfolio data
fetch(`${API_BASE}/api/portfolio`)
  .then(res => res.json())
  .then(data => console.log(data));

// Upload thumbnail
const formData = new FormData();
formData.append('project_id', 'abc123');
formData.append('image', fileInput.files[0]);

fetch(`${API_BASE}/api/portfolio/project/thumbnail`, {
  method: 'POST',
  body: formData
})
  .then(res => res.json())
  .then(data => console.log('Uploaded:', data));

// Update user preferences
fetch(`${API_BASE}/api/user-preferences`, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    name: 'John Doe',
    email: 'john@example.com',
    github_user: 'johndoe',
    education: 'Computer Science',
    industry: 'Software',
    job_title: 'Software Engineer'
  })
})
  .then(res => res.json())
  .then(data => console.log(data));

// Delete resume
fetch(`${API_BASE}/resume/123`, {
  method: 'DELETE'
})
  .then(res => res.json())
  .then(data => console.log('Deleted:', data));
```

---

## Quick Reference

**Data Retrieval:**
- Projects: `/api/projects`
- Single Project: `GET /api/projects/{signature}`
- Score Breakdown: `GET /api/projects/{signature}/score-breakdown`
- Skills: `/api/skills`
- Frequent Skills: `GET /api/skills/frequent`
- Chronological Skills: `GET /api/skills/chronological`
- Portfolio: `/api/portfolio`
- Preferences: `/api/user-preferences`
- Root: `GET /`

**Project Management:**
- Delete Project: `DELETE /api/projects/{signature}`
- Preview Override: `POST /api/projects/{signature}/score-override/preview`
- Apply Override: `POST /api/projects/{signature}/score-override`
- Clear Override: `POST /api/projects/{signature}/score-override/clear`

**Portfolio & Thumbnails:**
- Dashboard: `/api/portfolio-dashboard`
- Dashboard JS: `GET /api/static/portfolio.js`
- Upload Thumbnail: `POST /api/portfolio/project/thumbnail`
- Get Thumbnail: `/api/portfolio/project/thumbnail/{project_id}`
- Edit Project: `POST /api/portfolio/edit`

**File Management:**
- Upload Page: `/upload-file`
- Upload ZIP: `POST /upload-file`
- Resolve Upload: `GET /api/resolve-upload/{upload_id}`
- List Upload Projects: `GET /api/analysis/uploads/{upload_id}/projects`
- Run Analysis: `POST /api/analysis/run`

**Resume:**
- Create: `POST /resume`
- Get: `GET /resume`
- Get Saved: `GET /resume/{resume_id}`
- List Saved: `GET /resume_names`
- Save Edits: `POST /resume/{id}/edit`
- Add Projects: `POST /resume/{resume_id}/projects`
- Remove Project: `DELETE /resume/{resume_id}/project/{project_id}`
- Export PDF: `GET /resume/export/pdf`
- Export LaTeX: `GET /resume/export/tex`
- Delete: `DELETE /resume/{resume_id}`

**Privacy & Consent:**
- Get Status: `GET /api/privacy-consent`
- Record: `POST /api/privacy-consent`
- Revoke: `DELETE /api/privacy-consent`
- Get Text: `GET /api/privacy-consent/text`

**Chronological Manager:**
- List Projects: `GET /api/chronological/projects`
- Get Project: `GET /api/chronological/projects/{signature}`
- Update Dates: `PATCH /api/chronological/projects/{signature}/dates`
- Get Project Skills: `GET /api/chronological/projects/{signature}/skills`
- Add Project Skill: `POST /api/chronological/projects/{signature}/skills`
- Update Skill Date: `PATCH /api/chronological/skills/{skill_id}/date`
- Update Skill Name: `PATCH /api/chronological/skills/{skill_id}/name`
- Delete Skill: `DELETE /api/chronological/skills/{skill_id}`


## Error Handling

**404 Not Found:**
```json
{"detail": "Project not found"}
```

**400 Bad Request:**
```json
{"detail": "Invalid parameters"}
```

**500 Server Error:**
```json
{"detail": "Internal server error"}
```

---
**Last Updated:** March 2, 2026  
**Total Endpoints Documented:** 49  
**Questions?** Contact development team
