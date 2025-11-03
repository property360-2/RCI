# Richwell College Portal v3.0

**A comprehensive academic management system built with Django, featuring role-based access control, archive-first data management, and a modern, responsive UI.**

[![Django](https://img.shields.io/badge/Django-5.2.7-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.16.1-red.svg)](https://www.django-rest-framework.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🌟 Overview

The Richwell College Portal is a modern, full-featured academic management system designed for higher education institutions. It streamlines student enrollment, grade management, academic records, and provides powerful analytics for institutional oversight.

### Key Features

✅ **Role-Based Access Control (RBAC)** - 6 distinct roles with granular permissions
✅ **Archive-First Methodology** - Soft deletes preserve data integrity and enable full audit trails
✅ **Responsive Modern UI** - Tailwind CSS + Alpine.js + HTMX for seamless UX
✅ **RESTful API** - Comprehensive API with JWT authentication
✅ **Prerequisite Management** - Automatic validation of subject prerequisites
✅ **30-Unit Cap Enforcement** - Prevents student overloading
✅ **INC Grade Tracking** - Automated incomplete grade deadline management
✅ **Comprehensive Documentation** - 3,700+ lines of inline docstrings and user guides

---

## 📋 Table of Contents

- [Screenshots](#-screenshots)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [Project Structure](#-project-structure)
- [User Roles](#-user-roles)
- [Documentation](#-documentation)
- [Development Status](#-development-status)
- [Contributing](#-contributing)
- [License](#-license)

---

## 📸 Screenshots

### Login Page
Professional login interface with quick-access demo buttons and "Remember Me" functionality.

### Dean Dashboard
High-level analytics with enrollment stats, academic metrics, and system-wide insights.

### Registrar Dashboard
Student records management, enrollment control, and grade oversight.

### Professor Dashboard
Grade encoding interface, section management, and INC tracking.

### Student Dashboard
Personal grades, enrollment history, and academic progress tracking.

---

## 🛠 Tech Stack

### Backend
- **Django 5.2.7** - Python web framework
- **Django REST Framework 3.16.1** - RESTful API toolkit
- **SimpleJWT 5.5.1** - JWT authentication
- **PostgreSQL** - Production database (SQLite for development)
- **psycopg2-binary 2.9.11** - PostgreSQL adapter

### Frontend
- **Tailwind CSS** - Utility-first CSS framework
- **Alpine.js 3.x** - Lightweight JavaScript framework
- **HTMX 1.9.10** - Modern interactions without JavaScript
- **Atomic Design** - Component-based UI architecture

### DevOps
- **Gunicorn** - WSGI HTTP server
- **Nginx** - Reverse proxy and static file serving
- **Docker** - Containerization (optional)

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **pip** (Python package manager)
- **PostgreSQL 15+** (for production)
- **Git**

### Quick Start

```bash
# Clone the repository
git clone https://github.com/property360-2/RCI.git
cd RCI/richwell-portal

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

Visit **http://127.0.0.1:8000** to access the portal!

### Creating Test Users

```bash
python manage.py shell
```

```python
from users.models import User

# Create users for each role
User.objects.create_user(username='dean', password='deanpass', role=User.Role.DEAN)
User.objects.create_user(username='registrar', password='regpass', role=User.Role.REGISTRAR)
User.objects.create_user(username='admission', password='admpass', role=User.Role.ADMISSION)
User.objects.create_user(username='professor', password='profpass', role=User.Role.PROFESSOR)
User.objects.create_user(username='student', password='studpass', role=User.Role.STUDENT)
```

**For complete setup instructions, see [SETUP.md](documentation/SETUP.md)**

---

## 📁 Project Structure

```
RCI/
├── documentation/           # Comprehensive documentation
│   ├── concept.md          # Project architecture and design (639 lines)
│   ├── schema.md           # Database schema documentation (92 lines)
│   ├── SETUP.md            # Installation and deployment guide (700+ lines)
│   ├── USER_GUIDE.md       # User guide for all roles (1,100+ lines)
│   └── API.md              # REST API documentation (1,400+ lines)
│
└── richwell-portal/        # Django project
    ├── config/             # Django settings and URL routing
    ├── core/               # Reusable mixins and utilities
    │   └── models.py       # TimeStampMixin, ArchiveMixin (260 lines)
    ├── users/              # Custom user model and authentication
    │   ├── models.py       # User model with 6 roles (54 lines)
    │   └── views.py        # Authentication views (346 lines)
    ├── terms/              # Academic term management
    │   └── models.py       # Term model (360 lines)
    ├── courses/            # Degree programs (BSCS, BSBA, etc.)
    │   └── models.py       # Course model (210 lines)
    ├── subjects/           # Individual subjects with prerequisites
    │   └── models.py       # Subject model (395 lines)
    ├── sections/           # Class sections (Coming Soon)
    ├── students/           # Student records (Coming Soon)
    ├── enrollments/        # Student enrollments (Coming Soon)
    ├── grades/             # Grade records and INC tracking (Coming Soon)
    ├── archive_app/        # Archive management (Coming Soon)
    ├── audit/              # Audit trail logging (Coming Soon)
    └── templates/          # HTML templates
        ├── layouts/
        │   └── base.html   # Master template with navbar/sidebar
        ├── organisms/
        │   ├── navbar.html # Role-specific navigation (280 lines)
        │   └── sidebar.html # Collapsible sidebar (260 lines)
        └── pages/
            ├── login.html  # Login page with HTMX (166 lines)
            └── [role]/dashboard.html  # Role-specific dashboards
```

---

## 👥 User Roles

The portal supports **6 distinct roles** with specific permissions:

### 1. DEAN
**Access Level:** Full read access to all data
**Responsibilities:**
- Academic oversight and strategic planning
- View system-wide analytics and reports
- Monitor enrollment trends and grade distribution
- Access historical and archived data

### 2. REGISTRAR
**Access Level:** Full read/write for students, enrollments, grades
**Responsibilities:**
- Manage student records (create, edit, archive)
- Process enrollments and validate prerequisites
- Oversee grade records and resolve issues
- Archive graduated students
- Generate official transcripts

### 3. ADMISSION
**Access Level:** Create students, create enrollments, read-only for others
**Responsibilities:**
- Process new student applications
- Create student profiles for admitted applicants
- Quick-enroll new students in first-term subjects
- Track application and enrollment statistics

### 4. PROFESSOR
**Access Level:** Manage assigned sections, encode grades
**Responsibilities:**
- View assigned teaching sections
- Encode final grades for students
- Manage INC (Incomplete) grades
- Track and convert INC deadlines
- Access student rosters

### 5. STUDENT
**Access Level:** View own grades and enrollments (read-only)
**Responsibilities:**
- View current and historical grades
- Track enrollment status and schedule
- Monitor academic standing and progress
- Request unofficial transcripts

### 6. ADMIN
**Access Level:** Full system access
**Responsibilities:**
- System administration and configuration
- User management (create, edit, deactivate)
- Database maintenance
- System monitoring and backups

---

## 📚 Documentation

### Available Documentation

- **[SETUP.md](documentation/SETUP.md)** (700+ lines)
  - Installation guide for all platforms
  - PostgreSQL setup and configuration
  - Environment variables and secrets
  - Production deployment (Gunicorn + Nginx)
  - Docker deployment
  - Troubleshooting guide

- **[USER_GUIDE.md](documentation/USER_GUIDE.md)** (1,100+ lines)
  - Getting started guide
  - Login and authentication
  - Role-specific dashboard guides (6 roles)
  - Step-by-step task walkthroughs
  - 30+ FAQs
  - Support and training information

- **[API.md](documentation/API.md)** (1,400+ lines)
  - Complete REST API reference
  - JWT authentication guide
  - 50+ endpoint documentation
  - Request/response examples
  - Error handling and rate limiting
  - Code examples (JavaScript, Python, cURL)

- **[concept.md](documentation/concept.md)** (639 lines)
  - Project architecture and design philosophy
  - Archive-first methodology
  - Role and scope matrix
  - Backend architecture (11 apps)
  - API endpoint specifications
  - Frontend atomic design structure
  - 7-phase development roadmap

- **[schema.md](documentation/schema.md)** (92 lines)
  - Database schema reference
  - Table descriptions and relationships
  - Data rules and policies
  - Archive access matrix

### Inline Documentation

Every module includes comprehensive docstrings:
- **600+ lines** of inline documentation across core models
- **Module-level** docstrings explaining purpose and usage
- **Class-level** docstrings with business rules
- **Method-level** docstrings with parameters, returns, and examples
- **Usage examples** in code comments

---

## 🚧 Development Status

### ✅ Completed Features

- [x] **Core Architecture**
  - TimeStampMixin (auto timestamps)
  - ArchiveMixin (soft deletes)
  - Custom User model with 6 roles

- [x] **Authentication System**
  - Login with HTMX async form submission
  - Role-based dashboard routing
  - "Remember Me" functionality
  - Archive status validation
  - Session management

- [x] **Database Models**
  - Term model (academic periods)
  - Course model (degree programs)
  - Subject model (with prerequisites)
  - All models with comprehensive business logic

- [x] **UI Components**
  - Professional login page
  - Responsive navbar (role-specific)
  - Collapsible sidebar
  - Mobile-responsive design
  - 3 role-specific dashboards (Dean, Registrar, Admission)

- [x] **Documentation**
  - Setup guide (700+ lines)
  - User guide (1,100+ lines)
  - API documentation (1,400+ lines)
  - Inline docstrings (600+ lines)

### 🔄 In Progress / Coming Soon

- [ ] **Section Model**
  - Class sections with schedules
  - Professor assignments
  - Room allocation
  - Enrollment capacity

- [ ] **Student Model**
  - Complete student profiles
  - Academic standing tracking
  - Graduation requirements

- [ ] **Enrollment Model**
  - 30-unit cap enforcement (backend logic ready)
  - Prerequisite validation (backend logic ready)
  - Section capacity management
  - Add/drop period support

- [ ] **Grade Model**
  - Grade encoding by professors
  - INC tracking with deadlines
  - Automatic INC expiration
  - Grade change audit trail

- [ ] **Archive & Audit**
  - Bulk archive operations
  - Audit trail middleware
  - Archive search and filtering
  - Restore functionality

- [ ] **Analytics**
  - Dean dashboard charts
  - Enrollment trends
  - Grade distribution
  - At-risk student identification

- [ ] **REST API Implementation**
  - Implement DRF serializers
  - Create viewsets for all models
  - Add JWT authentication middleware
  - Configure CORS

- [ ] **Additional Dashboards**
  - Professor dashboard template
  - Student dashboard template
  - Admin dashboard template

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Reporting Issues

1. Check if issue already exists
2. Create a new issue with clear description
3. Include steps to reproduce
4. Attach screenshots if applicable

### Making Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Write/update tests
5. Update documentation
6. Commit with clear messages (`git commit -m 'feat: Add amazing feature'`)
7. Push to your fork (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Coding Standards

- Follow PEP 8 for Python code
- Write comprehensive docstrings
- Add type hints where applicable
- Include unit tests for new features
- Update documentation for user-facing changes

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Django** - Web framework
- **Tailwind CSS** - UI styling
- **HTMX** - Modern interactions
- **Alpine.js** - Reactive components
- **Django REST Framework** - API toolkit

---

## 📞 Support

For questions, issues, or feature requests:

- **GitHub Issues:** [https://github.com/property360-2/RCI/issues](https://github.com/property360-2/RCI/issues)
- **Email:** it-support@richwell.edu
- **Documentation:** `/documentation/` folder

---

## 📊 Project Stats

- **Total Lines of Code:** 5,000+
- **Documentation:** 3,700+ lines
- **Models Implemented:** 3 (Term, Course, Subject)
- **Models Planned:** 8 additional
- **UI Templates:** 8 (login, dashboards, organisms)
- **User Roles:** 6 (DEAN, REGISTRAR, ADMISSION, PROFESSOR, STUDENT, ADMIN)
- **Database Tables:** 10+ (with relationships)

---

**Built with ❤️ by the Richwell College IT Team**

**Version:** 3.0
**Last Updated:** 2024
**Status:** Active Development
