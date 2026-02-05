#!/bin/bash
# Setup script for p1person
# Installs dependencies and runs initial configuration

echo "================================================="
echo "p1person - PingOne Custom Attribute Manager"
echo "Setup Script v0.2"
echo "================================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 is not installed"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment and install dependencies
echo "Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Run tests
echo "Running unit tests..."
python test_p1person.py
TEST_RESULT=$?
echo ""

if [ $TEST_RESULT -eq 0 ]; then
    echo "✓ All tests passed"
    echo ""
    echo "================================================="
    echo "Setup Complete!"
    echo "================================================="
    echo ""
    echo "To use p1person:"
    echo "  1. Activate the virtual environment:"
    echo "     source venv/bin/activate"
    echo ""
    echo "  2. Run p1person:"
    echo "     python p1person.py -n  # Initial setup"
    echo "     python p1person.py -h  # Show help"
    echo ""
    echo "  3. When done, deactivate:"
    echo "     deactivate"
    echo ""
else
    echo "❌ Some tests failed"
    echo "Please review the errors above"
    exit 1
fi
