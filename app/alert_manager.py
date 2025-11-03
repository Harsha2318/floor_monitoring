"""
Alert Manager for monitoring employee absence and generating alerts
"""
import time
from datetime import datetime, timedelta
from threading import Thread, Lock
from typing import Dict, List, Callable
import logging

try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    logging.warning("Plyer not available for notifications")

try:
    import winsound
    WINSOUND_AVAILABLE = True
except ImportError:
    WINSOUND_AVAILABLE = False

from app import config
from app.database import Database
from app.tracking_system import TrackedPerson

logger = logging.getLogger(__name__)


class Alert:
    """Represents an absence alert"""
    
    def __init__(self, tracking_id: int, employee_id: str, 
                 left_at: datetime, timeout_minutes: int):
        self.tracking_id = tracking_id
        self.employee_id = employee_id
        self.left_at = left_at
        self.timeout_minutes = timeout_minutes
        self.alert_time = left_at + timedelta(minutes=timeout_minutes)
        self.triggered = False
        self.acknowledged = False
    
    def should_trigger(self) -> bool:
        """Check if alert should be triggered"""
        return not self.triggered and datetime.now() >= self.alert_time
    
    def time_remaining(self) -> float:
        """Get seconds remaining until alert"""
        remaining = (self.alert_time - datetime.now()).total_seconds()
        return max(0, remaining)


class AlertManager:
    """
    Manage absence alerts for employees
    Monitors when employees leave and triggers alerts after timeout
    """
    
    def __init__(self, database: Database, timeout_minutes: int = None):
        self.database = database
        self.timeout_minutes = timeout_minutes or config.ABSENCE_TIMEOUT_MINUTES
        self.pending_alerts: Dict[int, Alert] = {}  # tracking_id -> Alert
        self.alert_callbacks: List[Callable] = []
        self.lock = Lock()
        self.running = False
        self.monitor_thread = None
        
        logger.info(f"Alert Manager initialized with {self.timeout_minutes} min timeout")
    
    def start(self):
        """Start the alert monitoring thread"""
        if not self.running:
            self.running = True
            self.monitor_thread = Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("Alert monitoring started")
    
    def stop(self):
        """Stop the alert monitoring thread"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Alert monitoring stopped")
    
    def register_callback(self, callback: Callable):
        """
        Register a callback function to be called when alert is triggered
        Callback signature: callback(alert: Alert)
        """
        self.alert_callbacks.append(callback)
    
    def add_pending_alert(self, person: TrackedPerson):
        """
        Add a pending alert for a person who left
        
        Args:
            person: TrackedPerson who left the workspace
        """
        with self.lock:
            if person.tracking_id in self.pending_alerts:
                logger.debug(f"Alert already pending for tracking_id={person.tracking_id}")
                return
            
            alert = Alert(
                tracking_id=person.tracking_id,
                employee_id=person.employee_id or "Unknown",
                left_at=person.last_seen,
                timeout_minutes=self.timeout_minutes
            )
            
            self.pending_alerts[person.tracking_id] = alert
            
            logger.info(f"Added pending alert: tracking_id={person.tracking_id}, "
                       f"timeout={self.timeout_minutes}min, "
                       f"trigger_at={alert.alert_time}")
    
    def cancel_alert(self, tracking_id: int):
        """
        Cancel a pending alert (person returned)
        
        Args:
            tracking_id: Tracking ID of the person
        """
        with self.lock:
            if tracking_id in self.pending_alerts:
                alert = self.pending_alerts[tracking_id]
                if not alert.triggered:
                    del self.pending_alerts[tracking_id]
                    logger.info(f"Cancelled alert for tracking_id={tracking_id}")
    
    def _monitor_loop(self):
        """Monitor pending alerts and trigger when timeout is reached"""
        while self.running:
            try:
                self._check_alerts()
                time.sleep(config.ALERT_CHECK_INTERVAL)
            except Exception as e:
                logger.error(f"Error in alert monitor loop: {e}")
                time.sleep(5)
    
    def _check_alerts(self):
        """Check all pending alerts and trigger if needed"""
        with self.lock:
            alerts_to_trigger = []
            
            for tracking_id, alert in list(self.pending_alerts.items()):
                if alert.should_trigger():
                    alerts_to_trigger.append(alert)
            
            # Trigger alerts outside the lock
            for alert in alerts_to_trigger:
                self._trigger_alert(alert)
    
    def _trigger_alert(self, alert: Alert):
        """
        Trigger an alert
        
        Args:
            alert: Alert to trigger
        """
        alert.triggered = True
        
        # Save to database
        try:
            self.database.create_alert(
                tracking_id=alert.tracking_id,
                employee_id=alert.employee_id,
                left_at=alert.left_at,
                timeout_minutes=alert.timeout_minutes
            )
        except Exception as e:
            logger.error(f"Failed to save alert to database: {e}")
        
        # Generate notification
        self._show_notification(alert)
        
        # Play sound
        if config.ALERT_SOUND_ENABLED:
            self._play_alert_sound()
        
        # Call registered callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
        
        logger.warning(f"ALERT TRIGGERED: Employee {alert.employee_id} "
                      f"(tracking_id={alert.tracking_id}) absent for "
                      f"{alert.timeout_minutes} minutes")
    
    def _show_notification(self, alert: Alert):
        """Show desktop notification"""
        if not config.ALERT_NOTIFICATION_ENABLED:
            return
        
        if PLYER_AVAILABLE:
            try:
                employee_name = alert.employee_id or "Unknown Employee"
                notification.notify(
                    title="Employee Absence Alert",
                    message=f"{employee_name} has been absent for "
                           f"{alert.timeout_minutes} minutes",
                    app_name="Floor Monitoring System",
                    timeout=10
                )
            except Exception as e:
                logger.error(f"Failed to show notification: {e}")
        else:
            logger.warning("Plyer not available, cannot show notification")
    
    def _play_alert_sound(self):
        """Play alert sound (Windows only)"""
        if WINSOUND_AVAILABLE:
            try:
                # Play system alert sound
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except Exception as e:
                logger.error(f"Failed to play alert sound: {e}")
        else:
            logger.debug("Winsound not available")
    
    def get_pending_alerts(self) -> List[Alert]:
        """Get all pending alerts"""
        with self.lock:
            return list(self.pending_alerts.values())
    
    def get_triggered_alerts(self) -> List[Alert]:
        """Get all triggered but unacknowledged alerts"""
        with self.lock:
            return [alert for alert in self.pending_alerts.values() 
                   if alert.triggered and not alert.acknowledged]
    
    def acknowledge_alert(self, tracking_id: int):
        """
        Acknowledge an alert
        
        Args:
            tracking_id: Tracking ID of the alert
        """
        with self.lock:
            if tracking_id in self.pending_alerts:
                alert = self.pending_alerts[tracking_id]
                alert.acknowledged = True
                logger.info(f"Alert acknowledged: tracking_id={tracking_id}")
    
    def get_statistics(self) -> Dict:
        """Get alert statistics"""
        with self.lock:
            total_pending = len(self.pending_alerts)
            triggered = len([a for a in self.pending_alerts.values() if a.triggered])
            acknowledged = len([a for a in self.pending_alerts.values() if a.acknowledged])
            
            return {
                'total_pending': total_pending,
                'triggered': triggered,
                'acknowledged': acknowledged,
                'unacknowledged': triggered - acknowledged
            }


class AlertLogger:
    """Log all alerts to a file"""
    
    def __init__(self, log_file: str):
        self.log_file = log_file
        self.lock = Lock()
    
    def log_alert(self, alert: Alert):
        """Log an alert to file"""
        with self.lock:
            try:
                with open(self.log_file, 'a') as f:
                    timestamp = datetime.now().isoformat()
                    f.write(f"{timestamp}|{alert.tracking_id}|{alert.employee_id}|"
                           f"{alert.left_at.isoformat()}|{alert.timeout_minutes}\n")
            except Exception as e:
                logger.error(f"Failed to log alert to file: {e}")
