"""
Detection Engine for person detection using MediaPipe and YOLO
"""
import cv2
import numpy as np
from typing import List, Tuple, Optional
import logging
from dataclasses import dataclass

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    logging.warning("MediaPipe not available")

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logging.warning("YOLO not available")

from app import config

logger = logging.getLogger(__name__)


@dataclass
class Detection:
    """Represents a person detection"""
    bbox: Tuple[int, int, int, int]  # (x, y, width, height)
    confidence: float
    center: Tuple[int, int]
    frame_id: int


class DetectionEngine:
    """Handle person detection using various models"""
    
    def __init__(self, model_type: str = 'mediapipe'):
        self.model_type = model_type
        self.confidence_threshold = config.DETECTION_CONFIDENCE
        self.frame_count = 0
        
        # Initialize the selected model
        if model_type == 'mediapipe' and MEDIAPIPE_AVAILABLE:
            self._init_mediapipe()
        elif model_type == 'yolo' and YOLO_AVAILABLE:
            self._init_yolo()
        elif model_type == 'opencv':
            self._init_opencv()
        else:
            logger.warning(f"Falling back to OpenCV HOG detector")
            self._init_opencv()
    
    def _init_mediapipe(self):
        """Initialize MediaPipe Pose detection"""
        try:
            self.mp_pose = mp.solutions.pose
            self.pose = self.mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                min_detection_confidence=self.confidence_threshold,
                min_tracking_confidence=0.5
            )
            logger.info("MediaPipe Pose detector initialized")
        except Exception as e:
            logger.error(f"Failed to initialize MediaPipe: {e}")
            self._init_opencv()
    
    def _init_yolo(self):
        """Initialize YOLO model"""
        try:
            # Use YOLOv8n (nano) for faster inference
            self.model = YOLO('yolov8n.pt')
            logger.info("YOLOv8 model initialized")
        except Exception as e:
            logger.error(f"Failed to initialize YOLO: {e}")
            self._init_opencv()
    
    def _init_opencv(self):
        """Initialize OpenCV HOG person detector (fallback)"""
        try:
            self.hog = cv2.HOGDescriptor()
            self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
            self.model_type = 'opencv'
            logger.info("OpenCV HOG detector initialized")
        except Exception as e:
            logger.error(f"Failed to initialize OpenCV detector: {e}")
            raise
    
    def detect(self, frame: np.ndarray) -> List[Detection]:
        """
        Detect persons in the frame
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            List of Detection objects
        """
        self.frame_count += 1
        
        if self.model_type == 'mediapipe':
            return self._detect_mediapipe(frame)
        elif self.model_type == 'yolo':
            return self._detect_yolo(frame)
        else:
            return self._detect_opencv(frame)
    
    def _detect_mediapipe(self, frame: np.ndarray) -> List[Detection]:
        """Detect using MediaPipe"""
        detections = []
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)
        
        if results.pose_landmarks:
            # Get bounding box from pose landmarks
            h, w = frame.shape[:2]
            landmarks = results.pose_landmarks.landmark
            
            # Extract x, y coordinates
            x_coords = [lm.x * w for lm in landmarks]
            y_coords = [lm.y * h for lm in landmarks]
            
            # Calculate bounding box
            x_min = int(max(0, min(x_coords) - 20))
            y_min = int(max(0, min(y_coords) - 20))
            x_max = int(min(w, max(x_coords) + 20))
            y_max = int(min(h, max(y_coords) + 20))
            
            bbox = (x_min, y_min, x_max - x_min, y_max - y_min)
            center = (x_min + (x_max - x_min) // 2, y_min + (y_max - y_min) // 2)
            
            detection = Detection(
                bbox=bbox,
                confidence=0.9,  # MediaPipe doesn't provide confidence per detection
                center=center,
                frame_id=self.frame_count
            )
            detections.append(detection)
        
        return detections
    
    def _detect_yolo(self, frame: np.ndarray) -> List[Detection]:
        """Detect using YOLO"""
        detections = []
        
        # Run inference
        results = self.model(frame, verbose=False)
        
        # Process results
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Filter for person class (class 0 in COCO dataset)
                if int(box.cls[0]) == 0:
                    conf = float(box.conf[0])
                    if conf >= self.confidence_threshold:
                        # Get bounding box
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        bbox = (int(x1), int(y1), int(x2 - x1), int(y2 - y1))
                        center = (int(x1 + (x2 - x1) / 2), int(y1 + (y2 - y1) / 2))
                        
                        detection = Detection(
                            bbox=bbox,
                            confidence=conf,
                            center=center,
                            frame_id=self.frame_count
                        )
                        detections.append(detection)
        
        return detections
    
    def _detect_opencv(self, frame: np.ndarray) -> List[Detection]:
        """Detect using OpenCV HOG"""
        detections = []
        
        # Resize for faster detection
        scale = 0.5
        small_frame = cv2.resize(frame, None, fx=scale, fy=scale)
        
        # Detect people
        boxes, weights = self.hog.detectMultiScale(
            small_frame,
            winStride=(8, 8),
            padding=(8, 8),
            scale=1.05
        )
        
        # Process detections
        for (x, y, w, h), weight in zip(boxes, weights):
            if weight >= self.confidence_threshold:
                # Scale back to original size
                bbox = (int(x / scale), int(y / scale), 
                       int(w / scale), int(h / scale))
                center = (bbox[0] + bbox[2] // 2, bbox[1] + bbox[3] // 2)
                
                detection = Detection(
                    bbox=bbox,
                    confidence=float(weight),
                    center=center,
                    frame_id=self.frame_count
                )
                detections.append(detection)
        
        return detections
    
    def draw_detections(self, frame: np.ndarray, detections: List[Detection]) -> np.ndarray:
        """
        Draw detection boxes on frame
        
        Args:
            frame: Input frame
            detections: List of detections
            
        Returns:
            Frame with drawn detections
        """
        output = frame.copy()
        
        for det in detections:
            x, y, w, h = det.bbox
            
            # Draw bounding box
            color = (0, 255, 0)  # Green
            cv2.rectangle(output, (x, y), (x + w, y + h), color, 2)
            
            # Draw confidence
            label = f"{det.confidence:.2f}"
            cv2.putText(output, label, (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Draw center point
            cv2.circle(output, det.center, 4, (0, 0, 255), -1)
        
        return output
    
    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'pose'):
            self.pose.close()
        logger.info("Detection engine cleaned up")


class FaceRecognitionEngine:
    """Optional face recognition for employee identification"""
    
    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.known_faces = {}
        
        if enabled:
            try:
                import face_recognition
                self.face_recognition = face_recognition
                logger.info("Face recognition engine initialized")
            except ImportError:
                logger.warning("face_recognition library not available")
                self.enabled = False
    
    def load_known_faces(self, faces_dir: str):
        """Load known face encodings from directory"""
        if not self.enabled:
            return
        
        import os
        faces_path = config.FACES_DIR
        
        for filename in os.listdir(faces_path):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                employee_id = os.path.splitext(filename)[0]
                image_path = os.path.join(faces_path, filename)
                
                try:
                    image = self.face_recognition.load_image_file(image_path)
                    encoding = self.face_recognition.face_encodings(image)[0]
                    self.known_faces[employee_id] = encoding
                    logger.info(f"Loaded face for employee: {employee_id}")
                except Exception as e:
                    logger.error(f"Failed to load face for {employee_id}: {e}")
    
    def identify_face(self, frame: np.ndarray, bbox: Tuple[int, int, int, int]) -> Optional[str]:
        """
        Identify person by face
        
        Args:
            frame: Input frame
            bbox: Bounding box (x, y, w, h)
            
        Returns:
            Employee ID or None
        """
        if not self.enabled or not self.known_faces:
            return None
        
        try:
            x, y, w, h = bbox
            face_region = frame[y:y+h, x:x+w]
            
            # Get face encoding
            rgb_face = cv2.cvtColor(face_region, cv2.COLOR_BGR2RGB)
            encodings = self.face_recognition.face_encodings(rgb_face)
            
            if encodings:
                face_encoding = encodings[0]
                
                # Compare with known faces
                for employee_id, known_encoding in self.known_faces.items():
                    match = self.face_recognition.compare_faces(
                        [known_encoding], face_encoding, tolerance=0.6
                    )
                    if match[0]:
                        return employee_id
        except Exception as e:
            logger.debug(f"Face identification failed: {e}")
        
        return None
