# Richwell College Portal v3.0 - Setup & Installation Guide

Complete guide for setting up and deploying the Richwell College Portal, an academic management system built with Django.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Database Setup](#database-setup)
5. [Running the Development Server](#running-the-development-server)
6. [Creating Admin Users](#creating-admin-users)
7. [Loading Sample Data](#loading-sample-data)
8. [Production Deployment](#production-deployment)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before installing the Richwell College Portal, ensure you have the following installed:

### Required Software

- **Python 3.11+** - The project is built with Python 3.11
- **pip** - Python package installer
- **virtualenv** (recommended) - For isolated Python environments
- **Git** - For version control
- **PostgreSQL 15+** (for production) - SQLite is used for development

### Recommended Tools

- **VS Code** or **PyCharm** - IDE with Python support
- **Postman** - For API testing
- **pgAdmin** or **DBeaver** - PostgreSQL database management (production only)

### System Requirements

- **RAM:** Minimum 2GB, Recommended 4GB+
- **Disk Space:** Minimum 500MB for application + database
- **OS:** Linux, macOS, or Windows (with WSL recommended)

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/richwell-portal.git
cd richwell-portal
```

### 2. Create a Virtual Environment

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
cd richwell-portal
pip install -r requirements.txt
```

This will install:
- Django 5.2.7
- Django REST Framework 3.16.1
- SimpleJWT 5.5.1
- Pillow 12.0.0
- psycopg2-binary 2.9.11
- And other dependencies

### 4. Verify Installation

```bash
python manage.py --version
# Should output: 5.2.7
```

---

## Configuration

### 1. Environment Variables

Create a `.env` file in the project root (richwell-portal/):

```bash
# richwell-portal/.env

# Django Settings
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Development - SQLite)
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3

# Database (Production - PostgreSQL)
# DATABASE_ENGINE=django.db.backends.postgresql
# DATABASE_NAME=richwell_portal
# DATABASE_USER=richwell_user
# DATABASE_PASSWORD=secure_password_here
# DATABASE_HOST=localhost
# DATABASE_PORT=5432

# Security
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Email Configuration (Optional - for password reset)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Static/Media Files
STATIC_URL=/static/
MEDIA_URL=/media/
```

### 2. Generate Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and use it as your `SECRET_KEY` in `.env`.

### 3. Load Environment Variables

The project uses `python-dotenv` to automatically load `.env` variables. No additional configuration needed.

---

## Database Setup

### Development (SQLite)

SQLite is used by default for development. No additional setup required.

### Production (PostgreSQL)

#### 1. Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

#### 2. Create Database and User

```bash
sudo -u postgres psql

# Inside PostgreSQL shell:
CREATE DATABASE richwell_portal;
CREATE USER richwell_user WITH PASSWORD 'secure_password_here';
ALTER ROLE richwell_user SET client_encoding TO 'utf8';
ALTER ROLE richwell_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE richwell_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE richwell_portal TO richwell_user;
\q
```

#### 3. Update .env File

Update your `.env` file with PostgreSQL credentials (see Configuration section).

---

## Running the Development Server

### 1. Apply Database Migrations

```bash
python manage.py migrate
```

This creates all necessary database tables for:
- Users (custom user model with roles)
- Terms (academic semesters)
- Courses (degree programs)
- Subjects (individual courses)
- And other models

### 2. Create a Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 3. Start the Development Server

```bash
python manage.py runserver
```

The portal will be available at: **http://127.0.0.1:8000**

### 4. Access the Application

- **Login Page:** http://127.0.0.1:8000/login/
- **Admin Panel:** http://127.0.0.1:8000/admin/
- **Dashboard:** http://127.0.0.1:8000/dashboard/ (after login)

---

## Creating Admin Users

### Option 1: Django Admin

1. Login to admin panel: http://127.0.0.1:8000/admin/
2. Navigate to **Users** → **Add User**
3. Set username, password, and role
4. Save

### Option 2: Django Shell

```bash
python manage.py shell
```

```python
from users.models import User

# Create a Dean
dean = User.objects.create_user(
    username='dean',
    password='deanpassword',
    email='dean@richwell.edu',
    first_name='John',
    last_name='Smith',
    role=User.Role.DEAN
)

# Create a Registrar
registrar = User.objects.create_user(
    username='registrar',
    password='regpassword',
    email='registrar@richwell.edu',
    first_name='Jane',
    last_name='Doe',
    role=User.Role.REGISTRAR
)

# Create an Admission Officer
admission = User.objects.create_user(
    username='admission',
    password='admpassword',
    email='admission@richwell.edu',
    first_name='Mike',
    last_name='Johnson',
    role=User.Role.ADMISSION
)

# Create a Professor
professor = User.objects.create_user(
    username='professor',
    password='profpassword',
    email='prof@richwell.edu',
    first_name='Dr. Sarah',
    last_name='Williams',
    role=User.Role.PROFESSOR
)

# Create a Student
student = User.objects.create_user(
    username='student',
    password='studpassword',
    email='student@richwell.edu',
    first_name='Alice',
    last_name='Brown',
    role=User.Role.STUDENT
)

print("Test users created successfully!")
```

---

## Loading Sample Data

### Create Sample Academic Data

```bash
python manage.py shell
```

```python
from django.utils import timezone
from datetime import date, timedelta
from courses.models import Course
from subjects.models import Subject
from terms.models import Term

# Create Terms
fall_2024 = Term.objects.create(
    name="Fall 2024",
    slug="fall-2024",
    term_start=date(2024, 9, 1),
    term_end=date(2024, 12, 15),
    enrollment_start=date(2024, 7, 1),
    enrollment_end=date(2024, 9, 10),
    is_active=True
)

spring_2025 = Term.objects.create(
    name="Spring 2025",
    slug="spring-2025",
    term_start=date(2025, 1, 15),
    term_end=date(2025, 5, 15),
    enrollment_start=date(2024, 11, 1),
    enrollment_end=date(2025, 1, 20),
    is_active=False
)

# Create Courses (Degree Programs)
bscs = Course.objects.create(
    code="BSCS",
    name="Bachelor of Science in Computer Science",
    description="A 4-year program focusing on software development, algorithms, and computer systems",
    total_units=120,
    years_to_complete=4
)

bsba = Course.objects.create(
    code="BSBA",
    name="Bachelor of Science in Business Administration",
    description="A 4-year program covering management, finance, marketing, and entrepreneurship",
    total_units=120,
    years_to_complete=4
)

# Create Subjects for BSCS
comp101 = Subject.objects.create(
    code="COMP101",
    name="Introduction to Programming",
    description="Basic programming concepts using Python",
    units=3,
    year_level=1,
    course=bscs
)

comp102 = Subject.objects.create(
    code="COMP102",
    name="Data Structures and Algorithms",
    description="Fundamental data structures and algorithm design",
    units=3,
    year_level=1,
    course=bscs
)

# Add prerequisite
comp102.prerequisites.add(comp101)

math101 = Subject.objects.create(
    code="MATH101",
    name="Calculus I",
    description="Differential and integral calculus",
    units=3,
    year_level=1,
    course=bscs
)

# Create Subjects for BSBA
acct101 = Subject.objects.create(
    code="ACCT101",
    name="Principles of Accounting",
    description="Introduction to financial and managerial accounting",
    units=3,
    year_level=1,
    course=bsba
)

mgmt101 = Subject.objects.create(
    code="MGMT101",
    name="Principles of Management",
    description="Fundamentals of business management",
    units=3,
    year_level=1,
    course=bsba
)

print("Sample data created successfully!")
print(f"Terms: {Term.objects.count()}")
print(f"Courses: {Course.objects.count()}")
print(f"Subjects: {Subject.objects.count()}")
```

---

## Production Deployment

### 1. Security Checklist

- [ ] Set `DEBUG = False` in `.env`
- [ ] Generate new `SECRET_KEY` and keep it secret
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS properly
- [ ] Set up proper logging
- [ ] Enable Django security middleware

### 2. Static Files

```bash
# Collect static files
python manage.py collectstatic --no-input
```

### 3. Web Server Configuration

#### Option A: Gunicorn + Nginx

**Install Gunicorn:**
```bash
pip install gunicorn
```

**Run Gunicorn:**
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

**Nginx Configuration (example):**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/richwell-portal/staticfiles/;
    }

    location /media/ {
        alias /path/to/richwell-portal/media/;
    }
}
```

#### Option B: Docker Deployment

See `docker-compose.yml` in the repository for Docker setup.

---

## Troubleshooting

### Issue: "No module named 'django'"

**Solution:** Ensure you've activated the virtual environment and installed dependencies.

```bash
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Issue: Migration errors

**Solution:** Reset migrations (development only):

```bash
# Delete all migrations except __init__.py
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
rm db.sqlite3

# Recreate migrations
python manage.py makemigrations
python manage.py migrate
```

### Issue: "CSRF token missing or incorrect"

**Solution:** Clear browser cookies or ensure CSRF middleware is enabled in settings.

### Issue: Static files not loading

**Solution:** Run collectstatic and check STATIC_URL configuration:

```bash
python manage.py collectstatic
```

### Issue: Database connection error (PostgreSQL)

**Solution:** Verify PostgreSQL is running and credentials are correct:

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
psql -U richwell_user -d richwell_portal -h localhost
```

---

## Additional Resources

- **Django Documentation:** https://docs.djangoproject.com/
- **DRF Documentation:** https://www.django-rest-framework.org/
- **Tailwind CSS:** https://tailwindcss.com/docs
- **HTMX Documentation:** https://htmx.org/docs/

---

## Support

For issues or questions:
- **GitHub Issues:** https://github.com/your-org/richwell-portal/issues
- **Email:** it-support@richwell.edu
- **Documentation:** `/documentation/` folder in repository

---

**Last Updated:** 2024
**Version:** 3.0
**Maintainers:** Richwell College IT Team
