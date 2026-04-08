#!/bin/bash
# build.sh - Build deployable Copilot TUI application

set -e

# Configuration
PROJECT_NAME="copilot-tui"
VERSION="${VERSION:-0.1.0}"
PYTHON_VERSION="3.10"
BUILD_DIR="./build"
DIST_DIR="./dist"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Building Copilot TUI v${VERSION}${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}\n"

# Function to print status
status() {
    echo -e "${GREEN}✓${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check Python version
echo "Checking Python environment..."
PYTHON_INSTALLED=$(/bin/python3 --version 2>&1 | grep -oP '\d+\.\d+')
if ! command -v /bin/python3 &> /dev/null; then
    error "Python 3 is not installed"
    exit 1
fi
status "Python $PYTHON_INSTALLED found"

# Clean previous builds
echo -e "\nCleaning previous builds..."
rm -rf "$BUILD_DIR" "$DIST_DIR" build __pycache__ *.egg-info
status "Cleaned build directories"

# Install build dependencies
echo -e "\nInstalling build dependencies..."
/bin/python3 -m pip install --quiet --upgrade pip setuptools wheel build pyinstaller 2>&1 | grep -v "^Requirement already satisfied" || true
status "Dependencies installed"

# Install project dependencies
echo -e "\nInstalling project dependencies..."
if [ -f "requirements.txt" ]; then
    /bin/python3 -m pip install --quiet -r requirements.txt
    status "Project dependencies installed"
fi

# Build PyInstaller executable
echo -e "\nBuilding PyInstaller executable..."
/bin/python3 -m PyInstaller \
    --onefile \
    --name "$PROJECT_NAME" \
    --distpath "$DIST_DIR" \
    --workpath "$BUILD_DIR" \
    --specpath "$BUILD_DIR" \
    --add-data "$(pwd)/src/copilot_tui:copilot_tui" \
    --collect-all textual \
    --collect-all httpx \
    --hidden-import=httpx \
    --hidden-import=textual \
    --hidden-import=pydantic \
    --console \
    main.py

status "Built standalone executable: $DIST_DIR/$PROJECT_NAME"

# Create archives
echo -e "\nCreating distribution archives..."

# Tar.gz for Linux
tar -czf "$DIST_DIR/${PROJECT_NAME}-${VERSION}-linux-x86_64.tar.gz" \
    -C "$DIST_DIR" "$PROJECT_NAME"
status "Created: ${PROJECT_NAME}-${VERSION}-linux-x86_64.tar.gz"

# ZIP for Windows/cross-platform
cd "$DIST_DIR"
zip -q -r "${PROJECT_NAME}-${VERSION}-linux.zip" "$PROJECT_NAME"
cd ..
status "Created: ${PROJECT_NAME}-${VERSION}-linux.zip"

# Build Python wheel
echo -e "\nBuilding Python wheel package..."
/bin/python3 -m build --quiet 2>&1 | grep -v "^creating\|^running" || true
status "Built wheel packages"

# Display results
echo -e "\n${GREEN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          BUILD COMPLETE - OUTPUT SUMMARY           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}\n"

echo "📦 Standalone Executables:"
ls -lh "$DIST_DIR/$PROJECT_NAME" 2>/dev/null && echo "   Path: $DIST_DIR/$PROJECT_NAME\n" || true

echo "📦 Archives:"
ls -lh "$DIST_DIR"/${PROJECT_NAME}-${VERSION}* 2>/dev/null | awk '{print "   " $9 " (" $5 ")"}' || true

echo -e "\n📦 Python Packages:"
ls -lh dist/*.whl 2>/dev/null | awk '{print "   " $9 " (" $5 ")"}' || true
ls -lh dist/*.tar.gz 2>/dev/null | grep -v linux-x86_64 | awk '{print "   " $9 " (" $5 ")"}' || true

echo -e "\n${GREEN}DEPLOYMENT OPTIONS:${NC}\n"
echo "1. Use standalone executable:"
echo "   ./$DIST_DIR/$PROJECT_NAME --help"
echo ""
echo "2. Extract archive on target:"
echo "   tar -xzf $DIST_DIR/${PROJECT_NAME}-${VERSION}-linux-x86_64.tar.gz"
echo "   ./$PROJECT_NAME"
echo ""
echo "3. Install Python wheel:"
echo "   pip install $DIST_DIR/${PROJECT_NAME}-*.whl"
echo "   copilot-tui"
echo ""
echo "4. Docker build:"
echo "   docker build -t copilot-tui:latest ."
echo ""

echo -e "${YELLOW}Before running, set your API key:${NC}"
echo "   export COPILOT_API_KEY='your-github-copilot-api-key'"
echo ""

status "Build successful!"
