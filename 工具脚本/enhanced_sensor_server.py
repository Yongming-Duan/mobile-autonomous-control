#!/usr/bin/env python3
"""
Enhanced Termux Sensor HTTP Server
Provides complete HTTP API for Android hardware via Termux:API
Version: 3.0
Features: Sensors, Camera, Audio, GPS, SMS, Notifications, Clipboard, File Management
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from http.server import ThreadingMixIn
import subprocess
import json
import urllib.parse
import os
import base64
import threading
import time
from datetime import datetime
import re

# Configuration
SERVER_PORT = 9999
SERVER_HOST = '0.0.0.0'
UPLOAD_DIR = '/sdcard/sensor_server'

# Sensor mappings
SENSORS = {
    'accelerometer': 'Accelerometer',
    'magnetic': 'Magnetic Field',
    'gyroscope': 'Gyroscope',
    'light': 'Light',
    'pressure': 'Pressure',
    'temperature': 'Ambient Temperature',
    'proximity': 'Proximity',
    'gravity': 'Gravity',
    'linear_acceleration': 'Linear Acceleration',
    'rotation_vector': 'Rotation Vector',
    'orientation': 'Orientation',
    'humidity': 'Relative Humidity',
    'ambient_temperature': 'Ambient Temperature',
}

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    daemon_threads = True

class EnhancedSensorHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.upload_dir = UPLOAD_DIR
        os.makedirs(self.upload_dir, exist_ok=True)
        super().__init__(*args, **kwargs)

    def send_json_response(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))

    def send_text_response(self, text, status=200, content_type='text/plain'):
        """Send text response"""
        self.send_response(status)
        self.send_header('Content-Type', f'{content_type}; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(text.encode('utf-8'))

    def send_file_response(self, file_path, content_type='image/jpeg'):
        """Send file response"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_json_response({'status': 'error', 'message': 'File not found'}, 404)

    def do_OPTIONS(self):
        """Handle OPTIONS request for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        """Handle GET requests"""
        try:
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path
            query = urllib.parse.parse_qs(parsed.query)

            # Health check
            if path == '/health':
                self.send_json_response({
                    'status': 'healthy',
                    'service': 'enhanced-sensor-server',
                    'version': '3.0',
                    'timestamp': datetime.now().isoformat()
                })
                return

            # API documentation
            elif path == '/' or path == '/api':
                self.send_json_response({
                    'service': 'Enhanced Termux Sensor HTTP Server',
                    'version': '3.0',
                    'endpoints': {
                        # System
                        'GET /': 'API documentation',
                        'GET /health': 'Health check',
                        'GET /info': 'Server information',

                        # Sensors
                        'GET /sensors': 'List available sensors',
                        'GET /sensor/<type>': 'Get sensor reading',
                        'GET /sensor/<type>?limit=n': 'Get n readings',

                        # Camera
                        'GET /camera/info': 'Camera information',
                        'POST /camera/photo': 'Take photo',
                        'GET /camera/photo/<filename>': 'Get photo file',

                        # Audio
                        'POST /audio/record': 'Record audio',
                        'GET /audio/info': 'Microphone info',
                        'GET /audio/list': 'List recordings',
                        'GET /audio/<filename>': 'Get audio file',

                        # Location
                        'GET /location': 'Get GPS location',
                        'GET /location?last=true': 'Get last known location',

                        # Battery
                        'GET /battery': 'Get battery status',

                        # TTS
                        'GET /tts?text=...': 'Text-to-speech',
                        'GET /tts/engines': 'List TTS engines',

                        # SMS
                        'GET /sms/list': 'List SMS messages',
                        'GET /sms/send': 'Send SMS (POST required)',

                        # Notifications
                        'GET /notification/list': 'List notifications',

                        # Clipboard
                        'GET /clipboard': 'Get clipboard content',
                        'POST /clipboard': 'Set clipboard content',

                        # System info
                        'GET /system/info': 'System information',
                        'GET /system/wifi': 'WiFi information',
                        'GET /system/volume': 'Volume information',

                        # File operations
                        'GET /files/list': 'List files',
                        'GET /files/download': 'Download file',
                    }
                })
                return

            # Server info
            elif path == '/info':
                self.send_json_response({
                    'service': 'enhanced-sensor-server',
                    'version': '3.0',
                    'upload_dir': self.upload_dir,
                    'available_sensors': list(SENSORS.keys()),
                    'timestamp': datetime.now().isoformat()
                })
                return

            # ========== SENSORS ==========
            elif path == '/sensors':
                self._list_sensors()
                return

            elif path.startswith('/sensor/'):
                self._get_sensor_data(path, query)
                return

            # ========== CAMERA ==========
            elif path == '/camera/info':
                self._camera_info()
                return

            elif path.startswith('/camera/photo/'):
                filename = path.split('/')[-1]
                filepath = os.path.join(self.upload_dir, filename)
                self.send_file_response(filepath, 'image/jpeg')
                return

            elif path.startswith('/camera/list'):
                self._list_files('photo', '.jpg')
                return

            # ========== AUDIO ==========
            elif path == '/audio/info':
                self._audio_info()
                return

            elif path == '/audio/list':
                self._list_files('audio', '.wav')
                return

            elif path.startswith('/audio/'):
                filename = path.split('/')[-1]
                filepath = os.path.join(self.upload_dir, filename)
                self.send_file_response(filepath, 'audio/wav')
                return

            # ========== LOCATION ==========
            elif path == '/location':
                self._get_location(query)
                return

            # ========== BATTERY ==========
            elif path == '/battery':
                self._get_battery()
                return

            # ========== TTS ==========
            elif path == '/tts':
                text = query.get('text', ['Hello'])[0]
                rate = query.get('rate', ['1.0'])[0]
                pitch = query.get('pitch', ['1.0'])[0]
                self._tts_speak(text, rate, pitch)
                return

            elif path == '/tts/engines':
                self._tts_engines()
                return

            # ========== SMS ==========
            elif path == '/sms/list':
                limit = query.get('limit', ['10'])[0]
                offset = query.get('offset', ['0'])[0]
                self._sms_list(limit, offset)
                return

            # ========== NOTIFICATIONS ==========
            elif path == '/notification/list':
                self._notification_list()
                return

            # ========== CLIPBOARD ==========
            elif path == '/clipboard':
                self._get_clipboard()
                return

            # ========== SYSTEM INFO ==========
            elif path == '/system/info':
                self._system_info()
                return

            elif path == '/system/wifi':
                self._wifi_info()
                return

            elif path == '/system/volume':
                self._volume_info()
                return

            # ========== FILES ==========
            elif path == '/files/list':
                dir_path = query.get('path', [self.upload_dir])[0]
                self._list_files_path(dir_path)
                return

            # 404
            else:
                self.send_json_response({
                    'status': 'error',
                    'message': 'Not found',
                    'path': path
                }, 404)

        except Exception as e:
            self.send_json_response({
                'status': 'error',
                'message': f'Server error: {str(e)}',
                'path': path
            }, 500)

    def do_POST(self):
        """Handle POST requests"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                try:
                    data = json.loads(post_data.decode('utf-8'))
                except:
                    data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            else:
                data = {}

            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path
            query = urllib.parse.parse_qs(parsed.query)

            # ========== CAMERA ==========
            if path == '/camera/photo':
                camera_id = query.get('camera', ['0'])[0]
                self._camera_photo(camera_id)
                return

            # ========== AUDIO ==========
            elif path == '/audio/record':
                duration = query.get('duration', ['5'])[0]
                limit = query.get('limit', ['false'])[0].lower() == 'true'
                self._audio_record(duration, limit)
                return

            elif path == '/audio/record/stop':
                self._audio_record_stop()
                return

            # ========== LOCATION ==========
            elif path == '/location/update':
                self._location_update()
                return

            # ========== SMS ==========
            elif path == '/sms/send':
                number = query.get('number', [None])[0]
                text = query.get('text', [''])[0]
                if number:
                    self._sms_send(number, text)
                else:
                    self.send_json_response({'status': 'error', 'message': 'Number required'}, 400)
                return

            # ========== NOTIFICATIONS ==========
            elif path == '/notification/send':
                title = query.get('title', ['Notification'])[0]
                content = query.get('content', [''])[0]
                id = query.get('id', ['1'])[0]
                self._notification_send(title, content, id)
                return

            # ========== CLIPBOARD ==========
            elif path == '/clipboard':
                text = query.get('text', [''])[0]
                self._set_clipboard(text)
                return

            # ========== WIFI ==========
            elif path == '/system/scan':
                self._wifi_scan()
                return

            # 404
            else:
                self.send_json_response({
                    'status': 'error',
                    'message': 'Not found'
                }, 404)

        except Exception as e:
            self.send_json_response({
                'status': 'error',
                'message': f'Server error: {str(e)}'
            }, 500)

    # ========== SENSOR METHODS ==========

    def _list_sensors(self):
        """List all available sensors"""
        try:
            result = subprocess.run(
                ['termux-sensor', '-l'],
                capture_output=True,
                text=True,
                timeout=5
            )
            sensors_list = [s for s in result.stdout.strip().split('\n') if s]
            self.send_json_response({
                'status': 'success',
                'sensors': sensors_list,
                'count': len(sensors_list)
            })
        except Exception as e:
            self.send_json_response({'status': 'error', 'message': str(e)}, 500)

    def _get_sensor_data(self, path, query):
        """Get sensor reading"""
        sensor_type = path[8:]  # Remove '/sensor/'

        if sensor_type not in SENSORS and sensor_type != 'all':
            self.send_json_response({
                'status': 'error',
                'message': f'Unknown sensor: {sensor_type}',
                'available': list(SENSORS.keys())
            }, 400)
            return

        try:
            limit = query.get('limit', ['1'])[0]
            sensor_name = SENSORS.get(sensor_type, sensor_type.replace('_', ' ').title())

            cmd = ['termux-sensor', '-s', sensor_name, '-n', limit]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                # Parse sensor data
                data = self._parse_sensor_output(result.stdout, sensor_name)
                self.send_json_response({
                    'status': 'success',
                    'sensor': sensor_type,
                    'sensor_name': sensor_name,
                    'data': data,
                    'raw_output': result.stdout
                })
            else:
                self.send_json_response({
                    'status': 'error',
                    'message': result.stderr or 'Sensor read failed'
                }, 500)
        except Exception as e:
            self.send_json_response({'status': 'error', 'message': str(e)}, 500)

    def _parse_sensor_output(self, output, sensor_name):
        """Parse sensor output into structured data"""
        lines = output.strip().split('\n')
        data = []

        for line in lines[1:]:  # Skip first line (sensor name)
            if not line.strip():
                continue

            # Extract values
            match = re.search(r'values=\[(.*?)\]', line)
            time_match = re.search(r'time=(\d+)', line)

            if match:
                values = [float(x) if x.replace('.', '').replace('-', '').isdigit() else x
                         for x in match.group(1).split(', ')]

                entry = {'values': values}
                if time_match:
                    entry['timestamp'] = int(time_match.group(1))

                data.append(entry)

        return data

    # ========== CAMERA METHODS ==========

    def _camera_info(self):
        """Get camera information"""
        try:
            result = subprocess.run(
                ['termux-camera-info'],
                capture_output=True,
                text=True,
                timeout=5
            )
            self.send_json_response({
                'status': 'success',
                'cameras': result.stdout
            })
        except Exception as e:
            self.send_json_response({'status': 'error', 'message': str(e)}, 500)

    def _camera_photo(self, camera_id='0'):
        """Take a photo"""
        try:
            filename = f"photo_{int(time.time())}.jpg"
            filepath = os.path.join(self.upload_dir, filename)

            result = subprocess.run(
                ['termux-camera-photo', '-c', str(camera_id), filepath],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                self.send_json_response({
                    'status': 'success',
                    'message': 'Photo taken',
                    'filename': filename,
                    'path': filepath,
                    'url': f'/camera/photo/{filename}'
                })
            else:
                self.send_json_response({
                    'status': 'error',
                    'message': result.stderr or 'Failed to take photo'
                }, 500)
        except Exception as e:
            self.send_json_response({'status': 'error', 'message': str(e)}, 500)

    # ========== AUDIO METHODS ==========

    def _audio_info(self):
        """Get microphone info"""
        self.send_json_response({
            'status': 'success',
            'info': 'Audio recording available via termux-microphone-record'
        })

    def _audio_record(self, duration='5', limit=False):
        """Record audio"""
        try:
            filename = f"audio_{int(time.time())}.wav"
            filepath = os.path.join(self.upload_dir, filename)

            cmd = ['termux-microphone-record', '-f', filepath, '-l', str(duration)]
            if limit:
                cmd.append('--limit')

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=int(duration)+5)

            self.send_json_response({
                'status': 'success',
                'message': 'Audio recorded',
                'filename': filename,
                'path': filepath,
                'url': f'/audio/{filename}'
            })
        except Exception as e:
            self.send_json_response({'status': 'error', 'message': str(e)}, 500)

    def _audio_record_stop(self):
        """Stop audio recording"""
        try:
            subprocess.run(['termux-microphone-record', '-q'], capture_output=True, timeout=5)
            self.send_json_response({'status': 'success', 'message': 'Recording stopped'})
        except Exception as e:
            self.send_json_response({'status': 'error', 'message': str(e)}, 500)

    # ========== LOCATION METHODS ==========

    def _get_location(self, query):
        """Get GPS location"""
        try:
            last = query.get('last', ['false'])[0].lower() == 'true'

            cmd = ['termux-location']
            if last:
                cmd.append('-l')

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                data = json.loads(result.stdout)
                self.send_json_response({
                    'status': 'success',
                    'location': data
                })
            else:
                self.send_json_response({
                    'status': 'error',
                    'message': 'Failed to get location. Make sure GPS is enabled.'
                }, 500)
        except subprocess.TimeoutExpired:
            self.send_json_response({
                'status': 'error',
                'message': 'Location timeout. GPS may be disabled or no signal.'
            }, 500)
        except Exception as e:
            self.send_json_response({'status': 'error', 'message': str(e)}, 500)

    def _location_update(self):
        """Request location update"""
        try:
            result = subprocess.run(
                ['termux-location', '-p', 'gps', '-r', 'last'],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                self.send_json_response({'status': 'success', 'location': data})
            else:
                self.send_json_response({'status': 'error', 'message': 'Update failed'}, 500)
        except Exception as e:
            self.send_json_response({'status': 'error', 'message': str(e)}, 500)

    # ========== BATTERY METHODS ==========

    def _get_battery(self):
        """Get battery status"""
        try:
            result = subprocess.run(
                ['termux-battery-status'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                self.send_json_response({'status': 'success', 'battery': data})
            else:
                self.send_json_response({'status': 'error', 'message': result.stderr}, 500)
        except Exception as e:
            self.send_json_response({'status': 'error', 'message': str(e)}, 500)

    # ========== TTS METHODS ==========

    def _tts_speak(self, text, rate='1.0', pitch='1.0'):
        """Text to speech"""
        try:
            subprocess.run(
                ['termux-tts-speak', '-r', str(rate), '-p', str(pitch), text],
                capture_output=True,
                text=True,
                timeout=30
            )
            self.send_json_response({
                'status': 'success',
                'message': f'Speaking: {text}'
            })
        except Exception as e:
            self.send_json_response({'status': 'error', 'message': str(e)}, 500)

    def _tts_engines(self):
        """List TTS engines"""
        try:
            result = subprocess.run(
                ['termux-tts-engines'],
                capture_output=True,
                text=True,
                timeout=5
            )
            self.send_json_response({
                'status': 'success',
                'engines': result.stdout.strip().split('\n')
            })
        except Exception as e:
            self.send_json_response({'status': 'error', 'message': str(e)}, 500)

    # ========== SMS METHODS ==========

    def _sms_list(self, limit='10', offset='0'):
        """List SMS messages"""
        try:
            # Note: termux-sms-list command
            result = subprocess.run(
                ['termux-sms-list', '-l', limit, '-o', offset],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                self.send_json_response({'status': 'success', 'messages': data})
            else:
                self.send_json_response({'status': 'error', 'message': result.stderr}, 500)
        except Exception as e:
            self.send_json_response({'status': 'error', 'message': str(e)}, 500)

    def _sms_send(self, number, text):
        """Send SMS"""
        try:
            result = subprocess.run(
                ['termux-sms-send', '-n', number, text],
                capture_output=True,
                text=True,
                timeout=10
            )
            self.send_json_response({
                'status': 'success',
                'message': f'SMS sent to {number}'
            })
        except Exception as e:
            self.send_json_response({'status': 'error', 'message': str(e)}, 500)

    # ========== NOTIFICATION METHODS ==========

    def _notification_list(self):
        """List notifications"""
        try:
            result = subprocess.run(
                ['termux-notification-list'],
                capture_output=True,
                text=True,
                timeout=5
            )
            data = json.loads(result.stdout) if result.stdout else []
            self.send_json_response({'status': 'success', 'notifications': data})
        except Exception as e:
            self.send_json_response({'status': 'error', 'message': str(e)}, 500)

    def _notification_send(self, title, content, id='1'):
        """Send notification"""
        try:
            subprocess.run(
                ['termux-notification', '--id', id, '--title', title, '--content', content],
                capture_output=True,
                text=True,
                timeout=5
            )
            self.send_json_response({
                'status': 'success',
                'message': 'Notification sent'
            })
        except Exception as e:
            self.send_json_response({'status': 'error', 'message': str(e)}, 500)

    # ========== CLIPBOARD METHODS ==========

    def _get_clipboard(self):
        """Get clipboard content"""
        try:
            result = subprocess.run(
                ['termux-clipboard-get'],
                capture_output=True,
                text=True,
                timeout=5
            )
            self.send_json_response({
                'status': 'success',
                'content': result.stdout
            })
        except Exception as e:
            self.send_json_response({'status': 'error', 'message': str(e)}, 500)

    def _set_clipboard(self, text):
        """Set clipboard content"""
        try:
            subprocess.run(
                ['termux-clipboard-set', text],
                capture_output=True,
                text=True,
                timeout=5
            )
            self.send_json_response({
                'status': 'success',
                'message': 'Clipboard updated'
            })
        except Exception as e:
            self.send_json_response({'status': 'error', 'message': str(e)}, 500)

    # ========== SYSTEM INFO METHODS ==========

    def _system_info(self):
        """Get system information"""
        try:
            # Get various system info
            info = {
                'timestamp': datetime.now().isoformat(),
                'battery': json.loads(subprocess.run(
                    ['termux-battery-status'], capture_output=True, text=True, timeout=5
                ).stdout),
            }
            self.send_json_response({'status': 'success', 'system': info})
        except Exception as e:
            self.send_json_response({'status': 'error', 'message': str(e)}, 500)

    def _wifi_info(self):
        """Get WiFi information"""
        try:
            result = subprocess.run(
                ['termux-wifi-connectioninfo'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                self.send_json_response({'status': 'success', 'wifi': data})
            else:
                self.send_json_response({
                    'status': 'error',
                    'message': 'Failed to get WiFi info'
                }, 500)
        except Exception as e:
            self.send_json_response({'status': 'error', 'message': str(e)}, 500)

    def _wifi_scan(self):
        """Scan WiFi networks"""
        try:
            result = subprocess.run(
                ['termux-wifi-scaninfo'],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                self.send_json_response({'status': 'success', 'networks': data})
            else:
                self.send_json_response({'status': 'error', 'message': 'Scan failed'}, 500)
        except Exception as e:
            self.send_json_response({'status': 'error', 'message': str(e)}, 500)

    def _volume_info(self):
        """Get volume information"""
        try:
            result = subprocess.run(
                ['termux-volume'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                self.send_json_response({'status': 'success', 'volume': data})
            else:
                self.send_json_response({'status': 'error', 'message': result.stderr}, 500)
        except Exception as e:
            self.send_json_response({'status': 'error', 'message': str(e)}, 500)

    # ========== FILE METHODS ==========

    def _list_files(self, file_type, extension):
        """List files by type"""
        try:
            files = []
            for f in os.listdir(self.upload_dir):
                if f.endswith(extension):
                    filepath = os.path.join(self.upload_dir, f)
                    stat = os.stat(filepath)
                    files.append({
                        'filename': f,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'url': f'/{file_type}/{f}'
                    })
            files.sort(key=lambda x: x['modified'], reverse=True)
            self.send_json_response({'status': 'success', 'files': files})
        except Exception as e:
            self.send_json_response({'status': 'error', 'message': str(e)}, 500)

    def _list_files_path(self, dir_path):
        """List files in directory"""
        try:
            files = []
            for f in os.listdir(dir_path):
                filepath = os.path.join(dir_path, f)
                if os.path.isfile(filepath):
                    stat = os.stat(filepath)
                    files.append({
                        'filename': f,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
            self.send_json_response({'status': 'success', 'files': files})
        except Exception as e:
            self.send_json_response({'status': 'error', 'message': str(e)}, 500)

    def log_message(self, format, *args):
        """Custom logging"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {format % args}")


def run_server(port=SERVER_PORT, host=SERVER_HOST):
    """Start the enhanced HTTP server"""
    server_address = (host, port)
    httpd = ThreadedHTTPServer(server_address, EnhancedSensorHandler)

    print("=" * 60)
    print("   Enhanced Termux Sensor HTTP Server v3.0")
    print("=" * 60)
    print(f"✓ Server running on http://{host}:{port}")
    print(f"✓ Upload directory: {UPLOAD_DIR}")
    print(f"✓ Threading enabled for concurrent requests")
    print("\n📋 Available endpoints:")
    print("   System: GET /, /health, /info")
    print("   Sensors: GET /sensors, /sensor/<type>")
    print("   Camera: GET /camera/info, POST /camera/photo")
    print("   Audio: GET /audio/info, POST /audio/record")
    print("   Location: GET /location")
    print("   Battery: GET /battery")
    print("   TTS: GET /tts?text=...")
    print("   SMS: GET /sms/list, POST /sms/send")
    print("   Notifications: GET /notification/list, POST /notification/send")
    print("   Clipboard: GET /clipboard, POST /clipboard")
    print("   System: GET /system/info, /system/wifi, /system/volume")
    print("\n📚 API documentation: http://0.0.0.0:{}/".format(port))
    print("\nPress Ctrl+C to stop")
    print("=" * 60)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped.")
        httpd.server_close()


if __name__ == '__main__':
    run_server()
