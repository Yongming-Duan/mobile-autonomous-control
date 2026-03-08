#!/usr/bin/env python3
"""
Simple Auto Start - Simplified automated launcher
"""

import subprocess
import sys
import os
import time

# Paths
ADB_PATH = r"D:\工作日常\服务器搭建\荣耀手机刷机\工具软件\platform-tools\adb.exe"
SCRIPT_PATH = r"D:\工作日常\服务器搭建\荣耀手机刷机\工具脚本"

def run_cmd(cmd, description):
    """Run command and print result"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")

    try:
        if isinstance(cmd, str):
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        else:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.stdout:
            print(result.stdout)

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print("Command timed out")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("  Mobile Autonomous Control System - Auto Start")
    print("="*60)

    # Step 1: Check ADB
    print("\n[Step 1/6] Checking ADB connection...")
    if not run_cmd([ADB_PATH, "devices"], "ADB Devices"):
        print("\n❌ ADB not connected. Please connect your phone.")
        return 1

    print("✅ ADB connected")

    # Step 2: Setup port forwarding
    print("\n[Step 2/6] Setting up port forwarding...")
    run_cmd([ADB_PATH, "forward", "tcp:9999", "tcp:9999"], "Port Forwarding")
    print("✅ Port forwarding configured")

    # Step 3: Check sensor server
    print("\n[Step 3/6] Checking sensor server...")

    try:
        import requests
        response = requests.get("http://127.0.0.1:9999/health", timeout=3)

        if response.status_code == 200:
            print("✅ Sensor server is running")
            server_running = True
        else:
            print("⚠️  Sensor server returned error")
            server_running = False

    except Exception as e:
        print(f"⚠️  Cannot connect to sensor server: {e}")
        print("\n" + "="*60)
        print("  SENSOR SERVER NOT RUNNING")
        print("="*60)
        print("\nPlease start the sensor server on your phone:")
        print("  1. Open Termux")
        print("  2. Run: cd /sdcard")
        print("  3. Run: python enhanced_sensor_server.py")
        print("\nWaiting 30 seconds for server to start...")
        print("(You can start it now while I wait)")

        # Wait for user to start server
        for i in range(30, 0, -1):
            print(f"\rWaiting... {i}s ", end='', flush=True)
            time.sleep(1)

            # Check every 5 seconds
            if i % 5 == 0:
                try:
                    response = requests.get("http://127.0.0.1:9999/health", timeout=2)
                    if response.status_code == 200:
                        print("\n✅ Sensor server detected!")
                        server_running = True
                        break
                except:
                    pass

        print()  # New line after countdown

    # Step 4: Install dependencies
    print("\n[Step 4/6] Checking dependencies...")

    try:
        import requests
        print("  ✓ requests")
    except:
        print("  ✗ requests - installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "requests"], check=False)

    try:
        import flask
        print("  ✓ flask")
    except:
        print("  ✗ flask - installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "flask"], check=False)

    try:
        import flask_socketio
        print("  ✓ flask_socketio")
    except:
        print("  ✗ flask_socketio - installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "flask-socketio"], check=False)

    # Step 5: Test API
    print("\n[Step 5/6] Testing sensor API...")

    try:
        import requests

        # Test health
        response = requests.get("http://127.0.0.1:9999/health", timeout=3)
        if response.status_code == 200:
            print("  ✓ Health check")

        # Test sensors
        response = requests.get("http://127.0.0.1:9999/sensors", timeout=3)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ Found {data.get('count', 0)} sensors")

        # Test battery
        response = requests.get("http://127.0.0.1:9999/battery", timeout=3)
        if response.status_code == 200:
            data = response.json()
            battery = data.get('battery', {})
            print(f"  ✓ Battery: {battery.get('percentage')}%")

    except Exception as e:
        print(f"  ⚠️  API test failed: {e}")

    # Step 6: Start dashboard
    print("\n[Step 6/6] Starting Web Dashboard...")
    print("\n" + "="*60)
    print("  DASHBOARD STARTING")
    print("="*60)
    print(f"\n✓ Dashboard will be available at: http://localhost:5000")
    print("✓ Press Ctrl+C to stop the server")
    print("\nOpening browser...\n")

    # Open in browser
    try:
        import webbrowser
        webbrowser.open("http://localhost:5000")
    except:
        pass

    # Start dashboard
    os.chdir(SCRIPT_PATH)
    dashboard_path = os.path.join(SCRIPT_PATH, "dashboard.py")

    if os.path.exists(dashboard_path):
        try:
            subprocess.run([sys.executable, dashboard_path, "--port", "5000"])
        except KeyboardInterrupt:
            print("\n\n✓ Dashboard stopped")
    else:
        print(f"❌ Dashboard script not found: {dashboard_path}")

    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted")
        sys.exit(1)
