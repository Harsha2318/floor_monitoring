"""
Configuration settings for the Employee Monitoring System
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Application Settings
DEBUG = True
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
HOST = '0.0.0.0'
PORT = 5000

# Camera Settings
CAMERA_CONFIGS = {
    'usb_cameras': [
        # {'id': 0, 'name': 'USB Camera 1', 'type': 'usb'},
        # {'id': 1, 'name': 'USB Camera 2', 'type': 'usb'},
    ],
    'ip_cameras': [
        # {'url': 'rtsp://192.168.1.100:554/stream', 'name': 'IP Camera 1', 'type': 'ip'},
    ]
}

# Detection Settings
DETECTION_CONFIDENCE = 0.2  # Minimum confidence for person detection (lowered for better sensitivity)
# Detection model to use
# Options: 'mediapipe' (recommended), 'yolo' (best accuracy), 'opencv' (fastest, fallback)
# Set to 'opencv' if MediaPipe installation fails
DETECTION_MODEL = 'opencv'  # Changed to opencv for better compatibility
FRAME_SKIP = 2  # Process every nth frame to improve performance
MAX_FRAME_WIDTH = 640  # Resize frames for faster processing
MAX_FRAME_HEIGHT = 480

# Tracking Settings
TRACKING_MAX_DISAPPEARED = 30  # Max frames before considering person as left
TRACKING_MAX_DISTANCE = 50  # Max distance for tracking same person
FACE_RECOGNITION_ENABLED = False  # Enable face recognition for identification

# Alert Settings
ABSENCE_TIMEOUT_MINUTES = 20  # Default timeout in minutes
ALERT_SOUND_ENABLED = True
ALERT_NOTIFICATION_ENABLED = True
ALERT_CHECK_INTERVAL = 30  # Check for alerts every N seconds

# Database Settings
DATABASE_PATH = BASE_DIR / 'data' / 'monitoring.db'
DATABASE_URI = f'sqlite:///{DATABASE_PATH}'

# Logging Settings
LOG_LEVEL = 'INFO'
LOG_DIR = BASE_DIR / 'data' / 'logs'
LOG_FILE = LOG_DIR / 'app.log'

# Storage Settings
DATA_DIR = BASE_DIR / 'data'
MODELS_DIR = BASE_DIR / 'models'
FACES_DIR = DATA_DIR / 'faces'  # Store known faces for recognition

# Performance Settings
VIDEO_BUFFER_SIZE = 5
PROCESSING_THREADS = 2

# UI Settings
STREAM_FPS = 15  # FPS for video streaming to browser
STREAM_QUALITY = 80  # JPEG quality (1-100)

# Create necessary directories
for directory in [DATA_DIR, LOG_DIR, MODELS_DIR, FACES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Employee Settings
EMPLOYEE_DATABASE = {
    # Format: employee_id: {'name': 'Name', 'face_encoding': None}
    # Face encodings will be loaded from files
}
