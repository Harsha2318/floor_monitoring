#!/bin/bash
# Quick Start Script for Linux/Mac
# Run with: bash start.sh or ./start.sh

echo "========================================"
echo "Employee Monitoring System"
echo "Quick Start Script"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please run install.sh first."
    echo ""
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi

echo ""
echo "Starting Employee Monitoring System..."
echo ""
echo "The system will start shortly."
echo "Once started, open your browser to:"
echo "  http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the system"
echo "========================================"
echo ""

# Start the application
python run.py

# If we get here, the application stopped
echo ""
echo "System stopped."
