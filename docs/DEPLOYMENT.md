# Deployment Guide: Copilot TUI Application

This guide covers multiple methods to package and deploy the Copilot TUI application.

## Option 1: PyInstaller (Recommended for Standalone Executables)

### Installation

```bash
pip install pyinstaller
```

### Create Standalone Executable

```bash
# Create a single-file executable
pyinstaller --onefile --name copilot-tui \
  --add-data "src/copilot_tui:copilot_tui" \
  --collect-all textual \
  --collect-all httpx \
  main.py

# Executable will be in: dist/copilot-tui
```

### Configuration File for Reproducible Builds

Create `copilot-tui.spec`:

```bash
pyinstaller --onefile --specpath . \
  --name copilot-tui \
  --add-data "src/copilot_tui:copilot_tui" \
  --collect-all textual \
  --collect-all httpx \
  --distpath ./dist \
  --buildpath ./build \
  --hidden-import=textual \
  --hidden-import=httpx \
  main.py
```

### Using the Spec File

```bash
pyinstaller copilot-tui.spec
```

### Distribution

```bash
# Create tarball
cd dist
tar -czf copilot-tui-linux-x86_64.tar.gz copilot-tui
zip -r copilot-tui-linux.zip copilot-tui
```

---

## Option 2: Python Wheels (Recommended for Package Managers)

### Build Distribution

```bash
pip install build wheel
python -m build
```

This creates:
- `dist/*.whl` (Universal binary wheel)
- `dist/*.tar.gz` (Source distribution)

### Installation from Wheel

```bash
pip install copilot_tui-0.1.0-py3-none-any.whl

# Then run with:
copilot-tui
```

### Upload to PyPI

```bash
pip install twine
twine upload dist/*
```

---

## Option 3: Docker Containerization

### Create Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Set API key placeholder
ENV TENANT_ID=""
ENV CLIENT_ID=""

# Run the application
CMD ["python", "main.py"]
```

### Build Docker Image

```bash
docker build -t copilot-tui:latest .
docker tag copilot-tui:latest yourregistry/copilot-tui:0.1.0
```

### Run Container

```bash
docker run -it -e "TENANT_ID=your-tenant-id" \
  -e "CLIENT_ID=your-client-id" copilot-tui:latest
```

### Push to Registry

```bash
docker push yourregistry/copilot-tui:0.1.0
```

---

## Option 4: System Package (DEB for Ubuntu/Debian)

### Install Tools

```bash
pip install stdeb
```

### Create DEB Package

```bash
python setup.py --command-packages=stdeb.command bdist_deb
```

Package will be in `deb_dist/`:

```bash
sudo dpkg -i deb_dist/copilot-tui_0.1.0-1_all.deb
copilot-tui  # Run the app
```

---

## Option 5: Virtual Environment Bundle

### Create Portable Bundle

```bash
#!/bin/bash
# build-bundle.sh

mkdir -p copilot-tui-bundle
cd copilot-tui-bundle

# Create venv
python3 -m venv venv
source venv/bin/activate

# Install package
pip install --upgrade pip
pip install -r ../requirements.txt
cp -r ../src .
cp ../main.py .

# Create launcher script
cat > run.sh << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/venv/bin/activate"
export TENANT_ID="your-tenant-id"
export CLIENT_ID="your-client-id"
cd "$SCRIPT_DIR"
python main.py "$@"
EOF

chmod +x run.sh
cd ..

# Create archive
tar -czf copilot-tui-bundle.tar.gz copilot-tui-bundle/
```

### Use Bundle

```bash
tar -xzf copilot-tui-bundle.tar.gz
cd copilot-tui-bundle
export TENANT_ID="your-tenant-id"
export CLIENT_ID="your-client-id"
./run.sh
```

---

## Option 6: GitHub Releases

### Automated Builds with GitHub Actions

Create `.github/workflows/release.yml`:

```yaml
name: Build and Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install pyinstaller wheel build
          pip install -r requirements.txt
      
      - name: Build executable
        run: |
          pyinstaller --onefile \
            --add-data "src/copilot_tui:copilot_tui" \
            --collect-all textual \
            --collect-all httpx \
            main.py
      
      - name: Create archives
        run: |
          tar -czf copilot-tui-linux-x86_64.tar.gz dist/copilot-tui
          cd dist && zip -r ../copilot-tui-linux.zip copilot-tui && cd ..
      
      - name: Build wheel
        run: python -m build
      
      - name: Create release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            copilot-tui-linux-x86_64.tar.gz
            dist/copilot_tui-*.whl
            dist/copilot_tui-*.tar.gz
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

Deploy by pushing a tag:

```bash
git tag v0.1.0
git push origin v0.1.0
# GitHub Actions automatically builds and releases
```

---

## Comparison Table

| Method | Ease | Size | Portability | Dependencies | Best For |
|--------|------|------|-------------|--------------|----------|
| PyInstaller | ⭐⭐⭐⭐ | Large | High | None | Standalone apps, end users |
| Wheel | ⭐⭐⭐⭐⭐ | Small | High | pip | Package managers, PyPI |
| Docker | ⭐⭐⭐ | Very Large | Very High | Docker | Cloud, servers, CI/CD |
| DEB | ⭐⭐⭐ | Medium | Medium | dpkg | Linux/Ubuntu systems |
| Venv Bundle | ⭐⭐⭐⭐ | Medium | High | Python | Developers, testing |
| Source | ⭐⭐⭐⭐⭐ | Tiny | High | None | Git distribution |

---

## Recommended Deployment Strategy

### For End Users (Linux/WSL)
```bash
# Build PyInstaller executable
pyinstaller --onefile --add-data "src/copilot_tui:copilot_tui" \
  --collect-all textual --collect-all httpx main.py

# Distribution
tar -czf copilot-tui-linux-x86_64.tar.gz dist/copilot-tui
# Upload to GitHub Releases
```

### For Deployment on Servers
```bash
# Option A: Docker
docker build -t copilot-tui:latest .
docker push myregistry/copilot-tui:latest

# Option B: Python Package
python -m build
pip install dist/copilot_tui-0.1.0-py3-none-any.whl
```

### For Development/Testing
```bash
# Keep using source installation
pip install -r requirements.txt
python main.py
```

---

## Troubleshooting PyInstaller

### Issue: Module not found
```bash
# Add to PyInstaller command:
--hidden-import=module_name
```

### Issue: Textual not rendering
```bash
# Ensure all Textual plugins are collected:
--collect-submodules textual
```

### Issue: WSL path issues
```bash
# Convert Windows paths if running from WSL:
import os
if os.name == 'nt':
    # Windows path handling
```

### Creating a Spec File for Customization

```python
# copilot-tui.spec
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('src/copilot_tui', 'copilot_tui')],
    hiddenimports=['textual', 'httpx'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='copilot-tui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

---

## Distribution Checklist

- [ ] Test build process on target system
- [ ] Verify all dependencies are bundled
- [ ] Create version tags (git tag v0.1.0)
- [ ] Update CHANGELOG
- [ ] Test deployment on clean system
- [ ] Create README for deployment
- [ ] Publish to appropriate channel (GitHub, PyPI, etc.)
- [ ] Document system requirements
- [ ] Provide installation instructions
- [ ] Set up CI/CD for automated builds

---

## Quick Start Templates

### Build Everything At Once

```bash
#!/bin/bash
set -e

VERSION="0.1.0"

echo "Building PyInstaller executable..."
pyinstaller --onefile --name copilot-tui \
  --add-data "src/copilot_tui:copilot_tui" \
  --collect-all textual --collect-all httpx main.py

echo "Creating archives..."
tar -czf dist/copilot-tui-${VERSION}-linux-x86_64.tar.gz -C dist copilot-tui
cd dist && zip -r copilot-tui-${VERSION}-linux.zip copilot-tui && cd ..

echo "Building wheel..."
python -m build

echo "✓ Builds complete!"
echo "  - Executable: dist/copilot-tui"
echo "  - Archive: dist/copilot-tui-${VERSION}-linux-x86_64.tar.gz"
echo "  - Wheel: dist/copilot_tui-${VERSION}-py3-none-any.whl"
```

---

## For WSL Specific Deployment

```bash
# Create Windows-compatible launcher
cat > launch.cmd << 'EOF'
@echo off
cd /d "%~dp0"
wsl -d Ubuntu python main.py %*
EOF

# Or create PowerShell script
cat > launch.ps1 << 'EOF'
wsl -d Ubuntu -e python main.py $args
EOF
```

---

**Choose the method that best fits your use case. PyInstaller is recommended for most situations.**
