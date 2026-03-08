#!/usr/bin/env python3
"""
Simple Termux Sensor HTTP Server
Provides HTTP API for Android sensors via Termux
Uses only Python standard library
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess
import json
import urllib.parse
import os

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
    def send_json_response(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def send_text_response(self, text, status=200):
        """Send text response"""
        self.send_response(status)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(text.encode())

    def do_GET(self):
        """Handle GET requests"""
        try:
            # Parse path and query
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path
            query = urllib.parse.parse_qs(parsed.query)

            # Health check
            if path == '/health':
                self.send_json_response({'status': 'healthy', 'service': 'sensor-server'})
                return

            # API documentation
            elif path == '/':
                self.send_json_response({
                    'service': 'Termux Sensor HTTP Server',
                    'version': '2.0',
                    'endpoints': {
                        'GET /': 'API documentation',
                        'GET /health': 'Health check',
                        'GET /sensors': 'List available sensors',
                        'GET /sensor/<type>': 'Get sensor reading',
                        'GET /sensor/<type>?limit=n': 'Get n readings',
                        'GET /tts?text=...': 'Text-to-speech',
                        'GET /battery': 'Get battery status',
                    }
                })
                return

            # List sensors
            elif path == '/sensors':
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
                return

            # Battery status
            elif path == '/battery':
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
                return

            # TTS
            elif path == '/tts':
                text = query.get('text', ['Hello'])[0]
                try:
                    subprocess.run(
                        ['termux-tts-speak', text],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    self.send_json_response({'status': 'success', 'message': f'Speaking: {text}'})
                except Exception as e:
                    self.send_json_response({'status': 'error', 'message': str(e)}, 500)
                return

            # Sensor reading
            elif path.startswith('/sensor/'):
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
                    sensor_name = SENSORS.get(sensor_type, sensor_type.upper())

                    cmd = ['termux-sensor', '-s', sensor_name, '-n', limit]
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )

                    if result.returncode == 0:
                        # Parse the output (not JSON, but text format)
                        lines = result.stdout.strip().split('\n')
                        self.send_json_response({
                            'status': 'success',
                            'sensor': sensor_type,
                            'raw_output': result.stdout,
                            'lines': lines
                        })
                    else:
                        self.send_json_response({
                            'status': 'error',
                            'message': result.stderr or 'Sensor read failed'
                        }, 500)

                except Exception as e:
                    self.send_json_response({
                        'status': 'error',
                        'message': str(e)
                    }, 500)
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

    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

def run_server(port=9999):
    """Start the HTTP server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, SensorHandler)

    print("=" * 50)
    print("Simple Termux Sensor HTTP Server")
    print("=" * 50)
    print(f"Starting server on http://0.0.0.0:{port}")
    print("\nAvailable endpoints:")
    print("  GET /              - API documentation")
    print("  GET /health        - Health check")
    print("  GET /sensors       - List available sensors")
    print("  GET /sensor/<type> - Get sensor reading")
    print("  GET /tts?text=...  - Text-to-speech")
    print("  GET /battery       - Battery status")
    print("\nPress Ctrl+C to stop")
    print("=" * 50)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.server_close()

if __name__ == '__main__':
    run_server(9999)
