# Richwell College Portal v3.0 - API Documentation

Complete REST API documentation for the Richwell College Portal with authentication, endpoints, and usage examples.

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
   - [Authentication Endpoints](#authentication-endpoints)
   - [User Endpoints](#user-endpoints)
   - [Term Endpoints](#term-endpoints)
   - [Course Endpoints](#course-endpoints)
   - [Subject Endpoints](#subject-endpoints)
   - [Section Endpoints](#section-endpoints)
   - [Student Endpoints](#student-endpoints)
   - [Enrollment Endpoints](#enrollment-endpoints)
   - [Grade Endpoints](#grade-endpoints)
4. [Error Handling](#error-handling)
5. [Rate Limiting](#rate-limiting)
6. [Pagination](#pagination)
7. [Code Examples](#code-examples)

---

## Overview

### Base URL

```
Production: https://api.richwell.edu/v1/
Development: http://localhost:8000/api/v1/
```

### Response Format

All API responses use JSON format.

**Success Response:**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "Example"
  },
  "message": "Operation successful"
}
```

**Error Response:**
```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": {
    "field_name": ["Error description"]
  }
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 204 | No Content - Successful deletion |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 422 | Unprocessable Entity - Validation error |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server issue |

---

## Authentication

### JWT Token Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```http
Authorization: Bearer <your_access_token>
```

### Token Lifecycle

- **Access Token:** Valid for 15 minutes
- **Refresh Token:** Valid for 7 days
- **Refresh Before:** Refresh access token before expiry

### Obtaining Tokens

**Endpoint:** `POST /api/v1/auth/login/`

**Request:**
```json
{
  "username": "dean",
  "password": "deanpassword"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": 1,
      "username": "dean",
      "email": "dean@richwell.edu",
      "role": "DEAN",
      "full_name": "John Smith"
    }
  },
  "message": "Login successful"
}
```

### Refreshing Tokens

**Endpoint:** `POST /api/v1/auth/refresh/`

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Logout

**Endpoint:** `POST /api/v1/auth/logout/`

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Logout successful"
}
```

---

## API Endpoints

### Authentication Endpoints

#### Login
```http
POST /api/v1/auth/login/
```
Authenticate user and receive JWT tokens.

#### Refresh Token
```http
POST /api/v1/auth/refresh/
```
Refresh access token using refresh token.

#### Logout
```http
POST /api/v1/auth/logout/
```
Invalidate refresh token (blacklist).

#### Verify Token
```http
POST /api/v1/auth/verify/
```
Check if access token is valid.

**Request:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### User Endpoints

#### Get Current User
```http
GET /api/v1/users/me/
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "dean",
  "email": "dean@richwell.edu",
  "first_name": "John",
  "last_name": "Smith",
  "role": "DEAN",
  "archived": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### List Users (Admin/Dean only)
```http
GET /api/v1/users/
```

**Query Parameters:**
- `role` - Filter by role (DEAN, REGISTRAR, etc.)
- `archived` - Filter by archived status (true/false)
- `search` - Search by username, email, or name
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20)

**Response (200 OK):**
```json
{
  "count": 50,
  "next": "/api/v1/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "dean",
      "email": "dean@richwell.edu",
      "full_name": "John Smith",
      "role": "DEAN"
    }
  ]
}
```

#### Get User by ID
```http
GET /api/v1/users/{id}/
```

#### Update User
```http
PUT /api/v1/users/{id}/
PATCH /api/v1/users/{id}/
```

**Request (PATCH):**
```json
{
  "email": "newemail@richwell.edu",
  "first_name": "Jane"
}
```

#### Archive User
```http
POST /api/v1/users/{id}/archive/
```

**Request:**
```json
{
  "reason": "Graduated - Class of 2024"
}
```

#### Restore User
```http
POST /api/v1/users/{id}/restore/
```

---

### Term Endpoints

#### List Terms
```http
GET /api/v1/terms/
```

**Query Parameters:**
- `is_active` - Filter active enrollment term (true/false)
- `archived` - Include archived terms (true/false)
- `ordering` - Sort by field (e.g., `-term_start` for newest first)

**Response (200 OK):**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "name": "Fall 2024",
      "slug": "fall-2024",
      "term_start": "2024-09-01",
      "term_end": "2024-12-15",
      "enrollment_start": "2024-07-01",
      "enrollment_end": "2024-09-10",
      "is_active": true,
      "archived": false,
      "status": "Enrollment Open",
      "enrollment_stats": {
        "total_enrollments": 450,
        "total_students": 180,
        "total_sections": 45
      }
    }
  ]
}
```

#### Get Term by ID
```http
GET /api/v1/terms/{id}/
```

#### Create Term (Dean/Registrar only)
```http
POST /api/v1/terms/
```

**Request:**
```json
{
  "name": "Spring 2025",
  "slug": "spring-2025",
  "term_start": "2025-01-15",
  "term_end": "2025-05-15",
  "enrollment_start": "2024-11-01",
  "enrollment_end": "2025-01-20"
}
```

#### Update Term
```http
PUT /api/v1/terms/{id}/
PATCH /api/v1/terms/{id}/
```

#### Activate Term
```http
POST /api/v1/terms/{id}/activate/
```

Makes this term the active enrollment term (deactivates all others).

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Spring 2025 is now the active enrollment term"
}
```

#### Get Active Term
```http
GET /api/v1/terms/active/
```

Returns the currently active enrollment term.

---

### Course Endpoints

#### List Courses
```http
GET /api/v1/courses/
```

**Query Parameters:**
- `archived` - Include archived courses (true/false)
- `search` - Search by code or name
- `ordering` - Sort by field

**Response (200 OK):**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "code": "BSCS",
      "name": "Bachelor of Science in Computer Science",
      "description": "A 4-year program focusing on software development...",
      "total_units": 120,
      "years_to_complete": 4,
      "archived": false,
      "student_count": 180,
      "subject_count": 45
    }
  ]
}
```

#### Get Course by ID
```http
GET /api/v1/courses/{id}/
```

#### Get Course by Code
```http
GET /api/v1/courses/by-code/{code}/
```

Example: `/api/v1/courses/by-code/BSCS/`

#### Create Course (Dean/Registrar only)
```http
POST /api/v1/courses/
```

**Request:**
```json
{
  "code": "BSBA",
  "name": "Bachelor of Science in Business Administration",
  "description": "A 4-year program covering management, finance...",
  "total_units": 120,
  "years_to_complete": 4
}
```

#### Update Course
```http
PUT /api/v1/courses/{id}/
PATCH /api/v1/courses/{id}/
```

#### Get Course Subjects
```http
GET /api/v1/courses/{id}/subjects/
```

Returns all subjects belonging to this course.

**Query Parameters:**
- `year_level` - Filter by year level (1-5)
- `archived` - Include archived subjects

---

### Subject Endpoints

#### List Subjects
```http
GET /api/v1/subjects/
```

**Query Parameters:**
- `course` - Filter by course ID
- `year_level` - Filter by year level
- `has_prerequisites` - Filter subjects with prerequisites (true/false)
- `archived` - Include archived subjects
- `search` - Search by code or name

**Response (200 OK):**
```json
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "code": "COMP101",
      "name": "Introduction to Programming",
      "description": "Basic programming concepts using Python",
      "units": 3,
      "year_level": 1,
      "course": {
        "id": 1,
        "code": "BSCS",
        "name": "Bachelor of Science in Computer Science"
      },
      "prerequisites": [],
      "has_prerequisites": false,
      "archived": false,
      "average_grade": 2.5,
      "pass_rate": 85.5
    }
  ]
}
```

#### Get Subject by ID
```http
GET /api/v1/subjects/{id}/
```

#### Get Subject by Code
```http
GET /api/v1/subjects/by-code/{code}/
```

#### Create Subject (Dean/Registrar only)
```http
POST /api/v1/subjects/
```

**Request:**
```json
{
  "code": "COMP102",
  "name": "Data Structures and Algorithms",
  "description": "Fundamental data structures and algorithm design",
  "units": 3,
  "year_level": 1,
  "course": 1,
  "prerequisites": [1]
}
```

#### Update Subject
```http
PUT /api/v1/subjects/{id}/
PATCH /api/v1/subjects/{id}/
```

#### Add Prerequisite
```http
POST /api/v1/subjects/{id}/add-prerequisite/
```

**Request:**
```json
{
  "prerequisite_id": 1
}
```

#### Remove Prerequisite
```http
POST /api/v1/subjects/{id}/remove-prerequisite/
```

#### Check Student Eligibility
```http
POST /api/v1/subjects/{id}/check-eligibility/
```

Check if a student can enroll in this subject.

**Request:**
```json
{
  "student_id": 5
}
```

**Response (200 OK):**
```json
{
  "eligible": false,
  "missing_prerequisites": [
    {
      "id": 1,
      "code": "COMP101",
      "name": "Introduction to Programming"
    }
  ]
}
```

---

### Section Endpoints

(Coming Soon - Section model not yet implemented)

#### List Sections
```http
GET /api/v1/sections/
```

#### Create Section
```http
POST /api/v1/sections/
```

#### Assign Professor
```http
POST /api/v1/sections/{id}/assign-professor/
```

---

### Student Endpoints

(Coming Soon - Student model not yet implemented)

#### List Students
```http
GET /api/v1/students/
```

#### Create Student (Admission/Registrar only)
```http
POST /api/v1/students/
```

#### Get Student by ID
```http
GET /api/v1/students/{id}/
```

#### Get Student Transcript
```http
GET /api/v1/students/{id}/transcript/
```

---

### Enrollment Endpoints

(Coming Soon - Enrollment model not yet implemented)

#### List Enrollments
```http
GET /api/v1/enrollments/
```

#### Create Enrollment
```http
POST /api/v1/enrollments/
```

**Request:**
```json
{
  "student_id": 5,
  "section_id": 10,
  "term_id": 1
}
```

**Validation:**
- Checks 30-unit cap
- Validates prerequisites
- Ensures section isn't full
- Confirms enrollment period is open

#### Bulk Enrollment
```http
POST /api/v1/enrollments/bulk-create/
```

Enroll a student in multiple sections at once.

**Request:**
```json
{
  "student_id": 5,
  "term_id": 1,
  "section_ids": [10, 11, 12, 13]
}
```

---

### Grade Endpoints

(Coming Soon - Grade model not yet implemented)

#### List Grades
```http
GET /api/v1/grades/
```

#### Encode Grade (Professor only)
```http
POST /api/v1/grades/
```

**Request:**
```json
{
  "enrollment_id": 100,
  "grade": 2.5,
  "remarks": "Good performance"
}
```

**Grade Scale:**
- 5.0 = Excellent
- 4.0 = Very Good
- 3.0 = Good (Passing)
- 2.0 = Fair
- 1.0 = Failed
- INC = Incomplete

#### Encode INC Grade
```http
POST /api/v1/grades/
```

**Request:**
```json
{
  "enrollment_id": 100,
  "grade": "INC",
  "completion_deadline": "2025-05-15",
  "remarks": "Missing final project"
}
```

#### Convert INC to Final Grade
```http
PATCH /api/v1/grades/{id}/convert-inc/
```

**Request:**
```json
{
  "grade": 2.5,
  "remarks": "Completed requirements"
}
```

---

## Error Handling

### Validation Errors

**Response (422 Unprocessable Entity):**
```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": {
    "enrollment_end": ["Enrollment end date must be after enrollment start date."],
    "units": ["Ensure this value is less than or equal to 5."]
  }
}
```

### Authentication Errors

**Response (401 Unauthorized):**
```json
{
  "status": "error",
  "message": "Authentication credentials were not provided.",
  "code": "not_authenticated"
}
```

### Permission Errors

**Response (403 Forbidden):**
```json
{
  "status": "error",
  "message": "You do not have permission to perform this action.",
  "code": "permission_denied",
  "required_role": "DEAN or REGISTRAR"
}
```

### Not Found Errors

**Response (404 Not Found):**
```json
{
  "status": "error",
  "message": "Not found.",
  "code": "not_found"
}
```

---

## Rate Limiting

API requests are rate-limited to prevent abuse.

### Rate Limits

| Endpoint Type | Rate Limit |
|--------------|------------|
| Authentication | 5 requests/minute |
| Read Operations | 100 requests/minute |
| Write Operations | 30 requests/minute |

### Rate Limit Headers

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1609459200
```

### Rate Limit Exceeded

**Response (429 Too Many Requests):**
```json
{
  "status": "error",
  "message": "Request was throttled. Expected available in 45 seconds.",
  "code": "throttled",
  "available_in": 45
}
```

---

## Pagination

List endpoints return paginated results.

### Default Pagination

- **Default Page Size:** 20 items
- **Max Page Size:** 100 items

### Query Parameters

- `page` - Page number (default: 1)
- `page_size` - Items per page (max: 100)

### Response Format

```json
{
  "count": 150,
  "next": "/api/v1/students/?page=2&page_size=20",
  "previous": null,
  "results": [...]
}
```

### Cursor Pagination (Optional)

For large datasets, cursor-based pagination is more efficient:

```http
GET /api/v1/grades/?cursor=cD0yMDIzLTEyLTE1
```

---

## Code Examples

### JavaScript/Fetch API

```javascript
// Login
async function login(username, password) {
  const response = await fetch('http://localhost:8000/api/v1/auth/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });

  const data = await response.json();

  if (response.ok) {
    localStorage.setItem('access_token', data.data.access);
    localStorage.setItem('refresh_token', data.data.refresh);
    return data.data.user;
  } else {
    throw new Error(data.message);
  }
}

// Get terms with authentication
async function getTerms() {
  const accessToken = localStorage.getItem('access_token');

  const response = await fetch('http://localhost:8000/api/v1/terms/', {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
    },
  });

  if (response.ok) {
    return await response.json();
  } else if (response.status === 401) {
    // Token expired, refresh it
    await refreshToken();
    return getTerms(); // Retry
  }
}

// Refresh token
async function refreshToken() {
  const refreshToken = localStorage.getItem('refresh_token');

  const response = await fetch('http://localhost:8000/api/v1/auth/refresh/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ refresh: refreshToken }),
  });

  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('access_token', data.access);
  } else {
    // Refresh token expired, redirect to login
    window.location.href = '/login';
  }
}
```

### Python/Requests

```python
import requests

BASE_URL = 'http://localhost:8000/api/v1'

# Login
def login(username, password):
    response = requests.post(f'{BASE_URL}/auth/login/', json={
        'username': username,
        'password': password
    })

    if response.status_code == 200:
        data = response.json()['data']
        return data['access'], data['refresh']
    else:
        raise Exception(response.json()['message'])

# Get terms
def get_terms(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(f'{BASE_URL}/terms/', headers=headers)

    if response.status_code == 200:
        return response.json()['results']
    elif response.status_code == 401:
        # Token expired, refresh
        pass

# Create course
def create_course(access_token, course_data):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.post(f'{BASE_URL}/courses/',
                            json=course_data,
                            headers=headers)

    if response.status_code == 201:
        return response.json()
    else:
        raise Exception(response.json()['message'])

# Usage
access, refresh = login('dean', 'deanpassword')
terms = get_terms(access)

new_course = create_course(access, {
    'code': 'BSIT',
    'name': 'Bachelor of Science in Information Technology',
    'total_units': 120,
    'years_to_complete': 4
})
```

### cURL

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"dean","password":"deanpassword"}'

# Get terms (with authentication)
curl -X GET http://localhost:8000/api/v1/terms/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."

# Create course
curl -X POST http://localhost:8000/api/v1/courses/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "code": "BSIT",
    "name": "Bachelor of Science in Information Technology",
    "total_units": 120,
    "years_to_complete": 4
  }'

# Get subjects for a course
curl -X GET "http://localhost:8000/api/v1/subjects/?course=1&year_level=1" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

---

## Webhook Events (Coming Soon)

Subscribe to webhook events for real-time notifications:

### Available Events

- `enrollment.created` - Student enrolled in section
- `grade.submitted` - Professor submitted grades
- `inc.deadline_approaching` - INC deadline in 7 days
- `term.activated` - New term activated for enrollment

### Webhook Payload

```json
{
  "event": "enrollment.created",
  "timestamp": "2024-12-15T14:30:00Z",
  "data": {
    "enrollment_id": 150,
    "student_id": 5,
    "section_id": 10,
    "term": "Fall 2024"
  }
}
```

---

**API Version:** v1
**Last Updated:** 2024
**Maintained by:** Richwell College IT Team

For questions or support, contact: api-support@richwell.edu
