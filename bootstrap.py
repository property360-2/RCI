#!/usr/bin/env python3
"""
Richwell College Portal v3.0 - Bootstrap Script
Generates the complete Django project structure for Phase 0
"""

import os
import subprocess
from pathlib import Path

def create_directory_structure():
    """Create the complete project directory structure"""
    
    dirs = [
        # Root directories
        "richwell_portal",
        "richwell_portal/config",
        "richwell_portal/config/settings",
        
        # Core apps
        "richwell_portal/core",
        "richwell_portal/core/management",
        "richwell_portal/core/management/commands",
        "richwell_portal/core/migrations",
        "richwell_portal/core/tests",
        
        "richwell_portal/users",
        "richwell_portal/users/migrations",
        "richwell_portal/users/tests",
        "richwell_portal/users/templates",
        "richwell_portal/users/templates/users",
        
        "richwell_portal/audit",
        "richwell_portal/audit/migrations",
        "richwell_portal/audit/tests",
        
        "richwell_portal/archive",
        "richwell_portal/archive/migrations",
        "richwell_portal/archive/tests",
        
        "richwell_portal/students",
        "richwell_portal/students/migrations",
        "richwell_portal/students/tests",
        "richwell_portal/students/templates",
        "richwell_portal/students/templates/students",
        
        "richwell_portal/courses",
        "richwell_portal/courses/migrations",
        "richwell_portal/courses/tests",
        "richwell_portal/courses/templates",
        "richwell_portal/courses/templates/courses",
        
        "richwell_portal/subjects",
        "richwell_portal/subjects/migrations",
        "richwell_portal/subjects/tests",
        "richwell_portal/subjects/templates",
        "richwell_portal/subjects/templates/subjects",
        
        "richwell_portal/sections",
        "richwell_portal/sections/migrations",
        "richwell_portal/sections/tests",
        "richwell_portal/sections/templates",
        "richwell_portal/sections/templates/sections",
        
        "richwell_portal/enrollments",
        "richwell_portal/enrollments/migrations",
        "richwell_portal/enrollments/tests",
        "richwell_portal/enrollments/templates",
        "richwell_portal/enrollments/templates/enrollments",
        
        "richwell_portal/grades",
        "richwell_portal/grades/migrations",
        "richwell_portal/grades/tests",
        "richwell_portal/grades/templates",
        "richwell_portal/grades/templates/grades",
        
        "richwell_portal/terms",
        "richwell_portal/terms/migrations",
        "richwell_portal/terms/tests",
        
        # Static and media
        "richwell_portal/static",
        "richwell_portal/static/css",
        "richwell_portal/static/js",
        "richwell_portal/static/images",
        "richwell_portal/media",
        "richwell_portal/media/documents",
        
        # Templates
        "richwell_portal/templates",
        "richwell_portal/templates/base",
        "richwell_portal/templates/components",
        
        # Tests
        "tests",
        "tests/integration",
        "tests/fixtures",
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        # Create __init__.py for Python packages
        if not dir_path.endswith(('static', 'media', 'templates', 'images', 'css', 'js', 'documents', 'fixtures')):
            init_file = Path(dir_path) / "__init__.py"
            init_file.touch(exist_ok=True)
    
    print("✅ Directory structure created successfully!")

def create_requirements():
    """Create requirements files"""
    
    base_requirements = """# Base requirements for all environments
Django==5.0.1
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.1
django-cors-headers==4.3.1
django-environ==0.11.2
psycopg2-binary==2.9.9
Pillow==10.2.0
python-dateutil==2.8.2

# Testing
pytest==7.4.4
pytest-django==4.7.0
pytest-cov==4.1.0
factory-boy==3.3.0

# Code quality
ruff==0.1.14
black==23.12.1
mypy==1.8.0
django-stubs==4.2.7

# Utilities
python-dotenv==1.0.0
"""

    dev_requirements = """# Development requirements
-r base.txt

# Debugging
django-debug-toolbar==4.2.0
ipython==8.20.0

# Documentation
drf-spectacular==0.27.0
"""

    prod_requirements = """# Production requirements
-r base.txt

# Production server
gunicorn==21.2.0
whitenoise==6.6.0

# Monitoring
sentry-sdk==1.39.2

# CDN/Storage (optional - uncomment as needed)
# django-storages==1.14.2
# boto3==1.34.25
# django-cloudinary-storage==0.3.0
"""

    Path("requirements").mkdir(exist_ok=True)
    Path("requirements/base.txt").write_text(base_requirements)
    Path("requirements/dev.txt").write_text(dev_requirements)
    Path("requirements/prod.txt").write_text(prod_requirements)
    
    print("✅ Requirements files created!")

def create_env_templates():
    """Create .env templates"""
    
    env_template = """# Django Core
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,richwell.local

# Database (SQLite for testing, PostgreSQL for production)
DATABASE_URL=sqlite:///db.sqlite3
# For PostgreSQL: postgresql://user:password@localhost:5432/richwell_portal

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
CORS_ALLOW_CREDENTIALS=True

# JWT
JWT_SECRET=your-jwt-secret-here
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440

# CDN/Static (Optional - uncomment as needed)
# CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name
# AWS_ACCESS_KEY_ID=
# AWS_SECRET_ACCESS_KEY=
# AWS_STORAGE_BUCKET_NAME=
# AWS_S3_REGION_NAME=
# CDN_URL=https://cdn.richwell.edu

# Email (for production)
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=
# EMAIL_HOST_PASSWORD=

# Monitoring (Optional)
# SENTRY_DSN=
"""

    env_example = env_template.replace("your-secret-key-here-change-in-production", "django-insecure-example-key-DO-NOT-USE-IN-PRODUCTION")
    
    Path(".env.template").write_text(env_template)
    Path(".env.example").write_text(env_example)
    
    # Create actual .env if it doesn't exist
    if not Path(".env").exists():
        Path(".env").write_text(env_example)
    
    print("✅ Environment templates created!")

def create_gitignore():
    """Create .gitignore file"""
    
    gitignore = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/
.venv

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
/media
/staticfiles
.coverage
htmlcov/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
coverage.xml
*.cover

# Node (if needed later)
node_modules/
npm-debug.log
yarn-error.log
"""

    Path(".gitignore").write_text(gitignore)
    print("✅ .gitignore created!")

def create_docker_files():
    """Create Docker configuration files"""
    
    dockerfile = """FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    postgresql-client \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/base.txt requirements/
RUN pip install --no-cache-dir -r requirements/base.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
"""

    docker_compose = """version: '3.8'

services:
  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
    
  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=richwell_portal
      - POSTGRES_USER=richwell
      - POSTGRES_PASSWORD=richwell123
    ports:
      - "5432:5432"

volumes:
  postgres_data:
"""

    Path("Dockerfile").write_text(dockerfile)
    Path("docker-compose.yml").write_text(docker_compose)
    print("✅ Docker files created!")

def create_precommit_config():
    """Create pre-commit configuration"""
    
    precommit = """repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-merge-conflict
      
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.14
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.11
"""

    Path(".pre-commit-config.yaml").write_text(precommit)
    print("✅ Pre-commit configuration created!")

def create_pytest_config():
    """Create pytest configuration"""
    
    pytest_ini = """[tool:pytest]
DJANGO_SETTINGS_MODULE = config.settings.test
python_files = tests.py test_*.py *_tests.py
addopts = 
    --verbose
    --cov=richwell_portal
    --cov-report=html
    --cov-report=term-missing
    --ds=config.settings.test
testpaths = tests
"""

    pyproject = """[tool.black]
line-length = 100
target-version = ['py311']
include = '\\.pyi?$'
extend-exclude = '''
/(
  # directories
  \\.eggs
  | \\.git
  | \\.hg
  | \\.mypy_cache
  | \\.tox
  | \\.venv
  | build
  | dist
  | migrations
)/
'''

[tool.ruff]
line-length = 100
target-version = "py311"
exclude = [
    ".git",
    "__pycache__",
    "migrations",
    ".venv",
]

[tool.ruff.lint]
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "B",  # flake8-bugbear
    "C4",  # flake8-comprehensions
]
ignore = [
    "E501",  # line too long (handled by black)
    "B008",  # do not perform function calls in argument defaults
]

[tool.mypy]
python_version = "3.11"
check_untyped_defs = true
ignore_missing_imports = true
warn_unused_ignores = true
warn_redundant_casts = true
warn_unused_configs = true
plugins = ["mypy_django_plugin.main"]

[tool.django-stubs]
django_settings_module = "config.settings.base"
"""

    Path("pytest.ini").write_text(pytest_ini)
    Path("pyproject.toml").write_text(pyproject)
    print("✅ Test configuration created!")

def create_readme():
    """Create README.md"""
    
    readme = """# 🧩 Richwell College Portal v3.0

A modular, archive-first academic system covering enrollment, grade encoding, transferee mapping, section/curriculum management, and student analytics.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+ (optional, SQLite for testing)
- Docker & Docker Compose (optional)

### Local Setup

1. **Clone and setup virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements/dev.txt
```

2. **Setup environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Run migrations**
```bash
cd richwell_portal
python manage.py migrate
python manage.py createsuperuser
```

4. **Seed demo data**
```bash
python manage.py seed_demo
```

5. **Run development server**
```bash
python manage.py runserver
```

Visit http://localhost:8000

### Docker Setup

```bash
docker-compose up --build
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py seed_demo
```

## 📋 Development Workflow

### Running Tests
```bash
pytest
pytest --cov  # With coverage
```

### Code Quality
```bash
ruff check .
black .
mypy richwell_portal
```

### Pre-commit Hooks
```bash
pre-commit install
pre-commit run --all-files
```

## 🏗️ Architecture

### Apps Structure
- **core**: Common mixins, utilities, pagination, permissions
- **users**: Authentication, roles, profiles
- **students**: Student profiles, documents
- **courses**: Programs, curricula
- **subjects**: Subjects, prerequisites
- **sections**: Sections, capacity, professor assignment
- **enrollments**: Student-subject linking, unit cap
- **grades**: Grade encoding, INC records
- **terms**: School years, semesters
- **archive**: Restore endpoints, archive views
- **audit**: Audit trail logging

## 🎨 Design System

- **Primary**: Purple `#6B4EFF`
- **Accent**: Yellow `#FFD740`
- **Background**: White `#FFFFFF`
- **Surface**: Light Gray `#F7F7FB`

## 📖 Documentation

- [API Documentation](http://localhost:8000/api/docs/)
- [Development Plan](docs/PLAN.md)
- [Database Schema](docs/SCHEMA.md)

## 🧪 Testing

Run the test suite:
```bash
pytest -v
pytest --cov --cov-report=html
```

## 📦 Phase 0 - Completed ✅

- [x] Project structure
- [x] Settings split (base/dev/test/prod)
- [x] Docker configuration
- [x] CI/CD configuration
- [x] Environment templates
- [x] Testing setup

## 🚧 Current Phase

**Phase 1 - Auth & Roles** (In Progress)

## 📄 License

Proprietary - Richwell College

## 👥 Contributors

Built with ❤️ for Richwell College
"""

    Path("README.md").write_text(readme)
    print("✅ README created!")

def main():
    """Main bootstrap function"""
    print("🚀 Starting Richwell College Portal v3.0 Bootstrap...")
    print("=" * 60)
    
    create_directory_structure()
    create_requirements()
    create_env_templates()
    create_gitignore()
    create_docker_files()
    create_precommit_config()
    create_pytest_config()
    create_readme()
    
    print("=" * 60)
    print("✨ Bootstrap complete!")
    print("\n📝 Next steps:")
    print("1. cd richwell_portal")
    print("2. python -m venv venv")
    print("3. source venv/bin/activate  # Windows: venv\\Scripts\\activate")
    print("4. pip install -r requirements/dev.txt")
    print("5. Run the Django project setup script")

if __name__ == "__main__":
    main()