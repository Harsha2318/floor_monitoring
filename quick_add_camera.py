#!/usr/bin/env python3
"""Quick script to add working camera"""
import requests
import json

url = "http://localhost:5000/api/cameras/add"
camera_data = {
    "camera_id": "usb_camera_main",
    "name": "Main Camera", 
    "type": "usb",
    "source": "0"
}

try:
    response = requests.post(url, json=camera_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
