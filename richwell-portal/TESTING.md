# RCI Testing & Quality Suite

Comprehensive testing infrastructure for the Richwell College Portal (RCI) system.

## Overview

This testing suite provides comprehensive coverage for:
- **Core Models**: TimeStampMixin, ArchiveMixin, and base functionality
- **User Management**: Authentication, roles, permissions, rate limiting
- **Student Management**: Student profiles, enrollments, status tracking
- **Grade Management**: Grade records, INC tracking, auto-expiration
- **Permissions**: Role-Based Access Control (RBAC) for all modules
- **Database Optimization**: Query performance and indexing

## Test Structure

```
richwell-portal/
├── core/
│   ├── tests.py              # Core mixin and permission tests
│   ├── test_utils.py         # Test utilities and factories
│   └── permissions.py        # Custom permission classes
├── users/
│   └── tests.py              # User model and auth tests
├── students/
│   └── tests.py              # Student model and API tests
├── grades/
│   └── tests.py              # Grade and INC system tests
├── .coveragerc               # Coverage configuration
├── pytest.ini                # Pytest configuration
└── TESTING.md               # This file
```

## Running Tests

### Run All Tests

```bash
cd richwell-portal
python manage.py test
```

### Run Tests for Specific Module

```bash
# Core tests
python manage.py test core

# User tests
python manage.py test users

# Student tests
python manage.py test students

# Grade tests
python manage.py test grades
```

### Run Tests with Coverage

```bash
# Install coverage if not already installed
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test

# Generate coverage report
coverage report

# Generate HTML coverage report
coverage html
# Open htmlcov/index.html in browser
```

### Run Specific Test Classes

```bash
# Run only permission tests
python manage.py test core.tests.PermissionTests

# Run only user model tests
python manage.py test users.tests.UserModelTest

# Run only grade tests
python manage.py test grades.tests.GradeRecordModelTest
```

## Test Categories

### 1. Core Module Tests (`core/tests.py`)

**TimeStampMixinTest**
- Created/updated timestamp functionality
- Automatic timestamp updates
- Age calculation
- Default ordering

**ArchiveMixinTest**
- Soft delete (archive) functionality
- Archive/restore methods
- Audit trail preservation
- Query filtering

**PermissionTests**
- Role-based permission classes
- Read/write permission separation
- Permission inheritance
- Composite permissions

**PermissionIntegrationTest**
- Object-level permissions
- Cross-module permission checks
- Permission with actual models

### 2. User Module Tests (`users/tests.py`)

**UserModelTest**
- User creation with roles
- Default role assignment
- Archive/restore functionality
- Timestamp tracking

**JWTAuthenticationTest**
- Token generation
- Token refresh
- Protected endpoint access
- Invalid credential handling

**LoginRateLimitingTest**
- Rate limit enforcement
- Failed attempt tracking
- Successful login bypass

**UserPermissionsByRoleTest**
- Role assignment validation
- Role-based access patterns

### 3. Student Module Tests (`students/tests.py`)

**StudentModelTest**
- Student profile creation
- Archive functionality
- Status management
- Unique constraints

**StudentEnrollmentTest**
- Enrollment creation
- Multiple enrollments
- Enrollment status tracking

**StudentGPACalculationTest**
- GPA calculation logic
- Weighted grade averaging
- Unit consideration

**StudentAPIPermissionsTest**
- Admin access to all students
- Registrar access patterns
- Student self-access
- Unauthenticated denial

### 4. Grade Module Tests (`grades/tests.py`)

**GradeRecordModelTest**
- Grade record creation
- Valid grade ranges (1.0-5.0)
- Passing/failing identification
- Archive functionality

**INCRecordModelTest**
- INC record creation
- Deadline calculation (6/12 months)
- Status transitions
- Expiration detection

**GradeEncodingTest**
- Professor grade encoding
- Enrollment association
- Grade validation

**INCExpirationSystemTest**
- Overdue INC identification
- Auto-conversion to 5.0
- Status updates

## Test Utilities

### Factory Classes (`core/test_utils.py`)

All factories support `create()` and `create_batch()` methods:

```python
from core.test_utils import UserFactory, StudentFactory, GradeRecordFactory

# Create single instances
user = UserFactory.create(role=User.Role.ADMIN)
student = StudentFactory.create(user=user)
grade = GradeRecordFactory.create(student=student, grade=Decimal('2.00'))

# Create multiple instances
users = UserFactory.create_batch(10, role=User.Role.STUDENT)
students = StudentFactory.create_batch(20)
```

Available factories:
- `UserFactory` - Users with roles
- `StudentFactory` - Student profiles
- `CourseFactory` - Degree programs
- `SubjectFactory` - Course subjects
- `TermFactory` - Academic terms
- `SectionFactory` - Class sections
- `AssignedSubjectFactory` - Professor assignments
- `EnrollmentFactory` - Student enrollments
- `GradeRecordFactory` - Grade records
- `INCRecordFactory` - Incomplete grades
- `NotificationFactory` - Notifications

### BaseTestCase

Provides authenticated clients for all roles:

```python
from core.test_utils import BaseTestCase

class MyTest(BaseTestCase):
    def test_admin_access(self):
        client = self.get_admin_client()
        response = client.get('/api/v1/students/')
        self.assertEqual(response.status_code, 200)
```

Available client methods:
- `get_admin_client()` - Admin user
- `get_dean_client()` - Dean user
- `get_registrar_client()` - Registrar user
- `get_professor_client()` - Professor user
- `get_student_client()` - Student user

## Database Optimizations

### Added Indexes

Performance indexes have been added via migrations:

**Students** (`students/migrations/0004_add_performance_indexes.py`):
- `student_status_arch_idx`: enrollment_status + archived
- `student_user_arch_idx`: user + archived
- `student_id_idx`: student_id
- `student_created_arch_idx`: created_at + archived

**Grades** (`grades/migrations/0004_add_performance_indexes.py`):
- `grade_student_term_idx`: student + term + archived
- `grade_subject_term_idx`: subject + term
- `grade_value_arch_idx`: grade + archived
- `inc_status_deadline_idx`: status + deadline_date
- `inc_deadline_status_idx`: deadline_date + status
- `inc_grade_status_idx`: grade_record + status

**Enrollments** (`enrollments/migrations/0003_add_performance_indexes.py`):
- `enroll_student_term_idx`: student + term + status
- `enroll_section_status_idx`: section + status
- `enroll_term_status_idx`: term + status + archived
- `enroll_student_arch_idx`: student + archived

**Users** (`users/migrations/0003_add_performance_indexes.py`):
- `user_role_active_idx`: role + is_active + archived
- `user_username_active_idx`: username + is_active
- `user_email_active_idx`: email + is_active
- `user_archived_at_idx`: archived + archived_at

### Apply Migrations

```bash
python manage.py migrate
```

## Custom Permissions

### Available Permission Classes

Located in `core/permissions.py`:

**Single Role Permissions:**
- `IsAdmin` - Admin only
- `IsDean` - Dean only
- `IsRegistrar` - Registrar only
- `IsProfessor` - Professor only
- `IsStudent` - Student only

**Combined Role Permissions:**
- `IsAdminOrDeanOrRegistrar` - Admin, Dean, or Registrar
- `IsAdminOrRegistrar` - Admin or Registrar
- `IsRegistrarOrAdmission` - Registrar or Admission

**Functional Permissions:**
- `CanManageCourses` - Course management
- `CanManageGrades` - Grade encoding/viewing
- `CanManageEnrollments` - Enrollment management
- `CanManageStudents` - Student profile management
- `CanArchiveRestore` - Archive/restore records

**Composite Permissions:**
- `CoursePermission` - Complete course access control
- `StudentPermission` - Complete student access control

### Usage in ViewSets

```python
from rest_framework import viewsets
from core.permissions import CoursePermission

class CourseViewSet(viewsets.ModelViewSet):
    permission_classes = [CoursePermission]
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
```

## Best Practices

### 1. Use Factories for Test Data

```python
# Good ✓
student = StudentFactory.create(enrollment_status='ACTIVE')

# Avoid ✗
student = Student.objects.create(
    user=user,
    student_id='2024-001',
    date_of_birth=datetime(2000, 1, 1).date(),
    # ... many more fields
)
```

### 2. Use BaseTestCase for API Tests

```python
# Good ✓
class MyAPITest(BaseTestCase):
    def test_api_access(self):
        client = self.get_admin_client()
        response = client.get('/api/v1/students/')

# Avoid ✗
class MyAPITest(TestCase):
    def test_api_access(self):
        user = User.objects.create(...)
        token = RefreshToken.for_user(user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
```

### 3. Test Both Positive and Negative Cases

```python
def test_student_can_view_own_grades(self):
    """Positive case"""
    client = self.get_student_client()
    response = client.get('/my-grades/')
    self.assertEqual(response.status_code, 200)

def test_student_cannot_view_other_grades(self):
    """Negative case"""
    other_student = StudentFactory.create()
    own_grades = GradeRecord.objects.filter(student=self.student)
    self.assertNotIn(other_student, [g.student for g in own_grades])
```

### 4. Clear Cache in Rate Limiting Tests

```python
def setUp(self):
    cache.clear()

def tearDown(self):
    cache.clear()
```

## Test Coverage Goals

Target coverage by module:
- **Core**: 95%+ (mixins, permissions)
- **Users**: 90%+ (authentication, roles)
- **Students**: 85%+ (profiles, enrollments)
- **Grades**: 90%+ (grading, INC system)
- **Overall**: 85%+

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install coverage
      - name: Run migrations
        run: python manage.py migrate
      - name: Run tests with coverage
        run: |
          coverage run --source='.' manage.py test
          coverage report
          coverage html
      - name: Upload coverage
        uses: actions/upload-artifact@v2
        with:
          name: coverage-report
          path: htmlcov/
```

## Troubleshooting

### Django Not Installed

```bash
pip install -r requirements.txt
```

### Database Errors

```bash
# Reset database
rm db.sqlite3
python manage.py migrate
```

### Import Errors

```bash
# Ensure you're in the correct directory
cd richwell-portal

# Set PYTHONPATH if needed
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Test Data Conflicts

```bash
# Use --keepdb to speed up tests, but be aware of data conflicts
python manage.py test --keepdb

# Or force fresh database
python manage.py test --noinput
```

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain coverage above 85%
4. Update this documentation
5. Add factories for new models

## Resources

- Django Testing Documentation: https://docs.djangoproject.com/en/stable/topics/testing/
- DRF Testing: https://www.django-rest-framework.org/api-guide/testing/
- Coverage.py: https://coverage.readthedocs.io/
- Factory Pattern: https://en.wikipedia.org/wiki/Factory_method_pattern
