#!/usr/bin/env python3
"""Add a single camera with proper configuration"""

from app.database import Database

db = Database()

# Add camera with device 0
success = db.add_camera(
    camera_id="webcam_1",
    name="Webcam",
    camera_type="usb",
    source="0"
)

if success:
    print(f"✅ Camera added successfully!")
    print(f"   Camera ID: webcam_1")
    print(f"   Name: Webcam")
    print(f"   Source: 0")
else:
    print("❌ Failed to add camera")
print()
print("Now restart the server (Ctrl+C in the server terminal, then 'python run.py')")
