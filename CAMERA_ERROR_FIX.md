# Camera Access Troubleshooting Guide

## Error: -1072875772 (MSMF Error)

This error means **another application is using your camera**.

### Step 1: Close All Camera Applications

**Close these apps** (right-click taskbar → Close or use Task Manager):
- ✖️ Microsoft Teams
- ✖️ Zoom  
- ✖️ Skype
- ✖️ Discord
- ✖️ Windows Camera app
- ✖️ **ALL browser windows** (Chrome, Edge, Firefox)
- ✖️ OBS Studio
- ✖️ Any video recording software

### Step 2: Check Task Manager

1. Press `Ctrl+Shift+Esc` to open Task Manager
2. Look for these processes and **End Task**:
   - Teams
   - Zoom
   - Camera
   - Any browser (chrome.exe, msedge.exe)
3. Check "Background processes" section too

### Step 3: Stop the Server

In the PowerShell window where `python run.py` is running:
- Press `Ctrl+C` to stop it

### Step 4: Restart Fresh

```powershell
# 1. Close ALL apps using camera
# 2. Wait 5 seconds
# 3. Start server
python run.py
```

### Step 5: Test Camera Availability

```powershell
python test_camera.py
```

Should show: **✅ Device 0 is working!**

If still fails:
- Restart your computer
- Camera driver might need update

### Alternative: Use Different Camera Backend

If MSMF keeps failing, edit `app/camera_manager.py`:

Find line ~70:
```python
self.cap = cv2.VideoCapture(int(source))
```

Change to:
```python
self.cap = cv2.VideoCapture(int(source), cv2.CAP_DSHOW)  # Use DirectShow instead
```

This forces DirectShow backend which is more reliable.

---

**Most Common Cause:** Browser tabs with camera permission still open!
