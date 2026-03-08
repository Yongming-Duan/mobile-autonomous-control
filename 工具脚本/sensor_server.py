#!/usr/bin/env python3
"""
Termux Sensor HTTP Server
Provides HTTP API for Android sensors via Termux
"""

from flask import Flask, jsonify, send_file, request
import subprocess
import json
import os

app = Flask(__name__)

# Available sensors based on Termux
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

@app.route('/')
def index():
    """API documentation"""
    return jsonify({
        'service': 'Termux Sensor HTTP Server',
        'version': '1.0',
        'endpoints': {
            'GET /': 'API documentation',
            'GET /sensors': 'List available sensors',
            'GET /sensor/<type>': 'Get sensor reading (accelerometer, gyroscope, light, etc.)',
            'GET /sensor/<type>?limit=n': 'Get n readings',
            'GET /tts?text=...': 'Text-to-speech',
            'GET /battery': 'Get battery status',
        }
    })

@app.route('/sensors')
def list_sensors():
    """List available sensors"""
    try:
        result = subprocess.run(
            ['termux-sensor', '-l'],
            capture_output=True,
            text=True,
            timeout=5
        )
        sensors_list = result.stdout.strip().split('\n')
        return jsonify({
            'status': 'success',
            'sensors': sensors_list,
            'count': len(sensors_list)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/sensor/<sensor_type>')
def get_sensor(sensor_type):
    """Get sensor reading"""
    # Validate sensor type
    if sensor_type not in SENSORS and sensor_type not in ['all']:
        return jsonify({
            'status': 'error',
            'message': f'Unknown sensor: {sensor_type}',
            'available': list(SENSORS.keys())
        }), 400

    try:
        # Get limit from query parameter
        limit = request.args.get('limit', '1')

        # Run termux-sensor command
        cmd = ['termux-sensor', '-s', SENSORS.get(sensor_type, sensor_type.upper()), '-n', limit]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            # Parse JSON output from termux-sensor
            data = json.loads(result.stdout)
            return jsonify({
                'status': 'success',
                'sensor': sensor_type,
                'data': data
            })
        else:
            return jsonify({
                'status': 'error',
                'message': result.stderr or 'Sensor read failed'
            }), 500

    except json.JSONDecodeError:
        return jsonify({
            'status': 'error',
            'message': 'Failed to parse sensor data'
        }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/tts')
def text_to_speech():
    """Text-to-speech"""
    text = request.args.get('text', 'Hello')
    try:
        result = subprocess.run(
            ['termux-tts-speak', text],
            capture_output=True,
            text=True,
            timeout=10
        )
        return jsonify({
            'status': 'success',
            'message': f'Speaking: {text}'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/battery')
def battery():
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
            return jsonify({
                'status': 'success',
                'battery': data
            })
        else:
            return jsonify({
                'status': 'error',
                'message': result.stderr
            }), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'sensor-server'})

if __name__ == '__main__':
    print("=" * 50)
    print("Termux Sensor HTTP Server")
    print("=" * 50)
    print("Starting server on http://0.0.0.0:5000")
    print("\nAvailable endpoints:")
    print("  GET /              - API documentation")
    print("  GET /sensors       - List available sensors")
    print("  GET /sensor/<type> - Get sensor reading")
    print("  GET /tts?text=...  - Text-to-speech")
    print("  GET /battery       - Battery status")
    print("\nPress Ctrl+C to stop")
    print("=" * 50)

    app.run(host='0.0.0.0', port=9999, debug=False)
