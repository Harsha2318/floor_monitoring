#!/bin/bash
# Installation Script for Linux/Mac
# Run with: bash install.sh

echo "======================================"
echo "Employee Monitoring System - Installer"
echo "======================================"
echo ""

# Check Python installation
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ from your package manager"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "Found: $PYTHON_VERSION"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists, skipping..."
else
    python3 -m venv venv
    if [ $? -eq 0 ]; then
        echo "Virtual environment created successfully"
    else
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "Installing dependencies (this may take several minutes)..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================"
    echo "Installation completed successfully!"
    echo "======================================"
    echo ""
    echo "To start the system:"
    echo "1. Activate virtual environment: source venv/bin/activate"
    echo "2. Run: python run.py"
    echo "3. Open browser: http://localhost:5000"
    echo ""
    echo "For quick start guide, see: QUICKSTART.md"
else
    echo ""
    echo "ERROR: Installation failed"
    echo "Please check error messages above"
    echo ""
    echo "Common issues:"
    echo "- For dlib/face_recognition errors: These are optional, you can disable face recognition"
    echo "- For compilation errors: Install build-essential and cmake"
    echo "- For network errors: Check internet connection and try again"
    exit 1
fi
