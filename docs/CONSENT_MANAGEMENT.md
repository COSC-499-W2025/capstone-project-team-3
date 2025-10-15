# Consent Management System

This document describes the comprehensive consent management system implemented for the Productivity Analyzer application.

## Overview

The consent management system provides a complete solution for handling user consent in compliance with privacy regulations. It includes:

- Database schema for consent storage and history tracking
- RESTful API endpoints for consent operations
- Optional middleware for enforcing consent requirements
- Comprehensive privacy policy
- Version tracking for policy updates

## Architecture

### Database Layer (`app/data/db.py`)

The database includes two main tables:
- `USER`: Stores user information
- `CONSENT`: Stores consent records with version tracking and timestamps

Key functions:
- `init_db()`: Initialize database and create tables
- `create_consent()`: Create new consent record
- `get_consent_status()`: Get latest consent status for a user
- `update_consent()`: Update consent (creates new record for history)
- `get_consent_history()`: Get all consent records for a user

### Models (`app/models.py`)

Pydantic models for request/response validation:
- `ConsentRequest`: Request model for consent actions
- `ConsentResponse`: Response model for consent status
- `ConsentHistoryItem`: Model for consent history entries
- `PrivacyPolicyResponse`: Response model for privacy policy

### Service Layer (`app/consent_service.py`)

Business logic for consent management:
- `record_consent()`: Record a consent decision
- `check_consent()`: Check if user has given consent
- `revoke_consent()`: Revoke user consent
- `get_privacy_policy()`: Get current privacy policy
- `requires_reconsent()`: Check if user needs to re-consent

### API Routes (`app/consent_routes.py`)

RESTful endpoints under `/consent`:

#### GET `/consent/status/{user_id}`
Get the current consent status for a user.

**Response:**
```json
{
  "user_id": 1,
  "consent_given": true,
  "policy_version": "1.0.0",
  "timestamp": "2025-10-15 20:00:00",
  "has_consent": true
}
```

#### POST `/consent/accept`
Record that a user has accepted consent.

**Request:**
```json
{
  "user_id": 1,
  "consent_given": true,
  "policy_version": "1.0.0"
}
```

#### POST `/consent/decline`
Record that a user has declined consent.

**Request:**
```json
{
  "user_id": 1,
  "consent_given": false,
  "policy_version": "1.0.0"
}
```

#### POST `/consent/revoke/{user_id}`
Revoke consent for a user.

#### GET `/consent/history/{user_id}`
Get the complete consent history for a user.

#### GET `/consent/privacy-policy`
Get the current privacy policy with version information.

#### GET `/consent/requires-consent/{user_id}`
Check if a user needs to provide or update consent.

### Middleware (`app/consent_middleware.py`)

Optional middleware for enforcing consent requirements on protected endpoints.

**Features:**
- Automatically checks consent before allowing access to protected routes
- Exempts certain paths (root, docs, consent endpoints)
- Supports user identification via `X-User-ID` header or `user_id` query parameter
- Returns clear error messages when consent is required

**To enable middleware**, uncomment this line in `app/main.py`:
```python
app.add_middleware(ConsentMiddleware)
```

## Usage Examples

### Starting the Application

```bash
# Using Python module
python -m app.main

# Using Docker
docker compose up --build
```

### API Usage Examples

```bash
# Get privacy policy
curl http://localhost:8000/consent/privacy-policy

# Accept consent
curl -X POST http://localhost:8000/consent/accept \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "consent_given": true, "policy_version": "1.0.0"}'

# Check consent status
curl http://localhost:8000/consent/status/1

# Check if consent is required
curl http://localhost:8000/consent/requires-consent/1

# Revoke consent
curl -X POST http://localhost:8000/consent/revoke/1

# Get consent history
curl http://localhost:8000/consent/history/1

# Decline consent
curl -X POST http://localhost:8000/consent/decline \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "consent_given": false, "policy_version": "1.0.0"}'
```

## Privacy Policy

The system includes a comprehensive privacy policy covering:
- Information collection practices
- Data usage and storage
- User rights and consent options
- Tiered consent options (Basic/Enhanced Analysis)
- Contact information
- Policy update procedures

Current version: **1.0.0**

## Testing

The implementation includes comprehensive test coverage:

- **Database Tests** (`tests/test_consent_db.py`): 8 tests
- **Service Tests** (`tests/test_consent_service.py`): 13 tests
- **API Tests** (`tests/test_consent_api.py`): 14 tests
- **Middleware Tests** (`tests/test_consent_middleware.py`): 10 tests

Run all tests:
```bash
pytest -v
```

Run specific test file:
```bash
pytest tests/test_consent_api.py -v
```

## Features Implemented

### ✅ Determine Content on Consent Form
- Comprehensive privacy policy with clear permissions
- Tiered consent options (basic/enhanced analysis)
- Data usage and retention statements

### ✅ Implement Consent Screen UI (Backend Ready)
- API endpoints ready for frontend integration
- Privacy policy endpoint for display
- Accept/decline actions supported

### ✅ Store Consent Status Locally
- SQLite database with consent records
- Timestamp and version tracking
- Complete consent history maintained

### ✅ Enforce Access Restriction Until Consent is Given
- Optional middleware for enforcement
- Routing guards implemented
- Graceful degradation supported

### ✅ Handle Consent Decline & Permission Denial
- Decline workflow implemented
- Retry mechanisms supported
- Re-consent prompts for version changes

### ✅ Test Cases (Positive/Negative)
- 45 comprehensive tests
- Edge cases covered (revocation, version changes)
- All tests passing

## Security

- No SQL injection vulnerabilities (parameterized queries)
- Input validation using Pydantic models
- Proper error handling
- CodeQL security scan: **0 alerts**

## Future Enhancements

Potential improvements for future iterations:
1. User authentication integration
2. Frontend consent modal/overlay UI
3. Email notifications for policy changes
4. Consent analytics and reporting
5. Multi-language support for privacy policy
6. Consent export functionality
7. Fine-grained consent controls (per feature)

## API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI Schema: http://localhost:8000/openapi.json

## Database Schema

```sql
CREATE TABLE USER (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE CONSENT (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    policy_version TEXT,
    consent_given INTEGER DEFAULT 0,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id)
);
```

## Configuration

The system uses these configurable parameters:
- `CURRENT_POLICY_VERSION`: Current privacy policy version (in `consent_service.py`)
- `PRIVACY_POLICY_CONTENT`: Privacy policy text (in `consent_service.py`)
- `EXEMPT_PATHS`: Paths exempt from consent enforcement (in `consent_middleware.py`)
- `DB_PATH`: Database file location (in `db.py`)

## License

This consent management system is part of the Productivity Analyzer project.
