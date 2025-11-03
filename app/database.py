"""
Database models and operations for the Employee Monitoring System
"""
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import logging
from contextlib import contextmanager

from app import config

logger = logging.getLogger(__name__)


class Database:
    """Handle all database operations"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.DATABASE_PATH
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Employees table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    face_encoding BLOB,
                    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    active BOOLEAN DEFAULT 1
                )
            """)
            
            # Presence logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS presence_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id TEXT,
                    tracking_id INTEGER NOT NULL,
                    camera_id TEXT NOT NULL,
                    entry_time TIMESTAMP NOT NULL,
                    exit_time TIMESTAMP,
                    duration_seconds INTEGER,
                    status TEXT DEFAULT 'present',
                    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
                )
            """)
            
            # Absence alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS absence_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id TEXT,
                    tracking_id INTEGER NOT NULL,
                    left_at TIMESTAMP NOT NULL,
                    alert_triggered_at TIMESTAMP NOT NULL,
                    timeout_minutes INTEGER NOT NULL,
                    acknowledged BOOLEAN DEFAULT 0,
                    acknowledged_at TIMESTAMP,
                    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
                )
            """)
            
            # System configuration table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Camera configurations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cameras (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    camera_id TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    source TEXT NOT NULL,
                    active BOOLEAN DEFAULT 1,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_presence_employee 
                ON presence_logs(employee_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_presence_times 
                ON presence_logs(entry_time, exit_time)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_alerts_acknowledged 
                ON absence_alerts(acknowledged)
            """)
            
            logger.info("Database initialized successfully")
    
    # Employee Operations
    def add_employee(self, employee_id: str, name: str, face_encoding: bytes = None) -> bool:
        """Add a new employee"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO employees (employee_id, name, face_encoding)
                    VALUES (?, ?, ?)
                """, (employee_id, name, face_encoding))
                logger.info(f"Added employee: {name} ({employee_id})")
                return True
        except sqlite3.IntegrityError:
            logger.warning(f"Employee {employee_id} already exists")
            return False
    
    def get_employee(self, employee_id: str) -> Optional[Dict]:
        """Get employee details"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM employees WHERE employee_id = ?
            """, (employee_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_employees(self, active_only: bool = True) -> List[Dict]:
        """Get all employees"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM employees"
            if active_only:
                query += " WHERE active = 1"
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]
    
    # Presence Logging Operations
    def log_entry(self, tracking_id: int, camera_id: str, employee_id: str = None) -> int:
        """Log employee entry"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO presence_logs 
                (tracking_id, camera_id, employee_id, entry_time, status)
                VALUES (?, ?, ?, ?, 'present')
            """, (tracking_id, camera_id, employee_id, datetime.now()))
            log_id = cursor.lastrowid
            logger.info(f"Logged entry: tracking_id={tracking_id}, camera={camera_id}")
            return log_id
    
    def log_exit(self, tracking_id: int, camera_id: str) -> bool:
        """Log employee exit"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Find the most recent open entry for this tracking_id
            cursor.execute("""
                SELECT id, entry_time FROM presence_logs
                WHERE tracking_id = ? AND camera_id = ? AND exit_time IS NULL
                ORDER BY entry_time DESC LIMIT 1
            """, (tracking_id, camera_id))
            
            row = cursor.fetchone()
            if row:
                log_id = row['id']
                entry_time = datetime.fromisoformat(row['entry_time'])
                exit_time = datetime.now()
                duration = int((exit_time - entry_time).total_seconds())
                
                cursor.execute("""
                    UPDATE presence_logs
                    SET exit_time = ?, duration_seconds = ?, status = 'left'
                    WHERE id = ?
                """, (exit_time, duration, log_id))
                
                logger.info(f"Logged exit: tracking_id={tracking_id}, duration={duration}s")
                return True
            return False
    
    def get_active_presences(self, camera_id: str = None) -> List[Dict]:
        """Get all currently present employees"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT pl.*, e.name as employee_name
                FROM presence_logs pl
                LEFT JOIN employees e ON pl.employee_id = e.employee_id
                WHERE pl.exit_time IS NULL
            """
            params = []
            if camera_id:
                query += " AND pl.camera_id = ?"
                params.append(camera_id)
            query += " ORDER BY pl.entry_time DESC"
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_presence_history(self, start_date: datetime = None, 
                            end_date: datetime = None,
                            employee_id: str = None) -> List[Dict]:
        """Get presence history with filters"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT pl.*, e.name as employee_name
                FROM presence_logs pl
                LEFT JOIN employees e ON pl.employee_id = e.employee_id
                WHERE 1=1
            """
            params = []
            
            if start_date:
                query += " AND pl.entry_time >= ?"
                params.append(start_date)
            if end_date:
                query += " AND pl.entry_time <= ?"
                params.append(end_date)
            if employee_id:
                query += " AND pl.employee_id = ?"
                params.append(employee_id)
            
            query += " ORDER BY pl.entry_time DESC LIMIT 1000"
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    # Alert Operations
    def create_alert(self, tracking_id: int, employee_id: str, 
                     left_at: datetime, timeout_minutes: int) -> int:
        """Create an absence alert"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO absence_alerts
                (tracking_id, employee_id, left_at, alert_triggered_at, timeout_minutes)
                VALUES (?, ?, ?, ?, ?)
            """, (tracking_id, employee_id, left_at, datetime.now(), timeout_minutes))
            alert_id = cursor.lastrowid
            logger.warning(f"Alert created: tracking_id={tracking_id}, timeout={timeout_minutes}min")
            return alert_id
    
    def get_unacknowledged_alerts(self) -> List[Dict]:
        """Get all unacknowledged alerts"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.*, e.name as employee_name
                FROM absence_alerts a
                LEFT JOIN employees e ON a.employee_id = e.employee_id
                WHERE a.acknowledged = 0
                ORDER BY a.alert_triggered_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def acknowledge_alert(self, alert_id: int) -> bool:
        """Acknowledge an alert"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE absence_alerts
                SET acknowledged = 1, acknowledged_at = ?
                WHERE id = ?
            """, (datetime.now(), alert_id))
            return cursor.rowcount > 0
    
    # Camera Operations
    def add_camera(self, camera_id: str, name: str, camera_type: str, source: str) -> bool:
        """Add a new camera configuration"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO cameras (camera_id, name, type, source)
                    VALUES (?, ?, ?, ?)
                """, (camera_id, name, camera_type, source))
                return True
        except sqlite3.IntegrityError:
            return False
    
    def get_cameras(self, active_only: bool = True) -> List[Dict]:
        """Get all cameras"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM cameras"
            if active_only:
                query += " WHERE active = 1"
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]
    
    # Statistics
    def get_statistics(self, start_date: datetime = None, 
                       end_date: datetime = None) -> Dict:
        """Get system statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Default to today if no dates provided
            if not start_date:
                start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            if not end_date:
                end_date = datetime.now()
            
            stats = {}
            
            # Total entries
            cursor.execute("""
                SELECT COUNT(*) as count FROM presence_logs
                WHERE entry_time BETWEEN ? AND ?
            """, (start_date, end_date))
            stats['total_entries'] = cursor.fetchone()['count']
            
            # Currently present
            cursor.execute("""
                SELECT COUNT(DISTINCT tracking_id) as count FROM presence_logs
                WHERE exit_time IS NULL
            """)
            stats['currently_present'] = cursor.fetchone()['count']
            
            # Total alerts
            cursor.execute("""
                SELECT COUNT(*) as count FROM absence_alerts
                WHERE left_at BETWEEN ? AND ?
            """, (start_date, end_date))
            stats['total_alerts'] = cursor.fetchone()['count']
            
            # Unacknowledged alerts
            cursor.execute("""
                SELECT COUNT(*) as count FROM absence_alerts
                WHERE acknowledged = 0
            """)
            stats['unacknowledged_alerts'] = cursor.fetchone()['count']
            
            # Average presence duration (in minutes)
            cursor.execute("""
                SELECT AVG(duration_seconds) as avg_duration FROM presence_logs
                WHERE entry_time BETWEEN ? AND ? AND duration_seconds IS NOT NULL
            """, (start_date, end_date))
            avg_seconds = cursor.fetchone()['avg_duration']
            stats['avg_presence_minutes'] = round(avg_seconds / 60, 2) if avg_seconds else 0
            
            return stats
