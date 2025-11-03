# Testing Guide

## Running Tests

### Run All Tests
```powershell
pytest
```

### Run Specific Test File
```powershell
pytest tests/test_detection.py
pytest tests/test_tracking.py
pytest tests/test_database.py
pytest tests/test_alerts.py
```

### Run with Verbose Output
```powershell
pytest -v
```

### Run with Coverage Report
```powershell
pytest --cov=app --cov-report=html
```
Then open `htmlcov/index.html` to view coverage report.

## Test Coverage

Current test modules:
- **test_detection.py**: Detection engine functionality
- **test_tracking.py**: Person tracking across frames
- **test_database.py**: Database operations
- **test_alerts.py**: Alert system functionality

## Manual Testing Checklist

### Basic Functionality
- [ ] System starts without errors
- [ ] Web interface loads at http://localhost:5000
- [ ] Can add USB camera
- [ ] Can add IP camera
- [ ] Can start monitoring
- [ ] Can stop monitoring

### Camera Testing
- [ ] USB camera shows video feed
- [ ] Multiple cameras work simultaneously
- [ ] Camera can be added via web interface
- [ ] Camera can be removed

### Detection Testing
- [ ] Person detection works with MediaPipe
- [ ] Person detection works with OpenCV
- [ ] Bounding boxes appear around detected persons
- [ ] Detection count updates in real-time

### Tracking Testing
- [ ] Persons get unique tracking IDs
- [ ] Tracking IDs persist across frames
- [ ] New persons get new IDs
- [ ] Persons leaving are detected

### Presence Logging
- [ ] Entry time is logged when person appears
- [ ] Exit time is logged when person leaves
- [ ] Duration is calculated correctly
- [ ] Presence status tab shows active persons
- [ ] History tab shows past records

### Alert System
- [ ] Alert is created when person leaves
- [ ] Alert triggers after configured timeout
- [ ] Desktop notification appears (if enabled)
- [ ] Alert sound plays (if enabled)
- [ ] Alert appears in Alerts tab
- [ ] Alert can be acknowledged
- [ ] Alert statistics update

### Database
- [ ] Database file is created
- [ ] Data persists after restart
- [ ] Historical data is retrievable
- [ ] Statistics are accurate

### UI/UX
- [ ] All tabs are accessible
- [ ] Statistics cards update
- [ ] Video streams display correctly
- [ ] Tables populate with data
- [ ] Date filters work
- [ ] Forms validate input

## Performance Testing

### Load Testing
Test with multiple cameras:
1. Add 2-3 cameras
2. Start monitoring
3. Observe CPU and memory usage
4. Check frame rate
5. Verify all cameras process smoothly

### Stress Testing
Test with high activity:
1. Have multiple people in camera view
2. People entering and leaving frequently
3. Monitor system responsiveness
4. Check for memory leaks (run for extended period)

### Expected Performance

**Minimum System (Core i5, 8GB RAM):**
- 1-2 cameras at 640x480
- 10-15 FPS processing
- CPU usage: 40-60%
- RAM usage: 500MB-1GB

**Recommended System (Core i7, 16GB RAM):**
- 3-4 cameras at 1280x720
- 20-30 FPS processing
- CPU usage: 30-50%
- RAM usage: 1-2GB

## Integration Testing Scenarios

### Scenario 1: Complete Workflow
1. Start system
2. Add camera
3. Start monitoring
4. Person enters (detected)
5. Person stays for 5 minutes
6. Person leaves
7. Wait for timeout
8. Alert triggers
9. Acknowledge alert
10. Review history

### Scenario 2: Multiple Persons
1. Start monitoring
2. Person A enters
3. Person B enters
4. Both tracked with different IDs
5. Person A leaves
6. Person B stays
7. Only Person A alert triggers
8. Person B remains in presence list

### Scenario 3: Quick Entry/Exit
1. Person enters
2. Person leaves within 1 minute
3. Entry and exit logged
4. No alert triggers (too short)

## Troubleshooting Tests

### Camera Issues
```python
# Test camera connectivity
import cv2
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
assert ret == True
assert frame is not None
cap.release()
```

### Detection Issues
```python
# Test detection engine
from app.detection_engine import DetectionEngine
engine = DetectionEngine('opencv')
assert engine is not None
```

### Database Issues
```python
# Test database connection
from app.database import Database
db = Database()
cameras = db.get_cameras()
assert isinstance(cameras, list)
```

## Automated Test Plan

### Unit Tests (pytest)
- All core functions tested
- Edge cases covered
- Error handling verified

### Integration Tests
- Component interactions tested
- Data flow verified
- API endpoints tested

### System Tests
- End-to-end workflows
- Performance benchmarks
- Stress tests

## Test Data

### Sample Employees
```python
employees = [
    {'employee_id': 'EMP001', 'name': 'John Doe'},
    {'employee_id': 'EMP002', 'name': 'Jane Smith'},
    {'employee_id': 'EMP003', 'name': 'Bob Johnson'},
]
```

### Sample Camera Configs
```python
cameras = [
    {'camera_id': 'test_usb', 'name': 'Test USB', 'type': 'usb', 'source': '0'},
    {'camera_id': 'test_ip', 'name': 'Test IP', 'type': 'ip', 'source': 'rtsp://test'},
]
```

## Bug Reporting Template

When reporting issues, include:
1. System specifications (CPU, RAM, OS)
2. Python version
3. Steps to reproduce
4. Expected behavior
5. Actual behavior
6. Error messages from logs
7. Screenshots (if applicable)

## Continuous Testing

For ongoing development:
1. Run tests before committing code
2. Verify all tests pass
3. Check code coverage
4. Update tests for new features
5. Document test procedures
