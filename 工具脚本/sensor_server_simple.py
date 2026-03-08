#!/usr/bin/env python3
"""
Simple Termux Sensor HTTP Server
Using Python's built-in http.server (no Flask required)
"""

import subprocess
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time

# Available sensors
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
}

class SensorHandler(BaseHTTPRequestHandler):
    def send_json(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)

        try:
            if path == '/':
                self.send_json({
                    'service': 'Termux Sensor HTTP Server',
                    'version': '2.0 (Simple)',
                    'endpoints': {
                        'GET /': 'API documentation',
                        'GET /sensors': 'List available sensors',
                        'GET /sensor/<type>': 'Get sensor reading',
                        'GET /tts?text=...': 'Text-to-speech',
                        'GET /battery': 'Get battery status',
                        'GET /health': 'Health check',
                    }
                })

            elif path == '/sensors':
                result = subprocess.run(
                    ['termux-sensor', '-l'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                sensors_list = result.stdout.strip().split('\n')
                self.send_json({
                    'status': 'success',
                    'sensors': sensors_list,
                    'count': len(sensors_list)
                })

            elif path.startswith('/sensor/'):
                sensor_type = path[8:]  # Remove '/sensor/'
                if sensor_type not in SENSORS:
                    self.send_json({
                        'status': 'error',
                        'message': f'Unknown sensor: {sensor_type}',
                        'available': list(SENSORS.keys())
                    }, 400)
                    return

                limit = query.get('limit', ['1'])[0]
                cmd = ['termux-sensor', '-s', SENSORS.get(sensor_type, sensor_type.upper()), '-n', limit]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    self.send_json({
                        'status': 'success',
                        'sensor': sensor_type,
                        'data': data
                    })
                else:
                    self.send_json({
                        'status': 'error',
                        'message': result.stderr or 'Sensor read failed'
                    }, 500)

            elif path == '/tts':
                text = query.get('text', ['Hello'])[0]
                subprocess.run(['termux-tts-speak', text], capture_output=True, timeout=10)
                self.send_json({
                    'status': 'success',
                    'message': f'Speaking: {text}'
                })

            elif path == '/battery':
                result = subprocess.run(
                    ['termux-battery-status'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    self.send_json({'status': 'success', 'battery': data})
                else:
                    self.send_json({'status': 'error', 'message': result.stderr}, 500)

            elif path == '/health':
                self.send_json({'status': 'healthy', 'service': 'sensor-server'})

            else:
                self.send_json({'status': 'error', 'message': 'Not found'}, 404)

        except Exception as e:
            self.send_json({'status': 'error', 'message': str(e)}, 500)

    def log_message(self, format, *args):
        """Custom log to suppress default logging"""
        print(f"[{self.log_date_time_string()}] {format % args}")

def run_server(port=9999):
    """Run the HTTP server"""
    server = HTTPServer(('0.0.0.0', port), SensorHandler)

    print("=" * 50)
    print("Termux Sensor HTTP Server (Simple)")
    print("=" * 50)
    print(f"Starting server on http://0.0.0.0:{port}")
    print("\nAvailable endpoints:")
    print("  GET /              - API documentation")
    print("  GET /sensors       - List available sensors")
    print("  GET /sensor/<type> - Get sensor reading")
    print("  GET /tts?text=...  - Text-to-speech")
    print("  GET /battery       - Battery status")
    print("  GET /health        - Health check")
    print("\nPress Ctrl+C to stop")
    print("=" * 50)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        server.shutdown()

if __name__ == '__main__':
    run_server(port=9999)
