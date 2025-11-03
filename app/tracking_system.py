"""
Tracking system for maintaining identity of detected persons across frames
"""
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging
from scipy.spatial import distance as dist

from app.detection_engine import Detection
from app import config

logger = logging.getLogger(__name__)


@dataclass
class TrackedPerson:
    """Represents a tracked person across frames"""
    tracking_id: int
    employee_id: Optional[str] = None
    centroid: Tuple[int, int] = (0, 0)
    bbox: Tuple[int, int, int, int] = (0, 0, 0, 0)
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    disappeared_frames: int = 0
    is_active: bool = True
    camera_id: str = ""
    confidence: float = 0.0


class CentroidTracker:
    """
    Track objects using centroid tracking algorithm
    Based on correlation between centroids in consecutive frames
    """
    
    def __init__(self, max_disappeared: int = 30, max_distance: float = 50):
        """
        Initialize the centroid tracker
        
        Args:
            max_disappeared: Maximum frames an object can disappear before being deregistered
            max_distance: Maximum distance for matching centroids between frames
        """
        self.next_object_id = 1
        self.objects: Dict[int, TrackedPerson] = {}
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance
    
    def register(self, centroid: Tuple[int, int], bbox: Tuple[int, int, int, int],
                 confidence: float, camera_id: str) -> TrackedPerson:
        """Register a new tracked object"""
        tracking_id = self.next_object_id
        self.next_object_id += 1
        
        tracked_person = TrackedPerson(
            tracking_id=tracking_id,
            centroid=centroid,
            bbox=bbox,
            confidence=confidence,
            camera_id=camera_id
        )
        
        self.objects[tracking_id] = tracked_person
        logger.info(f"Registered new person: tracking_id={tracking_id}")
        return tracked_person
    
    def deregister(self, tracking_id: int):
        """Remove a tracked object"""
        if tracking_id in self.objects:
            person = self.objects[tracking_id]
            person.is_active = False
            logger.info(f"Deregistered person: tracking_id={tracking_id}")
            # Keep in dict for history but mark inactive
            # del self.objects[tracking_id]
    
    def update(self, detections: List[Detection], camera_id: str) -> Dict[int, TrackedPerson]:
        """
        Update tracked objects with new detections
        
        Args:
            detections: List of Detection objects
            camera_id: Camera identifier
            
        Returns:
            Dictionary of tracking_id -> TrackedPerson
        """
        # If no detections, mark all as disappeared
        if len(detections) == 0:
            for tracking_id in list(self.objects.keys()):
                person = self.objects[tracking_id]
                if person.is_active and person.camera_id == camera_id:
                    person.disappeared_frames += 1
                    person.last_seen = datetime.now()
                    
                    # Deregister if disappeared too long
                    if person.disappeared_frames > self.max_disappeared:
                        self.deregister(tracking_id)
            
            return self.objects
        
        # Get input centroids
        input_centroids = np.array([det.center for det in detections])
        
        # If no existing objects, register all detections
        active_objects = {k: v for k, v in self.objects.items() 
                         if v.is_active and v.camera_id == camera_id}
        
        if len(active_objects) == 0:
            for i, det in enumerate(detections):
                self.register(det.center, det.bbox, det.confidence, camera_id)
        else:
            # Get existing centroids
            object_ids = list(active_objects.keys())
            object_centroids = np.array([obj.centroid for obj in active_objects.values()])
            
            # Compute distance between each pair
            D = dist.cdist(object_centroids, input_centroids)
            
            # Match objects to detections
            # Find minimum value in each row, then sort by these values
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]
            
            used_rows = set()
            used_cols = set()
            
            # Update matched objects
            for (row, col) in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue
                
                # Check if distance is acceptable
                if D[row, col] > self.max_distance:
                    continue
                
                tracking_id = object_ids[row]
                person = self.objects[tracking_id]
                
                # Update person information
                person.centroid = detections[col].center
                person.bbox = detections[col].bbox
                person.confidence = detections[col].confidence
                person.disappeared_frames = 0
                person.last_seen = datetime.now()
                
                used_rows.add(row)
                used_cols.add(col)
            
            # Handle unmatched existing objects (disappeared)
            unused_rows = set(range(D.shape[0])) - used_rows
            for row in unused_rows:
                tracking_id = object_ids[row]
                person = self.objects[tracking_id]
                person.disappeared_frames += 1
                person.last_seen = datetime.now()
                
                if person.disappeared_frames > self.max_disappeared:
                    self.deregister(tracking_id)
            
            # Register new detections (unmatched)
            unused_cols = set(range(D.shape[1])) - used_cols
            for col in unused_cols:
                det = detections[col]
                self.register(det.center, det.bbox, det.confidence, camera_id)
        
        return self.objects
    
    def get_active_persons(self, camera_id: str = None) -> Dict[int, TrackedPerson]:
        """Get all currently active tracked persons"""
        if camera_id:
            return {k: v for k, v in self.objects.items() 
                   if v.is_active and v.camera_id == camera_id}
        return {k: v for k, v in self.objects.items() if v.is_active}
    
    def get_person(self, tracking_id: int) -> Optional[TrackedPerson]:
        """Get a specific tracked person"""
        return self.objects.get(tracking_id)
    
    def set_employee_id(self, tracking_id: int, employee_id: str):
        """Associate an employee ID with a tracked person"""
        if tracking_id in self.objects:
            self.objects[tracking_id].employee_id = employee_id
            logger.info(f"Associated tracking_id={tracking_id} with employee={employee_id}")
    
    def clear_camera(self, camera_id: str):
        """Clear all tracked persons for a specific camera"""
        for tracking_id in list(self.objects.keys()):
            person = self.objects[tracking_id]
            if person.camera_id == camera_id:
                self.deregister(tracking_id)
        logger.info(f"Cleared all tracked persons for camera: {camera_id}")


class TrackingManager:
    """
    High-level tracking manager that coordinates detection and tracking
    Manages multiple cameras and integrates with face recognition
    """
    
    def __init__(self, face_recognition_engine=None):
        self.trackers: Dict[str, CentroidTracker] = {}
        self.face_recognition = face_recognition_engine
    
    def get_tracker(self, camera_id: str) -> CentroidTracker:
        """Get or create tracker for a camera"""
        if camera_id not in self.trackers:
            self.trackers[camera_id] = CentroidTracker(
                max_disappeared=config.TRACKING_MAX_DISAPPEARED,
                max_distance=config.TRACKING_MAX_DISTANCE
            )
        return self.trackers[camera_id]
    
    def update(self, camera_id: str, detections: List[Detection], 
               frame: np.ndarray = None) -> Dict[int, TrackedPerson]:
        """
        Update tracking for a camera
        
        Args:
            camera_id: Camera identifier
            detections: List of detections
            frame: Optional frame for face recognition
            
        Returns:
            Dictionary of active tracked persons
        """
        tracker = self.get_tracker(camera_id)
        tracked_persons = tracker.update(detections, camera_id)
        
        # Optionally identify using face recognition
        if self.face_recognition and frame is not None:
            for tracking_id, person in tracked_persons.items():
                if person.is_active and person.employee_id is None:
                    employee_id = self.face_recognition.identify_face(
                        frame, person.bbox
                    )
                    if employee_id:
                        tracker.set_employee_id(tracking_id, employee_id)
        
        return tracked_persons
    
    def get_active_persons(self, camera_id: str = None) -> Dict[int, TrackedPerson]:
        """Get all active tracked persons across all or specific camera"""
        if camera_id:
            tracker = self.get_tracker(camera_id)
            return tracker.get_active_persons()
        
        # Aggregate across all cameras
        all_persons = {}
        for tracker in self.trackers.values():
            all_persons.update(tracker.get_active_persons())
        return all_persons
    
    def get_newly_left_persons(self, camera_id: str) -> List[TrackedPerson]:
        """Get persons who just became inactive (left the scene)"""
        tracker = self.get_tracker(camera_id)
        newly_left = []
        
        for person in tracker.objects.values():
            # Check if just deregistered (disappeared_frames == max_disappeared + 1)
            if (not person.is_active and 
                person.camera_id == camera_id and
                person.disappeared_frames == tracker.max_disappeared + 1):
                newly_left.append(person)
        
        return newly_left
    
    def clear_camera(self, camera_id: str):
        """Clear tracking for a camera"""
        if camera_id in self.trackers:
            self.trackers[camera_id].clear_camera(camera_id)
    
    def get_statistics(self) -> Dict:
        """Get tracking statistics"""
        total_tracked = sum(len(t.objects) for t in self.trackers.values())
        total_active = sum(
            len(t.get_active_persons()) for t in self.trackers.values()
        )
        
        return {
            'total_cameras': len(self.trackers),
            'total_tracked': total_tracked,
            'total_active': total_active,
            'cameras': {
                cam_id: {
                    'total': len(tracker.objects),
                    'active': len(tracker.get_active_persons())
                }
                for cam_id, tracker in self.trackers.items()
            }
        }
