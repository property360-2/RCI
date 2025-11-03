#!/bin/bash
# Richwell College Portal - Setup Script (Cross-platform)
# setup.sh
set -e

echo "🎓 Richwell College Portal v3.0 - Setup"
echo "======================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Detect Python executable
echo -e "${BLUE}Checking Python version...${NC}"

if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v py &>/dev/null; then
    PYTHON=py
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo "❌ No Python found. Install Python 3.8+ first."
    exit 1
fi

python_version=$($PYTHON --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo -e "${BLUE}Creating virtual environment...${NC}"
$PYTHON -m venv venv

# Activate venv (Windows vs Linux/macOS)
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements/dev.txt

# Setup environment file
if [ ! -f .env ]; then
    echo -e "${BLUE}Creating .env file...${NC}"
    cp .env.template .env
    echo -e "${GREEN}✓ .env file created. Please update with your settings.${NC}"
else
    echo -e "${GREEN}✓ .env file already exists.${NC}"
fi

# Create necessary directories
echo -e "${BLUE}Creating directories...${NC}"
mkdir -p static staticfiles media logs

# Create Django apps
echo -e "${BLUE}Setting up Django apps...${NC}"

# Create config package
mkdir -p config/settings
touch config/__init__.py
touch config/settings/__init__.py

# Create core app
$PYTHON manage.py startapp core 2>/dev/null || echo "core app already exists"

# Create users app
$PYTHON manage.py startapp users 2>/dev/null || echo "users app already exists"

# Create audit app
$PYTHON manage.py startapp audit 2>/dev/null || echo "audit app already exists"

# Create archive app
$PYTHON manage.py startapp archive 2>/dev/null || echo "archive app already exists"

# Run migrations
echo -e "${BLUE}Running migrations...${NC}"
$PYTHON manage.py makemigrations
$PYTHON manage.py migrate

# Install pre-commit hooks
echo -e "${BLUE}Installing pre-commit hooks...${NC}"
pre-commit install

echo ""
echo -e "${GREEN}✓ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment manually if needed:"
echo "   - Linux/macOS: source venv/bin/activate"
echo "   - Windows Git Bash: source venv/Scripts/activate"
echo "2. Create superuser: $PYTHON manage.py createsuperuser"
echo "3. Run development server: $PYTHON manage.py runserver"
echo "4. Visit http://localhost:8000/healthz to verify"
echo ""
echo "For Docker setup, run: docker-compose up -d"
