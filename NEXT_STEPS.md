# 🎉 SYSTEM RUNNING - Quick Action Guide

## ✅ Current Status
Your Employee Monitoring System is **LIVE** and **OPERATIONAL**!

```
Server: ✅ Running on http://localhost:5000
Dashboard: ✅ Accessible and loading
API: ✅ All endpoints responding (200 OK)
WebSocket: ✅ Real-time updates active
Detection: ✅ OpenCV initialized
Database: ✅ SQLite ready
Monitoring: Ready to start (click green "Start" button)
```

## 📸 Add Your First Camera - 3 Easy Ways

### 🖱️ **Option 1: Via Dashboard (EASIEST)**

1. **You're already in the dashboard!** Look at the top navigation tabs
2. **Click "Configuration" tab**
3. **Fill in the form:**
   - Camera ID: `usb_camera_1`
   - Camera Name: `Main Camera`
   - Type: Select "USB Camera"
   - Source: `0` (try 1 or 2 if 0 doesn't work)
4. **Click "Add Camera" button**
5. **Go to "Live View" tab**
6. **Click the green "Start" button** in top-right
7. **You should see video!** 🎥

### 💻 **Option 2: Via PowerShell Script**

Open a NEW PowerShell terminal (don't close the one running the server):

```powershell
cd C:\Users\harsh\floor_monitoring
.\add_camera.ps1
```

This automatically adds a USB camera and starts monitoring!

### 🔧 **Option 3: Via API Command**

Open a NEW PowerShell terminal:

```powershell
# Add camera
Invoke-RestMethod -Uri "http://localhost:5000/api/cameras/add" -Method POST -ContentType "application/json" -Body '{"camera_id":"usb_0","name":"USB Camera","type":"usb","source":"0"}'

# Start monitoring
Invoke-RestMethod -Uri "http://localhost:5000/api/system/start" -Method POST
```

## 🎥 Finding Your Camera Source Number

Windows camera device IDs:
- **0** = Primary camera (usually built-in webcam)
- **1** = Secondary camera
- **2** = Third camera

**Test your camera first:**
- Open Windows Camera app
- Make sure camera works
- Close the Camera app before using monitoring system

## 🎯 What Each Tab Does

| Tab | Purpose | What You'll See |
|-----|---------|----------------|
| **Live View** | Real-time video | Video feeds with green boxes around detected persons |
| **Presence Status** | Who's present now | List of currently detected persons with entry times |
| **Alerts** | Absence notifications | Alerts when someone is gone >20 min |
| **History** | Past logs | Complete entry/exit history with timestamps |
| **Configuration** | System settings | Add/remove cameras, view system config |

## 🚀 Quick Test Procedure

1. **Add Camera** (see options above)
2. **Click "Start"** in top-right (green button)
3. **Go to "Live View" tab**
4. **Walk in front of camera** - you'll see a green box around you
5. **Check "Presence Status"** - should show you're present
6. **Walk away** - system logs your exit
7. **Wait 20 minutes** (or change timeout in config.py) - you'll get an alert!

## ⚙️ Customization (Optional)

Edit `app/config.py` to change settings:

```python
# Alert timeout (minutes before alert)
ABSENCE_TIMEOUT_MINUTES = 20  # Change to 1 for testing

# Detection model
DETECTION_MODEL = 'opencv'  # or 'mediapipe' if installed

# Frame processing
FRAME_SKIP = 2  # Process every 2nd frame (higher = faster but less accurate)
MAX_FRAME_WIDTH = 640  # Lower = faster processing
```

After changing config, **restart the server** (Ctrl+C, then `python run.py`)

## 🐛 Troubleshooting

### Camera Not Working?
```powershell
# Test different source numbers
# Try 0, 1, or 2 in the Configuration tab
Source: 0  # First try
Source: 1  # If 0 doesn't work
Source: 2  # If 1 doesn't work
```

### "Cannot capture from camera" Error?
1. **Close other apps** using camera (Zoom, Teams, Skype)
2. **Check Windows Privacy Settings**:
   - Settings → Privacy → Camera
   - Allow desktop apps to access camera
3. **Restart the server**: Ctrl+C, then `python run.py`

### No Detection Boxes Showing?
- Make sure you clicked the **green "Start" button**
- Stand in good lighting
- Move around a bit to trigger detection
- Check you're in "Live View" tab

### Server Stopped Working?
```powershell
# Restart it
cd C:\Users\harsh\floor_monitoring
python run.py
```

## 📊 API Reference (For Developers)

```bash
# System Control
POST /api/system/start       # Start monitoring
POST /api/system/stop        # Stop monitoring
GET  /api/system/status      # Get status

# Cameras
GET  /api/cameras            # List all cameras
POST /api/cameras/add        # Add new camera
  Body: {"camera_id": "...", "name": "...", "type": "usb|ip", "source": "0"}

# Data
GET /api/presence/active     # Currently present persons
GET /api/presence/history    # Historical logs
GET /api/alerts/active       # Active alerts
GET /api/statistics          # System metrics
```

## 🎓 Advanced Features

### Multiple Cameras
Add as many as you want! Each camera gets processed independently:
```
Configuration Tab → Add Camera Form → Add multiple times
```

### IP Cameras (RTSP)
```json
{
  "camera_id": "ip_camera_1",
  "name": "Office IP Camera",
  "type": "ip",
  "source": "rtsp://username:password@192.168.1.100:554/stream"
}
```

### Employee Face Recognition (Optional)
1. Install: `pip install face_recognition`
2. Place face images in `data/faces/` folder
   - Format: `employee_name.jpg`
3. Set in config.py: `FACE_RECOGNITION_ENABLED = True`
4. Restart server

## 🎉 You're Ready!

Your system is fully operational. Just **add a camera** using any method above and you're monitoring!

**Dashboard:** http://localhost:5000

---

**Need more help?** Check:
- `README.md` - Full documentation
- `QUICKSTART.md` - 5-minute guide
- `TESTING.md` - Test procedures
- `CAMERA_SETUP.md` - Detailed camera setup

**Everything working?** Great! Your employee monitoring system is complete! 🚀
