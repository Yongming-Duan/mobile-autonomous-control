#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Launcher - Simplified startup script
系统启动器 - 简化版启动脚本
"""

import sys
import os
import subprocess

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def check_adb():
    """Check ADB connection"""
    print("=" * 60)
    print("Step 1: Check ADB Connection")
    print("=" * 60)

    try:
        # Find ADB
        adb_path = r"D:\工作日常\服务器搭建\荣耀手机刷机\工具软件\platform-tools\adb.exe"

        if not os.path.exists(adb_path):
            print(f"ADB not found at: {adb_path}")
            return False

        # Check devices
        result = subprocess.run(
            [adb_path, "devices"],
            capture_output=True,
            text=True,
            timeout=10
        )

        print("\nADB Devices:")
        print(result.stdout)

        if "device" in result.stdout:
            print("\n[OK] ADB device connected")
            return True
        else:
            print("\n[FAIL] No ADB device found")
            print("\nPlease check:")
            print("  1. Phone is connected via USB")
            print("  2. USB debugging is enabled")
            print("  3. Phone is authorized for ADB")
            return False

    except Exception as e:
        print(f"\n[ERROR] {e}")
        return False


def setup_port_forward():
    """Setup ADB port forwarding"""
    print("\n" + "=" * 60)
    print("Step 2: Setup Port Forwarding")
    print("=" * 60)

    try:
        adb_path = r"D:\工作日常\服务器搭建\荣耀手机刷机\工具软件\platform-tools\adb.exe"

        result = subprocess.run(
            [adb_path, "forward", "tcp:9999", "tcp:9999"],
            capture_output=True,
            text=True,
            timeout=10
        )

        print("\n[OK] Port forwarding configured: 9999")
        return True

    except Exception as e:
        print(f"\n[ERROR] {e}")
        return False


def check_sensor_server():
    """Check if sensor server is running"""
    print("\n" + "=" * 60)
    print("Step 3: Check Sensor Server")
    print("=" * 60)

    try:
        import requests

        response = requests.get("http://127.0.0.1:9999/health", timeout=5)

        if response.status_code == 200:
            data = response.json()
            print(f"\n[OK] Sensor server is running")
            print(f"  Service: {data.get('service')}")
            print(f"  Version: {data.get('version')}")
            print(f"  Status: {data.get('status')}")
            return True
        else:
            print(f"\n[FAIL] Server returned status {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("\n[WARN] Cannot connect to sensor server")
        print("\nPlease start the server in Termux:")
        print("  cd /sdcard")
        print("  python enhanced_sensor_server.py")
        return False

    except Exception as e:
        print(f"\n[ERROR] {e}")
        return False


def check_dependencies():
    """Check Python dependencies"""
    print("\n" + "=" * 60)
    print("Step 4: Check Python Dependencies")
    print("=" * 60)

    missing = []

    # Check requests
    try:
        import requests
        print("  [OK] requests")
    except ImportError:
        print("  [MISSING] requests")
        missing.append("requests")

    # Check flask
    try:
        import flask
        print("  [OK] flask")
    except ImportError:
        print("  [MISSING] flask")
        missing.append("flask")

    # Check flask_socketio
    try:
        import flask_socketio
        print("  [OK] flask_socketio")
    except ImportError:
        print("  [MISSING] flask_socketio")
        missing.append("flask_socketio")

    if missing:
        print(f"\n[WARN] Missing packages: {', '.join(missing)}")
        print("\nInstall with:")
        print(f"  pip install {' '.join(missing)}")
        return False

    print("\n[OK] All dependencies installed")
    return True


def show_menu():
    """Show startup menu"""
    print("\n" + "=" * 60)
    print("Step 5: Choose Startup Mode")
    print("=" * 60)
    print("\nOptions:")
    print("  1. Quick Test (test all components)")
    print("  2. Start Web Dashboard (http://localhost:5000)")
    print("  3. Start Data Collector")
    print("  4. Start Simple Server Test")
    print("  5. Exit")
    print()


def main():
    """Main function"""
    print("\n")
    print("*" * 60)
    print("*" + " " * 58 + "*")
    print("*" + "  Mobile Autonomous Control System - Launcher  ".center(58) + "*")
    print("*" + " " * 58 + "*")
    print("*" * 60)
    print()

    # Step 1: Check ADB
    if not check_adb():
        print("\nPlease fix ADB connection first")
        input("\nPress Enter to exit...")
        return 1

    # Step 2: Setup port forwarding
    if not setup_port_forward():
        print("\nFailed to setup port forwarding")
        input("\nPress Enter to exit...")
        return 1

    # Step 3: Check sensor server
    server_ok = check_sensor_server()

    if not server_ok:
        print("\nSensor server is not running!")
        print("\nPlease start it in Termux first:")
        print("  1. Open Termux on your phone")
        print("  2. Run: cd /sdcard")
        print("  3. Run: python enhanced_sensor_server.py")
        print("  4. Keep Termux open")

        cont = input("\nContinue anyway? (y/n): ").lower()
        if cont != 'y':
            return 1

    # Step 4: Check dependencies
    deps_ok = check_dependencies()

    if not deps_ok:
        print("\nInstalling missing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "requests", "flask", "flask-socketio"])

    # Show menu
    while True:
        show_menu()
        choice = input("Select option (1-5): ").strip()

        if choice == '1':
            print("\n" + "=" * 60)
            print("Running Quick Test...")
            print("=" * 60)
            # Run simple sensor test
            try:
                import requests
                response = requests.get("http://127.0.0.1:9999/sensors", timeout=10)
                if response.status_code == 200:
                    sensors = response.json()
                    print(f"\nAvailable sensors: {sensors.get('count', 0)}")
                    for sensor in sensors.get('sensors', [])[:5]:
                        print(f"  - {sensor}")

                    print("\n[OK] Sensor server is working!")
                else:
                    print("\n[FAIL] Sensor server error")
            except Exception as e:
                print(f"\n[ERROR] {e}")

            input("\nPress Enter to continue...")

        elif choice == '2':
            print("\n" + "=" * 60)
            print("Starting Web Dashboard...")
            print("=" * 60)
            print("\nDashboard URL: http://localhost:5000")
            print("Press Ctrl+C to stop")
            print()

            try:
                subprocess.run([
                    sys.executable,
                    "dashboard.py",
                    "--port", "5000"
                ], check=True)
            except KeyboardInterrupt:
                print("\n\nDashboard stopped")

        elif choice == '3':
            print("\n" + "=" * 60)
            print("Starting Data Collector...")
            print("=" * 60)
            print("\nPress Ctrl+C to stop")
            print()

            try:
                subprocess.run([
                    sys.executable,
                    "data_collector.py"
                ], check=True)
            except KeyboardInterrupt:
                print("\n\nData collector stopped")

        elif choice == '4':
            print("\n" + "=" * 60)
            print("Simple Server Test")
            print("=" * 60)

            try:
                import requests

                # Test battery
                print("\n1. Testing battery...")
                response = requests.get("http://127.0.0.1:9999/battery", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    print(f"   Battery: {data.get('battery', {}).get('percentage')}%")
                else:
                    print("   Failed")

                # Test accelerometer
                print("\n2. Testing accelerometer...")
                response = requests.get("http://127.0.0.1:9999/sensor/accelerometer", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    print(f"   Data received")
                else:
                    print("   Failed")

                print("\n[OK] Server test completed")

            except Exception as e:
                print(f"\n[ERROR] {e}")

            input("\nPress Enter to continue...")

        elif choice == '5':
            print("\nGoodbye!")
            break

        else:
            print("\nInvalid option. Please try again.")

    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
