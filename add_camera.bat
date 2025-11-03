@echo off
REM Quick Camera Setup Script for Windows
REM This script adds a default USB camera and starts monitoring

echo ========================================
echo Adding USB Camera to Monitoring System
echo ========================================
echo.

echo Waiting for server to be ready...
timeout /t 2 /nobreak >nul

echo Adding camera (USB device 0)...
curl -X POST http://localhost:5000/api/cameras/add ^
  -H "Content-Type: application/json" ^
  -d "{\"camera_id\":\"usb_camera_1\",\"name\":\"Main USB Camera\",\"type\":\"usb\",\"source\":\"0\"}"

echo.
echo.

echo Checking camera list...
curl http://localhost:5000/api/cameras
echo.
echo.

echo Starting monitoring system...
curl -X POST http://localhost:5000/api/system/start
echo.
echo.

echo ========================================
echo Camera Setup Complete!
echo ========================================
echo.
echo Open your browser to: http://localhost:5000
echo Go to "Live View" tab to see the video feed
echo.
echo If camera doesn't work:
echo   - Try source "1" or "2" instead of "0"
echo   - Close other apps using the camera
echo   - Check Windows Camera app first
echo.
pause
