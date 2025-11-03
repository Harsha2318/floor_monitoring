# Quick Start Guide

## Installation (5 minutes)

1. **Install Python 3.8+**
   - Download from [python.org](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"

2. **Open PowerShell in Project Directory**
   ```powershell
   cd C:\Users\harsh\floor_monitoring
   ```

3. **Create Virtual Environment**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

4. **Install Dependencies**
   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

   **If errors occur**, install core packages first:
   ```powershell
   pip install Flask Flask-SocketIO Flask-CORS opencv-python numpy mediapipe SQLAlchemy plyer
   ```

## First Run (2 minutes)

1. **Start the Server**
   ```powershell
   python run.py
   ```

2. **Open Browser**
   - Navigate to: `http://localhost:5000`

3. **Add a Camera**
   - Click "Configuration" tab
   - Fill in camera details:
     - Camera ID: `usb_0`
     - Camera Name: `Webcam`
     - Type: Select "USB Camera"
     - Source: `0` (for first USB camera)
   - Click "Add Camera"

4. **Start Monitoring**
   - Click the green "Start" button
   - Switch to "Live View" tab to see video feed

## Basic Usage

### View Live Cameras
- Click "Live View" tab
- See detected persons with bounding boxes

### Monitor Presence
- Click "Presence Status" tab
- View currently present employees
- See entry times and duration

### Check Alerts
- Click "Alerts" tab
- View employees who have been absent
- Click "Acknowledge" to clear alerts

### Review History
- Click "History" tab
- Select date range
- Click "Filter" to view logs

## Common Issues

### Camera Not Working
- Try source values: 0, 1, 2
- Check if camera is used by another app
- Test camera with Windows Camera app first

### Slow Performance
- Edit `app/config.py`:
  ```python
  FRAME_SKIP = 3  # Process fewer frames
  MAX_FRAME_WIDTH = 320  # Smaller size
  ```

### Detection Not Working
- Switch to simpler model in `app/config.py`:
  ```python
  DETECTION_MODEL = 'opencv'
  ```

## Configuration Examples

### Multiple USB Cameras
```python
# app/config.py
CAMERA_CONFIGS = {
    'usb_cameras': [
        {'id': 0, 'name': 'Entrance', 'type': 'usb'},
        {'id': 1, 'name': 'Workspace', 'type': 'usb'},
    ]
}
```

### IP Camera
```python
# app/config.py
CAMERA_CONFIGS = {
    'ip_cameras': [
        {'url': 'rtsp://admin:password@192.168.1.100/stream', 
         'name': 'IP Cam 1', 'type': 'ip'},
    ]
}
```

### Adjust Alert Timeout
```python
# app/config.py
ABSENCE_TIMEOUT_MINUTES = 15  # Alert after 15 minutes
```

## Next Steps

1. **Add Employees** (Optional)
   - For face recognition
   - Add photos to `data/faces/` folder
   - Filename: `employee_id.jpg`

2. **Review Logs**
   - Check `data/logs/app.log` for details

3. **Backup Data**
   - Backup `data/monitoring.db` regularly

## Getting Help

Check logs: `data/logs/app.log`

Common log locations:
- Detection issues: Search for "Detection" in logs
- Camera issues: Search for "Camera" in logs
- Alert issues: Search for "Alert" in logs

## Stopping the System

1. In the web interface, click "Stop" button
2. Close the browser
3. Press `Ctrl+C` in PowerShell to stop server
4. Deactivate virtual environment:
   ```powershell
   deactivate
   ```

## Minimum Test Configuration

To test quickly with minimal requirements:

```python
# app/config.py
DEBUG = True
DETECTION_MODEL = 'opencv'  # Lightest model
FRAME_SKIP = 3
MAX_FRAME_WIDTH = 320
MAX_FRAME_HEIGHT = 240
FACE_RECOGNITION_ENABLED = False
CAMERA_CONFIGS = {
    'usb_cameras': [
        {'id': 0, 'name': 'Test Camera', 'type': 'usb'},
    ],
    'ip_cameras': []
}
```

Then run:
```powershell
python run.py
```

You should see the system start and be able to access it at `http://localhost:5000`.
