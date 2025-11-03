"""
Test suite for Alert Manager
"""
import pytest
from datetime import datetime, timedelta
import tempfile
import os
from app.database import Database
from app.alert_manager import AlertManager, Alert
from app.tracking_system import TrackedPerson


@pytest.fixture
def temp_database():
    """Create a temporary database"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    db = Database(db_path=path)
    yield db
    
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def alert_manager(temp_database):
    """Create alert manager instance"""
    return AlertManager(database=temp_database, timeout_minutes=20)


@pytest.fixture
def sample_person():
    """Create a sample tracked person"""
    return TrackedPerson(
        tracking_id=1,
        employee_id='EMP001',
        centroid=(100, 100),
        bbox=(80, 80, 40, 80),
        last_seen=datetime.now() - timedelta(minutes=5),
        camera_id='cam1'
    )


def test_alert_manager_initialization(alert_manager):
    """Test alert manager initializes correctly"""
    assert alert_manager is not None
    assert alert_manager.timeout_minutes == 20
    assert len(alert_manager.pending_alerts) == 0


def test_alert_creation():
    """Test alert object creation"""
    left_at = datetime.now() - timedelta(minutes=10)
    alert = Alert(
        tracking_id=1,
        employee_id='EMP001',
        left_at=left_at,
        timeout_minutes=20
    )
    
    assert alert is not None
    assert alert.tracking_id == 1
    assert alert.timeout_minutes == 20
    assert alert.triggered is False


def test_alert_should_trigger():
    """Test alert trigger condition"""
    # Alert that should trigger
    left_at = datetime.now() - timedelta(minutes=25)
    alert1 = Alert(1, 'EMP001', left_at, 20)
    assert alert1.should_trigger() is True
    
    # Alert that should not trigger
    left_at = datetime.now() - timedelta(minutes=10)
    alert2 = Alert(2, 'EMP002', left_at, 20)
    assert alert2.should_trigger() is False


def test_add_pending_alert(alert_manager, sample_person):
    """Test adding pending alert"""
    alert_manager.add_pending_alert(sample_person)
    
    assert len(alert_manager.pending_alerts) == 1
    assert sample_person.tracking_id in alert_manager.pending_alerts


def test_cancel_alert(alert_manager, sample_person):
    """Test canceling an alert"""
    alert_manager.add_pending_alert(sample_person)
    alert_manager.cancel_alert(sample_person.tracking_id)
    
    assert len(alert_manager.pending_alerts) == 0


def test_get_pending_alerts(alert_manager, sample_person):
    """Test getting pending alerts"""
    alert_manager.add_pending_alert(sample_person)
    
    pending = alert_manager.get_pending_alerts()
    assert len(pending) == 1


def test_acknowledge_alert(alert_manager, sample_person):
    """Test acknowledging alert"""
    alert_manager.add_pending_alert(sample_person)
    alert_manager.acknowledge_alert(sample_person.tracking_id)
    
    alert = alert_manager.pending_alerts[sample_person.tracking_id]
    assert alert.acknowledged is True


def test_get_statistics(alert_manager, sample_person):
    """Test getting alert statistics"""
    alert_manager.add_pending_alert(sample_person)
    
    stats = alert_manager.get_statistics()
    
    assert 'total_pending' in stats
    assert 'triggered' in stats
    assert 'acknowledged' in stats
    assert stats['total_pending'] == 1


def test_callback_registration(alert_manager):
    """Test callback registration"""
    callback_called = False
    
    def test_callback(alert):
        nonlocal callback_called
        callback_called = True
    
    alert_manager.register_callback(test_callback)
    
    # Manually trigger to test callback
    left_at = datetime.now() - timedelta(minutes=30)
    alert = Alert(1, 'EMP001', left_at, 20)
    alert_manager.pending_alerts[1] = alert
    alert_manager._trigger_alert(alert)
    
    assert callback_called is True


def test_time_remaining():
    """Test time remaining calculation"""
    left_at = datetime.now() - timedelta(minutes=10)
    alert = Alert(1, 'EMP001', left_at, 20)
    
    remaining = alert.time_remaining()
    assert remaining > 0
    assert remaining < 20 * 60  # Less than 20 minutes in seconds
