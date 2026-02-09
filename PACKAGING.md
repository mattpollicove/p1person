# Packaging Guide for p1person

This guide provides instructions for packaging, distributing, and publishing the p1person application as a Python package.

## Table of Contents

- [Overview](#overview)
- [Package Structure](#package-structure)
- [Setup Configuration Files](#setup-configuration-files)
- [Building the Package](#building-the-package)
- [Local Installation](#local-installation)
- [Publishing to PyPI](#publishing-to-pypi)
- [Version Management](#version-management)
- [Distribution Best Practices](#distribution-best-practices)

---

## Overview

The p1person project can be packaged and distributed as a Python package, allowing users to install it via pip. This makes it easier to install dependencies, manage versions, and distribute the application.

**Current Version:** 0.2

---

## Package Structure

The current project structure is suitable for packaging. The recommended structure is:

```
P1person/
├── p1person.py                 # Main entry point
├── config_manager.py           # Configuration module
├── pingone_client.py           # PingOne API client
├── attribute_manager.py        # Attribute operations
├── logger.py                   # Logging functionality
├── test_p1person.py           # Test suite
├── requirements.txt           # Dependencies
├── setup.py                   # Package setup file (to create)
├── pyproject.toml            # Modern Python packaging (to create)
├── README.md                 # Documentation
├── LICENSE                   # License file
└── MANIFEST.in               # Include additional files (to create)
```

---

## Setup Configuration Files

### 1. Create `setup.py`

Create a `setup.py` file in the project root:

```python
#!/usr/bin/env python3
"""Setup script for p1person package."""

from setuptools import setup, find_packages
import os

# Read version from p1person.py
VERSION = "0.2"

# Read long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="p1person",
    version=VERSION,
    author="Your Name",
    author_email="your.email@example.com",
    description="PingOne Custom Attribute Management Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/p1person",
    py_modules=[
        "p1person",
        "config_manager",
        "pingone_client",
        "attribute_manager",
        "logger",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        "Topic :: System :: Systems Administration :: Authentication/Directory",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "p1person=p1person:main",
        ],
    },
    include_package_data=True,
    keywords="pingone ldap inetorgperson attributes identity management",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/p1person/issues",
        "Source": "https://github.com/yourusername/p1person",
        "Documentation": "https://github.com/yourusername/p1person#readme",
    },
)
```

**Note:** Update the `author`, `author_email`, and URLs with your actual information.

### 2. Create `pyproject.toml`

Modern Python packaging uses `pyproject.toml`. Create this file:

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "p1person"
version = "0.2"
description = "PingOne Custom Attribute Management Tool"
readme = "README.md"
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
license = {text = "MIT"}
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: System Administrators",
    "Intended Audience :: Developers",
    "Topic :: System :: Systems Administration :: Authentication/Directory",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Operating System :: OS Independent",
    "Environment :: Console",
]
keywords = ["pingone", "ldap", "inetorgperson", "attributes", "identity", "management"]
dependencies = [
    "requests>=2.31.0",
    "cryptography>=41.0.0",
]
requires-python = ">=3.7"

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "flake8>=6.0.0",
    "mypy>=1.0.0",
]

[project.urls]
Homepage = "https://github.com/yourusername/p1person"
Documentation = "https://github.com/yourusername/p1person#readme"
Repository = "https://github.com/yourusername/p1person"
"Bug Tracker" = "https://github.com/yourusername/p1person/issues"

[project.scripts]
p1person = "p1person:main"

[tool.setuptools]
py-modules = ["p1person", "config_manager", "pingone_client", "attribute_manager", "logger"]
```

### 3. Create `MANIFEST.in`

This file specifies additional files to include in the distribution:

```
include README.md
include LICENSE
include CHANGELOG.md
include QUICKSTART.md
include INSTALL.md
include requirements.txt
include p1person.prompt
include p1person.properties.example
recursive-exclude * __pycache__
recursive-exclude * *.py[co]
exclude .gitignore
exclude setup.sh
exclude setup.bat
exclude test_p1person.py
exclude p1person.properties
```

### 4. Update `p1person.py` Entry Point

Ensure your `p1person.py` has a proper main function:

```python
def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description='PingOne Custom Attribute Management Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    # ... rest of argument parsing ...
    # ... application logic ...

if __name__ == "__main__":
    main()
```

---

## Building the Package

### Install Build Tools

First, ensure you have the necessary build tools:

```bash
pip install --upgrade pip setuptools wheel build twine
```

### Build Distribution Packages

#### Using `build` (Recommended - Modern Approach)

```bash
python -m build
```

This creates both wheel and source distributions in the `dist/` directory:
- `p1person-0.2-py3-none-any.whl` (wheel distribution)
- `p1person-0.2.tar.gz` (source distribution)

#### Using `setup.py` (Traditional Approach)

```bash
# Create source distribution
python setup.py sdist

# Create wheel distribution
python setup.py bdist_wheel

# Create both
python setup.py sdist bdist_wheel
```

### Verify the Build

Check the contents of the distributions:

```bash
# List contents of wheel
unzip -l dist/p1person-0.2-py3-none-any.whl

# List contents of source distribution
tar -tzf dist/p1person-0.2.tar.gz
```

---

## Local Installation

### Install in Development Mode

For development, install the package in editable mode:

```bash
pip install -e .
```

This allows you to make changes to the code without reinstalling.

### Install from Local Build

```bash
pip install dist/p1person-0.2-py3-none-any.whl
```

### Install from Source

```bash
pip install .
```

### Verify Installation

After installation, you can run the tool directly:

```bash
p1person --help
p1person --version
p1person -d
```

---

## Publishing to PyPI

### Test PyPI (Recommended First)

Before publishing to the official PyPI, test on TestPyPI:

1. **Create TestPyPI Account**: Register at https://test.pypi.org/account/register/

2. **Create API Token**: 
   - Go to Account Settings → API tokens
   - Create a token for the entire account or specific project

3. **Configure `.pypirc`** (Optional):

```ini
[distutils]
index-servers =
    pypi
    testpypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token-here

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-your-production-api-token-here
```

4. **Upload to TestPyPI**:

```bash
twine upload --repository testpypi dist/*
```

5. **Test Installation from TestPyPI**:

```bash
pip install --index-url https://test.pypi.org/simple/ --no-deps p1person
```

### Production PyPI

1. **Create PyPI Account**: Register at https://pypi.org/account/register/

2. **Create API Token**: Similar to TestPyPI

3. **Upload to PyPI**:

```bash
twine upload dist/*
```

4. **Verify**:

```bash
pip install p1person
```

### Using Twine with Token (Recommended)

```bash
# Upload with token directly
twine upload -u __token__ -p pypi-your-api-token-here dist/*
```

---

## Version Management

### Updating Version Numbers

When releasing a new version, update the version in multiple locations:

1. **`p1person.py`**: Update the `VERSION` constant
2. **`setup.py`**: Update the `VERSION` variable
3. **`pyproject.toml`**: Update the `version` field
4. **`README.md`**: Update the version in the documentation
5. **`CHANGELOG.md`**: Add release notes for the new version

### Version Numbering Scheme

Follow Semantic Versioning (SemVer):
- **MAJOR.MINOR.PATCH** (e.g., 0.2.0)
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Tagging Releases

After publishing, tag the release in Git:

```bash
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin v0.2.0
```

---

## Distribution Best Practices

### Pre-Release Checklist

- [ ] Update version numbers in all files
- [ ] Update CHANGELOG.md with release notes
- [ ] Run all tests: `python -m unittest test_p1person.py`
- [ ] Verify README.md is current and accurate
- [ ] Check LICENSE file is correct
- [ ] Build distributions: `python -m build`
- [ ] Check distributions with `twine check dist/*`
- [ ] Test installation locally
- [ ] Test on TestPyPI before production release

### Clean Build Environment

Before building, clean old build artifacts:

```bash
# Remove old distributions
rm -rf dist/ build/ *.egg-info/

# Remove Python cache files
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
```

Or create a clean-up script:

```bash
#!/bin/bash
# clean.sh
rm -rf dist/ build/ *.egg-info/
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
echo "Build artifacts cleaned"
```

### Check Package Quality

```bash
# Check distribution files
twine check dist/*

# Verify package metadata
python setup.py check --metadata --strict
```

### Security Considerations

- **Never commit** `.pypirc` or API tokens to version control
- Use API tokens instead of passwords for PyPI
- Scope tokens to specific projects when possible
- Rotate tokens periodically
- Use environment variables for sensitive data in CI/CD

### Automation with GitHub Actions

Create `.github/workflows/publish.yml` for automated publishing:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.x'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Check package
      run: twine check dist/*
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

---

## Additional Resources

- **Python Packaging Guide**: https://packaging.python.org/
- **setuptools Documentation**: https://setuptools.pypa.io/
- **Twine Documentation**: https://twine.readthedocs.io/
- **PyPI**: https://pypi.org/
- **TestPyPI**: https://test.pypi.org/
- **Semantic Versioning**: https://semver.org/

---

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError` after installation
- **Solution**: Ensure all modules are listed in `py_modules` in setup.py

**Issue**: Entry point not working
- **Solution**: Verify the `main()` function exists and the entry point format is correct

**Issue**: Package files missing
- **Solution**: Check `MANIFEST.in` and ensure all necessary files are included

**Issue**: Twine upload fails with 403
- **Solution**: Check API token permissions and ensure the package name isn't already taken

**Issue**: Version conflict errors
- **Solution**: Ensure version numbers match across all configuration files

---

## Contact & Support

For issues related to packaging or distribution, please open an issue on the project's GitHub repository.

---

*Last Updated: February 9, 2026*
*Package Version: 0.2*
