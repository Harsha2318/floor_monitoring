# Installation Fix Script - Simple Version#!/usr/bin/env pwsh

# No Unicode characters for better compatibility# Installation Fix Script for Employee Monitoring System



Write-Host "======================================"Write-Host "======================================" -ForegroundColor Cyan

Write-Host "Installation Fix Script"Write-Host "Installation Fix Script" -ForegroundColor Cyan

Write-Host "======================================"Write-Host "======================================" -ForegroundColor Cyan

Write-Host ""Write-Host ""



# Check if venv is activated# Ensure venv is activated

if (-not $env:VIRTUAL_ENV) {if (-not $env:VIRTUAL_ENV) {

    Write-Host "Activating virtual environment..."    Write-Host "Activating virtual environment..." -ForegroundColor Yellow

    & .\venv\Scripts\Activate.ps1    & .\venv\Scripts\Activate.ps1

}}



Write-Host "Virtual environment active"Write-Host "Virtual environment: $env:VIRTUAL_ENV" -ForegroundColor Green

Write-Host ""Write-Host ""



# Step 1: Build tools# Install build tools first

Write-Host "[1/6] Installing build dependencies..."Write-Host "[Step 1/6] Installing build dependencies..." -ForegroundColor Yellow

python -m pip install --upgrade pip setuptools wheelpython -m pip install --upgrade pip setuptools wheel

if ($LASTEXITCODE -ne 0) {if ($LASTEXITCODE -ne 0) {

    Write-Host "ERROR: Failed to install build tools"    Write-Host "ERROR: Failed to install build tools" -ForegroundColor Red

    exit 1    exit 1

}}

Write-Host "[OK] Build tools installed"Write-Host "✓ Build tools installed" -ForegroundColor Green

Write-Host ""Write-Host ""



# Step 2: NumPy# Install numpy with pre-built wheel (faster, no compilation needed)

Write-Host "[2/6] Installing numpy..."Write-Host "[Step 2/6] Installing numpy..." -ForegroundColor Yellow

pip install numpypip install numpy --no-cache-dir

if ($LASTEXITCODE -ne 0) {if ($LASTEXITCODE -ne 0) {

    Write-Host "ERROR: Failed to install numpy"    Write-Host "ERROR: Failed to install numpy" -ForegroundColor Red

    exit 1    exit 1

}}

Write-Host "[OK] NumPy installed"Write-Host "✓ NumPy installed" -ForegroundColor Green

Write-Host ""Write-Host ""



# Step 3: OpenCV# Install OpenCV

Write-Host "[3/6] Installing OpenCV..."Write-Host "[Step 3/6] Installing OpenCV..." -ForegroundColor Yellow

pip install opencv-python opencv-contrib-pythonpip install opencv-python opencv-contrib-python --no-cache-dir

if ($LASTEXITCODE -ne 0) {if ($LASTEXITCODE -ne 0) {

    Write-Host "ERROR: Failed to install OpenCV"    Write-Host "ERROR: Failed to install OpenCV" -ForegroundColor Red

    exit 1    exit 1

}}

Write-Host "[OK] OpenCV installed"Write-Host "✓ OpenCV installed" -ForegroundColor Green

Write-Host ""Write-Host ""



# Step 4: Flask# Install web framework

Write-Host "[4/6] Installing Flask and SocketIO..."Write-Host "[Step 4/6] Installing Flask and SocketIO..." -ForegroundColor Yellow

pip install Flask Flask-SocketIO Flask-CORS python-socketio python-engineiopip install Flask Flask-SocketIO Flask-CORS python-socketio python-engineio

if ($LASTEXITCODE -ne 0) {if ($LASTEXITCODE -ne 0) {

    Write-Host "ERROR: Failed to install Flask"    Write-Host "ERROR: Failed to install Flask" -ForegroundColor Red

    exit 1    exit 1

}}

Write-Host "[OK] Flask installed"Write-Host "✓ Flask installed" -ForegroundColor Green

Write-Host ""Write-Host ""



# Step 5: Core dependencies# Install core dependencies

Write-Host "[5/6] Installing core dependencies..."Write-Host "[Step 5/6] Installing core dependencies..." -ForegroundColor Yellow

pip install Pillow scipy SQLAlchemy python-dateutil pytest pytest-covpip install Pillow scipy SQLAlchemy python-dateutil

Write-Host "[OK] Core dependencies installed"if ($LASTEXITCODE -ne 0) {

Write-Host ""    Write-Host "WARNING: Some core dependencies failed" -ForegroundColor Yellow

}

# Step 6: Optional dependenciesWrite-Host "✓ Core dependencies installed" -ForegroundColor Green

Write-Host "[6/6] Installing optional dependencies..."Write-Host ""

pip install plyer

pip install mediapipe# Install optional dependencies (skip on failure)

Write-Host "[OK] Optional dependencies (some may have been skipped)"Write-Host "[Step 6/6] Installing optional dependencies..." -ForegroundColor Yellow

Write-Host ""Write-Host "  - MediaPipe (AI detection - optional)..." -ForegroundColor Gray

pip install mediapipe --no-cache-dir 2>$null

Write-Host "======================================"if ($LASTEXITCODE -eq 0) {

Write-Host "Verifying Installation"    Write-Host "    ✓ MediaPipe installed" -ForegroundColor Green

Write-Host "======================================"} else {

Write-Host ""    Write-Host "    ⚠ MediaPipe skipped (will use OpenCV)" -ForegroundColor Yellow

}

# Test critical imports

Write-Host "Testing OpenCV..."Write-Host "  - Testing framework..." -ForegroundColor Gray

python -c "import cv2; print('  Version:', cv2.__version__)"pip install pytest pytest-cov

Write-Host "    ✓ Pytest installed" -ForegroundColor Green

Write-Host "Testing Flask..."

python -c "import flask; print('  Version:', flask.__version__)"Write-Host "  - Alert system..." -ForegroundColor Gray

pip install plyer 2>$null

Write-Host "Testing NumPy..."if ($LASTEXITCODE -eq 0) {

python -c "import numpy; print('  Version:', numpy.__version__)"    Write-Host "    ✓ Plyer installed" -ForegroundColor Green

} else {

Write-Host "Testing SocketIO..."    Write-Host "    ⚠ Plyer skipped (notifications may not work)" -ForegroundColor Yellow

python -c "import flask_socketio; print('  OK')"}



Write-Host ""Write-Host ""

Write-Host "======================================"Write-Host "======================================" -ForegroundColor Cyan

Write-Host "Installation Complete!"Write-Host "Installation Summary" -ForegroundColor Cyan

Write-Host "======================================"Write-Host "======================================" -ForegroundColor Cyan

Write-Host ""Write-Host ""

Write-Host "Next steps:"

Write-Host "  1. python validate_system.py"# Verify critical packages

Write-Host "  2. python run.py"Write-Host "Verifying installation..." -ForegroundColor Yellow

Write-Host "  3. Open: http://localhost:5000"Write-Host ""

Write-Host ""

$allGood = $true

# Test imports
$testResult = python -c "import cv2; print('OK:', cv2.__version__)" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[PASS] OpenCV: $testResult" -ForegroundColor Green
} else {
    Write-Host "[FAIL] OpenCV: FAILED" -ForegroundColor Red
    $allGood = $false
}

$testResult = python -c "import flask; print('OK:', flask.__version__)" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[PASS] Flask: $testResult" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Flask: FAILED" -ForegroundColor Red
    $allGood = $false
}

$testResult = python -c "import numpy; print('OK:', numpy.__version__)" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[PASS] NumPy: $testResult" -ForegroundColor Green
} else {
    Write-Host "[FAIL] NumPy: FAILED" -ForegroundColor Red
    $allGood = $false
}

$testResult = python -c "import flask_socketio; print('OK')" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[PASS] Flask-SocketIO: OK" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Flask-SocketIO: FAILED" -ForegroundColor Red
    $allGood = $false
}

# Optional packages
$testResult = python -c "import mediapipe; print('OK')" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[PASS] MediaPipe: OK" -ForegroundColor Green
} else {
    Write-Host "[WARN] MediaPipe: Not available (will use OpenCV)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan

if ($allGood) {
    Write-Host "✓ Installation Complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Run: python validate_system.py" -ForegroundColor White
    Write-Host "  2. Run: python run.py" -ForegroundColor White
    Write-Host "  3. Open: http://localhost:5000" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "✗ Installation had errors" -ForegroundColor Red
    Write-Host ""
    Write-Host "Try manual installation:" -ForegroundColor Yellow
    Write-Host "  1. pip install --upgrade pip setuptools wheel" -ForegroundColor White
    Write-Host "  2. pip install -r requirements_minimal.txt" -ForegroundColor White
    Write-Host ""
    exit 1
}
