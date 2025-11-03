# 📁 Richwell College Portal - Project Structure

```
richwell-portal/
│
├── 📂 config/                          # Django project configuration
│   ├── __init__.py
│   ├── asgi.py                         # ASGI config
│   ├── wsgi.py                         # WSGI config
│   ├── celery.py                       # Celery app (to be created)
│   ├── urls.py                         # Root URL configuration
│   │
│   └── 📂 settings/                    # Split settings
│       ├── __init__.py
│       ├── base.py                     # Base settings (all envs)
│       ├── dev.py                      # Development (SQLite)
│       └── prod.py                     # Production (PostgreSQL + S3)
│
├── 📂 core/                            # Core models & utilities
│   ├── __init__.py
│   ├── models.py                       # TimeStampMixin, ArchiveMixin, Managers
│   ├── permissions.py                  # Custom DRF permissions (Phase 1)
│   ├── pagination.py                   # Custom pagination (Phase 1)
│   └── utils.py                        # Helper functions
│
├── 📂 users/                           # User authentication & roles
│   ├── __init__.py
│   ├── models.py                       # User (with Role), Profile
│   ├── admin.py                        # User/Profile admin
│   ├── serializers.py                  # DRF serializers (Phase 1)
│   ├── views.py                        # Auth views (Phase 1)
│   └── urls.py                         # Auth endpoints (Phase 1)
│
├── 📂 audit/                           # Audit trail system
│   ├── __init__.py
│   ├── models.py                       # AuditTrail
│   ├── services.py                     # AuditService (logging)
│   ├── admin.py                        # Read-only audit admin
│   └── signals.py                      # Auto-logging signals (optional)
│
├── 📂 archive/                         # Archive/restore endpoints
│   ├── __init__.py
│   ├── views.py                        # Restore endpoints (Phase 5)
│   └── urls.py                         # Archive routes (Phase 5)
│
├── 📂 terms/                           # School years & semesters (Phase 2)
│   ├── __init__.py
│   ├── models.py                       # Term
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── 📂 courses/                         # Degree programs (Phase 2)
│   ├── __init__.py
│   ├── models.py                       # Course
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── 📂 subjects/                        # Academic subjects (Phase 2)
│   ├── __init__.py
│   ├── models.py                       # Subject, SubjectPrereq
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── 📂 sections/                        # Class sections (Phase 2)
│   ├── __init__.py
│   ├── models.py                       # Section, AssignedSubject
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── 📂 students/                        # Student profiles (Phase 2)
│   ├── __init__.py
│   ├── models.py                       # Student
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── 📂 enrollments/                     # Enrollment workflow (Phase 3)
│   ├── __init__.py
│   ├── models.py                       # Enrollment
│   ├── services.py                     # 30-unit cap logic
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── 📂 grades/                          # Grade encoding & INC (Phase 4)
│   ├── __init__.py
│   ├── models.py                       # GradeRecord, INCRecord
│   ├── services.py                     # INC policy logic
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tasks.py                        # Celery tasks (INC expiry)
│
├── 📂 analytics/                       # Analytics endpoints (Phase 6)
│   ├── __init__.py
│   ├── services.py                     # Computed stats
│   ├── views.py
│   └── urls.py
│
├── 📂 static/                          # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
│
├── 📂 staticfiles/                     # Collected static (collectstatic output)
│
├── 📂 media/                           # User uploads
│   ├── avatars/
│   └── documents/
│
├── 📂 templates/                       # Django templates
│   ├── base.html
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── dashboard/
│   │   ├── dean.html
│   │   ├── registrar.html
│   │   ├── admission.html
│   │   ├── professor.html
│   │   └── student.html
│   └── components/
│       ├── navbar.html
│       └── sidebar.html
│
├── 📂 tests/                           # Test suite
│   ├── __init__.py
│   ├── conftest.py                     # Pytest fixtures
│   ├── test_health.py
│   ├── test_core_models.py
│   ├── test_users.py                   # User model tests
│   ├── test_audit.py                   # Audit trail tests
│   └── ...                             # More tests per phase
│
├── 📂 requirements/                    # Python dependencies
│   ├── base.txt                        # Production dependencies
│   └── dev.txt                         # Development dependencies
│
├── 📂 .github/                         # GitHub specific files
│   └── workflows/
│       └── ci.yml                      # CI/CD pipeline
│
├── 📂 logs/                            # Application logs (production)
│
├── 📄 .env.template                    # Environment variables template
├── 📄 .env                             # Local environment (gitignored)
├── 📄 .gitignore                       # Git ignore rules
├── 📄 .pre-commit-config.yaml          # Pre-commit hooks
├── 📄 docker-compose.yml               # Docker services
├── 📄 Dockerfile                       # Docker image
├── 📄 docker-entrypoint.sh             # Container initialization
├── 📄 manage.py                        # Django management script
├── 📄 Makefile                         # Development commands
├── 📄 pytest.ini                       # Pytest configuration
├── 📄 ruff.toml                        # Ruff linter config
├── 📄 setup.sh                         # Setup script
├── 📄 README.md                        # Project documentation
├── 📄 PHASE_0_CHECKLIST.md             # Phase 0 completion checklist
└── 📄 PROJECT_STRUCTURE.md             # This file
```

---

## 🗂️ App Breakdown by Phase

### Phase 0 (Bootstrap) — COMPLETE ✅
- `config/` - Settings & URLs
- `core/` - Mixins & base models
- `users/` - User model with roles
- `audit/` - Audit trail
- `archive/` - Archive structure (endpoints in Phase 5)

### Phase 1 (Auth & Roles)
- `users/` - JWT endpoints, serializers, permissions
- `core/` - DRF permission classes

### Phase 2 (Academic Skeleton)
- `terms/` - School year/semester management
- `courses/` - Degree programs
- `subjects/` - Subjects + prerequisites
- `sections/` - Sections + professor assignment
- `students/` - Student profiles

### Phase 3 (Enrollment)
- `enrollments/` - Enrollment workflow + 30-unit cap

### Phase 4 (Grades & INC)
- `grades/` - Grade encoding + INC tracking

### Phase 5 (Archive & Audit)
- `archive/` - Restore endpoints
- Enhanced audit views

### Phase 6 (Analytics)
- `analytics/` - Dashboard data endpoints

---

## 📝 Key Design Patterns

### 1. **Archive Pattern**
All models with `ArchiveMixin` support:
- `.archive(user)` - Soft delete
- `.restore()` - Undelete
- `.objects.all()` - All records
- `.active.all()` - Active only (default manager)
- `.archived.all()` - Archived only

### 2. **Audit Pattern**
All mutations logged via `AuditService`:
```python
from audit.services import AuditService

AuditService.log(
    actor=request.user,
    action=AuditTrail.Action.UPDATE,
    instance=obj,
    old_instance=old_obj,
    request=request
)
```

### 3. **Role-Based Permissions**
```python
# In views
class SectionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsDean | IsReadOnly]
    
# Custom permissions in core/permissions.py
class IsDean(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_dean
```

### 4. **Template Inheritance**
```html
<!-- base.html -->
{% block content %}{% endblock %}

<!-- dashboard/dean.html -->
{% extends 'base.html' %}
{% block content %}
  <!-- Dean-specific content -->
{% endblock %}
```

---

## 🔧 Configuration Files

### Environment Variables (.env)
- `SECRET_KEY` - Django secret
- `DEBUG` - Debug mode
- `DATABASE_URL` - DB connection string
- `REDIS_URL` - Celery broker
- `SENTRY_DSN` - Error tracking
- `AWS_*` - S3 credentials (production)

### Settings Split
- **base.py** - Shared settings (DB, DRF, JWT)
- **dev.py** - SQLite, DEBUG=True, Django Debug Toolbar
- **prod.py** - PostgreSQL, S3, HTTPS enforcement

---

## 🚀 Quick Reference

### Create New App
```bash
python manage.py startapp <app_name>
```

### Add to INSTALLED_APPS
```python
# config/settings/base.py
INSTALLED_APPS = [
    ...
    '<app_name>',
]
```

### Register Admin
```python
# <app_name>/admin.py
from django.contrib import admin
from .models import MyModel

@admin.register(MyModel)
class MyModelAdmin(admin.ModelAdmin):
    list_display = ('field1', 'field2')
```

### Create Tests
```python
# tests/test_<app_name>.py
import pytest

@pytest.mark.django_db
class TestMyModel:
    def test_something(self):
        assert True
```

---

**Last Updated**: Phase 0 Bootstrap  
**Next**: Phase 1 — Auth & Roles