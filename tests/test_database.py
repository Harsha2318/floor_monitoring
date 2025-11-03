"""
Test suite for Database operations
"""
import pytest
from datetime import datetime, timedelta
import tempfile
import os
from app.database import Database


@pytest.fixture
def temp_database():
    """Create a temporary database for testing"""
    # Create temp file
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    db = Database(db_path=path)
    yield db
    
    # Cleanup
    if os.path.exists(path):
        os.remove(path)


def test_database_initialization(temp_database):
    """Test database initializes correctly"""
    assert temp_database is not None
    
    # Check that tables exist
    with temp_database.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row['name'] for row in cursor.fetchall()]
        
        assert 'employees' in tables
        assert 'presence_logs' in tables
        assert 'absence_alerts' in tables
        assert 'cameras' in tables


def test_add_employee(temp_database):
    """Test adding an employee"""
    success = temp_database.add_employee('EMP001', 'John Doe')
    assert success is True
    
    # Try adding duplicate
    success = temp_database.add_employee('EMP001', 'Jane Doe')
    assert success is False


def test_get_employee(temp_database):
    """Test getting employee details"""
    temp_database.add_employee('EMP001', 'John Doe')
    
    employee = temp_database.get_employee('EMP001')
    assert employee is not None
    assert employee['employee_id'] == 'EMP001'
    assert employee['name'] == 'John Doe'


def test_get_all_employees(temp_database):
    """Test getting all employees"""
    temp_database.add_employee('EMP001', 'John Doe')
    temp_database.add_employee('EMP002', 'Jane Smith')
    
    employees = temp_database.get_all_employees()
    assert len(employees) == 2


def test_log_entry(temp_database):
    """Test logging entry"""
    log_id = temp_database.log_entry(
        tracking_id=1,
        camera_id='cam1',
        employee_id='EMP001'
    )
    
    assert log_id is not None
    assert log_id > 0


def test_log_exit(temp_database):
    """Test logging exit"""
    # First log entry
    temp_database.log_entry(
        tracking_id=1,
        camera_id='cam1',
        employee_id='EMP001'
    )
    
    # Then log exit
    success = temp_database.log_exit(tracking_id=1, camera_id='cam1')
    assert success is True


def test_get_active_presences(temp_database):
    """Test getting active presences"""
    # Log some entries
    temp_database.log_entry(1, 'cam1', 'EMP001')
    temp_database.log_entry(2, 'cam1', 'EMP002')
    
    active = temp_database.get_active_presences('cam1')
    assert len(active) == 2


def test_get_presence_history(temp_database):
    """Test getting presence history"""
    # Log entry and exit
    temp_database.log_entry(1, 'cam1', 'EMP001')
    temp_database.log_exit(1, 'cam1')
    
    history = temp_database.get_presence_history()
    assert len(history) > 0


def test_create_alert(temp_database):
    """Test creating an alert"""
    left_at = datetime.now() - timedelta(minutes=30)
    
    alert_id = temp_database.create_alert(
        tracking_id=1,
        employee_id='EMP001',
        left_at=left_at,
        timeout_minutes=20
    )
    
    assert alert_id is not None
    assert alert_id > 0


def test_get_unacknowledged_alerts(temp_database):
    """Test getting unacknowledged alerts"""
    left_at = datetime.now() - timedelta(minutes=30)
    
    temp_database.create_alert(1, 'EMP001', left_at, 20)
    
    alerts = temp_database.get_unacknowledged_alerts()
    assert len(alerts) > 0


def test_acknowledge_alert(temp_database):
    """Test acknowledging an alert"""
    left_at = datetime.now() - timedelta(minutes=30)
    alert_id = temp_database.create_alert(1, 'EMP001', left_at, 20)
    
    success = temp_database.acknowledge_alert(alert_id)
    assert success is True
    
    alerts = temp_database.get_unacknowledged_alerts()
    assert len(alerts) == 0


def test_add_camera(temp_database):
    """Test adding a camera"""
    success = temp_database.add_camera('cam1', 'Camera 1', 'usb', '0')
    assert success is True
    
    # Try adding duplicate
    success = temp_database.add_camera('cam1', 'Camera 1', 'usb', '0')
    assert success is False


def test_get_cameras(temp_database):
    """Test getting cameras"""
    temp_database.add_camera('cam1', 'Camera 1', 'usb', '0')
    temp_database.add_camera('cam2', 'Camera 2', 'ip', 'rtsp://example.com')
    
    cameras = temp_database.get_cameras()
    assert len(cameras) == 2


def test_get_statistics(temp_database):
    """Test getting statistics"""
    # Log some data
    temp_database.log_entry(1, 'cam1', 'EMP001')
    temp_database.log_entry(2, 'cam1', 'EMP002')
    
    stats = temp_database.get_statistics()
    
    assert 'total_entries' in stats
    assert 'currently_present' in stats
    assert 'total_alerts' in stats
    assert stats['total_entries'] >= 2
