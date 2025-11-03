"""
Test suite for Tracking System
"""
import pytest
from datetime import datetime
from app.tracking_system import CentroidTracker, TrackedPerson, TrackingManager
from app.detection_engine import Detection


@pytest.fixture
def centroid_tracker():
    """Create a centroid tracker instance"""
    return CentroidTracker(max_disappeared=5, max_distance=50)


@pytest.fixture
def sample_detections():
    """Create sample detections"""
    return [
        Detection(bbox=(100, 100, 50, 100), confidence=0.9, center=(125, 150), frame_id=1),
        Detection(bbox=(300, 200, 50, 100), confidence=0.85, center=(325, 250), frame_id=1),
    ]


def test_tracker_initialization(centroid_tracker):
    """Test tracker initializes correctly"""
    assert centroid_tracker is not None
    assert centroid_tracker.next_object_id == 1
    assert len(centroid_tracker.objects) == 0


def test_register_person(centroid_tracker):
    """Test registering a new person"""
    person = centroid_tracker.register(
        centroid=(100, 100),
        bbox=(80, 80, 40, 80),
        confidence=0.9,
        camera_id="cam1"
    )
    
    assert person is not None
    assert person.tracking_id == 1
    assert person.is_active is True
    assert person.camera_id == "cam1"
    assert len(centroid_tracker.objects) == 1


def test_update_with_detections(centroid_tracker, sample_detections):
    """Test updating tracker with detections"""
    tracked = centroid_tracker.update(sample_detections, "cam1")
    
    assert len(tracked) >= len(sample_detections)
    
    # Check active persons
    active = centroid_tracker.get_active_persons("cam1")
    assert len(active) == len(sample_detections)


def test_update_without_detections(centroid_tracker, sample_detections):
    """Test updating with no detections (persons disappearing)"""
    # First, add some persons
    centroid_tracker.update(sample_detections, "cam1")
    
    # Then update with no detections
    for _ in range(10):
        centroid_tracker.update([], "cam1")
    
    # All should be deregistered
    active = centroid_tracker.get_active_persons("cam1")
    assert len(active) == 0


def test_tracking_persistence(centroid_tracker):
    """Test that tracking persists across similar detections"""
    det1 = [Detection(bbox=(100, 100, 50, 100), confidence=0.9, center=(125, 150), frame_id=1)]
    
    # First update
    tracked1 = centroid_tracker.update(det1, "cam1")
    tracking_id = list(tracked1.keys())[0]
    
    # Second update with similar detection
    det2 = [Detection(bbox=(105, 105, 50, 100), confidence=0.9, center=(130, 155), frame_id=2)]
    tracked2 = centroid_tracker.update(det2, "cam1")
    
    # Should have same tracking ID
    assert tracking_id in tracked2


def test_set_employee_id(centroid_tracker, sample_detections):
    """Test setting employee ID for a tracked person"""
    tracked = centroid_tracker.update(sample_detections, "cam1")
    tracking_id = list(tracked.keys())[0]
    
    centroid_tracker.set_employee_id(tracking_id, "EMP001")
    
    person = centroid_tracker.get_person(tracking_id)
    assert person.employee_id == "EMP001"


def test_clear_camera(centroid_tracker, sample_detections):
    """Test clearing all tracked persons for a camera"""
    centroid_tracker.update(sample_detections, "cam1")
    centroid_tracker.update(sample_detections, "cam2")
    
    centroid_tracker.clear_camera("cam1")
    
    active_cam1 = centroid_tracker.get_active_persons("cam1")
    active_cam2 = centroid_tracker.get_active_persons("cam2")
    
    assert len(active_cam1) == 0
    assert len(active_cam2) > 0


def test_tracking_manager():
    """Test tracking manager"""
    manager = TrackingManager()
    
    # Test getting tracker
    tracker = manager.get_tracker("cam1")
    assert tracker is not None
    
    # Test statistics
    stats = manager.get_statistics()
    assert 'total_cameras' in stats
    assert 'total_tracked' in stats
