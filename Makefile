.PHONY: help install migrate test lint format clean run docker-up docker-down

help:
	@echo "Richwell College Portal - Available Commands"
	@echo "=============================================="
	@echo "install      - Install dependencies"
	@echo "migrate      - Run database migrations"
	@echo "test         - Run tests with coverage"
	@echo "lint         - Run code quality checks"
	@echo "format       - Format code with black and isort"
	@echo "clean        - Remove cache and temp files"
	@echo "run          - Run development server"
	@echo "shell        - Open Django shell"
	@echo "superuser    - Create superuser"
	@echo "docker-up    - Start Docker containers"
	@echo "docker-down  - Stop Docker containers"
	@echo "collectstatic - Collect static files"

install:
	pip install -r requirements/dev.txt
	pre-commit install

migrate:
	python manage.py makemigrations
	python manage.py migrate

test:
	pytest --cov --cov-report=html --cov-report=term

lint:
	ruff check .
	black --check .
	isort --check-only .

format:
	black .
	isort .
	ruff check --fix .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage .pytest_cache/

run:
	python manage.py runserver

shell:
	python manage.py shell_plus

superuser:
	python manage.py createsuperuser

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

collectstatic:
	python manage.py collectstatic --noinput --clear

# Database commands
db-reset:
	rm -f db.sqlite3
	python manage.py migrate

# Backup commands
backup:
	python manage.py dumpdata --natural-foreign --natural-primary --indent 2 > backup_$$(date +%Y%m%d_%H%M%S).json

# Development workflow
dev: install migrate run

# Production workflow
deploy: lint test collectstatic
	@echo "✓ All checks passed. Ready to deploy!"