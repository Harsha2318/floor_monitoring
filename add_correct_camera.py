#!/usr/bin/env python3
"""
Add camera with CORRECT device 0
"""
import requests
import json
import time

# Wait for server to be ready
print("Waiting for server...")
time.sleep(2)

url = "http://localhost:5000/api/cameras/add"
camera_data = {
    "camera_id": "usb_main",
    "name": "Main Camera", 
    "type": "usb",
    "source": "0"  # CRITICAL: Use device 0, not 1!
}

try:
    print(f"Adding camera with source 0...")
    response = requests.post(url, json=camera_data, timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("\n✅ SUCCESS! Camera added with device 0")
        print("Open http://localhost:5000 and go to Live View tab")
    else:
        print(f"\n❌ Failed: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nMake sure server is running with: python run.py")
