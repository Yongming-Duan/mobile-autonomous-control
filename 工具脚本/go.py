#!/usr/bin/env python3
"""
Auto Start - Windows compatible version
"""

import subprocess
import sys
import os
import time

# Paths
ADB_PATH = r"D:\工作日常\服务器搭建\荣耀手机刷机\工具软件\platform-tools\adb.exe"
SCRIPT_PATH = r"D:\工作日常\服务器搭建\荣耀手机刷机\工具脚本"

def main():
    print("\n" + "="*70)
    print("  Mobile Autonomous Control System - Auto Start")
    print("="*70)

    # Step 1: Check ADB
    print("\n[Step 1/6] Checking ADB connection...")

    try:
        result = subprocess.run(
            [ADB_PATH, "devices"],
            capture_output=True,
            text=True,
            timeout=10
        )

        print(result.stdout)

        if "device" not in result.stdout:
            print("\n[ERROR] ADB device not connected")
            print("\nPlease check:")
            print("  1. Phone is connected via USB")
            print("  2. USB debugging is enabled")
            print("  3. Phone is authorized")
            input("\nPress Enter to exit...")
            return 1

        print("[OK] ADB connected")

    except Exception as e:
        print(f"[ERROR] {e}")
        input("\nPress Enter to exit...")
        return 1

    # Step 2: Setup port forwarding
    print("\n[Step 2/6] Setting up port forwarding...")

    try:
        subprocess.run(
            [ADB_PATH, "forward", "tcp:9999", "tcp:9999"],
            capture_output=True,
            timeout=10
        )
        print("[OK] Port forwarding configured (9999)")

    except Exception as e:
        print(f"[ERROR] {e}")
        return 1

    # Step 3: Check sensor server
    print("\n[Step 3/6] Checking sensor server...")

    server_running = False

    try:
        import requests
        response = requests.get("http://127.0.0.1:9999/health", timeout=3)

        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Sensor server is running (v{data.get('version')})")
            server_running = True

    except requests.exceptions.Timeout:
        pass
    except requests.exceptions.ConnectionError:
        pass
    except Exception as e:
        print(f"[WARN] {e}")

    if not server_running:
        print("\n" + "="*70)
        print("  SENSOR SERVER NOT RUNNING")
        print("="*70)
        print("\nPlease start the sensor server on your phone:")
        print("  1. Open Termux on your phone")
        print("  2. Run: cd /sdcard")
        print("  3. Run: python enhanced_sensor_server.py")
        print("  4. Keep Termux open")
        print("\n" + "="*70)
        print("\nI will wait for the server to start...")
        print("Checking every 5 seconds for up to 2 minutes")
        print("\nYou can start the server NOW while I wait")

        # Wait loop
        for i in range(24, 0, -1):
            print(f"\rChecking... {i*5} seconds remaining", end='', flush=True)
            time.sleep(5)

            try:
                import requests
                response = requests.get("http://127.0.0.1:9999/health", timeout=2)

                if response.status_code == 200:
                    print("\n\n[OK] Sensor server detected!")
                    server_running = True
                    break

            except:
                pass

        print()  # New line

        if not server_running:
            print("\n[WARN] Server still not detected. Continuing anyway...")

    # Step 4: Check dependencies
    print("\n[Step 4/6] Checking dependencies...")

    missing = []

    try:
        import requests
        print("  [OK] requests")
    except ImportError:
        print("  [MISSING] requests")
        missing.append("requests")

    try:
        import flask
        print("  [OK] flask")
    except ImportError:
        print("  [MISSING] flask")
        missing.append("flask")

    try:
        import flask_socketio
        print("  [OK] flask_socketio")
    except ImportError:
        print("  [MISSING] flask_socketio")
        missing.append("flask_socketio")

    if missing:
        print(f"\n[INFO] Installing missing packages: {', '.join(missing)}")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install"] + missing,
                check=True,
                timeout=120
            )
            print("[OK] Dependencies installed")
        except Exception as e:
            print(f"[ERROR] Failed to install: {e}")
            return 1

    # Step 5: Test API
    print("\n[Step 5/6] Testing sensor API...")

    if server_running:
        try:
            import requests

            # Health check
            response = requests.get("http://127.0.0.1:9999/health", timeout=3)
            if response.status_code == 200:
                print("  [OK] Health check")

            # List sensors
            response = requests.get("http://127.0.0.1:9999/sensors", timeout=3)
            if response.status_code == 200:
                data = response.json()
                print(f"  [OK] Found {data.get('count', 0)} sensors")
                for sensor in data.get('sensors', [])[:5]:
                    print(f"         - {sensor}")

            # Battery
            response = requests.get("http://127.0.0.1:9999/battery", timeout=3)
            if response.status_code == 200:
                data = response.json()
                battery = data.get('battery', {})
                print(f"  [OK] Battery: {battery.get('percentage')}% ({battery.get('status')})")

        except Exception as e:
            print(f"  [WARN] API test failed: {e}")
    else:
        print("  [SKIP] Skipping API tests (server not running)")

    # Step 6: Start dashboard
    print("\n[Step 6/6] Starting Web Dashboard...")
    print("\n" + "="*70)
    print("  WEB DASHBOARD")
    print("="*70)

    os.chdir(SCRIPT_PATH)
    dashboard_path = os.path.join(SCRIPT_PATH, "dashboard.py")

    if not os.path.exists(dashboard_path):
        print(f"[ERROR] Dashboard not found: {dashboard_path}")
        return 1

    print(f"\n[INFO] Dashboard URL: http://localhost:5000")
    print("[INFO] Press Ctrl+C to stop the server")

    # Open browser
    try:
        import webbrowser
        print("[INFO] Opening in browser...")
        webbrowser.open("http://localhost:5000")
    except Exception as e:
        print(f"[WARN] Could not open browser: {e}")

    print("\n" + "="*70)
    print("  DASHBOARD STARTING")
    print("="*70)
    print()

    try:
        subprocess.run([sys.executable, dashboard_path, "--port", "5000"])
    except KeyboardInterrupt:
        print("\n\n[OK] Dashboard stopped")
        return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
