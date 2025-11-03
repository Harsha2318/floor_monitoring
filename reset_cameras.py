#!/usr/bin/env python3
"""
Camera Reset Tool
Removes all cameras from the database to start fresh.
"""

import sqlite3
import os

def reset_cameras():
    """Remove all cameras from the database."""
    db_path = os.path.join('data', 'monitoring.db')
    
    if not os.path.exists(db_path):
        print("❌ Database not found at:", db_path)
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Count existing cameras
        cursor.execute("SELECT COUNT(*) FROM cameras")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("ℹ️  No cameras found in database")
        else:
            print(f"Found {count} camera(s) in database")
            
            # Show cameras
            cursor.execute("SELECT camera_id, name, type, source FROM cameras")
            cameras = cursor.fetchall()
            print("\nCurrent cameras:")
            for cam in cameras:
                print(f"  - {cam[1]} (ID: {cam[0]}, Type: {cam[2]}, Source: {cam[3]})")
            
            # Delete all cameras
            cursor.execute("DELETE FROM cameras")
            conn.commit()
            print(f"\n✅ Removed all {count} camera(s) from database")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error resetting cameras: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Camera Reset Tool")
    print("=" * 60)
    print("\nThis will remove ALL cameras from the database.")
    print("The monitoring system must be stopped first.\n")
    
    response = input("Continue? (yes/no): ").strip().lower()
    
    if response == 'yes':
        reset_cameras()
    else:
        print("Cancelled")
