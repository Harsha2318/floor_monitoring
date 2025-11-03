"""
Main Flask application for Employee Monitoring System
"""
import cv2
import numpy as np
from flask import render_template, Response, jsonify, request
from flask_socketio import emit
import json
import logging
from datetime import datetime, timedelta
from threading import Thread
import time

from app import app, socketio, config
from app.database import Database
from app.camera_manager import CameraManager
from app.detection_engine import DetectionEngine, FaceRecognitionEngine
from app.tracking_system import TrackingManager
from app.alert_manager import AlertManager

logger = logging.getLogger(__name__)

# Initialize components
db = Database()
camera_manager = CameraManager()
detection_engine = DetectionEngine(model_type=config.DETECTION_MODEL)
face_recognition = FaceRecognitionEngine(enabled=config.FACE_RECOGNITION_ENABLED)
tracking_manager = TrackingManager(face_recognition_engine=face_recognition)
alert_manager = AlertManager(database=db, timeout_minutes=config.ABSENCE_TIMEOUT_MINUTES)

# Global state
processing_active = False
processing_thread = None


def process_cameras():
    """Main processing loop for all cameras"""
    global processing_active
    
    frame_skip_counter = 0
    
    while processing_active:
        try:
            active_cameras = camera_manager.get_active_cameras()
            
            for camera_id in active_cameras:
                frame = camera_manager.get_frame(camera_id)
                
                if frame is None:
                    continue
                
                # Skip frames for performance
                frame_skip_counter += 1
                if frame_skip_counter % config.FRAME_SKIP != 0:
                    continue
                
                # Detect persons
                detections = detection_engine.detect(frame)
                
                # Update tracking
                tracked_persons = tracking_manager.update(camera_id, detections, frame)
                
                # Check for newly present persons (log entry)
                active_persons = tracking_manager.get_active_persons(camera_id)
                for tracking_id, person in active_persons.items():
                    # Check if this is a new entry (just became active)
                    existing_logs = db.get_active_presences(camera_id)
                    existing_ids = [log['tracking_id'] for log in existing_logs]
                    
                    if tracking_id not in existing_ids:
                        db.log_entry(tracking_id, camera_id, person.employee_id)
                
                # Check for persons who left
                newly_left = tracking_manager.get_newly_left_persons(camera_id)
                for person in newly_left:
                    # Log exit
                    db.log_exit(person.tracking_id, camera_id)
                    
                    # Add pending alert
                    alert_manager.add_pending_alert(person)
                
                # Emit real-time updates via WebSocket
                socketio.emit('camera_update', {
                    'camera_id': camera_id,
                    'detections': len(detections),
                    'tracked': len(active_persons),
                    'timestamp': datetime.now().isoformat()
                })
            
            # Small delay to prevent CPU overload
            time.sleep(0.01)
            
        except Exception as e:
            logger.error(f"Error in processing loop: {e}")
            time.sleep(1)


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/cameras')
def get_cameras():
    """Get list of all cameras"""
    cameras = camera_manager.get_all_cameras()
    return jsonify([{
        'camera_id': cam.camera_id,
        'name': cam.name,
        'type': cam.camera_type,
        'is_active': cam.is_active,
        'resolution': cam.resolution,
        'fps': cam.fps
    } for cam in cameras])


@app.route('/api/cameras/add', methods=['POST'])
def add_camera():
    """Add a new camera"""
    data = request.json
    success = camera_manager.add_camera(
        camera_id=data['camera_id'],
        name=data['name'],
        camera_type=data['type'],
        source=data['source']
    )
    
    if success:
        # Also add to database
        db.add_camera(data['camera_id'], data['name'], data['type'], data['source'])
    
    return jsonify({'success': success})


@app.route('/api/cameras/<camera_id>/remove', methods=['POST'])
def remove_camera(camera_id):
    """Remove a camera"""
    camera_manager.remove_camera(camera_id)
    return jsonify({'success': True})


def generate_frames(camera_id):
    """Generate video frames for streaming"""
    while True:
        try:
            frame = camera_manager.get_frame(camera_id)
            
            if frame is None:
                time.sleep(0.1)
                continue
            
            # Get detections and draw on frame
            detections = detection_engine.detect(frame)
            frame_with_detections = detection_engine.draw_detections(frame, detections)
            
            # Draw tracking information
            active_persons = tracking_manager.get_active_persons(camera_id)
            for tracking_id, person in active_persons.items():
                x, y, w, h = person.bbox
                # Draw tracking ID
                label = f"ID:{tracking_id}"
                if person.employee_id:
                    label += f" ({person.employee_id})"
                
                cv2.putText(frame_with_detections, label, (x, y - 25),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame_with_detections,
                                      [cv2.IMWRITE_JPEG_QUALITY, config.STREAM_QUALITY])
            
            if ret:
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            time.sleep(1.0 / config.STREAM_FPS)
            
        except Exception as e:
            logger.error(f"Error generating frames for {camera_id}: {e}")
            time.sleep(1)


@app.route('/video_feed/<camera_id>')
def video_feed(camera_id):
    """Video streaming route"""
    return Response(generate_frames(camera_id),
                   mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/presence/active')
def get_active_presence():
    """Get all currently present employees"""
    presences = db.get_active_presences()
    return jsonify(presences)


@app.route('/api/presence/history')
def get_presence_history():
    """Get presence history with filters"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    employee_id = request.args.get('employee_id')
    
    if start_date:
        start_date = datetime.fromisoformat(start_date)
    if end_date:
        end_date = datetime.fromisoformat(end_date)
    
    history = db.get_presence_history(start_date, end_date, employee_id)
    return jsonify(history)


@app.route('/api/alerts/active')
def get_active_alerts():
    """Get all unacknowledged alerts"""
    alerts = db.get_unacknowledged_alerts()
    return jsonify(alerts)


@app.route('/api/alerts/<int:alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(alert_id):
    """Acknowledge an alert"""
    success = db.acknowledge_alert(alert_id)
    return jsonify({'success': success})


@app.route('/api/statistics')
def get_statistics():
    """Get system statistics"""
    # Get date range from query params
    days = int(request.args.get('days', 1))
    start_date = datetime.now() - timedelta(days=days)
    end_date = datetime.now()
    
    stats = db.get_statistics(start_date, end_date)
    
    # Add tracking statistics
    tracking_stats = tracking_manager.get_statistics()
    stats['tracking'] = tracking_stats
    
    # Add alert statistics
    alert_stats = alert_manager.get_statistics()
    stats['alerts'] = alert_stats
    
    # Add camera statistics
    camera_stats = camera_manager.get_statistics()
    stats['cameras'] = camera_stats
    
    return jsonify(stats)


@app.route('/api/employees')
def get_employees():
    """Get all employees"""
    employees = db.get_all_employees()
    return jsonify(employees)


@app.route('/api/employees/add', methods=['POST'])
def add_employee():
    """Add a new employee"""
    data = request.json
    success = db.add_employee(
        employee_id=data['employee_id'],
        name=data['name']
    )
    return jsonify({'success': success})


@app.route('/api/system/start', methods=['POST'])
def start_system():
    """Start the monitoring system"""
    global processing_active, processing_thread
    
    if not processing_active:
        processing_active = True
        processing_thread = Thread(target=process_cameras, daemon=True)
        processing_thread.start()
        
        alert_manager.start()
        
        logger.info("Monitoring system started")
        return jsonify({'success': True, 'message': 'System started'})
    
    return jsonify({'success': False, 'message': 'System already running'})


@app.route('/api/system/stop', methods=['POST'])
def stop_system():
    """Stop the monitoring system"""
    global processing_active
    
    processing_active = False
    alert_manager.stop()
    
    logger.info("Monitoring system stopped")
    return jsonify({'success': True, 'message': 'System stopped'})


@app.route('/api/system/status')
def get_system_status():
    """Get system status"""
    return jsonify({
        'processing_active': processing_active,
        'cameras_active': len(camera_manager.get_active_cameras()),
        'total_cameras': len(camera_manager.cameras),
        'detection_model': config.DETECTION_MODEL,
        'alert_timeout': config.ABSENCE_TIMEOUT_MINUTES
    })


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info("Client connected")
    emit('connected', {'message': 'Connected to monitoring system'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info("Client disconnected")


def init_system():
    """Initialize the system on startup"""
    logger.info("Initializing system...")
    
    # Load face recognition data if enabled
    if config.FACE_RECOGNITION_ENABLED and face_recognition.enabled:
        face_recognition.load_known_faces(config.FACES_DIR)
    
    # Initialize cameras from database
    cameras = db.get_cameras()
    for cam in cameras:
        camera_manager.add_camera(
            camera_id=cam['camera_id'],
            name=cam['name'],
            camera_type=cam['type'],
            source=cam['source']
        )
    
    # If no cameras in database, try to initialize from config
    if not cameras:
        camera_manager.initialize_from_config()
    
    # Register alert callback
    def alert_callback(alert):
        socketio.emit('alert', {
            'tracking_id': alert.tracking_id,
            'employee_id': alert.employee_id,
            'left_at': alert.left_at.isoformat(),
            'timeout_minutes': alert.timeout_minutes
        })
    
    alert_manager.register_callback(alert_callback)
    
    logger.info("System initialization complete")


# Initialize on import
init_system()
