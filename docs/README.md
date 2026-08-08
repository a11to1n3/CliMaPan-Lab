# CliMaPan-Lab Documentation

This directory contains the complete documentation for CliMaPan-Lab, built with Sphinx and designed for deployment on Read the Docs.

## 🚀 Quick Setup for Read the Docs

### Step 1: Connect to Read the Docs

1. Go to [readthedocs.org](https://readthedocs.org)
2. Sign in with your GitHub account
3. Click "Import a Project"
4. Select the `CliMaPan-Lab` repository
5. Click "Next" and configure:
   - **Name**: `climapan-lab`
   - **Repository URL**: `https://github.com/a11to1n3/CliMaPan-Lab`
   - **Default Branch**: `main`
   - **Language**: `English`
   - **Programming Language**: `Python`

### Step 2: Configure Build Settings

The `.readthedocs.yaml` file in the project root automatically configures:
- ✅ Python 3.10 environment
- ✅ Sphinx documentation builder
- ✅ Required dependencies installation
- ✅ PDF and ePub generation

### Step 3: Optional - Set up Webhook for GitHub Actions

To enable automatic builds triggered by GitHub Actions:

1. In your Read the Docs project, go to Admin → Integrations
2. Copy the webhook URL
3. Add it as a GitHub secret:
   - Go to GitHub repository Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `RTD_WEBHOOK_URL`
   - Value: The webhook URL from Read the Docs

## 📖 Documentation Structure

```
docs/
├── conf.py                 # Sphinx configuration
├── index.rst               # Main documentation page
├── installation.rst        # Install & ambr>=0.4.7 pins
├── quickstart.rst          # First simulation (daily steps, Polars results)
├── amber.rst               # AMBER API, monthly recording, vectorized/OOP checks
├── calibration.rst         # Calibration pipeline & evaluation notes
├── climate.rst             # Climate module
├── odd_protocol.rst        # ODD+D model description
├── api/                    # API documentation
│   ├── index.rst
│   ├── model.rst
│   └── agents.rst
├── contributing.rst
├── changelog.rst
├── license.rst
├── requirements.txt
├── Makefile
└── _static/
```

User-facing summary of the same topics also lives in the repository root ``README.md``.

## 🔨 Building Documentation Locally

### Prerequisites

```bash
pip install -r requirements.txt
```

### Build Commands

```bash
# Quick build
cd docs
make html

# Or using Sphinx directly
sphinx-build -b html . _build/html

# Clean build
make clean
make html

# Check for broken links
make linkcheck
```

### Using the Automation Script

```bash
# Basic build
python scripts/update_docs.py

# Full update with all checks
python scripts/update_docs.py --all

# Clean build with link checking
python scripts/update_docs.py --clean --check-links

# Update API docs and trigger RTD build
python scripts/update_docs.py --update-api --trigger-rtd
```

## 🔄 Automatic Updates

Documentation automatically updates when:

- ✅ Code is pushed to `main` branch
- ✅ Documentation files are modified
- ✅ API changes are made in the codebase
- ✅ GitHub Actions workflow runs successfully

The GitHub Actions workflow (`.github/workflows/docs.yml`) handles:

1. **Build Verification** - Ensures docs build without errors
2. **Link Checking** - Validates all external links
3. **GitHub Pages Deployment** - Backup hosting on GitHub Pages
4. **Read the Docs Trigger** - Automatic RTD build triggering
5. **Docstring Coverage** - Code documentation quality checks

## 📊 Documentation Quality

### Docstring Coverage

The project uses `interrogate` to monitor docstring coverage:

```bash
# Check coverage
interrogate climapan_lab/ --ignore-init-method --ignore-magic --fail-under=50

# Generate coverage badge
interrogate climapan_lab/ --generate-badge docs/_static/
```

### Link Validation

```bash
# Check all external links
cd docs
sphinx-build -b linkcheck . _build/linkcheck
```

## 🌐 Accessing Documentation

Once deployed, documentation will be available at:

- **Latest Version**: https://climapan-lab.readthedocs.io/en/latest/
- **Stable Version**: https://climapan-lab.readthedocs.io/en/stable/
- **GitHub Pages**: https://a11to1n3.github.io/CliMaPan-Lab/docs/

## 🛠️ Troubleshooting

### Common Issues

**Build Fails on Read the Docs**
- Check the build log in RTD admin panel
- Verify all dependencies are in `docs/requirements.txt`
- Ensure `.readthedocs.yaml` is properly configured

**Missing API Documentation**
- Run `python scripts/update_docs.py --update-api`
- Check that modules have proper docstrings
- Verify import paths in `docs/api/*.rst` files

**Links Not Working**
- Run link check: `make linkcheck`
- Update broken external links
- Check internal cross-references

**Webhook Not Triggering**
- Verify `RTD_WEBHOOK_URL` secret is set in GitHub
- Check webhook URL in Read the Docs admin panel
- Ensure GitHub Actions workflow has necessary permissions

### Manual Build Trigger

If automatic builds aren't working:

1. Go to your RTD project admin
2. Click "Builds" tab
3. Click "Build Version" button
4. Select "latest" and click "Build"

## 📝 Contributing to Documentation

### Adding New Pages

1. Create new `.rst` file in appropriate directory
2. Add to table of contents in parent `index.rst`
3. Use proper RST formatting and cross-references

### Updating API Documentation

API documentation is auto-generated from code docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief description of the function.
    
    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2
        
    Returns:
        Description of return value
        
    Example:
        >>> example_function("test", 42)
        True
    """
    return True
```

### Writing Style Guide

- Use clear, concise language
- Include code examples where helpful
- Cross-reference related sections
- Follow Google/NumPy docstring conventions
- Test all code examples

## 🎯 Next Steps

1. **Set up Read the Docs account** and import the repository
2. **Configure webhook** for automatic builds (optional)
3. **Customize domain** (optional): Configure custom domain in RTD settings
4. **Add more content**: Examples, tutorials, advanced guides
5. **Monitor coverage**: Keep docstring coverage above 50% 