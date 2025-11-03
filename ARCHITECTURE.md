# System Architecture Diagrams

## High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           CLIENT BROWSER                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │   Live   │  │ Presence │  │  Alerts  │  │ History  │           │
│  │   View   │  │  Status  │  │ Manager  │  │ Viewer   │           │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘           │
│       │             │              │              │                  │
└───────┼─────────────┼──────────────┼──────────────┼──────────────────┘
        │             │              │              │
        │ HTTP        │ WebSocket    │ HTTP         │ HTTP
        │ MJPEG       │ (Real-time)  │ (REST API)   │ (REST API)
        ▼             ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      FLASK WEB SERVER (Python)                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    Main Application (main.py)                   │ │
│  │  • HTTP Routes (GET/POST)                                      │ │
│  │  • WebSocket Handlers (SocketIO)                               │ │
│  │  • Video Streaming (MJPEG)                                     │ │
│  │  • API Endpoints (REST)                                        │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │   Camera     │  │  Detection   │  │   Tracking   │             │
│  │   Manager    │─▶│   Engine     │─▶│   System     │             │
│  │              │  │              │  │              │             │
│  │ • USB Cams   │  │ • MediaPipe  │  │ • Centroid   │             │
│  │ • IP Cams    │  │ • YOLO       │  │ • Multi-ID   │             │
│  │ • Threading  │  │ • OpenCV     │  │ • Persist    │             │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘             │
│         │                  │                  │                      │
│         │                  │                  ▼                      │
│         │                  │         ┌──────────────┐               │
│         │                  │         │    Alert     │               │
│         │                  │         │   Manager    │               │
│         │                  │         │              │               │
│         │                  │         │ • Timeout    │               │
│         │                  │         │ • Notify     │               │
│         │                  │         │ • Sound      │               │
│         │                  │         └──────┬───────┘               │
│         │                  │                │                        │
│         ▼                  ▼                ▼                        │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                  Database Layer (database.py)                   │ │
│  │  • Employee Management                                          │ │
│  │  • Presence Logging                                             │ │
│  │  • Alert Storage                                                │ │
│  │  • Statistics Generation                                        │ │
│  └────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────┬───────────────────────────────────┘
                                    │
                                    ▼
                            ┌───────────────┐
                            │ SQLite Database│
                            │ monitoring.db  │
                            └───────────────┘
                                    ▲
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
            ┌───────┴────────┐              ┌──────┴──────┐
            │  Hardware      │              │   Logs      │
            │  ┌───────────┐ │              │  data/logs/ │
            │  │ USB Camera│ │              └─────────────┘
            │  └───────────┘ │
            │  ┌───────────┐ │
            │  │ IP Camera │ │
            │  └───────────┘ │
            └────────────────┘
```

## Data Flow Diagram

```
1. VIDEO CAPTURE
   ┌─────────┐
   │ Camera  │
   │ Stream  │
   └────┬────┘
        │ Raw frames
        ▼
2. DETECTION
   ┌─────────────┐
   │ Detection   │──────┐
   │ Engine      │      │ Bounding boxes
   └─────────────┘      │ + confidence
                        ▼
3. TRACKING            ┌──────────────┐
   ┌─────────────┐     │ Tracked      │
   │ Tracking    │◀────┤ Persons      │
   │ System      │     └──────────────┘
   └──────┬──────┘
          │ Tracking IDs + status
          │
          ├─────────────────┬─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
   ┌──────────┐      ┌──────────┐     ┌──────────┐
   │  Entry   │      │   Exit   │     │  Alert   │
   │  Event   │      │  Event   │     │  Event   │
   └────┬─────┘      └────┬─────┘     └────┬─────┘
        │                 │                 │
        ▼                 ▼                 ▼
   ┌─────────────────────────────────────────────┐
   │            Database Storage                  │
   │  • presence_logs                             │
   │  • absence_alerts                            │
   │  • statistics                                │
   └──────────────────┬──────────────────────────┘
                      │
                      ▼
   ┌─────────────────────────────────────────────┐
   │            Real-time Updates                 │
   │  • WebSocket to browser                      │
   │  • UI refresh                                │
   │  • Alert notifications                       │
   └─────────────────────────────────────────────┘
```

## Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Camera Manager                            │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │  Camera 1  │  │  Camera 2  │  │  Camera N  │           │
│  │  Thread    │  │  Thread    │  │  Thread    │           │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘           │
└────────┼────────────────┼────────────────┼──────────────────┘
         │ Frame Queue    │ Frame Queue    │ Frame Queue
         ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│                  Processing Thread                           │
│                                                              │
│  for each camera:                                           │
│    frame = get_frame(camera_id)                             │
│    detections = detect(frame)        ◀── Detection Engine   │
│    persons = track(detections)       ◀── Tracking System    │
│                                                              │
│    for person in persons:                                   │
│      if new_person:                                         │
│        log_entry(person)             ◀── Database          │
│                                                              │
│      if person_left:                                        │
│        log_exit(person)              ◀── Database          │
│        create_alert(person)          ◀── Alert Manager     │
│                                                              │
│    emit_update(camera_id, stats)     ◀── WebSocket         │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Alert Monitor Thread                      │
│                                                              │
│  while running:                                             │
│    for alert in pending_alerts:                             │
│      if time_exceeded(alert):                               │
│        trigger_alert(alert)          ◀── Desktop Notif.    │
│        play_sound()                  ◀── Sound Player      │
│        save_to_db(alert)             ◀── Database          │
│        emit_alert(alert)             ◀── WebSocket         │
│    sleep(30 seconds)                                        │
└─────────────────────────────────────────────────────────────┘
```

## Database Schema Diagram

```
┌─────────────────────────┐
│      employees          │
├─────────────────────────┤
│ id (PK)                 │
│ employee_id (UNIQUE)    │◀───┐
│ name                    │    │ Foreign Key
│ face_encoding (BLOB)    │    │
│ registered_at           │    │
│ active                  │    │
└─────────────────────────┘    │
                               │
┌─────────────────────────┐    │
│    presence_logs        │    │
├─────────────────────────┤    │
│ id (PK)                 │    │
│ employee_id (FK)        │────┘
│ tracking_id             │
│ camera_id               │
│ entry_time              │
│ exit_time               │
│ duration_seconds        │
│ status                  │
└─────────────────────────┘
            │
            │ Related to
            │
┌─────────────────────────┐
│    absence_alerts       │
├─────────────────────────┤
│ id (PK)                 │
│ employee_id (FK)        │────┐
│ tracking_id             │    │
│ left_at                 │    │ Foreign Key
│ alert_triggered_at      │    │
│ timeout_minutes         │    │
│ acknowledged            │    │
│ acknowledged_at         │    │
└─────────────────────────┘    │
                               │
┌─────────────────────────┐    │
│       cameras           │    │
├─────────────────────────┤    │
│ id (PK)                 │    │
│ camera_id (UNIQUE)      │    │
│ name                    │    │
│ type                    │    │
│ source                  │    │
│ active                  │    │
│ added_at                │    │
└─────────────────────────┘    │
                               │
┌─────────────────────────┐    │
│    system_config        │    │
├─────────────────────────┤    │
│ key (PK)                │    │
│ value                   │    │
│ updated_at              │    │
└─────────────────────────┘    │
```

## Detection Flow Diagram

```
Input Frame (640x480)
        │
        ▼
┌────────────────┐
│  Preprocessing │
│  • Resize      │
│  • Color Conv. │
└───────┬────────┘
        │
        ▼
┌────────────────┐
│ Detection Model│◀───── Model Selection
│ • MediaPipe    │       (config.py)
│ • YOLO         │
│ • OpenCV HOG   │
└───────┬────────┘
        │
        ▼
┌────────────────┐
│  Filter by     │
│  Confidence    │◀───── DETECTION_CONFIDENCE
│  Threshold     │       (config.py)
└───────┬────────┘
        │
        ▼
┌────────────────┐
│ Detection List │
│ [bbox, conf,   │
│  center, id]   │
└───────┬────────┘
        │
        ▼
To Tracking System
```

## Tracking Flow Diagram

```
Detections (current frame)
        │
        ▼
┌─────────────────────┐
│ Get Existing        │
│ Tracked Objects     │
└──────────┬──────────┘
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
No Objects    Has Objects
    │             │
    │             ▼
    │     ┌──────────────────┐
    │     │ Calculate Distance│
    │     │ Matrix (D)        │
    │     │ Between Centroids │
    │     └────────┬──────────┘
    │              │
    │              ▼
    │     ┌──────────────────┐
    │     │ Hungarian        │
    │     │ Assignment       │
    │     └────────┬─────────┘
    │              │
    │       ┌──────┴──────┐
    │       │             │
    │       ▼             ▼
    │   Matched      Unmatched
    │   Pairs        Objects
    │       │             │
    │       ▼             ▼
    │   ┌────────┐   ┌────────┐
    │   │ Update │   │Increment│
    │   │ Object │   │Disappear│
    │   └────────┘   │Counter  │
    │                └───┬────┘
    │                    │
    │                    ▼
    │            ┌──────────────┐
    │            │ Check Max    │
    │            │ Disappeared  │
    │            └───┬──────────┘
    │                │
    │         ┌──────┴──────┐
    │         │             │
    │         ▼             ▼
    │   Still Active  Deregister
    │                       │
    ▼                       ▼
┌────────────────────────────────┐
│ Register New Objects           │
│ (Unmatched detections)         │
└────────────────┬───────────────┘
                 │
                 ▼
     Updated Tracking Dictionary
```

## Alert System State Diagram

```
        Person Detected
              │
              ▼
        ┌──────────┐
        │ PRESENT  │
        └─────┬────┘
              │
              │ Disappears for
              │ N frames
              ▼
        ┌──────────┐
        │   LEFT   │──────────────┐
        └─────┬────┘              │
              │                   │
              │ Create Alert      │ Returns
              ▼                   │ before timeout
    ┌──────────────────┐          │
    │  PENDING ALERT   │          │
    │  (Waiting for    │          │
    │   timeout)       │◀─────────┘
    └─────┬────────────┘   Cancel Alert
          │
          │ Timeout
          │ Exceeded
          ▼
    ┌──────────────────┐
    │ ALERT TRIGGERED  │
    │  • Notification  │
    │  • Sound         │
    │  • WebSocket     │
    └─────┬────────────┘
          │
          │ User Action
          ▼
    ┌──────────────────┐
    │  ACKNOWLEDGED    │
    └──────────────────┘
```

## WebSocket Communication Flow

```
Browser                    Server
   │                         │
   │──── connect() ─────────▶│
   │                         │
   │◀─── connected event ────│
   │                         │
   │                         │ Processing
   │                         │ Loop
   │                         │
   │◀─── camera_update ──────│
   │     {camera_id,         │
   │      detections,        │
   │      tracked}           │
   │                         │
   │◀─── alert event ────────│
   │     {tracking_id,       │
   │      employee_id,       │
   │      timeout}           │
   │                         │
   │──── acknowledge() ──────▶│
   │                         │
   │◀─── ack response ───────│
   │                         │
```

## File System Structure

```
floor_monitoring/
├── app/                    # Application core
│   ├── __init__.py        # Flask initialization
│   ├── main.py            # Routes & logic
│   ├── config.py          # Configuration
│   ├── database.py        # Database layer
│   ├── camera_manager.py  # Camera handling
│   ├── detection_engine.py# Detection
│   ├── tracking_system.py # Tracking
│   └── alert_manager.py   # Alerts
│
├── templates/             # HTML templates
│   └── index.html        # Main dashboard
│
├── static/               # Static assets
│   ├── css/
│   │   └── style.css    # Styles
│   └── js/
│       └── app.js       # Frontend logic
│
├── tests/                # Test suite
│   ├── __init__.py
│   ├── test_detection.py
│   ├── test_tracking.py
│   ├── test_database.py
│   └── test_alerts.py
│
├── data/                 # Runtime data
│   ├── monitoring.db    # SQLite database
│   ├── logs/           # Application logs
│   └── faces/          # Face images
│
├── models/              # AI models
│   └── (auto-downloaded)
│
└── [config files]       # Various configs
```

This diagram shows the complete architecture, data flows, and interactions of the Employee Monitoring System.
