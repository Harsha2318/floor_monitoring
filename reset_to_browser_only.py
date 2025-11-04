#!/usr/bin/env python3
"""
Reset system to browser-only cameras
Removes all USB/IP cameras and ensures clean state
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database import Database
from app.camera_manager import CameraManager

def main():
    print("=" * 60)
    print("BROWSER-ONLY CAMERA RESET")
    print("=" * 60)
    
    db = Database()
    
    # Get all cameras
    cameras = db.get_cameras(active_only=False)
    print(f"\nFound {len(cameras)} camera(s) in database:")
    for cam in cameras:
        print(f"  - {cam['name']} (ID: {cam['camera_id']}, Type: {cam['type']})")
    
    # Remove all non-browser cameras
    removed = 0
    for cam in cameras:
        if cam['type'] != 'browser':
            print(f"\n❌ Removing {cam['type']} camera: {cam['name']} ({cam['camera_id']})")
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM cameras WHERE camera_id = ?", (cam['camera_id'],))
            removed += 1
    
    if removed > 0:
        print(f"\n✅ Removed {removed} non-browser camera(s)")
    else:
        print("\n✅ No non-browser cameras found")
    
    # Check for browser cameras
    cameras = db.get_cameras(active_only=False)
    browser_cams = [c for c in cameras if c['type'] == 'browser']
    
    if len(browser_cams) == 0:
        print("\n📝 No browser cameras exist. Add one in Configuration tab:")
        print("   - Camera ID: browser_live")
        print("   - Camera Name: Live Camera")
        print("   - Type: Browser (This device)")
        print("   - Source: local")
    else:
        print(f"\n✅ {len(browser_cams)} browser camera(s) configured:")
        for cam in browser_cams:
            print(f"   - {cam['name']} ({cam['camera_id']})")
    
    print("\n" + "=" * 60)
    print("✅ System is now browser-only!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Restart the Flask server (python run.py)")
    print("2. Refresh your browser")
    print("3. Go to Live View and click 'Start Camera'")
    print("4. Allow browser camera permission")
    print("\n❌ Python will NEVER access your camera!")
    print("✅ Only your browser will use the webcam!")

if __name__ == "__main__":
    main()
