#!/bin/bash
# Build script for p1person package
# This script cleans old builds and creates new distribution packages

set -e  # Exit on error

echo "==================================="
echo "p1person Package Build Script"
echo "==================================="
echo ""

# Step 1: Clean old build artifacts
echo "Step 1: Cleaning old build artifacts..."
rm -rf dist/ build/ *.egg-info/
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
echo "✓ Cleaned"
echo ""

# Step 2: Check if build tools are installed
echo "Step 2: Checking build tools..."
if ! python3 -c "import build" 2>/dev/null; then
    echo "Installing build tools..."
    pip install --upgrade build twine
fi
echo "✓ Build tools ready"
echo ""

# Step 3: Build the package
echo "Step 3: Building distributions..."
python3 -m build
echo "✓ Build complete"
echo ""

# Step 4: Check the distributions
echo "Step 4: Checking distributions..."
twine check dist/*
echo "✓ Distributions validated"
echo ""

# Step 5: List created files
echo "Step 5: Created distribution files:"
ls -lh dist/
echo ""

echo "==================================="
echo "Build Complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "  • Test locally: pip install dist/*.whl"
echo "  • Upload to TestPyPI: twine upload --repository testpypi dist/*"
echo "  • Upload to PyPI: twine upload dist/*"
echo ""
