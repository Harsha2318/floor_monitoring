# Quick Camera Setup Script for PowerShell
# This script adds a default USB camera and starts monitoring

Write-Host "========================================"
Write-Host "Adding USB Camera to Monitoring System"
Write-Host "========================================"
Write-Host ""

Write-Host "Waiting for server to be ready..."
Start-Sleep -Seconds 2

try {
    Write-Host "Adding camera (USB device 0)..."
    $response = Invoke-RestMethod -Uri "http://localhost:5000/api/cameras/add" `
        -Method POST `
        -ContentType "application/json" `
        -Body '{"camera_id":"usb_camera_1","name":"Main USB Camera","type":"usb","source":"0"}'
    
    Write-Host "Success: $($response.message)" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "Checking camera list..."
    $cameras = Invoke-RestMethod -Uri "http://localhost:5000/api/cameras"
    Write-Host "Cameras configured: $($cameras.Count)" -ForegroundColor Cyan
    foreach ($cam in $cameras) {
        Write-Host "  - $($cam.name) ($($cam.camera_id))" -ForegroundColor White
    }
    Write-Host ""
    
    Write-Host "Starting monitoring system..."
    $startResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/system/start" -Method POST
    Write-Host "Status: $($startResponse.status)" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "========================================"
    Write-Host "Camera Setup Complete!" -ForegroundColor Green
    Write-Host "========================================"
    Write-Host ""
    Write-Host "Open your browser to: http://localhost:5000" -ForegroundColor Cyan
    Write-Host "Go to 'Live View' tab to see the video feed" -ForegroundColor Cyan
    Write-Host ""
    
} catch {
    Write-Host "ERROR: Failed to add camera" -ForegroundColor Red
    Write-Host "Make sure the monitoring system is running (python run.py)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Error details: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Is the server running? Check http://localhost:5000" -ForegroundColor White
    Write-Host "  2. Try different source numbers: 0, 1, or 2" -ForegroundColor White
    Write-Host "  3. Close other apps using the camera" -ForegroundColor White
    Write-Host "  4. Test with Windows Camera app first" -ForegroundColor White
}

Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
