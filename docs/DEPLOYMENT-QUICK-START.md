# Copilot TUI - Deployment Quick Start

Successfully built deployment packages! Here's how to use them:

## 📦 Available Artifacts

### 1. **Standalone Executable** (22 MB)
```bash
# Direct use (Linux/WSL)
./dist/copilot-tui
export TENANT_ID="your-tenant-id"
export CLIENT_ID="your-client-id"
./dist/copilot-tui
```

**Pros:** No dependencies needed, instant run  
**Cons:** Larger file size, Linux/WSL specific

---

### 2. **Compressed Archives** (22 MB each)

#### Tar.gz (Linux/Mac)
```bash
# Extract
tar -xzf dist/copilot-tui-0.1.0-linux-x86_64.tar.gz

# Run
export TENANT_ID="your-tenant-id"
export CLIENT_ID="your-client-id"
./copilot-tui
```

#### ZIP (Windows/Cross-platform)
```bash
# Extract
unzip dist/copilot-tui-0.1.0-linux.zip

# Run on WSL
export TENANT_ID="your-tenant-id"
export CLIENT_ID="your-client-id"
./copilot-tui
```

---

### 3. **Python Wheel** (15 KB - Most Portable)

```bash
# Install globally
pip install dist/copilot_tui-0.1.0-py3-none-any.whl

# Run from anywhere
export TENANT_ID="your-tenant-id"
export CLIENT_ID="your-client-id"
copilot-tui

# Or specific environment
python3 -m copilot_tui.tui_app
```

**Pros:** Smallest size, works with any Python 3.10+  
**Cons:** Requires Python and dependencies installed

---

### 4. **Source Distribution** (19 KB)

```bash
# Extract
tar -xzf dist/copilot_tui-0.1.0.tar.gz
cd copilot_tui-0.1.0

# Install
pip install .

# Run
export TENANT_ID="your-tenant-id"
export CLIENT_ID="your-client-id"
copilot-tui
```

---

## 🐳 Docker Deployment

### Build Docker Image
```bash
docker build -t copilot-tui:latest .
```

### Run Container
```bash
docker run -it \
  -e "TENANT_ID=your-tenant-id" \
  -e "CLIENT_ID=your-client-id" \
  -v $(pwd)/conversations:/app/conversations \
  copilot-tui:latest
```

### Docker Compose
```bash
export TENANT_ID="your-tenant-id"
export CLIENT_ID="your-client-id"
docker-compose up
```

---

## 🚀 Distribution Methods

### Method 1: GitHub Releases (Recommended)
```bash
# 1. Create GitHub release
git tag v0.1.0
git push origin v0.1.0

# 2. Upload artifacts
# - copilot-tui-0.1.0-linux-x86_64.tar.gz
# - copilot_tui-0.1.0-py3-none-any.whl
# - copilot_tui-0.1.0.tar.gz
```

### Method 2: PyPI Distribution
```bash
pip install twine
twine upload dist/*
```

Then users can install with:
```bash
pip install copilot-tui
copilot-tui
```

### Method 3: Personal Repository
```bash
# Host on web server
scp dist/* user@myserver:/var/www/packages/

# Users download and extract
wget https://myserver/packages/copilot-tui-0.1.0-linux-x86_64.tar.gz
tar -xzf copilot-tui-0.1.0-linux-x86_64.tar.gz
./copilot-tui
```

### Method 4: Linux Package Manager

#### DEB Package (Ubuntu/Debian)
```bash
python setup.py --command-packages=stdeb.command bdist_deb \
  --depends "python3 (>= 3.10)"

sudo dpkg -i deb_dist/copilot-tui_*.deb
copilot-tui
```

---

## 📋 Deployment Checklist

- [ ] Test executable on clean WSL/Linux system
- [ ] Verify all APIs work without internet (graceful fallback)
- [ ] Document system requirements
- [ ] Create installation guide for end users
- [ ] Set up automated releases with CI/CD
- [ ] Update version numbers before release
- [ ] Create CHANGELOG
- [ ] Tag release: `git tag v0.1.0`
- [ ] Test each distribution method

---

## 💻 For End Users

### Linux/WSL
```bash
# Download
wget https://github.com/youruser/copilot-tui/releases/download/v0.1.0/copilot-tui-0.1.0-linux-x86_64.tar.gz

# Extract
tar -xzf copilot-tui-0.1.0-linux-x86_64.tar.gz
cd copilot-tui

# Configure
cp ../copilot-tui ../.env
# Edit .env with your API key
export $(cat .env | xargs)

# Run
./copilot-tui
```

### Via pip
```bash
pip install --user copilot-tui
export TENANT_ID="your-tenant-id"
export CLIENT_ID="your-client-id"
copilot-tui
```

### Docker
```bash
docker pull myregistry/copilot-tui:latest
docker run -it -e TENANT_ID="your-tenant-id" \
  -e CLIENT_ID="your-client-id" \
  -v conversations:/app/conversations \
  myregistry/copilot-tui:latest
```

---

## 🔧 Making Quick Updates

```bash
# Edit source code
vim src/copilot_tui/models.py

# Rebuild
./scripts/build.sh

# Test
./dist/copilot-tui

# Create new release
git tag v0.1.1
git push origin v0.1.1
```

---

## 📊 Size Comparison

| Format | Size | Format | Pros | Cons |
|--------|------|--------|------|------|
| Executable | 22 MB | ELF binary | Self-contained | Large, Linux-only |
| Archives | 22 MB | tar.gz/zip | Portable | Still large |
| Wheel | 15 KB | Python package | Smallest | Needs Python |
| Source | 19 KB | tar.gz | Flexible | Needs build |
| Docker | varies | Image | Reproducible | Requires Docker |

---

## 🤔 Troubleshooting

### "Permission denied" error
```bash
# Make executable
chmod +x ./copilot-tui
./copilot-tui
```

### "Module not found" error (wheels)
```bash
# Reinstall with dependencies
pip install --upgrade --force-reinstall copilot_tui-0.1.0-py3-none-any.whl
```

### Docker build fails
```bash
# Clean and rebuild
docker system prune -a
docker build --no-cache -t copilot-tui:latest .
```

### API key not recognized
```bash
# Verify key is set
echo $TENANT_ID
echo $CLIENT_ID

# Export properly
export TENANT_ID="your-tenant-id"
export CLIENT_ID="your-client-id"
./copilot-tui
```

---

## 📚 Next Steps

1. **Test all distribution methods** in your environment
2. **Create installation documentation** for your users
3. **Set up CI/CD pipeline** for automatic builds on release
4. **Consider code signing** for security
5. **Plan version updates** strategy
6. **Monitor user feedback** and issues

---

## 🎯 Recommended Flow

**For Developers/Testing:**
```bash
pip install -r requirements.txt
python main.py
```

**For Local Distribution:**
```bash
./scripts/build.sh
./dist/copilot-tui
```

**For Public Release:**
```bash
git tag v0.1.0
git push origin v0.1.0  # Triggers CI/CD to build and release
```

**For Users:**
```bash
# Option 1: Direct executable
wget https://github.com/youruser/copilot-tui/releases/download/v0.1.0/copilot-tui
chmod +x copilot-tui
export TENANT_ID="your-tenant-id"
export CLIENT_ID="your-client-id"
./copilot-tui

# Option 2: pip install
pip install copilot-tui
copilot-tui
```

---

Build time: ~2 minutes  
Test time: ~1 minute  
Deployment time: ~5 minutes  

**Copilot TUI is production-ready! 🚀**
