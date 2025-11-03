#!/usr/bin/env python3
"""
Camera Diagnostic Tool
Tests which camera devices are available and accessible on your system.
"""

import cv2
import sys

def test_camera(device_id):
    """Test if a camera device is accessible."""
    print(f"\nTesting camera device {device_id}...")
    
    try:
        cap = cv2.VideoCapture(device_id, cv2.CAP_DSHOW)  # DirectShow backend for Windows
        
        if not cap.isOpened():
            print(f"  ❌ Cannot open device {device_id}")
            return False
        
        # Try to read a frame
        ret, frame = cap.read()
        
        if not ret or frame is None:
            print(f"  ❌ Device {device_id} opened but cannot read frames")
            cap.release()
            return False
        
        # Get camera properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        print(f"  ✅ Device {device_id} is working!")
        print(f"     Resolution: {width}x{height}")
        print(f"     FPS: {fps}")
        print(f"     Frame shape: {frame.shape}")
        
        cap.release()
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing device {device_id}: {e}")
        return False

def main():
    print("=" * 60)
    print("Camera Diagnostic Tool")
    print("=" * 60)
    print("\nThis will test camera devices 0-4 to find working cameras.")
    print("Please close any other applications using your camera")
    print("(Teams, Zoom, Skype, Camera app, etc.)\n")
    
    input("Press Enter to start scanning...")
    
    working_cameras = []
    
    # Test devices 0-4
    for device_id in range(5):
        if test_camera(device_id):
            working_cameras.append(device_id)
    
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    if working_cameras:
        print(f"\n✅ Found {len(working_cameras)} working camera(s): {working_cameras}")
        print("\nRecommended configuration:")
        print(f"  - Use device ID: {working_cameras[0]}")
        print(f"  - Camera Source: {working_cameras[0]}")
        
        if len(working_cameras) > 1:
            print(f"\nAdditional cameras available: {working_cameras[1:]}")
    else:
        print("\n❌ No working cameras found!")
        print("\nTroubleshooting steps:")
        print("1. Check if camera is connected via USB")
        print("2. Close all apps using camera (Teams, Zoom, Camera app)")
        print("3. Check Windows Privacy settings:")
        print("   Settings → Privacy → Camera → Allow apps to access camera")
        print("4. Try restarting your computer")
        print("5. Update camera drivers in Device Manager")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
