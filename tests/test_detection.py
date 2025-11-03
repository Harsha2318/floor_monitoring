"""
Test suite for Detection Engine
"""
import pytest
import numpy as np
import cv2
from app.detection_engine import DetectionEngine, Detection


@pytest.fixture
def detection_engine():
    """Create a detection engine instance"""
    return DetectionEngine(model_type='opencv')


@pytest.fixture
def sample_frame():
    """Create a sample frame for testing"""
    # Create a blank frame with a person-like rectangle
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    # Draw a person-shaped rectangle
    cv2.rectangle(frame, (200, 100), (400, 400), (255, 255, 255), -1)
    return frame


def test_detection_engine_initialization(detection_engine):
    """Test detection engine initializes correctly"""
    assert detection_engine is not None
    assert detection_engine.model_type in ['mediapipe', 'yolo', 'opencv']
    assert detection_engine.confidence_threshold > 0


def test_detect_returns_list(detection_engine, sample_frame):
    """Test detect returns a list"""
    detections = detection_engine.detect(sample_frame)
    assert isinstance(detections, list)


def test_detection_properties(detection_engine, sample_frame):
    """Test detection object has required properties"""
    detections = detection_engine.detect(sample_frame)
    
    for det in detections:
        assert isinstance(det, Detection)
        assert isinstance(det.bbox, tuple)
        assert len(det.bbox) == 4
        assert isinstance(det.confidence, float)
        assert isinstance(det.center, tuple)
        assert len(det.center) == 2


def test_draw_detections(detection_engine, sample_frame):
    """Test drawing detections on frame"""
    detections = detection_engine.detect(sample_frame)
    output = detection_engine.draw_detections(sample_frame, detections)
    
    assert output is not None
    assert output.shape == sample_frame.shape


def test_frame_count_increments(detection_engine, sample_frame):
    """Test frame counter increments"""
    initial_count = detection_engine.frame_count
    detection_engine.detect(sample_frame)
    assert detection_engine.frame_count == initial_count + 1


def test_cleanup(detection_engine):
    """Test cleanup doesn't raise errors"""
    try:
        detection_engine.cleanup()
        assert True
    except Exception:
        assert False, "Cleanup raised an exception"
