#!/bin/bash
# Setup script for Repository Schema VENV

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Setting up Python virtual environment for Repository Schema..."
echo "Project root: $PROJECT_ROOT"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "Warning: Python $PYTHON_VERSION detected. Python $REQUIRED_VERSION+ recommended."
fi

# Create VENV if it doesn't exist
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$PROJECT_ROOT/venv"
else
    echo "Virtual environment already exists."
fi

# Activate VENV and install requirements
echo "Activating virtual environment and installing dependencies..."
source "$PROJECT_ROOT/venv/bin/activate"

if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r "$PROJECT_ROOT/requirements.txt"
    echo "Dependencies installed successfully."
else
    echo "Warning: requirements.txt not found in $PROJECT_ROOT"
fi

# Create necessary directories
echo "Creating output directories..."
mkdir -p "$PROJECT_ROOT/log"
mkdir -p "$PROJECT_ROOT/output/schemas"
mkdir -p "$PROJECT_ROOT/output/docs"

# Create .env template if it doesn't exist
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    cat > "$PROJECT_ROOT/.env" << 'EOF'
# Repository Schema Configuration

# Qdrant Configuration
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=

# VS Code Integration
VSCODE_EXTENSION_PATH=

# Logging
LOG_LEVEL=INFO
LOG_FILE=log/reposchema.log

# Development
DEBUG=false
EOF
    echo "Created .env template. Please configure your settings."
fi

echo ""
echo "Setup complete!"
echo ""
echo "To activate the virtual environment:"
echo "  source $PROJECT_ROOT/venv/bin/activate"
echo ""
echo "To run the repository schema generator:"
echo "  python $PROJECT_ROOT/repo-schema.py"
echo ""
echo "To validate setup:"
echo "  $PROJECT_ROOT/scripts/validate_setup.sh"