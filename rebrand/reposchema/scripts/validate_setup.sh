#!/bin/bash
# Validation script for Repository Schema setup

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Validating Repository Schema setup..."
echo "Project root: $PROJECT_ROOT"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
    fi
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check Python installation
echo "Checking Python installation..."
python3 --version > /dev/null 2>&1
check_result $? "Python 3 is installed"

# Check VENV existence
echo ""
echo "Checking virtual environment..."
if [ -d "$PROJECT_ROOT/venv" ]; then
    check_result 0 "Virtual environment exists"
else
    check_result 1 "Virtual environment missing"
fi

# Check VENV activation
echo ""
echo "Checking virtual environment activation..."
if [ -n "$VIRTUAL_ENV" ] && [[ "$VIRTUAL_ENV" == *"$PROJECT_ROOT/venv"* ]]; then
    check_result 0 "Virtual environment is active"
else
    warning "Virtual environment not active (run: source venv/bin/activate)"
fi

# Check Python packages
echo ""
echo "Checking required Python packages..."
REQUIRED_PACKAGES=("rdflib" "pathspec" "fastapi" "uvicorn" "pydantic")

for package in "${REQUIRED_PACKAGES[@]}"; do
    if [ -n "$VIRTUAL_ENV" ]; then
        python3 -c "import $package" > /dev/null 2>&1
        check_result $? "Package '$package' is installed"
    else
        warning "Cannot check packages - virtual environment not active"
        break
    fi
done

# Check directories
echo ""
echo "Checking directory structure..."
DIRECTORIES=("utils" "log" "output" "scripts")

for dir in "${DIRECTORIES[@]}"; do
    if [ -d "$PROJECT_ROOT/$dir" ]; then
        check_result 0 "Directory '$dir' exists"
    else
        check_result 1 "Directory '$dir' missing"
    fi
done

# Check files
echo ""
echo "Checking required files..."
FILES=("repo-schema.py" "requirements.txt" "README.md")

for file in "${FILES[@]}"; do
    if [ -f "$PROJECT_ROOT/$file" ]; then
        check_result 0 "File '$file' exists"
    else
        check_result 1 "File '$file' missing"
    fi
done

# Check utility files
echo ""
echo "Checking utility files..."
UTILS=("utils/venv_manager.py" "utils/qdrant_client.py")

for util in "${UTILS[@]}"; do
    if [ -f "$PROJECT_ROOT/$util" ]; then
        check_result 0 "Utility '$util' exists"
    else
        check_result 1 "Utility '$util' missing"
    fi
done

# Check configuration
echo ""
echo "Checking configuration..."
if [ -f "$PROJECT_ROOT/.env" ]; then
    check_result 0 "Environment configuration file exists"
else
    warning "Environment configuration file missing (.env)"
fi

# Qdrant connection check (if Qdrant URL is configured)
echo ""
echo "Checking Qdrant connection..."
if [ -f "$PROJECT_ROOT/.env" ]; then
    QDRANT_URL=$(grep "^QDRANT_URL=" "$PROJECT_ROOT/.env" | cut -d'=' -f2)
    if [ -n "$QDRANT_URL" ]; then
        echo "Testing connection to: $QDRANT_URL"
        if command -v curl &> /dev/null; then
            curl -s --max-time 5 "$QDRANT_URL/health" > /dev/null 2>&1
            if [ $? -eq 0 ]; then
                check_result 0 "Qdrant connection successful"
            else
                warning "Cannot connect to Qdrant at $QDRANT_URL"
            fi
        else
            warning "curl not available for connection testing"
        fi
    else
        warning "Qdrant URL not configured in .env"
    fi
else
    warning "Cannot check Qdrant - .env file missing"
fi

echo ""
echo "Validation complete!"
echo ""
echo "Next steps:"
echo "1. If VENV is not active: source venv/bin/activate"
echo "2. If packages are missing: pip install -r requirements.txt"
echo "3. Configure .env file with your settings"
echo "4. Test with: python repo-schema.py --help"