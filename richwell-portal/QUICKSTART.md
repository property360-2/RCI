# Richwell College Portal - Quick Start Guide

This guide will help you get the Richwell College Portal up and running quickly.

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Quick Setup

### 1. Create and Activate Virtual Environment

```bash
# Navigate to the project directory
cd richwell-portal

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and set your values (optional for development)
# For development, you can use the defaults
```

### 4. Run Database Migrations

```bash
python manage.py migrate
```

### 5. Seed Test Data

```bash
# Seed the database with test data
python manage.py seed_data

# Or clear existing data first and then seed
python manage.py seed_data --clear
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

### 7. Access the Application

Open your browser and navigate to:

**Web Application:**
- http://127.0.0.1:8000/

**Admin Panel:**
- http://127.0.0.1:8000/admin/

**API Endpoints:**
- http://127.0.0.1:8000/api/v1/

## Test Credentials

After running the seeder, you can login with these credentials:

| Role | Username | Password | Name |
|------|----------|----------|------|
| Admin | admin | password123 | System Administrator |
| Dean | dean.cs | password123 | Robert Mitchell |
| Registrar | registrar1 | password123 | Maria Rodriguez |
| Admission | admission1 | password123 | Emily Johnson |
| Professor | prof.johnson | password123 | Michael Johnson |
| Student | student001 | password123 | Juan Dela Cruz |

**Note:** All test accounts use the password `password123`

## What's Included in Test Data

The seeder creates:

- **13 Users** with different roles (Admin, Dean, Registrar, Admission, Professors)
- **30 Students** across different year levels and courses
- **5 Courses** (BSCS, BSIT, BSBA, BSAC, BEED)
- **21 Subjects** with prerequisites
- **3 Academic Terms** (1 active, 2 past)
- **~30 Sections** for the current term
- **~180 Enrollments** (students enrolled in subjects)
- **~126 Grade Records** (70% of enrollments graded)

## Available Features

### For Students
- View current enrollments
- Check grades
- View GPA and academic progress
- See class schedules

### For Professors
- View assigned sections
- Encode grades
- Manage INC records
- View student rosters

### For Registrars
- Manage student records
- Process enrollments
- Verify grades
- Generate reports

### For Deans
- View analytics
- Access all academic records
- Review performance metrics

### For Admission Officers
- Create new student records
- Process enrollments
- View applicant data

## API Usage

### Get JWT Token

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password123"}'
```

### Use Token to Access API

```bash
curl -X GET http://127.0.0.1:8000/api/v1/courses/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

For detailed API documentation, see [API_README.md](API_README.md)

## Troubleshooting

### Port Already in Use

If port 8000 is already in use, you can run the server on a different port:

```bash
python manage.py runserver 8080
```

### Database Issues

If you encounter database issues, try:

```bash
# Delete the database
rm db.sqlite3

# Delete migrations
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Recreate everything
python manage.py makemigrations
python manage.py migrate
python manage.py seed_data
```

### Import Errors

Make sure you're in the virtual environment:

```bash
# Check if venv is activated (you should see (venv) in your prompt)
which python

# If not activated, activate it
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

## Next Steps

1. **Explore the UI**: Login with different roles to see role-based dashboards
2. **Test the API**: Use the REST API endpoints to interact with data
3. **Customize**: Modify the seeder to add more specific test data
4. **Develop**: Start building additional features

## Important Notes

- **Security**: The `.env.example` file contains example values. In production, use strong secrets!
- **Debug Mode**: DEBUG is set to True by default for development. Set to False in production.
- **Database**: SQLite is used for development. For production, switch to PostgreSQL.

## Support

For issues or questions:
- Check the documentation in the `/documentation` folder
- Review the API documentation in `API_README.md`
- Check the project README in the root directory

---

**Happy Coding! 🚀**
