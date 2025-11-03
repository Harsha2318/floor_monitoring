@echo off
REM Quick Start Script for Windows
REM Double-click this file to start the system

echo ========================================
echo Employee Monitoring System
echo Quick Start Script
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo ERROR: Virtual environment not found!
    echo Please run install.ps1 first.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if activation worked
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo.
echo Starting Employee Monitoring System...
echo.
echo The system will start shortly.
echo Once started, open your browser to:
echo   http://localhost:5000
echo.
echo Press Ctrl+C to stop the system
echo ========================================
echo.

REM Start the application
python run.py

REM If we get here, the application stopped
echo.
echo System stopped.
pause
