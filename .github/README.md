# GitHub Workflows for CliMaPan-Lab

This directory contains GitHub Actions workflows for automated testing, security checks, and releases.

## Workflows Overview

### 🔄 `ci.yml` - Continuous Integration (Quick Checks)
**Triggers:** Every push and pull request  
**Purpose:** Fast feedback loop for developers

**What it does:**
- ✅ Quick Python syntax and import checks  
- ✅ Code formatting verification (Black, isort)
- ✅ Basic functionality tests only
- ✅ Package import smoke test

**Runtime:** ~2-3 minutes

---

### 🧪 `test.yml` - Comprehensive Testing 
**Triggers:** Push/PR to main/develop branches, manual dispatch  
**Purpose:** Full test suite with multiple Python versions

**What it does:**
- 🐍 Tests on Python 3.8, 3.9, 3.10, 3.11
- 🧪 Runs all 5 test categories (60+ tests):
  - Basic functionality
  - Model components  
  - Examples validation
  - Integration tests
  - Performance tests (main branch only)
- 📊 Code coverage reports (uploaded to Codecov)
- 📦 Package building and installation tests
- 🎯 Custom test runner validation

**Jobs:**
- `test`: Multi-version testing matrix
- `performance-tests`: Heavy performance testing (main branch only)
- `package-test`: Package building and console script testing
- `examples-test`: Example script validation

**Runtime:** ~10-15 minutes per Python version

---

### 🔒 `security-and-deps.yml` - Security & Dependency Management
**Triggers:** Weekly (Mondays 9 AM UTC), dependency file changes, manual dispatch  
**Purpose:** Security monitoring and dependency maintenance

**What it does:**
- 🛡️ **Security Checks:**
  - Safety: Known security vulnerabilities
  - Pip-audit: Python package vulnerabilities  
  - Bandit: Security issues in source code
- 📦 **Dependency Management:**
  - Lists outdated packages
  - Tests compatibility with latest versions
- 📈 **Code Quality:**
  - Cyclomatic complexity analysis
  - Maintainability index calculation
  - Code metrics reporting

**Artifacts Generated:**
- Security reports (JSON format)
- Dependency update recommendations
- Code complexity reports

**Runtime:** ~5-8 minutes

---

### 🚀 `release.yml` - Automated Releases
**Triggers:** Git tags (v*), manual dispatch  
**Purpose:** Automated package releases

**What it does:**
- ✅ Pre-release testing (full test suite)
- 📦 Package building and validation
- 📝 Automatic changelog generation
- 🏷️ GitHub release creation with assets
- 🔄 Post-release tasks and notifications

**Optional Features:**
- PyPI publishing (commented out - requires API token)
- Release asset uploads
- Pre-release detection (alpha/beta/rc tags)

**Runtime:** ~8-12 minutes

---

## Usage Instructions

### For Developers

**Daily Development:**
- `ci.yml` runs automatically on every commit
- Focus on passing the quick CI checks first
- Full test suite runs on PRs to main/develop

**Before Merging:**
- Ensure all workflows pass
- Check code coverage reports
- Review any security warnings

**Releasing:**
```bash
# Create and push a version tag
git tag v1.0.0
git push origin v1.0.0

# Or use manual workflow dispatch on GitHub
```

### For Maintainers

**Weekly Reviews:**
- Check security & dependency reports
- Update outdated dependencies if needed
- Review code complexity trends

**Release Process:**
1. Ensure main branch is stable
2. Update version in `setup.py`/`pyproject.toml`
3. Create git tag: `git tag v1.x.x`
4. Push tag: `git push origin v1.x.x`
5. Workflow automatically creates GitHub release

### Workflow Status Badges

Add these to your main README.md:

```markdown
[![CI](https://github.com/yourusername/CliMaPan-Lab/workflows/CI/badge.svg)](https://github.com/yourusername/CliMaPan-Lab/actions?query=workflow%3ACI)
[![Tests](https://github.com/yourusername/CliMaPan-Lab/workflows/Tests/badge.svg)](https://github.com/yourusername/CliMaPan-Lab/actions?query=workflow%3ATests)
[![Security](https://github.com/yourusername/CliMaPan-Lab/workflows/Security%20%26%20Dependencies/badge.svg)](https://github.com/yourusername/CliMaPan-Lab/actions?query=workflow%3A%22Security+%26+Dependencies%22)
```

## Configuration

### Required Secrets
- `GITHUB_TOKEN`: Automatically provided by GitHub
- `PYPI_API_TOKEN`: Required only if enabling PyPI publishing

### Optional Enhancements
- **Codecov Integration**: Sign up at codecov.io for detailed coverage reports
- **PyPI Publishing**: Uncomment lines in `release.yml` and add PyPI token
- **Slack/Discord Notifications**: Add notification steps to workflows

## Troubleshooting

**Common Issues:**

1. **Tests failing on specific Python version:**
   - Check compatibility in your code
   - Update requirements if needed

2. **Security warnings:**
   - Review and update vulnerable dependencies
   - Check if warnings are false positives

3. **Performance tests timing out:**
   - Adjust timeout values in workflow
   - Consider splitting into smaller test chunks

4. **Package build failures:**
   - Verify setup.py/pyproject.toml configuration
   - Check MANIFEST.in for missing files

**Getting Help:**
- Check workflow logs in GitHub Actions tab
- Review test outputs and error messages
- Consult the main project README for setup instructions 