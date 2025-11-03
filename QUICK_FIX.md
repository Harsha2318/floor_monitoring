# 🎯 QUICK FIX SUMMARY

## ✅ What We Fixed

1. **MediaPipe Import Error** - Fixed by making MediaPipe import lazy (only when needed)
2. **Camera Device Issues** - Identified that only device 0 works on your system
3. **Database Cleanup** - Removed 2 failing cameras that were causing continuous errors

## 📊 Camera Test Results

```
✅ Device 0: WORKING (640x480)
❌ Device 1: Not available
❌ Device 2-4: Not available
```

## 🚀 Next Steps - USE THE WEB INTERFACE

The server is running at **http://localhost:5000**

### Method 1: Via Web UI (EASIEST - RECOMMENDED)

1. **Open your browser** to `http://localhost:5000`
2. **Click the "Configuration" tab** (top right)
3. **Fill in the camera form:**
   - **Camera ID**: `usb_camera_main`
   - **Camera Name**: `Main Camera`
   - **Camera Type**: Select "USB Camera"
   - **Source/URL**: `0`
4. **Click "Add Camera" button**
5. **Go to "Live View" tab**
6. **Click the green "Start Monitoring" button**
7. **You should see yourself on camera!**

### Method 2: PowerShell Script

Open a **NEW** PowerShell window (don't close the server!) and run:

```powershell
cd C:\Users\harsh\floor_monitoring
.\add_camera.ps1
```

## 🔧 If Camera Shows "Failed to Read Frame"

**This usually means another app is using the camera. Close these apps:**
- Microsoft Teams
- Zoom
- Skype
- Windows Camera app
- Any browser tabs with camera access

**Then refresh the page and try again.**

## 📝 Important Notes

- **Keep the server terminal running** - Don't close it!
- **Use device source "0"** - It's the only one that works on your PC
- **One camera at a time** - Don't add multiple cameras using the same device
- **Close other camera apps** - Only one app can use the camera at once

## 🐛 Troubleshooting

### "Failed to read frame" errors:
```powershell
# Test if camera is accessible:
python test_camera.py

# If still failing, restart computer and try again
```

### Need to start over:
```powershell
# Stop server (Ctrl+C in server terminal)
# Reset cameras:
echo yes | python reset_cameras.py
# Restart server:
python run.py
```

## 🎬 Expected Behavior When Working

Once you add the camera and start monitoring:
- Live video feed appears in "Live View" tab
- Person detection boxes appear around people
- "Presence Status" shows when people are detected
- Entry/exit events are logged
- Alerts trigger after 20 minutes of absence

## ✨ System Status

- ✅ Server: Running
- ✅ Database: Clean (0 cameras)
- ✅ Detection: OpenCV HOG ready
- ✅ Alerts: Ready (20 min timeout)
- ⏳ Camera: **Needs to be added by you via web UI**

**Go add that camera now! Use the web interface - it's the easiest way!**
