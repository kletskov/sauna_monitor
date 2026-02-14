#!/usr/bin/env python3
"""Quick test script to verify the new UI template."""

import sys
import time
import subprocess
import requests

print("Starting test server...")
proc = subprocess.Popen(
    ["./venv/bin/python", "web_server.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Wait for server to start
time.sleep(8)

try:
    # Test main page
    print("\nTesting main page...")
    response = requests.get("http://localhost:5002/")
    if "background-image" in response.text:
        print("✓ Background image reference found in HTML")
    else:
        print("✗ Background image NOT found in HTML")

    if "cinco_background.png" in response.text:
        print("✓ Background image filename is correct")
    else:
        print("✗ Background image filename NOT found")

    # Test static file
    print("\nTesting static image...")
    img_response = requests.get("http://localhost:5002/static/cinco_background.png")
    if img_response.status_code == 200:
        print(f"✓ Image loaded successfully ({len(img_response.content)} bytes)")
    else:
        print(f"✗ Image failed to load (status: {img_response.status_code})")

    # Test temperature display
    print("\nTesting temperature data...")
    if response.status_code == 200:
        print("✓ Page loads successfully")
        if "temperature" in response.text.lower():
            print("✓ Temperature data present")

finally:
    print("\nStopping test server...")
    proc.terminate()
    proc.wait()

print("\n✓ Test complete!")
