#!/usr/bin/env python3
"""Test the sensor server"""

import urllib.request
import json

def test_endpoint(url):
    """Test a single endpoint"""
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            print(f"✓ {url}")
            print(f"  Response: {json.dumps(data, indent=2)}")
            return True
    except Exception as e:
        print(f"✗ {url}")
        print(f"  Error: {e}")
        return False

print("=" * 50)
print("Testing Sensor HTTP Server")
print("=" * 50)

# Test health
test_endpoint("http://127.0.0.1:9999/health")
print()

# Test sensors list
test_endpoint("http://127.0.0.1:9999/sensors")
print()

# Test accelerometer
test_endpoint("http://127.0.0.1:9999/sensor/accelerometer")
print()

# Test TTS
print("Testing TTS...")
try:
    with urllib.request.urlopen("http://127.0.0.1:9999/tts?text=Hello", timeout=5) as response:
        data = json.loads(response.read().decode())
        print(f"✓ TTS endpoint")
        print(f"  Response: {json.dumps(data, indent=2)}")
except Exception as e:
    print(f"✗ TTS endpoint")
    print(f"  Error: {e}")
print()

# Test battery
test_endpoint("http://127.0.0.1:9999/battery")
print()

print("=" * 50)
print("Test Complete!")
print("=" * 50)
