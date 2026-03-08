#!/usr/bin/env python3
"""
Sensor Dashboard - Web-based visualization
Flask-based real-time dashboard for sensor data
Version: 1.0
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from threading import Thread
import time
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sensor-dashboard-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables
DB_PATH = "sensor_data.db"
UPDATE_INTERVAL = 5  # seconds


# ==================== DATABASE HELPERS ====================

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def query_db(query: str, args: tuple = (), one: bool = False):
    """Query database and return results"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, args)
    results = cursor.fetchall()
    conn.close()

    if one:
        return results[0] if results else None
    return results


# ==================== ROUTES ====================

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')


@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/sensors')
def get_sensors():
    """Get available sensors"""
    sensors = query_db(
        'SELECT DISTINCT sensor_type FROM sensor_readings ORDER BY sensor_type'
    )
    return jsonify([s['sensor_type'] for s in sensors])


@app.route('/api/sensor/<sensor_type>/latest')
def get_sensor_latest(sensor_type: str):
    """Get latest sensor reading"""
    result = query_db(
        '''SELECT timestamp, value, values_json
           FROM sensor_readings
           WHERE sensor_type = ?
           ORDER BY timestamp DESC
           LIMIT 1''',
        (sensor_type,),
        one=True
    )

    if result:
        return jsonify({
            'sensor': sensor_type,
            'timestamp': result['timestamp'],
            'value': result['value'],
            'values': json.loads(result['values_json']) if result['values_json'] else []
        })

    return jsonify({'error': 'Not found'}), 404


@app.route('/api/sensor/<sensor_type>/history')
def get_sensor_history(sensor_type: str):
    """Get sensor history"""
    hours = request.args.get('hours', 24, type=int)
    limit = request.args.get('limit', 100, type=int)

    start_time = datetime.now() - timedelta(hours=hours)

    results = query_db(
        '''SELECT timestamp, value, values_json
           FROM sensor_readings
           WHERE sensor_type = ?
           AND timestamp > ?
           ORDER BY timestamp DESC
           LIMIT ?''',
        (sensor_type, start_time, limit)
    )

    data = [
        {
            'timestamp': r['timestamp'],
            'value': r['value'],
            'values': json.loads(r['values_json']) if r['values_json'] else []
        }
        for r in results
    ]

    return jsonify(data)


@app.route('/api/sensor/<sensor_type>/stats')
def get_sensor_stats(sensor_type: str):
    """Get sensor statistics"""
    hours = request.args.get('hours', 24, type=int)

    start_time = datetime.now() - timedelta(hours=hours)

    result = query_db(
        '''SELECT
            AVG(value) as avg_value,
            MIN(value) as min_value,
            MAX(value) as max_value,
            COUNT(*) as count
           FROM sensor_readings
           WHERE sensor_type = ?
           AND timestamp > ?''',
        (sensor_type, start_time),
        one=True
    )

    if result and result['avg_value']:
        return jsonify({
            'sensor': sensor_type,
            'period_hours': hours,
            'avg': result['avg_value'],
            'min': result['min_value'],
            'max': result['max_value'],
            'count': result['count']
        })

    return jsonify({'error': 'No data'}), 404


@app.route('/api/battery')
def get_battery():
    """Get battery status"""
    result = query_db(
        '''SELECT timestamp, percentage, status, temperature
           FROM battery_readings
           ORDER BY timestamp DESC
           LIMIT 1''',
        one=True
    )

    if result:
        return jsonify({
            'timestamp': result['timestamp'],
            'percentage': result['percentage'],
            'status': result['status'],
            'temperature': result['temperature']
        })

    return jsonify({'error': 'No data'}), 404


@app.route('/api/battery/history')
def get_battery_history():
    """Get battery history"""
    hours = request.args.get('hours', 24, type=int)

    start_time = datetime.now() - timedelta(hours=hours)

    results = query_db(
        '''SELECT timestamp, percentage, status, temperature
           FROM battery_readings
           WHERE timestamp > ?
           ORDER BY timestamp ASC''',
        (start_time,)
    )

    return jsonify([
        {
            'timestamp': r['timestamp'],
            'percentage': r['percentage'],
            'status': r['status'],
            'temperature': r['temperature']
        }
        for r in results
    ])


@app.route('/api/location/latest')
def get_location_latest():
    """Get latest location"""
    result = query_db(
        '''SELECT timestamp, latitude, longitude, accuracy
           FROM location_readings
           ORDER BY timestamp DESC
           LIMIT 1''',
        one=True
    )

    if result:
        return jsonify({
            'timestamp': result['timestamp'],
            'latitude': result['latitude'],
            'longitude': result['longitude'],
            'accuracy': result['accuracy']
        })

    return jsonify({'error': 'No data'}), 404


@app.route('/api/location/history')
def get_location_history():
    """Get location history"""
    hours = request.args.get('hours', 24, type=int)

    start_time = datetime.now() - timedelta(hours=hours)

    results = query_db(
        '''SELECT timestamp, latitude, longitude, accuracy
           FROM location_readings
           WHERE timestamp > ?
           ORDER BY timestamp ASC''',
        (start_time,)
    )

    return jsonify([
        {
            'timestamp': r['timestamp'],
            'latitude': r['latitude'],
            'longitude': r['longitude'],
            'accuracy': r['accuracy']
        }
        for r in results
    ])


@app.route('/api/events')
def get_events():
    """Get events"""
    hours = request.args.get('hours', 24, type=int)
    event_type = request.args.get('type')

    start_time = datetime.now() - timedelta(hours=hours)

    if event_type:
        results = query_db(
            '''SELECT timestamp, event_type, description, event_data
               FROM events
               WHERE event_type = ?
               AND timestamp > ?
               ORDER BY timestamp DESC
               LIMIT 50''',
            (event_type, start_time)
        )
    else:
        results = query_db(
            '''SELECT timestamp, event_type, description, event_data
               FROM events
               WHERE timestamp > ?
               ORDER BY timestamp DESC
               LIMIT 50''',
            (start_time,)
        )

    return jsonify([
        {
            'timestamp': r['timestamp'],
            'type': r['event_type'],
            'description': r['description'],
            'data': json.loads(r['event_data']) if r['event_data'] else {}
        }
        for r in results
    ])


@app.route('/api/stats')
def get_stats():
    """Get database statistics"""
    stats = {}

    for table in ['sensor_readings', 'battery_readings', 'location_readings', 'events']:
        result = query_db(f'SELECT COUNT(*) as count FROM {table}', one=True)
        stats[table] = result['count']

    return jsonify(stats)


@app.route('/api/dashboard')
def get_dashboard_data():
    """Get all dashboard data in one request"""
    data = {
        'timestamp': datetime.now().isoformat(),
        'battery': None,
        'location': None,
        'sensors': {}
    }

    # Battery
    battery = query_db(
        '''SELECT timestamp, percentage, status, temperature
           FROM battery_readings
           ORDER BY timestamp DESC
           LIMIT 1''',
        one=True
    )
    if battery:
        data['battery'] = {
            'percentage': battery['percentage'],
            'status': battery['status'],
            'temperature': battery['temperature']
        }

    # Location
    location = query_db(
        '''SELECT timestamp, latitude, longitude, accuracy
           FROM location_readings
           ORDER BY timestamp DESC
           LIMIT 1''',
        one=True
    )
    if location:
        data['location'] = {
            'latitude': location['latitude'],
            'longitude': location['longitude'],
            'accuracy': location['accuracy']
        }

    # Sensors (latest readings)
    for sensor in ['accelerometer', 'gyroscope', 'light', 'pressure']:
        result = query_db(
            '''SELECT timestamp, value, values_json
               FROM sensor_readings
               WHERE sensor_type = ?
               ORDER BY timestamp DESC
               LIMIT 1''',
            (sensor,),
            one=True
        )
        if result:
            data['sensors'][sensor] = {
                'value': result['value'],
                'values': json.loads(result['values_json']) if result['values_json'] else [],
                'timestamp': result['timestamp']
            }

    return jsonify(data)


# ==================== SOCKET.IO EVENTS ====================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f'Client connected: {request.sid}')
    emit('connected', {'timestamp': datetime.now().isoformat()})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f'Client disconnected: {request.sid}')


@socketio.on('subscribe')
def handle_subscribe(data):
    """Handle subscription to sensor updates"""
    sensor = data.get('sensor')
    logger.info(f'Client {request.sid} subscribed to {sensor}')
    emit('subscribed', {'sensor': sensor})


def broadcast_updates():
    """Background thread to broadcast updates"""
    while True:
        try:
            # Get latest data
            battery = query_db(
                '''SELECT percentage, status, temperature
                   FROM battery_readings
                   ORDER BY timestamp DESC
                   LIMIT 1''',
                one=True
            )

            if battery:
                socketio.emit('battery_update', {
                    'percentage': battery['percentage'],
                    'status': battery['status'],
                    'temperature': battery['temperature'],
                    'timestamp': datetime.now().isoformat()
                })

            # Broadcast sensor updates
            for sensor in ['accelerometer', 'light']:
                result = query_db(
                    '''SELECT timestamp, value, values_json
                       FROM sensor_readings
                       WHERE sensor_type = ?
                       ORDER BY timestamp DESC
                       LIMIT 1''',
                    (sensor,),
                    one=True
                )

                if result:
                    socketio.emit(f'{sensor}_update', {
                        'value': result['value'],
                        'values': json.loads(result['values_json']) if result['values_json'] else [],
                        'timestamp': result['timestamp']
                    })

            time.sleep(UPDATE_INTERVAL)

        except Exception as e:
            logger.error(f'Broadcast error: {e}')
            time.sleep(UPDATE_INTERVAL)


# ==================== MAIN ====================

def run_dashboard(host='0.0.0.0', port=5000, debug=False):
    """Run dashboard server"""
    logger.info(f"Starting dashboard on http://{host}:{port}")

    # Start broadcast thread
    broadcast_thread = Thread(target=broadcast_updates, daemon=True)
    broadcast_thread.start()

    # Run SocketIO server
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Sensor Dashboard Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host address')
    parser.add_argument('--port', type=int, default=5000, help='Port number')
    parser.add_argument('--debug', action='store_true', help='Debug mode')

    args = parser.parse_args()

    run_dashboard(host=args.host, port=args.port, debug=args.debug)
