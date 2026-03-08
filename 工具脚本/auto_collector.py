
import sys
import time
sys.path.insert(0, r'D:\工作日常\服务器搭建\荣耀手机刷机\工具脚本')

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
    print("\n[COLLECTOR] Stopping...")
    collector.stop()
    print("[COLLECTOR] Stopped")
