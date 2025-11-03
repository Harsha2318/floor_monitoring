# Employee Monitoring and Workspace Management System

A complete, locally deployable employee monitoring system for MSMEs (Micro, Small, and Medium Enterprises) with real-time video processing, employee tracking, and absence alerting.

## Features

- **Real-time Video Monitoring**: Support for USB and IP cameras
- **Person Detection**: AI-powered detection using MediaPipe, YOLO, or OpenCV
- **Employee Tracking**: Track unique individuals across frames
- **Presence Logging**: Detailed logs of entry/exit times and duration
- **Absence Alerts**: Configurable timeout alerts with desktop notifications
- **Web Dashboard**: Real-time monitoring interface
- **Local Storage**: SQLite database for all data
- **No Cloud Dependency**: Fully local deployment

## System Requirements

### Hardware
- **CPU**: Intel Core i5 or equivalent (quad-core recommended)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB free space
- **Camera**: USB webcam or IP camera with RTSP support
- **OS**: Windows 10/11, Linux, or macOS

### Software
- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for cloning repository)

## Installation

### Step 1: Clone or Download the Repository

```powershell
# Using Git
git clone <repository-url>
cd floor_monitoring

# Or download and extract the ZIP file
```

### Step 2: Create a Virtual Environment (Recommended)

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1

# On Windows CMD:
.\venv\Scripts\activate.bat

# On Linux/Mac:
source venv/bin/activate
```

### Step 3: Install Dependencies

```powershell
# Install all required packages
pip install -r requirements.txt
```

**Note**: Some packages like `dlib` and `face-recognition` may require additional system dependencies. If you encounter issues:

- **For face recognition (optional)**: If installation fails, you can disable it in `app/config.py`
- **For dlib on Windows**: You may need Visual C++ build tools

### Step 4: Configure the System

Edit `app/config.py` to configure your cameras and settings:

```python
# Camera Settings
CAMERA_CONFIGS = {
    'usb_cameras': [
        {'id': 0, 'name': 'USB Camera 1', 'type': 'usb'},
    ],
    'ip_cameras': [
        # {'url': 'rtsp://192.168.1.100:554/stream', 'name': 'IP Camera 1', 'type': 'ip'},
    ]
}

# Alert Settings
ABSENCE_TIMEOUT_MINUTES = 20  # Alert after 20 minutes absence

# Detection Settings
DETECTION_MODEL = 'mediapipe'  # Options: 'mediapipe', 'yolo', 'opencv'
```

### Step 5: Initialize the Database

The database is automatically created on first run. The system creates:
- `data/monitoring.db` - SQLite database
- `data/logs/` - Application logs
- `data/faces/` - Face images for recognition (optional)

## Running the System

### Start the Server

```powershell
# Make sure virtual environment is activated
python run.py
```

The server will start on `http://localhost:5000`

### Access the Dashboard

Open your web browser and navigate to:
```
http://localhost:5000
```

### Using the Dashboard

1. **Configuration Tab**: Add cameras before starting
   - Click "Configuration" tab
   - Enter camera details (ID, name, type, source)
   - Click "Add Camera"

2. **Start Monitoring**: 
   - Click the green "Start" button in the top navigation
   - System begins processing video feeds

3. **Live View Tab**: 
   - View real-time video streams
   - See detection boxes around people
   - Monitor detection counts

4. **Presence Status Tab**:
   - See all currently present employees
   - View entry times and durations

5. **Alerts Tab**:
   - View absence alerts
   - Acknowledge alerts

6. **History Tab**:
   - Review historical presence data
   - Filter by date range

## Camera Configuration

### USB Cameras

For USB cameras, use the device index (usually 0 for first camera, 1 for second, etc.):

```python
# In app/config.py
CAMERA_CONFIGS = {
    'usb_cameras': [
        {'id': 0, 'name': 'Front Door Camera', 'type': 'usb'},
        {'id': 1, 'name': 'Workspace Camera', 'type': 'usb'},
    ]
}
```

Or add via the web interface:
- Camera ID: `usb_0`
- Camera Name: `Front Door Camera`
- Type: `usb`
- Source: `0`

### IP Cameras (RTSP)

For IP cameras, use the RTSP URL:

```python
# In app/config.py
CAMERA_CONFIGS = {
    'ip_cameras': [
        {'url': 'rtsp://admin:password@192.168.1.100:554/stream', 
         'name': 'IP Camera 1', 'type': 'ip'},
    ]
}
```

Or add via the web interface:
- Camera ID: `ip_1`
- Camera Name: `IP Camera 1`
- Type: `ip`
- Source: `rtsp://admin:password@192.168.1.100:554/stream`

## Configuration Options

### Detection Models

The system supports three detection models:

1. **MediaPipe** (Recommended for CPU):
   - Fast and efficient
   - Good accuracy
   - Lower resource usage
   ```python
   DETECTION_MODEL = 'mediapipe'
   ```

2. **YOLO** (Best accuracy, requires more resources):
   - High accuracy
   - Slower on CPU
   - Best with GPU
   ```python
   DETECTION_MODEL = 'yolo'
   ```

3. **OpenCV HOG** (Fallback):
   - Lightweight
   - Basic detection
   - Works on any system
   ```python
   DETECTION_MODEL = 'opencv'
   ```

### Alert Settings

```python
# Absence timeout in minutes
ABSENCE_TIMEOUT_MINUTES = 20

# Enable/disable alert features
ALERT_SOUND_ENABLED = True
ALERT_NOTIFICATION_ENABLED = True

# Check interval in seconds
ALERT_CHECK_INTERVAL = 30
```

### Performance Settings

```python
# Process every Nth frame (higher = faster, less accurate)
FRAME_SKIP = 2

# Maximum frame size for processing
MAX_FRAME_WIDTH = 640
MAX_FRAME_HEIGHT = 480

# Tracking settings
TRACKING_MAX_DISAPPEARED = 30  # Frames before person is considered gone
TRACKING_MAX_DISTANCE = 50     # Max pixel distance for same person
```

### Face Recognition (Optional)

To enable employee identification by face:

```python
FACE_RECOGNITION_ENABLED = True
```

Then add employee face images to `data/faces/` directory:
- Filename: `employee_id.jpg` (e.g., `EMP001.jpg`)
- One face per image
- Clear, frontal face photo

## Testing

Run the automated test suite:

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_detection.py
```

Test files:
- `tests/test_detection.py` - Detection engine tests
- `tests/test_tracking.py` - Tracking system tests
- `tests/test_database.py` - Database operations tests
- `tests/test_alerts.py` - Alert manager tests

## Troubleshooting

### Camera Not Detected

1. Check camera connection
2. Verify device index (try 0, 1, 2)
3. Check camera permissions
4. For IP cameras, test RTSP URL with VLC player

### Detection Not Working

1. Check detection model installation
2. Try switching to 'opencv' model
3. Verify frame is being captured
4. Check logs in `data/logs/app.log`

### Performance Issues

1. Increase `FRAME_SKIP` value
2. Reduce `MAX_FRAME_WIDTH` and `MAX_FRAME_HEIGHT`
3. Switch to a lighter detection model
4. Reduce number of cameras
5. Close other applications

### Alerts Not Showing

1. Check `ABSENCE_TIMEOUT_MINUTES` setting
2. Verify alert system is started
3. Check browser notification permissions
4. Review logs for errors

## Project Structure

```
floor_monitoring/
├── app/
│   ├── __init__.py           # Flask app initialization
│   ├── main.py               # Main application logic
│   ├── config.py             # Configuration settings
│   ├── database.py           # Database operations
│   ├── camera_manager.py     # Camera handling
│   ├── detection_engine.py   # Person detection
│   ├── tracking_system.py    # Person tracking
│   └── alert_manager.py      # Alert management
├── static/
│   ├── css/
│   │   └── style.css         # Stylesheets
│   └── js/
│       └── app.js            # Frontend JavaScript
├── templates/
│   └── index.html            # Main dashboard template
├── tests/
│   ├── test_detection.py     # Detection tests
│   ├── test_tracking.py      # Tracking tests
│   ├── test_database.py      # Database tests
│   └── test_alerts.py        # Alert tests
├── data/
│   ├── monitoring.db         # SQLite database
│   ├── logs/                 # Application logs
│   └── faces/                # Employee face images
├── requirements.txt          # Python dependencies
├── run.py                    # Application entry point
└── README.md                 # This file
```

## API Endpoints

The system provides REST API endpoints:

### System Control
- `POST /api/system/start` - Start monitoring
- `POST /api/system/stop` - Stop monitoring
- `GET /api/system/status` - Get system status

### Cameras
- `GET /api/cameras` - List all cameras
- `POST /api/cameras/add` - Add new camera
- `POST /api/cameras/<id>/remove` - Remove camera
- `GET /video_feed/<id>` - Video stream endpoint

### Presence
- `GET /api/presence/active` - Get currently present employees
- `GET /api/presence/history` - Get presence history

### Alerts
- `GET /api/alerts/active` - Get active alerts
- `POST /api/alerts/<id>/acknowledge` - Acknowledge alert

### Statistics
- `GET /api/statistics` - Get system statistics

## Database Schema

### employees
- `id`: Primary key
- `employee_id`: Unique employee identifier
- `name`: Employee name
- `face_encoding`: Face recognition data (optional)
- `registered_at`: Registration timestamp
- `active`: Active status

### presence_logs
- `id`: Primary key
- `employee_id`: Foreign key to employees
- `tracking_id`: Tracking system ID
- `camera_id`: Camera identifier
- `entry_time`: Entry timestamp
- `exit_time`: Exit timestamp
- `duration_seconds`: Presence duration
- `status`: Current status (present/left)

### absence_alerts
- `id`: Primary key
- `employee_id`: Foreign key to employees
- `tracking_id`: Tracking system ID
- `left_at`: When person left
- `alert_triggered_at`: Alert timestamp
- `timeout_minutes`: Configured timeout
- `acknowledged`: Acknowledgement status

### cameras
- `id`: Primary key
- `camera_id`: Unique camera identifier
- `name`: Camera name
- `type`: Camera type (usb/ip)
- `source`: Device ID or URL
- `active`: Active status

## Security Considerations

This system is designed for local deployment. For production use:

1. **Change default secret key** in `app/config.py`
2. **Restrict network access** - Use firewall rules
3. **Enable HTTPS** - Use reverse proxy with SSL
4. **Secure camera credentials** - Store securely, not in config
5. **Regular backups** - Backup `data/` directory
6. **Access control** - Add authentication if needed

## Performance Optimization

### For Limited Hardware

```python
# Optimize config for low-end systems
DETECTION_MODEL = 'opencv'  # Lightest model
FRAME_SKIP = 3              # Process fewer frames
MAX_FRAME_WIDTH = 320       # Smaller frame size
MAX_FRAME_HEIGHT = 240
PROCESSING_THREADS = 1      # Reduce threads
```

### For Better Accuracy

```python
# Optimize for accuracy with better hardware
DETECTION_MODEL = 'yolo'    # Best accuracy
FRAME_SKIP = 1              # Process every frame
MAX_FRAME_WIDTH = 1280      # Higher resolution
MAX_FRAME_HEIGHT = 720
FACE_RECOGNITION_ENABLED = True  # Enable face ID
```

## Maintenance

### Backup Database

```powershell
# Backup database
copy data\monitoring.db data\backup\monitoring_backup_$(Get-Date -Format 'yyyyMMdd').db
```

### Clear Old Logs

```powershell
# Keep only last 30 days
Get-ChildItem data\logs -Filter *.log | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | Remove-Item
```

### Monitor Disk Usage

The database grows over time. Monitor the `data/` directory size and archive old data periodically.

## Support and Contributing

For issues, questions, or contributions:
1. Check logs in `data/logs/app.log`
2. Review this documentation
3. Test with minimal configuration
4. Report issues with full error messages and logs

## License

This project is provided as-is for educational and business use.

## Acknowledgments

- OpenCV for computer vision
- MediaPipe for pose detection
- YOLO for object detection
- Flask for web framework
- Bootstrap for UI components
