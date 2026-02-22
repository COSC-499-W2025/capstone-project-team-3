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
| `404` | ❌ Not found |
| `400` | ❌ Bad request |
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
    "skills": ["Python", "FastAPI", "Docker"],
    "date_added": "2024-01-15T10:00:00Z"
  }
]
```

**Fields:**
- `id` - Unique identifier
- `name` - Project name
- `score` - Quality score (0-1)
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
    "source": "analyzed"
  }
]
```

**Fields:**
- `skill` - Technology name
- `frequency` - Usage count
- `source` - `analyzed` or `manual`

---

### 4. Get Top Skills

**What it does:** Returns most-used skills.

**URL:** `GET /api/skills/frequent?limit=10`

**Parameters:**
- `limit` - Number of results (default: 10, max: 50)

**Response:**
```json
[
  {
    "skill": "Python",
    "frequency": 8,
    "source": "code_analysis"
  },
  {
    "skill": "JavaScript",
    "frequency": 5,
    "source": "code_analysis"
  }
]
```

---

### 5. Get Recent Skills

**What it does:** Lists recently used skills.

**URL:** `GET /api/skills/chronological?limit=10`

**Response:**
```json
[
  {
    "skill": "React",
    "latest_use": "2024-02-10T15:30:00Z",
    "source": "analyzed",
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
  "phone": "+1-555-0123",
  "location": "San Francisco, CA",
  "job_title": "Software Engineer",
  "education": {
    "institution": "Your University",
    "degree": "BS Computer Science",
    "graduation_year": 2020
  }
}
```

---

### 7. Search Schools

**What it does:** Searches educational institutions.

**URL:** `GET /api/institutions/search?query=california&limit=5`

**Parameters:**
- `query` - Search term (required)
- `limit` - Results count (default: 10)

**Response:**
```json
[
  {
    "name": "University of California, Berkeley",
    "location": "Berkeley, CA",
    "type": "University"
  }
]
```

---

### 8. List All Schools

**What it does:** Returns all schools in database.

**URL:** `GET /api/institutions/list?limit=100`

**Parameters:**
- `limit` - Results count (default: 100)
- `offset` - Pagination offset

**Response:** Array of schools with name and location.

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
    "email": "you@example.com"
  },
  "overview": {
    "total_projects": 10,
    "avg_score": 0.82,
    "total_skills": 45,
    "total_languages": 8,
    "total_lines": 50000
  },
  "projects": [...],
  "graphs": {
    "language_distribution": {"Python": 5, "JavaScript": 3},
    "complexity_distribution": {...},
    "score_distribution": {...},
    "monthly_activity": {...},
    "top_skills": {...}
  }
}
```

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

### 11. Edit Portfolio Projects (Batch)

**What it does:** Updates multiple projects in a single request.

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
      "rank": 0.8
    }
  ]
}
```

**Supported fields:** `project_name`, `project_summary`, `created_at`, `last_modified`, `rank` (0.0-1.0)

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
- Image only (JPG, PNG, GIF, WebP, BMP)
- Max size: 5MB
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
- `404` - Project not found

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

**What it does:** Uploads and extracts ZIP file containing projects for analysis.

**URL:** `POST /upload-file`

**Content-Type:** `multipart/form-data`

**Form Data:**
- `file` - ZIP file with project folders

**Response:**
```json
{
  "status": "ok",
  "upload_id": "upload_abc123",
  "message": "File uploaded successfully",
  "projects_count": 3
}
```

**What happens:** System extracts ZIP and analyzes each project.

---

### 16. Update User Preferences

**What it does:** Updates your personal information and settings.

**URL:** `POST /api/user-preferences`

**Request:**
```json
{
  "name": "Your Name",
  "email": "you@example.com",
  "job_title": "Senior Engineer",
  "education": {
    "institution": "Your University",
    "degree": "BS Computer Science"
  }
}
```

**Response:**
```json
{
  "status": "ok",
  "message": "Preferences updated"
}
```

---

### 17. Get Resume (Master or Filtered)

**What it does:** Returns resume data (master or filtered by projects).

**URL:** `GET /resume?project_ids=proj1,proj2`

**Parameters:**
- `project_ids` - Optional comma-separated list (default: master resume)

**Response:**
```json
{
  "user_info": {...},
  "projects": [...],
  "skills": [...]
}
```

---

### 18. Export Resume as PDF (GET)

**What it does:** Downloads resume as PDF file.

**URL:** `GET /resume/export/pdf?project_ids=proj1,proj2`

**Parameters:**
- `project_ids` - Optional comma-separated list

**Response:** PDF file download.

**Alternative:** `POST /resume/export/pdf` with body `{"project_ids": [...]}`

---

### 19. Export Resume as LaTeX (GET)

**What it does:** Downloads resume as LaTeX (.tex) file.

**URL:** `GET /resume/export/tex?project_ids=proj1,proj2`

**Parameters:**
- `project_ids` - Optional comma-separated list

**Response:** .tex file download.

**Alternative:** `POST /resume/export/tex` with body `{"project_ids": [...]}`

**Note:** LaTeX can be edited and compiled to PDF.

---

### 20. Delete Resume

**What it does:** Deletes a saved resume (cannot delete Master Resume).

**URL:** `DELETE /resume/{resume_id}`

**Response:**
```json
{
  "status": "ok",
  "message": "Resume deleted successfully"
}
```

**Error:** `404` if resume doesn't exist.


---

### 21. Create Tailored Resume

**What it does:** Creates a new resume with selected projects.

**URL:** `POST /resume`

**Request:**
```json
{
  "project_ids": ["proj1", "proj2", "proj3"]
}
```

**Response:**
```json
{
  "resume_id": "resume_456",
  "message": "Resume created successfully"
}
```

**Error:** `400` if no projects selected.

---

### 22. Get Saved Resume

**What it does:** Loads a previously saved resume by ID.

**URL:** `GET /resume/{resume_id}`

**Response:**
```json
{
  "resume_id": 123,
  "projects": [...],
  "user_info": {...}
}
```

**Error:** `404` if resume not found.

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

---

### 24. Save Edited Resume

**What it does:** Saves edits to an existing resume.

**URL:** `POST /resume/{id}/edit`

**Request:**
```json
{
  "project_overrides": {...},
  "custom_sections": {...}
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

---

### 25. Get Project by Signature

**What it does:** Returns detailed information for a specific project.

**URL:** `GET /api/projects/{signature}`

**Response:**
```json
{
  "project_signature": "abc123",
  "name": "My Project",
  "summary": "Project description",
  "skills": [...],
  "languages": [...],
  "created_at": "2024-01-01",
  "score": 0.85
}
```

**Error:** `404` if project not found.

---

### 26. Record Privacy Consent

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

### 27. Get Privacy Consent Status

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

### 28. Revoke Privacy Consent

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

### 29. Get Privacy Consent Text

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

### 30. Resolve Upload Status

**What it does:** Returns status and path if uploaded ZIP exists.

**URL:** `GET /api/resolve-upload/{upload_id}`

**Response (found):**
```json
{
  "status": "ok",
  "path": "app/uploads/abc123.zip"
}
```

**Response (pending):**
```json
{
  "status": "pending"
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
    job_title: 'Software Engineer'
  })
})
  .then(res => res.json())
  .then(data => console.log(data));

// Delete resume
fetch(`${API_BASE}/api/resume/123`, {
  method: 'DELETE'
})
  .then(res => res.json())
  .then(data => console.log('Deleted:', data));
```

---

## Quick Reference

**Data Retrieval:**
- Projects: `/api/projects`
- Skills: `/api/skills`
- Portfolio: `/api/portfolio`
- Preferences: `/api/user-preferences`

**Portfolio & Thumbnails:**
- Dashboard: `/api/portfolio-dashboard`
- Upload Thumbnail: `POST /api/portfolio/project/thumbnail`
- Get Thumbnail: `/api/portfolio/project/thumbnail/{id}`
- Edit Project: `POST /api/portfolio/edit`

**File Management:**
- Upload Page: `/upload-file`
- Upload ZIP: `POST /upload-file`

**Resume:**
- Preview: `POST /api/resume/preview`
- Export PDF: `/api/resume/export/pdf`
- Export LaTeX: `/api/resume/export/tex`
- Delete: `DELETE /api/resume/{id}`

**Privacy & Consent:**
- Get Status: `GET /api/privacy-consent`
- Record: `POST /api/privacy-consent`
- Revoke: `DELETE /api/privacy-consent`
- Get Text: `GET /api/privacy-consent/text`


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
**Last Updated:** February 20, 2026  
**Total Endpoints Documented:** 30  
**Questions?** Contact development team
