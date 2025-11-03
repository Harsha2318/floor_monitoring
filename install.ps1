# Installation Script for Windows
# Run this in PowerShell with: .\install.ps1

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Employee Monitoring System - Installer" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}
Write-Host "Found: $pythonVersion" -ForegroundColor Green

# Create virtual environment
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists, skipping..." -ForegroundColor Yellow
} else {
    python -m venv venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Virtual environment created successfully" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host ""
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install requirements
Write-Host ""
Write-Host "Installing dependencies (this may take several minutes)..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "======================================" -ForegroundColor Green
    Write-Host "Installation completed successfully!" -ForegroundColor Green
    Write-Host "======================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "To start the system:" -ForegroundColor Cyan
    Write-Host "1. Make sure virtual environment is activated: .\venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host "2. Run: python run.py" -ForegroundColor White
    Write-Host "3. Open browser: http://localhost:5000" -ForegroundColor White
    Write-Host ""
    Write-Host "For quick start guide, see: QUICKSTART.md" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "ERROR: Installation failed" -ForegroundColor Red
    Write-Host "Please check error messages above" -ForegroundColor Red
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "- For dlib/face_recognition errors: These are optional, you can disable face recognition" -ForegroundColor White
    Write-Host "- For compilation errors: Install Visual C++ Build Tools" -ForegroundColor White
    Write-Host "- For network errors: Check internet connection and try again" -ForegroundColor White
    exit 1
}
