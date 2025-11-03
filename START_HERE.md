# 🚀 GETTING STARTED - Employee Monitoring System

## What You Have

A complete, working employee monitoring system with:
- ✅ Real-time video processing
- ✅ AI-powered person detection
- ✅ Employee tracking
- ✅ Absence alerts
- ✅ Web dashboard
- ✅ Complete documentation
- ✅ Automated tests
- ✅ Installation scripts

## Quick Start (5 Minutes)

### Option 1: Automated Installation (Recommended)

**Windows:**
```powershell
# Open PowerShell in project directory
cd C:\Users\harsh\floor_monitoring

# Run installer
.\install.ps1

# Activate environment
.\venv\Scripts\Activate.ps1

# Validate installation
python validate_system.py

# Start system
python run.py
```

**Linux/Mac:**
```bash
# Navigate to project
cd /path/to/floor_monitoring

# Run installer
bash install.sh

# Activate environment
source venv/bin/activate

# Validate installation
python validate_system.py

# Start system
python run.py
```

### Option 2: Manual Installation

```powershell
# 1. Create virtual environment
python -m venv venv

# 2. Activate it (Windows)
.\venv\Scripts\Activate.ps1
# Or (Linux/Mac)
source venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Validate
python validate_system.py

# 5. Run
python run.py
```

## First Use

1. **Open Browser**
   - Navigate to: `http://localhost:5000`
   - You should see the dashboard

2. **Add a Camera**
   - Click "Configuration" tab
   - Fill in camera details:
     - Camera ID: `usb_0`
     - Name: `My Camera`
     - Type: `USB Camera`
     - Source: `0` (try 0, 1, or 2)
   - Click "Add Camera"

3. **Start Monitoring**
   - Click green "Start" button
   - Switch to "Live View" tab
   - You should see video feed with detection boxes

4. **Test the System**
   - Walk in front of camera
   - Check "Presence Status" tab
   - Wait for configured timeout
   - Check "Alerts" tab

## Project Files

```
floor_monitoring/
├── README.md              ⭐ Complete documentation
├── QUICKSTART.md          ⭐ This file
├── PROJECT_SUMMARY.md     ⭐ Technical overview
├── TESTING.md            ⭐ Testing guide
├── DEPLOYMENT.md         ⭐ Production deployment
├── run.py                ⭐ Start here!
├── validate_system.py    ⭐ Check installation
├── requirements.txt      📦 Dependencies
├── install.ps1           🔧 Windows installer
├── install.sh            🔧 Linux/Mac installer
├── app/                  💻 Application code
│   ├── main.py          - Main application
│   ├── config.py        - Configuration
│   ├── database.py      - Database layer
│   ├── camera_manager.py - Camera handling
│   ├── detection_engine.py - Person detection
│   ├── tracking_system.py - Person tracking
│   └── alert_manager.py - Alert system
├── templates/           🎨 Web interface
│   └── index.html
├── static/             🎨 CSS & JavaScript
│   ├── css/style.css
│   └── js/app.js
├── tests/              🧪 Test suite
│   ├── test_detection.py
│   ├── test_tracking.py
│   ├── test_database.py
│   └── test_alerts.py
└── data/               💾 Data storage
    ├── monitoring.db   - Database (auto-created)
    ├── logs/          - Application logs
    └── faces/         - Face images (optional)
```

## Configuration

Edit `app/config.py` to customize:

```python
# Alert timeout (minutes)
ABSENCE_TIMEOUT_MINUTES = 20

# Detection model ('mediapipe', 'yolo', 'opencv')
DETECTION_MODEL = 'mediapipe'

# Camera configurations
CAMERA_CONFIGS = {
    'usb_cameras': [
        {'id': 0, 'name': 'Camera 1', 'type': 'usb'},
    ],
    'ip_cameras': [
        # {'url': 'rtsp://...', 'name': 'IP Cam', 'type': 'ip'},
    ]
}
```

## Common Issues

### "Module not found" errors
```powershell
pip install -r requirements.txt
```

### Camera not working
- Try different source numbers: 0, 1, 2
- Check if another app is using camera
- Test with Windows Camera app first

### Slow performance
Edit `app/config.py`:
```python
FRAME_SKIP = 3  # Process fewer frames
MAX_FRAME_WIDTH = 320
DETECTION_MODEL = 'opencv'  # Lighter model
```

### Can't access from other computers
Edit `app/config.py`:
```python
HOST = '0.0.0.0'  # Allow external connections
```
Add firewall rule for port 5000

## Testing

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run validation
python validate_system.py
```

## What to Read Next

1. **README.md** - Complete documentation (600+ lines)
   - All features explained
   - Full configuration guide
   - Troubleshooting
   - API documentation

2. **PROJECT_SUMMARY.md** - Technical overview
   - Architecture details
   - Code statistics
   - System requirements

3. **DEPLOYMENT.md** - Production setup
   - Network deployment
   - Security best practices
   - Backup procedures
   - Scaling considerations

4. **TESTING.md** - Testing guide
   - Test execution
   - Manual testing checklist
   - Performance testing

## Architecture at a Glance

```
Web Browser
    ↓
Flask Server
    ↓
┌───────────────────────────────┐
│ Camera → Detection → Tracking │
│           ↓                    │
│      Database ← Alerts         │
└───────────────────────────────┘
```

## Key Features

### Real-time Monitoring
- Live video feeds
- Person detection with bounding boxes
- Tracking IDs displayed
- Real-time statistics

### Presence Management
- Automatic entry/exit logging
- Duration calculation
- Current occupancy
- Historical records

### Absence Alerts
- Configurable timeout (default 20 min)
- Desktop notifications
- Sound alerts
- Alert acknowledgment
- WebSocket real-time updates

### Data & Analytics
- SQLite database
- Comprehensive logging
- Historical queries
- Statistics dashboard
- Export capabilities

## System Requirements

**Minimum:**
- Windows 10 / Ubuntu 20.04 / macOS 10.15
- Intel Core i5 or equivalent
- 8GB RAM
- USB camera or IP camera
- 10GB free space

**Recommended:**
- Intel Core i7
- 16GB RAM
- Multiple cameras
- SSD storage

## Support

**Documentation:**
- README.md - Complete guide
- Code comments - Inline documentation
- Error logs - `data/logs/app.log`

**Testing:**
- 39 automated tests
- Validation script included
- Test coverage report

**Examples:**
- Sample configurations
- Usage scenarios
- Deployment examples

## Next Steps

After basic setup:

1. **Configure alerts**: Adjust timeout in `app/config.py`
2. **Add employees**: For face recognition (optional)
3. **Optimize performance**: Tune detection settings
4. **Set up backups**: Database backup script included
5. **Network access**: Configure for multi-user access

## Production Checklist

Before production use:

- [ ] Change SECRET_KEY in config.py
- [ ] Set DEBUG = False
- [ ] Configure firewall rules
- [ ] Set up database backups
- [ ] Test alert system
- [ ] Configure camera credentials securely
- [ ] Set up monitoring/logging
- [ ] Test with real workload
- [ ] Document camera locations
- [ ] Train users on system

## Performance Tips

**For better speed:**
```python
FRAME_SKIP = 3          # Process fewer frames
MAX_FRAME_WIDTH = 320   # Smaller resolution
DETECTION_MODEL = 'opencv'  # Faster model
```

**For better accuracy:**
```python
FRAME_SKIP = 1          # Process every frame
MAX_FRAME_WIDTH = 1280  # Higher resolution
DETECTION_MODEL = 'yolo'  # Better detection
```

## Security Notes

✅ All data stored locally
✅ No cloud connectivity
✅ Configurable network access
✅ Session management included
✅ Input validation implemented
✅ SQL injection protected

For production:
- Change default SECRET_KEY
- Use HTTPS with reverse proxy
- Add user authentication
- Restrict network access
- Regular security updates

## Getting Help

1. Check `data/logs/app.log` for errors
2. Run `python validate_system.py`
3. Review README.md troubleshooting section
4. Check configuration in `app/config.py`
5. Verify camera connections
6. Test with minimal configuration

## Success Criteria

You'll know it's working when:
- ✅ Server starts without errors
- ✅ Browser loads dashboard at localhost:5000
- ✅ Camera video appears in Live View
- ✅ Bounding boxes appear around people
- ✅ Presence Status shows entries
- ✅ Alerts trigger after timeout

## Development

Want to extend the system?

**Add new detection model:**
- Edit `app/detection_engine.py`
- Implement new detection method
- Update config options

**Add new alert type:**
- Edit `app/alert_manager.py`
- Add alert conditions
- Update UI to display

**Customize UI:**
- Edit `templates/index.html`
- Modify `static/css/style.css`
- Update `static/js/app.js`

## License

This project is provided as-is for educational and business use.

## Acknowledgments

Built with: Flask, OpenCV, MediaPipe, YOLO, Bootstrap, Socket.IO

---

## 🎉 You're Ready to Go!

The system is complete and ready for deployment. Start with:

```powershell
python run.py
```

Then open: **http://localhost:5000**

**Good luck with your employee monitoring system!** 🚀
