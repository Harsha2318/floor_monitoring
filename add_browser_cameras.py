#!/usr/bin/env python3
"""
Add default browser cameras for Registration and Live Monitoring
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database import Database

def main():
    db = Database()
    
    # Add Live Monitoring camera
    success1 = db.add_camera('browser_live', 'Live Monitoring Camera', 'browser', 'local')
    if success1:
        print("✅ Added: Live Monitoring Camera (browser_live)")
    else:
        print("ℹ️  Live Monitoring Camera already exists")
    
    # Add Registration camera
    success2 = db.add_camera('browser_register', 'Registration Camera', 'browser', 'local')
    if success2:
        print("✅ Added: Registration Camera (browser_register)")
    else:
        print("ℹ️  Registration Camera already exists")
    
    print("\n" + "=" * 60)
    print("✅ Browser cameras configured!")
    print("=" * 60)
    print("\nYou now have TWO browser cameras:")
    print("1. Live Monitoring Camera - for tracking employee presence")
    print("2. Registration Camera - for registering new employees")
    print("\nNext: Restart server (python run.py) and refresh browser")

if __name__ == "__main__":
    main()
