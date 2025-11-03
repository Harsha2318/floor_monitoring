# 🎥 Quick Camera Setup Guide

Your Employee Monitoring System is **running successfully** on http://localhost:5000

## Current Status: ✅ OPERATIONAL
- Server running on port 5000
- Database initialized
- Detection engine ready (OpenCV)
- Alert system active

## 🚀 Quick Start: Add Your First Camera

### Option 1: Via Web Interface (Recommended)

1. **Open your browser** to: http://localhost:5000

2. **Click the "Configuration" tab** at the top

3. **Fill in the camera form:**
   ```
   Camera ID:   usb_camera_1
   Camera Name: Main Camera
   Type:        USB Camera
   Source:      0
   ```

4. **Click "Add Camera"**

5. **Go to "Live View" tab** and click the green **"Start"** button

### Option 2: Via API (For Testing)

Open a new PowerShell terminal and run:

```powershell
# Add a USB camera (device 0)
Invoke-RestMethod -Uri "http://localhost:5000/api/cameras/add" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"camera_id":"usb_0","name":"USB Camera","type":"usb","source":"0"}'

# Check if camera was added
Invoke-RestMethod -Uri "http://localhost:5000/api/cameras"

# Start monitoring
Invoke-RestMethod -Uri "http://localhost:5000/api/system/start" -Method POST
```

### Option 3: Pre-configure in Code

If you want cameras to auto-load on startup, edit `app/config.py`:

```python
CAMERA_CONFIGS = {
    'usb_cameras': [
        {'id': 0, 'name': 'USB Camera 1', 'type': 'usb'},
    ],
    'ip_cameras': [
        # Add IP cameras if you have them
        # {'url': 'rtsp://192.168.1.100:554/stream', 'name': 'IP Camera 1', 'type': 'ip'},
    ]
}
```

## 📋 Camera Source Numbers

Windows typically uses these device IDs:
- **0** = Built-in webcam or first USB camera
- **1** = Second camera (if available)
- **2** = Third camera (if available)

Try **0** first, if it doesn't work, try **1** or **2**.

## 🔍 Troubleshooting

### "Camera not working"
1. Check if another app is using the camera (close Zoom, Teams, etc.)
2. Try different source numbers: 0, 1, 2
3. Test your camera with Windows Camera app first

### "No video feed showing"
1. Make sure you clicked "Start" in the top-right
2. Wait 2-3 seconds for camera initialization
3. Check browser console (F12) for errors

### "Camera permission denied"
1. Close other apps using the camera
2. Restart the monitoring system
3. Check Windows camera privacy settings

## 🎯 What Happens Next?

Once you add a camera and start monitoring:

1. **Live View tab** - See real-time video with person detection boxes
2. **Presence Status tab** - View currently detected persons
3. **Alerts tab** - Get notified when someone leaves for >20 minutes
4. **History tab** - Review past entry/exit logs
5. **Statistics** - Dashboard shows metrics

## 🧪 Test the System

1. **Add camera** and **start monitoring**
2. **Walk in front of camera** - you should see a green detection box
3. **Check Presence Status** - should show "1 person present"
4. **Walk away from camera** - system will log your exit
5. **Wait 20 minutes** - you'll get an absence alert!

## 📊 API Endpoints Available

```bash
# Camera Management
GET    /api/cameras              # List all cameras
POST   /api/cameras/add          # Add new camera
POST   /api/cameras/<id>/remove  # Remove camera

# System Control
POST   /api/system/start         # Start monitoring
POST   /api/system/stop          # Stop monitoring
GET    /api/system/status        # Get system status

# Data Access
GET    /api/presence/active      # Currently present persons
GET    /api/presence/history     # Historical logs
GET    /api/alerts/active        # Active alerts
GET    /api/statistics           # System statistics

# Real-time
WS     /socket.io                # WebSocket for live updates
```

## 💡 Pro Tips

- **Multiple cameras**: Add as many as you need via the Configuration tab
- **IP cameras**: Use RTSP URLs like `rtsp://username:password@192.168.1.100:554/stream`
- **Performance**: If slow, reduce `MAX_FRAME_WIDTH` in `app/config.py`
- **Alert timeout**: Change `ABSENCE_TIMEOUT_MINUTES` in `app/config.py`

## 🎉 You're All Set!

Your system is ready to go. Just add a camera and start monitoring!

**Dashboard**: http://localhost:5000
**Status**: ✅ Running
**Port**: 5000
**Detection**: OpenCV (active)
**Database**: SQLite (ready)

---

Need help? Check the main README.md for full documentation.
