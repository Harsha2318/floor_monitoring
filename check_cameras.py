#!/usr/bin/env python3
"""Check current camera configuration"""

from app.database import Database

db = Database()
cameras = db.get_cameras()

print(f"Total cameras configured: {len(cameras)}")
print()

for cam in cameras:
    print(f"Camera ID: {cam['id']}")
    print(f"  Name: {cam['name']}")
    print(f"  Source: {cam['source']}")
    print(f"  Status: {cam['status']}")
    print()
