#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Start Script - Fully automated system launcher
自动启动脚本 - 全自动系统启动器
"""

import sys
import os
import subprocess
import time
import threading
import requests

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class AutoLauncher:
    """Automated system launcher"""

    def __init__(self):
        self.adb_path = r"D:\工作日常\服务器搭建\荣耀手机刷机\工具软件\platform-tools\adb.exe"
        self.script_path = r"D:\工作日常\服务器搭建\荣耀手机刷机\工具脚本"
        self.api_base = "http://127.0.0.1:9999"
        self.dashboard_url = "http://localhost:5000"
        self.server_running = False
        self.data_collector_process = None
        self.dashboard_process = None

    def log(self, message, level="INFO"):
        """Log message"""
        prefix = {
            "INFO": "[INFO]",
            "OK": "[OK]",
            "WARN": "[WARN]",
            "ERROR": "[ERROR]",
            "SUCCESS": "[SUCCESS]"
        }.get(level, "[INFO]")

        print(f"{prefix} {message}")

    def check_adb(self):
        """Check ADB connection"""
        self.log("Checking ADB connection...")

        try:
            result = subprocess.run(
                [self.adb_path, "devices"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if "device" in result.stdout:
                self.log("ADB device connected", "OK")
                return True
            else:
                self.log("No ADB device found", "ERROR")
                self.log("Please check:", "ERROR")
                self.log("  1. Phone is connected via USB", "ERROR")
                self.log("  2. USB debugging is enabled", "ERROR")
                self.log("  3. Phone is authorized", "ERROR")
                return False

        except Exception as e:
            self.log(f"ADB check failed: {e}", "ERROR")
            return False

    def setup_port_forwarding(self):
        """Setup ADB port forwarding"""
        self.log("Setting up port forwarding...")

        try:
            subprocess.run(
                [self.adb_path, "forward", "tcp:9999", "tcp:9999"],
                capture_output=True,
                timeout=10
            )
            self.log("Port forwarding configured: 9999", "OK")
            return True

        except Exception as e:
            self.log(f"Port forwarding failed: {e}", "ERROR")
            return False

    def check_sensor_server(self):
        """Check if sensor server is running"""
        self.log("Checking sensor server...")

        try:
            response = requests.get(f"{self.api_base}/health", timeout=3)

            if response.status_code == 200:
                data = response.json()
                self.log(f"Sensor server is running (v{data.get('version')})", "OK")
                self.server_running = True
                return True

        except requests.exceptions.Timeout:
            pass

        except requests.exceptions.ConnectionError:
            pass

        self.log("Sensor server is NOT running", "WARN")
        return False

    def wait_for_sensor_server(self, max_wait=60):
        """Wait for sensor server to start"""
        self.log(f"Waiting for sensor server (max {max_wait}s)...")

        for i in range(max_wait):
            if self.check_sensor_server():
                self.log("Sensor server detected!", "SUCCESS")
                return True

            # Progress indicator
            if i % 5 == 0:
                self.log(f"Still waiting... ({i}/{max_wait}s)")

            time.sleep(1)

        self.log("Sensor server not detected after timeout", "ERROR")
        return False

    def check_dependencies(self):
        """Check and install Python dependencies"""
        self.log("Checking Python dependencies...")

        required = {
            'requests': 'requests',
            'flask': 'flask',
            'flask_socketio': 'flask-socketio'
        }

        missing = []

        for module, package in required.items():
            try:
                __import__(module)
                self.log(f"  ✓ {package}", "OK")
            except ImportError:
                self.log(f"  ✗ {package} - missing", "WARN")
                missing.append(package)

        if missing:
            self.log(f"Installing missing packages: {', '.join(missing)}", "WARN")

            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install"] + missing,
                    check=True,
                    timeout=120
                )
                self.log("Dependencies installed", "SUCCESS")
            except Exception as e:
                self.log(f"Failed to install dependencies: {e}", "ERROR")
                return False

        return True

    def test_sensor_api(self):
        """Test sensor API endpoints"""
        self.log("Testing sensor API...")

        tests = [
            ("Health", f"{self.api_base}/health"),
            ("Sensors", f"{self.api_base}/sensors"),
            ("Battery", f"{self.api_base}/battery")
        ]

        passed = 0

        for name, url in tests:
            try:
                response = requests.get(url, timeout=5)

                if response.status_code == 200:
                    self.log(f"  ✓ {name}", "OK")
                    passed += 1
                else:
                    self.log(f"  ✗ {name} (status {response.status_code})", "WARN")

            except Exception as e:
                self.log(f"  ✗ {name}: {e}", "WARN")

        if passed == len(tests):
            self.log("All API tests passed!", "SUCCESS")
            return True
        else:
            self.log(f"{passed}/{len(tests)} tests passed", "WARN")
            return False

    def start_data_collector(self):
        """Start data collector in background"""
        self.log("Starting data collector...")

        try:
            # Create a simple collector script
            collector_script = os.path.join(self.script_path, "auto_collector.py")

            with open(collector_script, 'w', encoding='utf-8') as f:
                f.write("""
import sys
import time
sys.path.insert(0, r'""" + self.script_path + """')

from phone_controller import PhoneController
from data_collector import SensorDataCollector

controller = PhoneController()
collector = SensorDataCollector(
    controller=controller,
    collection_interval=10,
    db_path="sensor_data.db"
)

def on_data(sensor, values):
    print(f"[COLLECTOR] {sensor}: {values}")

collector.add_callback(on_data)

print("[COLLECTOR] Starting data collection...")
print("[COLLECTOR] Press Ctrl+C to stop")

collector.start(['accelerometer', 'light', 'battery'])

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\\n[COLLECTOR] Stopping...")
    collector.stop()
    print("[COLLECTOR] Stopped")
""")

            # Start in background
            if sys.platform == 'win32':
                # Windows: use START command
                self.data_collector_process = subprocess.Popen(
                    ["START", "/B", "python", collector_script],
                    shell=True,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:
                # Linux/Mac
                self.data_collector_process = subprocess.Popen(
                    [sys.executable, collector_script],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

            self.log("Data collector started in background", "SUCCESS")
            time.sleep(2)  # Let it initialize
            return True

        except Exception as e:
            self.log(f"Failed to start data collector: {e}", "ERROR")
            return False

    def start_dashboard(self):
        """Start web dashboard"""
        self.log("Starting web dashboard...")

        try:
            dashboard_script = os.path.join(self.script_path, "dashboard.py")

            if not os.path.exists(dashboard_script):
                self.log("Dashboard script not found!", "ERROR")
                return False

            # Start dashboard
            self.dashboard_process = subprocess.Popen(
                [sys.executable, dashboard_script, "--port", "5000"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.script_path
            )

            # Wait a bit for startup
            time.sleep(3)

            # Check if it's running
            try:
                response = requests.get(self.dashboard_url, timeout=2)
                if response.status_code == 200:
                    self.log(f"Dashboard is running at {self.dashboard_url}", "SUCCESS")
                    self.log("Opening dashboard in browser...", "INFO")
                    self.open_browser()
                    return True
            except:
                pass

            self.log("Dashboard started (may still be initializing)", "OK")
            self.log(f"Access at: {self.dashboard_url}", "INFO")
            return True

        except Exception as e:
            self.log(f"Failed to start dashboard: {e}", "ERROR")
            return False

    def open_browser(self):
        """Open dashboard in browser"""
        try:
            import webbrowser
            webbrowser.open(self.dashboard_url)
        except:
            pass

    def show_status(self):
        """Show system status"""
        print("\n" + "=" * 70)
        print("SYSTEM STATUS")
        print("=" * 70)

        # ADB
        adb_ok = self.check_adb() is not False

        # Port forwarding
        pf_ok = self.setup_port_forwarding() is not False

        # Sensor server
        server_ok = self.check_sensor_server()

        # Dashboard
        dashboard_running = False
        try:
            response = requests.get(self.dashboard_url, timeout=2)
            dashboard_running = response.status_code == 200
        except:
            pass

        print(f"\n{'Component':<20} {'Status':<15}")
        print("-" * 35)
        print(f"{'ADB Connection':<20} {'OK' if adb_ok else 'FAIL':<15}")
        print(f"{'Port Forwarding':<20} {'OK' if pf_ok else 'FAIL':<15}")
        print(f"{'Sensor Server':<20} {'RUNNING' if server_ok else 'STOPPED':<15}")
        print(f"{'Web Dashboard':<20} {'RUNNING' if dashboard_running else 'STOPPED':<15}")
        print(f"{'Data Collector':<20} {'RUNNING' if self.data_collector_process else 'STOPPED':<15}")

        print("\n" + "=" * 70)

        if server_ok and dashboard_running:
            self.log("System is fully operational!", "SUCCESS")
            self.log(f"Dashboard: {self.dashboard_url}", "INFO")
            return True
        else:
            self.log("System is not fully operational", "WARN")
            return False

    def auto_start(self):
        """Automatically start all components"""
        self.log("=" * 70, "INFO")
        self.log("Mobile Autonomous Control System - Auto Start", "INFO")
        self.log("=" * 70, "INFO")

        # Step 1: Check ADB
        print()
        if not self.check_adb():
            self.log("Please fix ADB connection first", "ERROR")
            return False

        # Step 2: Setup port forwarding
        print()
        if not self.setup_port_forwarding():
            return False

        # Step 3: Check sensor server
        print()
        if not self.check_sensor_server():
            self.log("", "INFO")
            self.log("=" * 70, "WARN")
            self.log("SENSOR SERVER NOT RUNNING - ACTION REQUIRED", "WARN")
            self.log("=" * 70, "WARN")
            self.log("", "WARN")
            self.log("Please start the sensor server on your phone:", "WARN")
            self.log("", "WARN")
            self.log("  1. Open Termux on your phone", "INFO")
            self.log("  2. Run: cd /sdcard", "INFO")
            self.log("  3. Run: python enhanced_sensor_server.py", "INFO")
            self.log("  4. Keep Termux open", "INFO")
            self.log("", "WARN")
            self.log("Waiting for sensor server to start...", "INFO")
            self.log("(I'll check every 3 seconds)", "INFO")
            self.log("", "WARN")

            # Wait for server
            if not self.wait_for_sensor_server(max_wait=120):
                self.log("Server not detected. Continuing anyway...", "WARN")

        # Step 4: Check dependencies
        print()
        if not self.check_dependencies():
            return False

        # Step 5: Test API (if server is running)
        if self.server_running:
            print()
            self.test_sensor_api()

        # Step 6: Start components
        print()
        self.log("=" * 70, "INFO")
        self.log("Starting System Components", "INFO")
        self.log("=" * 70, "INFO")

        # Data collector
        print()
        self.start_data_collector()

        # Dashboard
        print()
        self.start_dashboard()

        # Show final status
        print()
        self.show_status()

        # Keep running
        self.log("", "INFO")
        self.log("System is running!", "SUCCESS")
        self.log("", "INFO")
        self.log("Commands:", "INFO")
        self.log("  - Press Ctrl+C to stop", "INFO")
        self.log("  - Dashboard: http://localhost:5000", "INFO")
        self.log("  - API: http://127.0.0.1:9999", "INFO")
        self.log("", "INFO")

        try:
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            print()
            self.log("Shutting down...", "INFO")

            if self.dashboard_process:
                self.dashboard_process.terminate()
                self.log("Dashboard stopped", "OK")

            if self.data_collector_process:
                self.data_collector_process.terminate()
                self.log("Data collector stopped", "OK")

            self.log("Shutdown complete", "SUCCESS")

        return True


def main():
    """Main entry point"""
    launcher = AutoLauncher()

    try:
        return launcher.auto_start()

    except KeyboardInterrupt:
        print()
        launcher.log("Interrupted by user", "WARN")
        return 1

    except Exception as e:
        print()
        launcher.log(f"Unexpected error: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
