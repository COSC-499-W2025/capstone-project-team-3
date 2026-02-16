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

### 3. Get Specific Project

**What it does:** Returns details for one project.

**URL:** `GET /api/projects/{project_id}`

**Response:**
```json
{
  "id": "abc123",
  "name": "My Project",
  "score": 0.85,
  "skills": ["Python", "FastAPI", "Docker"]
}
```

---

### 4. Get All Skills

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

### 5. Get Top Skills

**What it does:** Returns most-used skills.

**URL:** `GET /api/skills/frequent?limit=10`

**Parameters:**
- `limit` - Number of results (default: 10, max: 50)

**Response:** Same as "Get All Skills", sorted by frequency.

---

### 6. Get Recent Skills

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

### 7. Get User Preferences

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

### 8. Search Schools

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

### 9. List All Schools

**What it does:** Returns all schools in database.

**URL:** `GET /api/institutions/list?limit=100`

**Parameters:**
- `limit` - Results count (default: 100)
- `offset` - Pagination offset

**Response:** Array of schools with name and location.

---

### 10. Get Portfolio Data

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

### 11. View Portfolio Dashboard

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

### 12. Edit Portfolio Project

**What it does:** Updates project information (rank, summary, dates).

**URL:** `POST /api/portfolio/edit`

**Request:**
```json
{
  "project_id": "abc123",
  "field": "summary",
  "value": "Updated description"
}
```

**Supported fields:** `rank`, `summary`, `dates`

**Response:**
```json
{
  "status": "ok",
  "message": "Project updated"
}
```

---

### 13. Upload Project Thumbnail

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

### 14. Get Project Thumbnail

**What it does:** Returns the thumbnail image file.

**URL:** `GET /api/portfolio/project/thumbnail/{project_id}`

**Response:** Image file (JPG, PNG, etc.)

**Headers:** Includes no-cache headers to prevent caching.

**Error:** `404` if thumbnail doesn't exist.

---

### 15. Upload File Page

**What it does:** Shows HTML page for uploading project ZIP files.

**URL:** `GET /upload-file`

**Response:** HTML page with file upload form.

---

### 16. Upload Projects ZIP

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

### 17. Update User Preferences

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

### 18. Preview Resume

**What it does:** Generates HTML preview of resume.

**URL:** `POST /api/resume/preview`

**Request:**
```json
{
  "resume_id": "resume_123"
}
```

**Response:** HTML page showing resume layout.

---

### 19. Export Resume as PDF

**What it does:** Downloads resume as PDF file.

**URL:** `GET /api/resume/export/pdf?resume_id=resume_123`

**Response:** PDF file download.

---

### 20. Export Resume as LaTeX

**What it does:** Downloads resume as LaTeX (.tex) file.

**URL:** `GET /api/resume/export/tex?resume_id=resume_123`

**Response:** .tex file download.

**Note:** LaTeX can be edited and compiled to PDF.

---

### 21. Delete Resume

**What it does:** Deletes a saved resume.

**URL:** `DELETE /api/resume/{resume_id}`

**Response:**
```json
{
  "status": "ok",
  "message": "Resume deleted successfully"
}
```

**Error:** `404` if resume doesn't exist.


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
**Last Updated:** February 16, 2026  
**Total Endpoints Documented:** 21  
**Questions?** Contact development team
