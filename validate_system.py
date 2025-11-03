"""
System Validation Script
Run this after installation to verify everything is working
"""
import sys
import os
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_result(test_name, passed, message=""):
    """Print test result"""
    status = "✓ PASS" if passed else "✗ FAIL"
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{status}{reset} - {test_name}")
    if message:
        print(f"      {message}")

def main():
    print_header("System Validation")
    
    all_passed = True
    
    # Test 1: Python version
    print_header("1. Python Environment")
    python_version = sys.version_info
    passed = python_version >= (3, 8)
    print_result("Python Version", passed, 
                 f"Found {python_version.major}.{python_version.minor}.{python_version.micro}")
    all_passed &= passed
    
    # Test 2: Required modules
    print_header("2. Core Dependencies")
    
    required_modules = [
        ('flask', 'Flask'),
        ('flask_socketio', 'Flask-SocketIO'),
        ('cv2', 'OpenCV'),
        ('numpy', 'NumPy'),
        ('sqlite3', 'SQLite3'),
    ]
    
    for module_name, display_name in required_modules:
        try:
            __import__(module_name)
            print_result(display_name, True)
        except ImportError:
            print_result(display_name, False, f"Module '{module_name}' not found")
            all_passed = False
    
    # Test 3: Optional modules
    print_header("3. Optional Dependencies")
    
    optional_modules = [
        ('mediapipe', 'MediaPipe'),
        ('ultralytics', 'YOLOv8'),
        ('face_recognition', 'Face Recognition'),
        ('plyer', 'Plyer (Notifications)'),
    ]
    
    for module_name, display_name in optional_modules:
        try:
            __import__(module_name)
            print_result(display_name, True, "Available")
        except ImportError:
            print_result(display_name, True, "Not installed (optional)")
    
    # Test 4: Project structure
    print_header("4. Project Structure")
    
    required_dirs = [
        'app',
        'templates',
        'static',
        'tests',
        'data',
    ]
    
    for dir_name in required_dirs:
        path = Path(__file__).parent / dir_name
        passed = path.exists()
        print_result(f"Directory: {dir_name}/", passed)
        all_passed &= passed
    
    # Test 5: Configuration
    print_header("5. Configuration")
    
    try:
        from app import config
        print_result("Config Module", True)
        
        # Check important config values
        checks = [
            ('DATABASE_PATH', config.DATABASE_PATH),
            ('LOG_DIR', config.LOG_DIR),
            ('DATA_DIR', config.DATA_DIR),
        ]
        
        for name, value in checks:
            print_result(f"  {name}", value is not None, str(value))
        
    except Exception as e:
        print_result("Config Module", False, str(e))
        all_passed = False
    
    # Test 6: Database initialization
    print_header("6. Database")
    
    try:
        from app.database import Database
        db = Database()
        print_result("Database Creation", True)
        
        # Test basic operations
        employees = db.get_all_employees()
        print_result("Database Query", True, f"Found {len(employees)} employees")
        
    except Exception as e:
        print_result("Database", False, str(e))
        all_passed = False
    
    # Test 7: Camera support
    print_header("7. Camera Support")
    
    try:
        import cv2
        
        # Try to open default camera
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            print_result("USB Camera Access", ret, 
                        "Camera detected and can capture frames")
        else:
            print_result("USB Camera Access", True, 
                        "No camera detected (this is okay for IP cameras)")
    except Exception as e:
        print_result("Camera Support", False, str(e))
    
    # Test 8: Detection engines
    print_header("8. Detection Engines")
    
    try:
        from app.detection_engine import DetectionEngine
        
        # Test OpenCV (always available)
        try:
            engine = DetectionEngine('opencv')
            print_result("OpenCV Detection", True)
        except Exception as e:
            print_result("OpenCV Detection", False, str(e))
            all_passed = False
        
        # Test MediaPipe
        try:
            engine = DetectionEngine('mediapipe')
            print_result("MediaPipe Detection", True)
        except:
            print_result("MediaPipe Detection", True, 
                        "Not available (optional)")
        
        # Test YOLO
        try:
            engine = DetectionEngine('yolo')
            print_result("YOLO Detection", True)
        except:
            print_result("YOLO Detection", True, 
                        "Not available (optional)")
        
    except Exception as e:
        print_result("Detection Engines", False, str(e))
        all_passed = False
    
    # Test 9: Tracking system
    print_header("9. Tracking System")
    
    try:
        from app.tracking_system import TrackingManager
        manager = TrackingManager()
        print_result("Tracking Manager", True)
    except Exception as e:
        print_result("Tracking Manager", False, str(e))
        all_passed = False
    
    # Test 10: Alert system
    print_header("10. Alert System")
    
    try:
        from app.alert_manager import AlertManager
        from app.database import Database
        db = Database()
        alert_mgr = AlertManager(db)
        print_result("Alert Manager", True)
    except Exception as e:
        print_result("Alert Manager", False, str(e))
        all_passed = False
    
    # Test 11: Web application
    print_header("11. Web Application")
    
    try:
        from app import app, socketio
        print_result("Flask Application", True)
        print_result("SocketIO", socketio is not None)
    except Exception as e:
        print_result("Web Application", False, str(e))
        all_passed = False
    
    # Test 12: Test suite
    print_header("12. Test Suite")
    
    test_files = [
        'tests/test_detection.py',
        'tests/test_tracking.py',
        'tests/test_database.py',
        'tests/test_alerts.py',
    ]
    
    for test_file in test_files:
        path = Path(__file__).parent / test_file
        passed = path.exists()
        print_result(f"  {test_file}", passed)
    
    # Final summary
    print_header("Validation Summary")
    
    if all_passed:
        print("\n✓ All critical tests passed!")
        print("\nThe system is ready to use. To start:")
        print("  1. Activate virtual environment")
        print("  2. Run: python run.py")
        print("  3. Open browser: http://localhost:5000")
        print("\nFor quick start guide, see: QUICKSTART.md")
        return 0
    else:
        print("\n✗ Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Run: pip install -r requirements.txt")
        print("  - Check Python version (3.8+ required)")
        print("  - Verify all files were extracted correctly")
        print("\nFor help, see: README.md")
        return 1

if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nValidation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
