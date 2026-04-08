.PHONY: help install test build execute package docker clean release

# Variables
PYTHON := python3
PIP := pip3
VERSION := 0.1.0
PROJECT_NAME := copilot-tui
VENV_DIR := venv

help:
	@echo "Copilot TUI - Build and Deployment Commands"
	@echo ""
	@echo "Development:"
	@echo "  make install        Install dependencies"
	@echo "  make test          Run unit tests"
	@echo "  make execute       Run the application"
	@echo "  make lint          Run code linters"
	@echo "  make format        Format code with black"
	@echo ""
	@echo "Building:"
	@echo "  make build         Build PyInstaller executable"
	@echo "  make package       Build wheel and source distributions"
	@echo "  make docker        Build Docker image"
	@echo ""
	@echo "Deployment:"
	@echo "  make docker-run    Run application in Docker"
	@echo "  make docker-push   Push Docker image to registry"
	@echo "  make release       Create GitHub release artifacts"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean         Remove build artifacts"
	@echo "  make venv          Create and activate virtual environment"

# Development targets
install:
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -r requirements.txt
	$(PIP) install pytest pytest-asyncio build wheel pyinstaller
	@echo "✓ Dependencies installed"

test:
	@echo "Running tests..."
	$(PYTHON) -m pytest tests/ -v --tb=short
	@echo "✓ Tests completed"

execute:
	@echo "Running Copilot TUI..."
	$(PYTHON) main.py

lint:
	@echo "Running linters..."
	$(PIP) install pylint flake8 black isort 2>/dev/null || true
	pylint src/copilot_tui/*.py main.py || true
	flake8 src/copilot_tui/*.py main.py || true
	@echo "✓ Lint check complete"

format:
	@echo "Formatting code..."
	$(PIP) install black isort 2>/dev/null || true
	isort src/ main.py examples.py
	black src/ main.py examples.py
	@echo "✓ Code formatted"

# Build targets
build:
	@echo "Building PyInstaller executable..."
	bash build.sh

package:
	@echo "Building wheel and source distributions..."
	$(PYTHON) -m build
	@echo "✓ Packages built in dist/"

docker:
	@echo "Building Docker image..."
	docker build -t $(PROJECT_NAME):latest .
	docker tag $(PROJECT_NAME):latest $(PROJECT_NAME):$(VERSION)
	@echo "✓ Docker image built"
	docker images | grep $(PROJECT_NAME)

# Deployment targets
docker-run:
	@echo "Running Docker container..."
	docker run -it \
		-e "COPILOT_API_KEY=${COPILOT_API_KEY}" \
		-v $(PWD)/conversations:/app/conversations \
		$(PROJECT_NAME):latest

docker-compose-up:
	@echo "Starting with docker-compose..."
	docker-compose up

docker-compose-down:
	@echo "Stopping docker-compose services..."
	docker-compose down

docker-push:
	@echo "Pushing Docker image (set DOCKER_REGISTRY first)"
	docker tag $(PROJECT_NAME):latest $${DOCKER_REGISTRY}/$(PROJECT_NAME):$(VERSION)
	docker push $${DOCKER_REGISTRY}/$(PROJECT_NAME):$(VERSION)
	@echo "✓ Image pushed"

release:
	@echo "Creating release artifacts..."
	@mkdir -p release
	@cp dist/$(PROJECT_NAME)-$(VERSION)-linux-x86_64.tar.gz release/ 2>/dev/null || true
	@cp dist/$(PROJECT_NAME)_*-py3-none-any.whl release/ 2>/dev/null || true
	@cp dist/$(PROJECT_NAME)-*.tar.gz release/ 2>/dev/null || true
	@echo "✓ Release artifacts in release/"
	@ls -lh release/

# Maintenance targets
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build dist __pycache__ *.egg-info .pytest_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✓ Cleaned"

venv:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "✓ Virtual environment created"
	@echo "Activate with: source $(VENV_DIR)/bin/activate"

# Combined targets
all: clean install test build package docker
	@echo "✓ All builds complete!"

dev-setup: venv install
	@echo "✓ Development environment ready"
	@echo "Activate: source $(VENV_DIR)/bin/activate"

# WSL-specific targets
wsl-install:
	@echo "Setting up for WSL..."
	sudo apt-get update
	sudo apt-get install -y python3 python3-pip python3-venv
	make install
	@echo "✓ WSL environment ready"

# Distribution
dist: clean install test build package
	@echo "✓ Distribution packages ready in dist/"
	@ls -lh dist/

# Show version
version:
	@echo "Copilot TUI v$(VERSION)"
	@$(PYTHON) --version

# Check setup
check:
	@echo "Checking environment..."
	@command -v $(PYTHON) >/dev/null 2>&1 && echo "✓ Python installed" || echo "✗ Python not found"
	@command -v $(PIP) >/dev/null 2>&1 && echo "✓ pip installed" || echo "✗ pip not found"
	@[ -f requirements.txt ] && echo "✓ requirements.txt found" || echo "✗ requirements.txt not found"
	@[ -f main.py ] && echo "✓ main.py found" || echo "✗ main.py not found"
	@[ -d src/copilot_tui ] && echo "✓ Source directory found" || echo "✗ Source directory not found"
	@echo ""
	@$(PYTHON) -c "import sys; print(f'Python: {sys.version}')"
