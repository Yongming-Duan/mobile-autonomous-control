#!/usr/bin/env python3
"""
Sensor Data Collector
Continuous data collection and storage system
Version: 1.0
"""

import sqlite3
import json
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from collections import deque
import requests
import os

from phone_controller import PhoneController

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SensorDataCollector:
    """
    Continuous sensor data collection system
    """

    def __init__(
        self,
        controller: PhoneController,
        db_path: str = "sensor_data.db",
        collection_interval: int = 10,
        buffer_size: int = 1000
    ):
        """
        Initialize data collector

        Args:
            controller: PhoneController instance
            db_path: SQLite database path
            collection_interval: Collection interval in seconds
            buffer_size: In-memory buffer size
        """
        self.controller = controller
        self.db_path = db_path
        self.collection_interval = collection_interval
        self.buffer_size = buffer_size

        self.running = False
        self.collection_thread: Optional[threading.Thread] = None
        self.callbacks: List[Callable] = []

        # In-memory buffer for real-time data
        self.buffer = {
            sensor: deque(maxlen=buffer_size)
            for sensor in [
                'accelerometer', 'gyroscope', 'light', 'pressure',
                'proximity', 'magnetic', 'battery'
            ]
        }

        # Initialize database
        self._init_database()

        logger.info(f"SensorDataCollector initialized (interval={collection_interval}s)")

    def _init_database(self):
        """Initialize SQLite database"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = self.conn.cursor()

        # Main sensor readings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                sensor_type TEXT NOT NULL,
                value REAL,
                values_json JSON,
                raw_output TEXT,
                source TEXT
            )
        ''')

        # Create indexes for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_sensor_timestamp
            ON sensor_readings(timestamp, sensor_type)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_sensor_type
            ON sensor_readings(sensor_type)
        ''')

        # Battery readings table (optimized)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS battery_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                percentage INTEGER,
                status TEXT,
                health TEXT,
                temperature REAL,
                plugged TEXT
            )
        ''')

        # Location readings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS location_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                latitude REAL,
                longitude REAL,
                accuracy REAL,
                altitude REAL,
                bearing REAL,
                speed REAL,
                provider TEXT
            )
        ''')

        # Events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT,
                event_data JSON,
                description TEXT
            )
        ''')

        # Statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE UNIQUE,
                sensor_type TEXT,
                avg_value REAL,
                min_value REAL,
                max_value REAL,
                count INTEGER
            )
        ''')

        self.conn.commit()
        logger.info(f"Database initialized: {self.db_path}")

    def add_callback(self, callback: Callable):
        """Add callback function to be called on new data"""
        self.callbacks.append(callback)

    def start(self, sensors: Optional[List[str]] = None):
        """
        Start data collection

        Args:
            sensors: List of sensors to collect (None = all)
        """
        if self.running:
            logger.warning("Collection already running")
            return

        self.running = True
        self.sensors = sensors or [
            'accelerometer', 'gyroscope', 'light', 'pressure',
            'proximity', 'magnetic', 'battery'
        ]

        self.collection_thread = threading.Thread(
            target=self._collection_loop,
            daemon=True
        )
        self.collection_thread.start()

        logger.info(f"Data collection started: {self.sensors}")

    def stop(self):
        """Stop data collection"""
        self.running = False
        if self.collection_thread:
            self.collection_thread.join(timeout=5)
        logger.info("Data collection stopped")

    def _collection_loop(self):
        """Main collection loop (runs in thread)"""
        logger.info("Collection loop started")

        while self.running:
            try:
                for sensor in self.sensors:
                    if not self.running:
                        break

                    self._collect_sensor(sensor)
                    time.sleep(0.5)  # Small delay between sensors

                # Wait for next cycle
                time.sleep(self.collection_interval)

            except Exception as e:
                logger.error(f"Collection error: {e}")
                time.sleep(self.collection_interval)

        logger.info("Collection loop ended")

    def _collect_sensor(self, sensor_type: str):
        """Collect reading from single sensor"""
        try:
            if sensor_type == 'battery':
                data = self.controller.get_battery()
                if data:
                    self._store_battery(data)
                    self.buffer['battery'].append({
                        'timestamp': datetime.now().isoformat(),
                        'data': data
                    })

            elif sensor_type == 'location':
                data = self.controller.get_location(use_last=True)
                if data:
                    self._store_location(data)

            else:
                result = self.controller.get_sensor_data(sensor_type, 1)

                if result.get('status') == 'success':
                    data_list = result.get('data', [])

                    if data_list:
                        data = data_list[0]
                        values = data.get('values', [])

                        # Store in database
                        self._store_reading(sensor_type, values, result)

                        # Add to buffer
                        self.buffer[sensor_type].append({
                            'timestamp': datetime.now().isoformat(),
                            'values': values
                        })

                        # Call callbacks
                        for callback in self.callbacks:
                            try:
                                callback(sensor_type, values)
                            except Exception as e:
                                logger.error(f"Callback error: {e}")

        except Exception as e:
            logger.error(f"Failed to collect {sensor_type}: {e}")

    def _store_reading(self, sensor_type: str, values: List, raw_result: Dict):
        """Store sensor reading in database"""
        cursor = self.conn.cursor()

        # Use first value for single-value sensors
        value = values[0] if values else None

        cursor.execute(
            '''INSERT INTO sensor_readings
               (sensor_type, value, values_json, raw_output, source)
               VALUES (?, ?, ?, ?, ?)''',
            (
                sensor_type,
                value,
                json.dumps(values),
                raw_result.get('raw_output'),
                'termux_api'
            )
        )

        self.conn.commit()

    def _store_battery(self, battery_data: Dict):
        """Store battery reading"""
        cursor = self.conn.cursor()

        cursor.execute(
            '''INSERT INTO battery_readings
               (percentage, status, health, temperature, plugged)
               VALUES (?, ?, ?, ?, ?)''',
            (
                battery_data.get('percentage'),
                battery_data.get('status'),
                battery_data.get('health'),
                battery_data.get('temperature'),
                battery_data.get('plugged')
            )
        )

        self.conn.commit()

    def _store_location(self, location_data: Dict):
        """Store location reading"""
        cursor = self.conn.cursor()

        cursor.execute(
            '''INSERT INTO location_readings
               (latitude, longitude, accuracy, altitude, bearing, speed, provider)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (
                location_data.get('latitude'),
                location_data.get('longitude'),
                location_data.get('accuracy'),
                location_data.get('altitude'),
                location_data.get('bearing'),
                location_data.get('speed'),
                location_data.get('provider')
            )
        )

        self.conn.commit()

    def log_event(self, event_type: str, description: str, data: Optional[Dict] = None):
        """Log an event"""
        cursor = self.conn.cursor()

        cursor.execute(
            '''INSERT INTO events (event_type, description, event_data)
               VALUES (?, ?, ?)''',
            (event_type, description, json.dumps(data or {}))
        )

        self.conn.commit()
        logger.info(f"Event logged: {event_type} - {description}")

    # ==================== QUERY METHODS ====================

    def get_latest_readings(self, sensor_type: str, limit: int = 10) -> List[Dict]:
        """Get latest readings for sensor"""
        cursor = self.conn.cursor()

        cursor.execute(
            '''SELECT timestamp, value, values_json
               FROM sensor_readings
               WHERE sensor_type = ?
               ORDER BY timestamp DESC
               LIMIT ?''',
            (sensor_type, limit)
        )

        rows = cursor.fetchall()

        return [
            {
                'timestamp': row[0],
                'value': row[1],
                'values': json.loads(row[2]) if row[2] else []
            }
            for row in rows
        ]

    def get_readings_by_timerange(
        self,
        sensor_type: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[Dict]:
        """Get readings within time range"""
        cursor = self.conn.cursor()

        cursor.execute(
            '''SELECT timestamp, value, values_json
               FROM sensor_readings
               WHERE sensor_type = ?
               AND timestamp BETWEEN ? AND ?
               ORDER BY timestamp ASC''',
            (sensor_type, start_time, end_time)
        )

        rows = cursor.fetchall()

        return [
            {
                'timestamp': row[0],
                'value': row[1],
                'values': json.loads(row[2]) if row[2] else []
            }
            for row in rows
        ]

    def get_statistics(
        self,
        sensor_type: str,
        hours: int = 24
    ) -> Optional[Dict]:
        """Get statistics for sensor"""
        cursor = self.conn.cursor()

        start_time = datetime.now() - timedelta(hours=hours)

        cursor.execute(
            '''SELECT
                AVG(value) as avg_value,
                MIN(value) as min_value,
                MAX(value) as max_value,
                COUNT(*) as count
               FROM sensor_readings
               WHERE sensor_type = ?
               AND timestamp > ?''',
            (sensor_type, start_time)
        )

        row = cursor.fetchone()

        if row and row[0]:
            return {
                'sensor': sensor_type,
                'period_hours': hours,
                'avg': row[0],
                'min': row[1],
                'max': row[2],
                'count': row[3]
            }

        return None

    def get_battery_history(self, hours: int = 24) -> List[Dict]:
        """Get battery history"""
        cursor = self.conn.cursor()

        start_time = datetime.now() - timedelta(hours=hours)

        cursor.execute(
            '''SELECT timestamp, percentage, status, temperature
               FROM battery_readings
               WHERE timestamp > ?
               ORDER BY timestamp ASC''',
            (start_time,)
        )

        rows = cursor.fetchall()

        return [
            {
                'timestamp': row[0],
                'percentage': row[1],
                'status': row[2],
                'temperature': row[3]
            }
            for row in rows
        ]

    def get_location_history(self, hours: int = 24) -> List[Dict]:
        """Get location history"""
        cursor = self.conn.cursor()

        start_time = datetime.now() - timedelta(hours=hours)

        cursor.execute(
            '''SELECT timestamp, latitude, longitude, accuracy
               FROM location_readings
               WHERE timestamp > ?
               ORDER BY timestamp ASC''',
            (start_time,)
        )

        rows = cursor.fetchall()

        return [
            {
                'timestamp': row[0],
                'latitude': row[1],
                'longitude': row[2],
                'accuracy': row[3]
            }
            for row in rows
        ]

    def get_events(
        self,
        event_type: Optional[str] = None,
        hours: int = 24
    ) -> List[Dict]:
        """Get events"""
        cursor = self.conn.cursor()

        start_time = datetime.now() - timedelta(hours=hours)

        if event_type:
            cursor.execute(
                '''SELECT timestamp, event_type, description, event_data
                   FROM events
                   WHERE event_type = ?
                   AND timestamp > ?
                   ORDER BY timestamp DESC''',
                (event_type, start_time)
            )
        else:
            cursor.execute(
                '''SELECT timestamp, event_type, description, event_data
                   FROM events
                   WHERE timestamp > ?
                   ORDER BY timestamp DESC''',
                (start_time,)
            )

        rows = cursor.fetchall()

        return [
            {
                'timestamp': row[0],
                'type': row[1],
                'description': row[2],
                'data': json.loads(row[3]) if row[3] else {}
            }
            for row in rows
        ]

    # ==================== REAL-TIME DATA ====================

    def get_latest_buffer_data(self, sensor_type: str, count: int = 10) -> List[Dict]:
        """Get latest data from in-memory buffer"""
        if sensor_type in self.buffer:
            return list(self.buffer[sensor_type])[-count:]
        return []

    def export_to_csv(
        self,
        sensor_type: str,
        start_time: datetime,
        end_time: datetime,
        filename: str
    ):
        """Export readings to CSV file"""
        import csv

        data = self.get_readings_by_timerange(sensor_type, start_time, end_time)

        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'value', 'values'])

            for row in data:
                values_str = json.dumps(row['values'])
                writer.writerow([row['timestamp'], row['value'], values_str])

        logger.info(f"Exported {len(data)} readings to {filename}")

    # ==================== MAINTENANCE ====================

    def cleanup_old_data(self, days: int = 30):
        """Remove data older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)

        cursor = self.conn.cursor()

        # Clean sensor readings
        cursor.execute(
            'DELETE FROM sensor_readings WHERE timestamp < ?',
            (cutoff_date,)
        )
        sensor_deleted = cursor.rowcount

        # Clean battery readings
        cursor.execute(
            'DELETE FROM battery_readings WHERE timestamp < ?',
            (cutoff_date,)
        )
        battery_deleted = cursor.rowcount

        # Clean location readings
        cursor.execute(
            'DELETE FROM location_readings WHERE timestamp < ?',
            (cutoff_date,)
        )
        location_deleted = cursor.rowcount

        # Clean events
        cursor.execute(
            'DELETE FROM events WHERE timestamp < ?',
            (cutoff_date,)
        )
        events_deleted = cursor.rowcount

        self.conn.commit()

        logger.info(
            f"Cleanup completed: {sensor_deleted} sensor readings, "
            f"{battery_deleted} battery, {location_deleted} location, "
            f"{events_deleted} events"
        )

    def get_database_size(self) -> Dict[str, int]:
        """Get database statistics"""
        cursor = self.conn.cursor()

        stats = {}

        # Count records in each table
        for table in ['sensor_readings', 'battery_readings', 'location_readings', 'events']:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            stats[table] = cursor.fetchone()[0]

        # Get database file size
        if os.path.exists(self.db_path):
            stats['file_size_mb'] = os.path.getsize(self.db_path) / (1024 * 1024)

        return stats


# ==================== CONVENIENCE FUNCTIONS ====================

def start_collector(
    controller: PhoneController,
    sensors: Optional[List[str]] = None,
    interval: int = 10,
    db_path: str = "sensor_data.db"
) -> SensorDataCollector:
    """
    Factory function to create and start data collector

    Args:
        controller: PhoneController instance
        sensors: List of sensors to collect
        interval: Collection interval in seconds
        db_path: Database path

    Returns:
        Running SensorDataCollector instance
    """
    collector = SensorDataCollector(
        controller=controller,
        db_path=db_path,
        collection_interval=interval
    )

    collector.start(sensors)

    return collector


if __name__ == "__main__":
    # Example usage
    controller = PhoneController()

    # Create collector
    collector = SensorDataCollector(
        controller=controller,
        collection_interval=5
    )

    # Add callback for real-time processing
    def on_new_data(sensor_type, values):
        print(f"{datetime.now()}: {sensor_type} = {values}")

    collector.add_callback(on_new_data)

    # Start collection
    collector.start(['accelerometer', 'light', 'battery'])

    try:
        print("Collecting data... Press Ctrl+C to stop")
        while True:
            time.sleep(1)

            # Print statistics every 30 seconds
            if int(time.time()) % 30 == 0:
                stats = collector.get_statistics('accelerometer', 1)
                if stats:
                    print(f"\nStats: {stats}\n")

    except KeyboardInterrupt:
        print("\nStopping collection...")
        collector.stop()

        # Print database stats
        db_stats = collector.get_database_size()
        print(f"\nDatabase stats: {db_stats}")
