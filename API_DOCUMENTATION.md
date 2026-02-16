# Project Insights API Documentation

**Version:** 1.0  
**Server:** `http://localhost:8000` (development)

---

## Overview

This document explains the core data retrieval endpoints in Project Insights. These endpoints let you read information about projects, skills, and preferences.

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

## Quick Reference

**Key Endpoints:**
- Projects: `/api/projects`
- Skills: `/api/skills`
- Top Skills: `/api/skills/frequent`
- Health: `/health`

---

## Testing Examples

### Using curl

```bash
# Get all projects
curl http://localhost:8000/api/projects

# Get specific project
curl http://localhost:8000/api/projects/abc123

# Get all skills
curl http://localhost:8000/api/skills

# Get top skills
curl http://localhost:8000/api/skills/frequent?limit=10

# Search schools
curl "http://localhost:8000/api/institutions/search?query=stanford"
```

### Using JavaScript

```javascript
const API_BASE = 'http://localhost:8000';

// Get all projects
fetch(`${API_BASE}/api/projects`)
  .then(res => res.json())
  .then(data => console.log(data));

// Get top skills
fetch(`${API_BASE}/api/skills/frequent?limit=10`)
  .then(res => res.json())
  .then(data => console.log(data));

// Search schools
fetch(`${API_BASE}/api/institutions/search?query=stanford`)
  .then(res => res.json())
  .then(data => console.log(data));
```

---

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

## Common Questions

**Q: How do I get my project ID?**  
A: Call `/api/projects` and use the `id` field.

**Q: Can I filter projects by skill?**  
A: Not currently. Retrieve all and filter client-side.

**Q: What's the difference between "analyzed" and "manual" skills?**  
A: `analyzed` = auto-detected from code, `manual` = user-added.

**Q: How often is data updated?**  
A: When you upload and analyze new projects.

---

## Best Practices

**Projects:**
- Check health endpoint first
- Get all projects to see availability
- Use specific endpoint for details

**Skills:**
- Use `/api/skills/frequent` for top skills
- Use `/api/skills/chronological` for recent
- Use `/api/skills` for complete list

**Schools:**
- Use 3+ characters in search
- Limit results to 5-10
- Use dropdown/autocomplete UI

---

## Additional Resources

- Code: `app/api/routes/`
- Tests: `tests/api/`
- README for setup

---

**Last Updated:** February 14, 2026  
**Questions?** Contact development team
