#!/usr/bin/env python3
"""
Phone Hardware Controller
Complete Python wrapper for Android hardware control via Termux API
Version: 1.0
"""

import subprocess
import requests
import json
import time
import base64
import os
from datetime import datetime
from typing import Optional, Dict, List, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PhoneController:
    """
    Complete controller for Android phone hardware via Termux API
    Combines direct ADB control with HTTP API calls
    """

    def __init__(
        self,
        adb_path: str = "adb",
        api_base: str = "http://127.0.0.1:9999",
        device_id: Optional[str] = None
    ):
        """
        Initialize phone controller

        Args:
            adb_path: Path to ADB executable
            api_base: Base URL for Termux sensor HTTP server
            device_id: Specific device ID (if multiple devices connected)
        """
        self.adb_path = adb_path
        self.api_base = api_base
        self.device_id = device_id
        self._setup_adb_forward()

    def _setup_adb_forward(self):
        """Setup ADB port forwarding"""
        try:
            self._adb_command(["forward", "tcp:9999", "tcp:9999"])
            logger.info("ADB port forwarding configured")
        except Exception as e:
            logger.warning(f"Failed to setup port forwarding: {e}")

    def _adb_command(self, args: List[str], timeout: int = 30) -> subprocess.CompletedProcess:
        """
        Execute ADB command

        Args:
            args: Command arguments (without 'adb' prefix)
            timeout: Command timeout in seconds

        Returns:
            subprocess.CompletedProcess
        """
        cmd = [self.adb_path]
        if self.device_id:
            cmd.extend(["-s", self.device_id])
        cmd.extend(args)

        logger.debug(f"ADB command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

        if result.returncode != 0:
            logger.error(f"ADB command failed: {result.stderr}")

        return result

    def _api_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        timeout: int = 10
    ) -> Dict[str, Any]:
        """
        Make HTTP API request to sensor server

        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint
            params: Query parameters
            data: POST data
            timeout: Request timeout

        Returns:
            JSON response as dictionary
        """
        url = f"{self.api_base}{endpoint}"

        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, timeout=timeout)
            elif method.upper() == "POST":
                response = requests.post(url, params=params, json=data, timeout=timeout)
            elif method.upper() == "DELETE":
                response = requests.delete(url, params=params, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {"status": "error", "message": str(e)}

    # ==================== SYSTEM CONTROL ====================

    def health_check(self) -> Dict[str, Any]:
        """
        Check if sensor server is healthy

        Returns:
            Server health status
        """
        return self._api_request("GET", "/health")

    def server_info(self) -> Dict[str, Any]:
        """
        Get server information

        Returns:
            Server info including available sensors
        """
        return self._api_request("GET", "/info")

    def list_sensors(self) -> Dict[str, Any]:
        """
        List all available sensors

        Returns:
            List of available sensors
        """
        return self._api_request("GET", "/sensors")

    # ==================== SENSORS ====================

    def get_sensor_data(self, sensor_type: str, limit: int = 1) -> Dict[str, Any]:
        """
        Get sensor reading

        Args:
            sensor_type: Type of sensor (accelerometer, gyroscope, light, etc.)
            limit: Number of readings to take

        Returns:
            Sensor data
        """
        return self._api_request("GET", f"/sensor/{sensor_type}", params={"limit": limit})

    def get_accelerometer(self, limit: int = 1) -> Optional[List[float]]:
        """Get accelerometer data [x, y, z]"""
        result = self.get_sensor_data("accelerometer", limit)
        if result.get("status") == "success" and result.get("data"):
            return result["data"][0]["values"]
        return None

    def get_gyroscope(self, limit: int = 1) -> Optional[List[float]]:
        """Get gyroscope data [x, y, z]"""
        result = self.get_sensor_data("gyroscope", limit)
        if result.get("status") == "success" and result.get("data"):
            return result["data"][0]["values"]
        return None

    def get_light(self) -> Optional[float]:
        """Get light level in lux"""
        result = self.get_sensor_data("light", 1)
        if result.get("status") == "success" and result.get("data"):
            return result["data"][0]["values"][0]
        return None

    def get_pressure(self) -> Optional[float]:
        """Get pressure in hPa"""
        result = self.get_sensor_data("pressure", 1)
        if result.get("status") == "success" and result.get("data"):
            return result["data"][0]["values"][0]
        return None

    def get_proximity(self) -> Optional[float]:
        """Get proximity distance"""
        result = self.get_sensor_data("proximity", 1)
        if result.get("status") == "success" and result.get("data"):
            return result["data"][0]["values"][0]
        return None

    def get_magnetic_field(self, limit: int = 1) -> Optional[List[float]]:
        """Get magnetic field [x, y, z]"""
        result = self.get_sensor_data("magnetic", limit)
        if result.get("status") == "success" and result.get("data"):
            return result["data"][0]["values"]
        return None

    # ==================== CAMERA ====================

    def camera_info(self) -> Dict[str, Any]:
        """
        Get camera information

        Returns:
            Camera details
        """
        return self._api_request("GET", "/camera/info")

    def take_photo(self, camera_id: str = "0") -> Dict[str, Any]:
        """
        Take a photo

        Args:
            camera_id: Camera ID (default "0" for back camera)

        Returns:
            Photo info with filename and URL
        """
        return self._api_request("POST", "/camera/photo", params={"camera": camera_id})

    def take_photo_adb(self) -> bool:
        """
        Take photo using ADB (opens camera app)

        Returns:
            True if successful
        """
        try:
            # Start camera
            self._adb_command([
                "shell", "am", "start", "-a",
                "android.media.action.IMAGE_CAPTURE"
            ])
            time.sleep(2)

            # Press enter to focus/shoot
            self._adb_command(["shell", "input", "keyevent", "66"])
            time.sleep(1)

            # Press back to exit
            self._adb_command(["shell", "input", "keyevent", "4"])

            return True
        except Exception as e:
            logger.error(f"Failed to take photo via ADB: {e}")
            return False

    def list_photos(self) -> List[Dict]:
        """
        List all photos

        Returns:
            List of photo info
        """
        result = self._api_request("GET", "/camera/list")
        if result.get("status") == "success":
            return result.get("files", [])
        return []

    def download_photo(self, filename: str, save_path: str) -> bool:
        """
        Download photo from device

        Args:
            filename: Photo filename
            save_path: Local save path

        Returns:
            True if successful
        """
        try:
            url = f"{self.api_base}/camera/photo/{filename}"
            response = requests.get(url, timeout=30)

            with open(save_path, 'wb') as f:
                f.write(response.content)

            logger.info(f"Photo saved to {save_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to download photo: {e}")
            return False

    # ==================== AUDIO ====================

    def record_audio(self, duration: int = 5, limit: bool = True) -> Dict[str, Any]:
        """
        Record audio

        Args:
            duration: Recording duration in seconds
            limit: Whether to limit to duration

        Returns:
            Recording info
        """
        return self._api_request(
            "POST",
            "/audio/record",
            params={"duration": duration, "limit": str(limit).lower()}
        )

    def stop_recording(self) -> Dict[str, Any]:
        """Stop audio recording"""
        return self._api_request("POST", "/audio/record/stop")

    def list_recordings(self) -> List[Dict]:
        """List all audio recordings"""
        result = self._api_request("GET", "/audio/list")
        if result.get("status") == "success":
            return result.get("files", [])
        return []

    def download_recording(self, filename: str, save_path: str) -> bool:
        """Download audio recording"""
        try:
            url = f"{self.api_base}/audio/{filename}"
            response = requests.get(url, timeout=60)

            with open(save_path, 'wb') as f:
                f.write(response.content)

            logger.info(f"Recording saved to {save_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to download recording: {e}")
            return False

    # ==================== LOCATION ====================

    def get_location(self, use_last: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get GPS location

        Args:
            use_last: Use last known location (faster)

        Returns:
            Location data with latitude, longitude, accuracy
        """
        result = self._api_request("GET", "/location", params={"last": str(use_last).lower()})

        if result.get("status") == "success":
            return result.get("location")

        return None

    def update_location(self) -> Optional[Dict[str, Any]]:
        """
        Request fresh location update

        Returns:
            Updated location data
        """
        result = self._api_request("POST", "/location/update")
        if result.get("status") == "success":
            return result.get("location")
        return None

    # ==================== BATTERY ====================

    def get_battery(self) -> Optional[Dict[str, Any]]:
        """
        Get battery status

        Returns:
            Battery info including percentage, status, temperature
        """
        result = self._api_request("GET", "/battery")

        if result.get("status") == "success":
            return result.get("battery")

        return None

    def get_battery_percentage(self) -> Optional[int]:
        """Get battery percentage"""
        battery = self.get_battery()
        if battery:
            return battery.get("percentage")
        return None

    def is_charging(self) -> Optional[bool]:
        """Check if device is charging"""
        battery = self.get_battery()
        if battery:
            status = battery.get("status", "").lower()
            return "charging" in status
        return None

    # ==================== TEXT TO SPEECH ====================

    def speak(self, text: str, rate: float = 1.0, pitch: float = 1.0) -> bool:
        """
        Convert text to speech

        Args:
            text: Text to speak
            rate: Speech rate (0.1 - 10.0, default 1.0)
            pitch: Speech pitch (0.1 - 2.0, default 1.0)

        Returns:
            True if successful
        """
        result = self._api_request(
            "GET",
            "/tts",
            params={"text": text, "rate": str(rate), "pitch": str(pitch)}
        )
        return result.get("status") == "success"

    def list_tts_engines(self) -> List[str]:
        """List available TTS engines"""
        result = self._api_request("GET", "/tts/engines")
        if result.get("status") == "success":
            return result.get("engines", [])
        return []

    # ==================== SMS ====================

    def list_sms(self, limit: int = 10, offset: int = 0) -> List[Dict]:
        """
        List SMS messages

        Args:
            limit: Number of messages
            offset: Offset for pagination

        Returns:
            List of SMS messages
        """
        result = self._api_request(
            "GET",
            "/sms/list",
            params={"limit": limit, "offset": offset}
        )

        if result.get("status") == "success":
            return result.get("messages", [])

        return []

    def send_sms(self, number: str, text: str) -> bool:
        """
        Send SMS message

        Args:
            number: Phone number
            text: Message text

        Returns:
            True if successful
        """
        result = self._api_request(
            "POST",
            "/sms/send",
            params={"number": number, "text": text}
        )
        return result.get("status") == "success"

    # ==================== NOTIFICATIONS ====================

    def list_notifications(self) -> List[Dict]:
        """List active notifications"""
        result = self._api_request("GET", "/notification/list")
        if result.get("status") == "success":
            return result.get("notifications", [])
        return []

    def send_notification(
        self,
        title: str,
        content: str,
        notification_id: str = "1"
    ) -> bool:
        """
        Send notification

        Args:
            title: Notification title
            content: Notification content
            notification_id: Notification ID

        Returns:
            True if successful
        """
        result = self._api_request(
            "POST",
            "/notification/send",
            params={"title": title, "content": content, "id": notification_id}
        )
        return result.get("status") == "success"

    # ==================== CLIPBOARD ====================

    def get_clipboard(self) -> Optional[str]:
        """
        Get clipboard content

        Returns:
            Clipboard text
        """
        result = self._api_request("GET", "/clipboard")
        if result.get("status") == "success":
            return result.get("content")
        return None

    def set_clipboard(self, text: str) -> bool:
        """
        Set clipboard content

        Args:
            text: Text to set

        Returns:
            True if successful
        """
        result = self._api_request("POST", "/clipboard", params={"text": text})
        return result.get("status") == "success"

    # ==================== SYSTEM INFO ====================

    def get_system_info(self) -> Optional[Dict]:
        """Get system information"""
        result = self._api_request("GET", "/system/info")
        if result.get("status") == "success":
            return result.get("system")
        return None

    def get_wifi_info(self) -> Optional[Dict]:
        """Get WiFi connection info"""
        result = self._api_request("GET", "/system/wifi")
        if result.get("status") == "success":
            return result.get("wifi")
        return None

    def get_volume(self) -> Optional[Dict]:
        """Get volume information"""
        result = self._api_request("GET", "/system/volume")
        if result.get("status") == "success":
            return result.get("volume")
        return None

    def scan_wifi_networks(self) -> Optional[List[Dict]]:
        """Scan WiFi networks"""
        result = self._api_request("POST", "/system/scan")
        if result.get("status") == "success":
            return result.get("networks")
        return None

    # ==================== ADB INPUT ====================

    def press_key(self, keycode: int) -> bool:
        """
        Simulate key press via ADB

        Args:
            keycode: Android keycode (e.g., 4=BACK, 66=ENTER)

        Returns:
            True if successful
        """
        try:
            result = self._adb_command(["shell", "input", "keyevent", str(keycode)])
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to press key: {e}")
            return False

    def input_text(self, text: str) -> bool:
        """
        Input text via ADB

        Args:
            text: Text to input

        Returns:
            True if successful
        """
        try:
            # Replace spaces with %s
            formatted = text.replace(" ", "%s")
            result = self._adb_command(["shell", "input", "text", formatted])
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to input text: {e}")
            return False

    def tap(self, x: int, y: int) -> bool:
        """
        Simulate screen tap via ADB

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            True if successful
        """
        try:
            result = self._adb_command(["shell", "input", "tap", str(x), str(y)])
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to tap: {e}")
            return False

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> bool:
        """
        Simulate swipe gesture via ADB

        Args:
            x1, y1: Start coordinates
            x2, y2: End coordinates
            duration: Swipe duration in ms

        Returns:
            True if successful
        """
        try:
            result = self._adb_command([
                "shell", "input", "swipe",
                str(x1), str(y1), str(x2), str(y2), str(duration)
            ])
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to swipe: {e}")
            return False

    def start_app(self, package_activity: str) -> bool:
        """
        Start Android app

        Args:
            package_activity: Package/Activity (e.g., com.android.settings/.Settings)

        Returns:
            True if successful
        """
        try:
            result = self._adb_command(["shell", "am", "start", "-n", package_activity])
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to start app: {e}")
            return False

    def take_screenshot(self, save_path: str) -> bool:
        """
        Take screenshot

        Args:
            save_path: Local path to save screenshot

        Returns:
            True if successful
        """
        try:
            # Take screenshot on device
            device_path = "/sdcard/screenshot.png"
            self._adb_command(["shell", "screencap", "-p", device_path])

            # Pull to local
            self._adb_command(["pull", device_path, save_path])

            logger.info(f"Screenshot saved to {save_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return False

    # ==================== UTILITY METHODS ====================

    def get_environment_snapshot(self) -> Dict[str, Any]:
        """
        Get complete environment snapshot

        Returns:
            Dictionary with all sensor data
        """
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "battery": self.get_battery(),
            "sensors": {
                "accelerometer": self.get_accelerometer(),
                "gyroscope": self.get_gyroscope(),
                "light": self.get_light(),
                "pressure": self.get_pressure(),
                "proximity": self.get_proximity(),
                "magnetic": self.get_magnetic_field(),
            },
            "location": self.get_location(use_last=True),
            "wifi": self.get_wifi_info(),
            "storage": self.get_system_info(),
        }

        return snapshot

    def print_status(self):
        """Print current device status"""
        print("\n" + "=" * 60)
        print("           PHONE STATUS SNAPSHOT")
        print("=" * 60)

        # Battery
        battery = self.get_battery()
        if battery:
            print(f"🔋 Battery: {battery.get('percentage')}% ({battery.get('status')})")
            print(f"   Temperature: {battery.get('temperature')/10}°C")

        # Location
        location = self.get_location(use_last=True)
        if location:
            print(f"📍 Location: {location.get('latitude')}, {location.get('longitude')}")
            print(f"   Accuracy: {location.get('accuracy')}m")

        # Sensors
        print(f"💡 Light: {self.get_light()} lux")
        print(f"🔊 Proximity: {self.get_proximity()}")

        accel = self.get_accelerometer()
        if accel:
            print(f"📱 Accelerometer: X={accel[0]:.2f}, Y={accel[1]:.2f}, Z={accel[2]:.2f}")

        # WiFi
        wifi = self.get_wifi_info()
        if wifi:
            print(f"📶 WiFi: {wifi.get('ssid')} ({wifi.get('frequency')} MHz)")

        print("=" * 60 + "\n")


# ==================== CONVENIENCE FUNCTIONS ====================

def create_controller(
    adb_path: str = "adb",
    api_base: str = "http://127.0.0.1:9999",
    device_id: Optional[str] = None
) -> PhoneController:
    """
    Factory function to create phone controller

    Args:
        adb_path: Path to ADB executable
        api_base: Base URL for sensor server
        device_id: Device ID

    Returns:
        PhoneController instance
    """
    return PhoneController(adb_path, api_base, device_id)


# ==================== MAIN / EXAMPLES ====================

if __name__ == "__main__":
    import sys

    # Example usage
    controller = create_controller()

    print("Testing Phone Controller...")

    # Health check
    print("\n1. Health check:")
    health = controller.health_check()
    print(f"   {health}")

    # Get battery
    print("\n2. Battery status:")
    battery = controller.get_battery()
    print(f"   {battery}")

    # Get sensors
    print("\n3. Light sensor:")
    light = controller.get_light()
    print(f"   {light} lux")

    # Print full status
    controller.print_status()
