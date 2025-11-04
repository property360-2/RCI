# Richwell College Portal - REST API

## Overview

The Richwell College Portal provides a RESTful API built with Django REST Framework for programmatic access to the system's data and functionality.

## Base URL

```
http://localhost:8000/api/v1/
```

## Authentication

The API uses JWT (JSON Web Token) authentication.

### Getting a Token

**Endpoint:** `POST /api/v1/auth/token/`

**Request Body:**
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Using the Token

Include the access token in the Authorization header:

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Refreshing the Token

**Endpoint:** `POST /api/v1/auth/token/refresh/`

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## Available Endpoints

### Courses

| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/api/v1/courses/` | List all courses | Authenticated |
| POST | `/api/v1/courses/` | Create a new course | DEAN, REGISTRAR, ADMIN |
| GET | `/api/v1/courses/{id}/` | Get course details | Authenticated |
| PUT | `/api/v1/courses/{id}/` | Update a course | DEAN, REGISTRAR, ADMIN |
| PATCH | `/api/v1/courses/{id}/` | Partial update | DEAN, REGISTRAR, ADMIN |
| DELETE | `/api/v1/courses/{id}/` | Archive a course | DEAN, REGISTRAR, ADMIN |
| POST | `/api/v1/courses/{id}/restore/` | Restore archived course | DEAN, REGISTRAR, ADMIN |
| GET | `/api/v1/courses/{id}/subjects/` | Get subjects in course | Authenticated |
| GET | `/api/v1/courses/{id}/students/` | Get students in course | Authenticated |
| GET | `/api/v1/courses/statistics/` | Get course statistics | Authenticated |

#### Query Parameters

- `archived`: Filter by archived status (true/false)
- `search`: Search by code, name, or description
- `ordering`: Sort by code, name, or created_at (prefix with `-` for descending)

#### Example Requests

**List Courses:**
```bash
curl -X GET http://localhost:8000/api/v1/courses/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Create Course:**
```bash
curl -X POST http://localhost:8000/api/v1/courses/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "BSCS",
    "name": "Bachelor of Science in Computer Science",
    "description": "Four-year degree program in Computer Science",
    "total_units": 180
  }'
```

**Search Courses:**
```bash
curl -X GET "http://localhost:8000/api/v1/courses/?search=computer" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Subjects

| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/api/v1/subjects/` | List all subjects | Authenticated |
| POST | `/api/v1/subjects/` | Create a new subject | DEAN, REGISTRAR, ADMIN |
| GET | `/api/v1/subjects/{id}/` | Get subject details | Authenticated |
| PUT | `/api/v1/subjects/{id}/` | Update a subject | DEAN, REGISTRAR, ADMIN |
| PATCH | `/api/v1/subjects/{id}/` | Partial update | DEAN, REGISTRAR, ADMIN |
| DELETE | `/api/v1/subjects/{id}/` | Archive a subject | DEAN, REGISTRAR, ADMIN |
| POST | `/api/v1/subjects/{id}/restore/` | Restore archived subject | DEAN, REGISTRAR, ADMIN |
| GET | `/api/v1/subjects/{id}/sections/` | Get sections for subject | Authenticated |
| GET | `/api/v1/subjects/{id}/prerequisites/` | Get prerequisites | Authenticated |
| POST | `/api/v1/subjects/{id}/check_prerequisites/` | Check if student meets prerequisites | Authenticated |

#### Query Parameters

- `archived`: Filter by archived status (true/false)
- `course`: Filter by course ID
- `units`: Filter by unit count
- `search`: Search by code, name, or description
- `ordering`: Sort by code, name, units, or created_at

#### Example Requests

**List Subjects:**
```bash
curl -X GET http://localhost:8000/api/v1/subjects/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Create Subject:**
```bash
curl -X POST http://localhost:8000/api/v1/subjects/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "CS101",
    "name": "Introduction to Programming",
    "description": "Fundamentals of programming using Python",
    "units": 3,
    "course": 1,
    "prerequisites": []
  }'
```

**Filter Subjects by Course:**
```bash
curl -X GET "http://localhost:8000/api/v1/subjects/?course=1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Response Format

### Success Response

```json
{
  "id": 1,
  "code": "BSCS",
  "name": "Bachelor of Science in Computer Science",
  "description": "Four-year degree program",
  "total_units": 180,
  "archived": false,
  "created_at": "2024-11-04T10:30:00Z",
  "updated_at": "2024-11-04T10:30:00Z"
}
```

### List Response

```json
{
  "count": 10,
  "next": "http://localhost:8000/api/v1/courses/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "code": "BSCS",
      "name": "Bachelor of Science in Computer Science",
      "total_units": 180,
      "archived": false
    }
  ]
}
```

### Error Response

```json
{
  "error": "You do not have permission to perform this action."
}
```

## Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 204 | No Content (successful deletion) |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Internal Server Error |

## Rate Limiting

Currently, there are no rate limits enforced. This will be added in future updates.

## Pagination

List endpoints are paginated with 20 items per page by default. Use the `page` query parameter to navigate:

```
/api/v1/courses/?page=2
```

## Filtering

Most list endpoints support filtering through query parameters. Refer to each endpoint's documentation for available filters.

## Future Endpoints

The following endpoints are planned for future releases:

- Students API
- Sections API
- Terms API
- Enrollments API
- Grades API
- Users API

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run migrations:
   ```bash
   python manage.py migrate
   ```

3. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

4. Run the development server:
   ```bash
   python manage.py runserver
   ```

5. Access the API at: `http://localhost:8000/api/v1/`

## Testing the API

You can use tools like:
- cURL (command line)
- Postman (GUI)
- HTTPie (command line)
- Django REST Framework's browsable API (in browser)

Visit `http://localhost:8000/api/v1/` in your browser to access the browsable API.
