"""
Camera Manager for handling multiple USB and IP cameras
"""
import cv2
import numpy as np
from typing import Dict, Optional, List, Tuple
from threading import Thread, Lock
from queue import Queue
import time
import logging
from dataclasses import dataclass

from app import config

logger = logging.getLogger(__name__)


@dataclass
class CameraInfo:
    """Information about a camera"""
    camera_id: str
    name: str
    camera_type: str  # 'usb' or 'ip'
    source: str  # Device ID or RTSP URL
    is_active: bool = False
    fps: float = 0.0
    resolution: Tuple[int, int] = (0, 0)
    last_frame_time: float = 0.0


class CameraStream:
    """Handle video stream from a single camera"""
    
    def __init__(self, camera_info: CameraInfo, buffer_size: int = 5):
        self.camera_info = camera_info
        self.buffer_size = buffer_size
        self.frame_queue = Queue(maxsize=buffer_size)
        self.capture = None
        self.thread = None
        self.stopped = False
        self.lock = Lock()
        self.frame_count = 0
        self.start_time = time.time()
        self.last_frame = None
    
    def start(self) -> bool:
        """Start the camera stream"""
        try:
            # Open video capture
            if self.camera_info.camera_type == 'usb':
                source = int(self.camera_info.source)
            else:
                source = self.camera_info.source
            
            self.capture = cv2.VideoCapture(source)
            
            if not self.capture.isOpened():
                logger.error(f"Failed to open camera: {self.camera_info.name}")
                return False
            
            # Set camera properties for better performance
            self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Get camera properties
            width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = self.capture.get(cv2.CAP_PROP_FPS)
            
            self.camera_info.resolution = (width, height)
            self.camera_info.fps = fps if fps > 0 else 30
            self.camera_info.is_active = True
            
            # Start the thread
            self.stopped = False
            self.thread = Thread(target=self._update, daemon=True)
            self.thread.start()
            
            logger.info(f"Started camera: {self.camera_info.name} "
                       f"({width}x{height} @ {fps}fps)")
            return True
            
        except Exception as e:
            logger.error(f"Error starting camera {self.camera_info.name}: {e}")
            return False
    
    def _update(self):
        """Read frames from camera in a separate thread"""
        while not self.stopped:
            if self.capture is None or not self.capture.isOpened():
                logger.warning(f"Camera {self.camera_info.name} disconnected")
                time.sleep(1)
                continue
            
            ret, frame = self.capture.read()
            
            if not ret:
                logger.warning(f"Failed to read frame from {self.camera_info.name}")
                time.sleep(0.1)
                continue
            
            # Resize frame if configured
            if config.MAX_FRAME_WIDTH and config.MAX_FRAME_HEIGHT:
                h, w = frame.shape[:2]
                if w > config.MAX_FRAME_WIDTH or h > config.MAX_FRAME_HEIGHT:
                    scale = min(config.MAX_FRAME_WIDTH / w, 
                              config.MAX_FRAME_HEIGHT / h)
                    new_w = int(w * scale)
                    new_h = int(h * scale)
                    frame = cv2.resize(frame, (new_w, new_h))
            
            # Update last frame
            with self.lock:
                self.last_frame = frame
                self.frame_count += 1
                self.camera_info.last_frame_time = time.time()
            
            # Add to queue (non-blocking)
            if not self.frame_queue.full():
                self.frame_queue.put(frame)
            else:
                # Remove oldest frame
                try:
                    self.frame_queue.get_nowait()
                    self.frame_queue.put(frame)
                except:
                    pass
    
    def read(self) -> Optional[np.ndarray]:
        """Read a frame from the queue"""
        if self.frame_queue.empty():
            with self.lock:
                return self.last_frame
        
        try:
            return self.frame_queue.get(timeout=1)
        except:
            with self.lock:
                return self.last_frame
    
    def get_latest_frame(self) -> Optional[np.ndarray]:
        """Get the most recent frame without queue"""
        with self.lock:
            return self.last_frame.copy() if self.last_frame is not None else None
    
    def get_fps(self) -> float:
        """Calculate actual FPS"""
        elapsed = time.time() - self.start_time
        if elapsed > 0:
            return self.frame_count / elapsed
        return 0.0
    
    def stop(self):
        """Stop the camera stream"""
        self.stopped = True
        
        if self.thread is not None:
            self.thread.join(timeout=2)
        
        if self.capture is not None:
            self.capture.release()
        
        self.camera_info.is_active = False
        logger.info(f"Stopped camera: {self.camera_info.name}")
    
    def is_active(self) -> bool:
        """Check if camera is active"""
        return self.camera_info.is_active and not self.stopped


class CameraManager:
    """Manage multiple camera streams"""
    
    def __init__(self):
        self.cameras: Dict[str, CameraStream] = {}
        self.lock = Lock()
    
    def add_camera(self, camera_id: str, name: str, 
                   camera_type: str, source: str) -> bool:
        """
        Add a new camera
        
        Args:
            camera_id: Unique identifier
            name: Display name
            camera_type: 'usb' or 'ip'
            source: Device ID (int) or RTSP URL (str)
            
        Returns:
            True if camera was added successfully
        """
        with self.lock:
            if camera_id in self.cameras:
                logger.warning(f"Camera {camera_id} already exists")
                return False
            
            camera_info = CameraInfo(
                camera_id=camera_id,
                name=name,
                camera_type=camera_type,
                source=source
            )
            
            stream = CameraStream(camera_info)
            
            if stream.start():
                self.cameras[camera_id] = stream
                logger.info(f"Added camera: {name} ({camera_id})")
                return True
            else:
                logger.error(f"Failed to start camera: {name}")
                return False
    
    def remove_camera(self, camera_id: str):
        """Remove a camera"""
        with self.lock:
            if camera_id in self.cameras:
                self.cameras[camera_id].stop()
                del self.cameras[camera_id]
                logger.info(f"Removed camera: {camera_id}")
    
    def get_camera(self, camera_id: str) -> Optional[CameraStream]:
        """Get a camera stream"""
        return self.cameras.get(camera_id)
    
    def get_frame(self, camera_id: str) -> Optional[np.ndarray]:
        """Get a frame from a specific camera"""
        camera = self.get_camera(camera_id)
        if camera and camera.is_active():
            return camera.get_latest_frame()
        return None
    
    def get_all_cameras(self) -> List[CameraInfo]:
        """Get information about all cameras"""
        return [cam.camera_info for cam in self.cameras.values()]
    
    def get_active_cameras(self) -> List[str]:
        """Get list of active camera IDs"""
        return [cam_id for cam_id, cam in self.cameras.items() 
                if cam.is_active()]
    
    def stop_all(self):
        """Stop all cameras"""
        with self.lock:
            for camera in self.cameras.values():
                camera.stop()
            self.cameras.clear()
            logger.info("Stopped all cameras")
    
    def initialize_from_config(self):
        """Initialize cameras from config"""
        # Add USB cameras
        for cam_config in config.CAMERA_CONFIGS.get('usb_cameras', []):
            self.add_camera(
                camera_id=f"usb_{cam_config['id']}",
                name=cam_config['name'],
                camera_type='usb',
                source=str(cam_config['id'])
            )
        
        # Add IP cameras
        for i, cam_config in enumerate(config.CAMERA_CONFIGS.get('ip_cameras', [])):
            self.add_camera(
                camera_id=f"ip_{i}",
                name=cam_config['name'],
                camera_type='ip',
                source=cam_config['url']
            )
    
    def get_statistics(self) -> Dict:
        """Get statistics for all cameras"""
        stats = {}
        for cam_id, camera in self.cameras.items():
            stats[cam_id] = {
                'name': camera.camera_info.name,
                'type': camera.camera_info.camera_type,
                'is_active': camera.is_active(),
                'fps': camera.get_fps(),
                'resolution': camera.camera_info.resolution,
                'frame_count': camera.frame_count
            }
        return stats
