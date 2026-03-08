# 手机自主化控制系统 - 完整部署指南

**版本：** 1.0
**最后更新：** 2026-03-08
**适用设备：** 荣耀7 (PLK-AL10) 或其他Android设备

---

## 目录

1. [系统概述](#系统概述)
2. [文件清单](#文件清单)
3. [快速开始](#快速开始)
4. [模块详解](#模块详解)
5. [使用示例](#使用示例)
6. [API参考](#api参考)
7. [故障排除](#故障排除)

---

## 系统概述

### 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         PC/服务器端                           │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐     │
│  │   Dashboard  │   │ Data Collector│  │  AutoGLM     │     │
│  │   (Flask)    │   │ (SQLite)      │  │  Agent       │     │
│  └──────────────┘   └──────────────┘   └──────────────┘     │
└─────────┬──────────────────┬──────────────────┬──────────────┘
          │ HTTP             │ Python API       │ ADB
          │                  │                  │
┌─────────┼──────────────────┼──────────────────┼──────────────┐
│         │         Android Device (荣耀7)      │              │
│         ▼                  ▼                  ▼              │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐     │
│  │   Browser    │   │Termux HTTP   │   │Termux:API    │     │
│  │   Dashboard  │   │Server v3.0   │   │Hardware Layer │     │
│  │              │   │   Port 9999  │   │              │     │
│  └──────────────┘   └──────────────┘   └──────────────┘     │
│                           │                  │              │
│                           ▼                  ▼              │
│                    ┌──────────────┐   ┌──────────────┐       │
│                    │ Sensors Data │   │  Hardware    │       │
│                    │  Collection  │   │  Control     │       │
│                    └──────────────┘   └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### 核心功能

| 功能 | 实现方式 | 状态 |
|------|----------|------|
| **传感器数据采集** | Termux:API + Python | ✅ |
| **硬件控制** | HTTP API + ADB | ✅ |
| **AI自主决策** | AutoGLM | ✅ |
| **数据存储** | SQLite | ✅ |
| **可视化仪表板** | Flask + SocketIO | ✅ |
| **实时反馈** | WebSocket | ✅ |

---

## 文件清单

### 核心脚本

```
工具脚本/
├── enhanced_sensor_server.py    # 增强版传感器HTTP服务器 (v3.0)
├── phone_controller.py          # Python硬件控制封装
├── autonomous_agent.py          # AI自主化Agent
├── data_collector.py            # 数据采集系统
├── dashboard.py                 # Web仪表板服务器
├── templates/
│   └── dashboard.html           # 仪表板HTML模板
├── simple_sensor_server.py      # 原始传感器服务器 (v2.0)
└── DEPLOYMENT_GUIDE.md          # 本文档
```

### 依赖关系

```
enhanced_sensor_server.py
    └── 独立运行 (Termux环境)

phone_controller.py
    ├── requests (HTTP客户端)
    └── subprocess (ADB调用)

autonomous_agent.py
    ├── phone_controller.py
    ├── requests (AutoGLM API)
    └── sqlite3 (记忆存储)

data_collector.py
    ├── phone_controller.py
    └── sqlite3 (数据存储)

dashboard.py
    ├── flask (Web服务器)
    ├── flask_socketio (WebSocket)
    └── sqlite3 (数据查询)
```

---

## 快速开始

### 步骤1: 准备Termux环境

```bash
# 在Termux中执行

# 1. 更新包
pkg update && pkg upgrade

# 2. 安装Python
pkg install python

# 3. 安装依赖
pip install requests flask flask-socketio

# 4. 创建工作目录
mkdir -p ~/sensor_server
cd ~/sensor_server
```

### 步骤2: 部署增强版传感器服务器

```bash
# 将 enhanced_sensor_server.py 推送到手机
adb push enhanced_sensor_server.py /sdcard/
adb push simple_sensor_server.py /sdcard/

# 在Termux中启动
cd /sdcard
python enhanced_sensor_server.py
```

**预期输出：**
```
============================================================
   Enhanced Termux Sensor HTTP Server v3.0
============================================================
✓ Server running on http://0.0.0.0:9999
✓ Upload directory: /sdcard/sensor_server
✓ Threading enabled for concurrent requests
...
```

### 步骤3: 设置ADB端口转发

```bash
# 在PC端执行
adb forward tcp:9999 tcp:9999
```

### 步骤4: 测试传感器API

```bash
# 测试健康检查
curl http://127.0.0.1:9999/health

# 测试传感器列表
curl http://127.0.0.1:9999/sensors

# 测试加速度计
curl http://127.0.0.1:9999/sensor/accelerometer

# 测试电池状态
curl http://127.0.0.1:9999/battery
```

### 步骤5: 启动数据采集

```bash
# 在PC端运行

# 创建测试脚本 test_collector.py
python3 << 'EOF'
from phone_controller import PhoneController
from data_collector import SensorDataCollector

# 创建控制器
controller = PhoneController()

# 启动数据采集
collector = SensorDataCollector(
    controller=controller,
    collection_interval=10
)

# 添加回调
def on_data(sensor_type, values):
    print(f"{sensor_type}: {values}")

collector.add_callback(on_data)

# 开始采集
collector.start(['accelerometer', 'light', 'battery'])

print("Press Ctrl+C to stop...")
try:
    import time
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    collector.stop()
    print("\nStopped")
EOF
```

### 步骤6: 启动Web仪表板

```bash
# 在PC端运行

# 安装依赖
pip install flask flask-socketio

# 启动仪表板
python dashboard.py --port 5000

# 访问 http://localhost:5000
```

---

## 模块详解

### 1. enhanced_sensor_server.py

**功能：** 增强版HTTP传感器服务器

**端口：** 9999

**支持的功能：**

| 类别 | 端点 | 方法 | 说明 |
|------|------|------|------|
| 系统 | `/health` | GET | 健康检查 |
| 系统 | `/` | GET | API文档 |
| 传感器 | `/sensors` | GET | 列出传感器 |
| 传感器 | `/sensor/<type>` | GET | 读取传感器 |
| 摄像头 | `/camera/info` | GET | 摄像头信息 |
| 摄像头 | `/camera/photo` | POST | 拍照 |
| 音频 | `/audio/record` | POST | 录音 |
| 音频 | `/audio/record/stop` | POST | 停止录音 |
| 位置 | `/location` | GET | GPS位置 |
| 电池 | `/battery` | GET | 电池状态 |
| TTS | `/tts` | GET | 语音合成 |
| SMS | `/sms/list` | GET | 短信列表 |
| SMS | `/sms/send` | POST | 发送短信 |
| 通知 | `/notification/list` | GET | 通知列表 |
| 通知 | `/notification/send` | POST | 发送通知 |
| 剪贴板 | `/clipboard` | GET/POST | 剪贴板操作 |
| 系统 | `/system/info` | GET | 系统信息 |
| 系统 | `/system/wifi` | GET | WiFi信息 |

**使用示例：**

```python
import requests

BASE_URL = "http://127.0.0.1:9999"

# 获取电池状态
response = requests.get(f"{BASE_URL}/battery")
battery = response.json()
print(f"Battery: {battery['battery']['percentage']}%")

# 拍照
response = requests.post(f"{BASE_URL}/camera/photo", params={"camera": "0"})
result = response.json()
print(f"Photo saved: {result['filename']}")

# 语音合成
requests.get(f"{BASE_URL}/tts", params={"text": "Hello World"})
```

### 2. phone_controller.py

**功能：** Python硬件控制封装

**类：** `PhoneController`

**主要方法：**

```python
controller = PhoneController(
    adb_path="adb",
    api_base="http://127.0.0.1:9999"
)

# 传感器
accel = controller.get_accelerometer()
light = controller.get_light()

# 摄像头
controller.take_photo()
photos = controller.list_photos()

# 音频
controller.record_audio(duration=5)

# 位置
location = controller.get_location()

# 电池
battery = controller.get_battery()
percentage = controller.get_battery_percentage()

# TTS
controller.speak("Hello")

# SMS
controller.send_sms("1234567890", "Test message")

# ADB控制
controller.tap(500, 500)
controller.swipe(100, 100, 500, 500)
controller.input_text("Hello")
controller.start_app("com.android.settings")

# 环境快照
snapshot = controller.get_environment_snapshot()
controller.print_status()
```

### 3. autonomous_agent.py

**功能：** AI自主化Agent

**类：** `AutonomousAgent`

**工作流程：**

```
感知环境 (perceive_environment)
    ↓
AI决策 (make_decision via AutoGLM)
    ↓
执行动作 (execute_action)
    ↓
获取反馈 (feedback)
    ↓
循环 (repeat)
```

**使用示例：**

```python
from phone_controller import PhoneController
from autonomous_agent import AutonomousAgent

# 创建Agent
controller = PhoneController()
agent = AutonomousAgent(
    controller=controller,
    api_key="YOUR_AUTOGLM_API_KEY",
    model="autoglm-phone"
)

# 运行自主化循环
agent.run_autonomous_cycle(
    task="Monitor the environment and report any changes",
    cycles=5,
    cycle_delay=10
)

# 获取报告
report = agent.generate_report()
print(report)
```

**预设Agent：**

```python
from autonomous_agent import SurveillanceAgent, EnvironmentMonitorAgent

# 安防监控Agent
surveillance = SurveillanceAgent(
    controller=controller,
    api_key=API_KEY
)
surveillance.run_surveillance_cycle()

# 环境监控Agent
monitor = EnvironmentMonitorAgent(
    controller=controller,
    api_key=API_KEY
)
monitor.run_monitoring_cycle()
```

### 4. data_collector.py

**功能：** 持续数据采集和存储

**类：** `SensorDataCollector`

**数据库表：**

- `sensor_readings` - 传感器读数
- `battery_readings` - 电池数据
- `location_readings` - 位置数据
- `events` - 事件日志
- `daily_stats` - 每日统计

**使用示例：**

```python
from phone_controller import PhoneController
from data_collector import SensorDataCollector

controller = PhoneController()

# 创建采集器
collector = SensorDataCollector(
    controller=controller,
    db_path="sensor_data.db",
    collection_interval=10
)

# 添加实时回调
def on_new_data(sensor_type, values):
    print(f"{sensor_type}: {values}")

collector.add_callback(on_new_data)

# 启动采集
collector.start(['accelerometer', 'light', 'battery'])

# 查询历史数据
stats = collector.get_statistics('accelerometer', hours=24)
print(f"Average acceleration: {stats['avg']}")

battery_history = collector.get_battery_history(hours=24)

# 导出数据
from datetime import datetime, timedelta
collector.export_to_csv(
    'accelerometer',
    datetime.now() - timedelta(hours=24),
    datetime.now(),
    'accelerometer_data.csv'
)

# 清理旧数据
collector.cleanup_old_data(days=30)

# 停止采集
collector.stop()
```

### 5. dashboard.py

**功能：** Web可视化仪表板

**启动：**

```bash
python dashboard.py --host 0.0.0.0 --port 5000
```

**访问：** http://localhost:5000

**特性：**

- 实时数据更新 (WebSocket)
- 电池历史图表
- 传感器实时显示
- GPS位置显示
- 事件日志
- 响应式设计

**API端点：**

| 端点 | 说明 |
|------|------|
| `/` | 仪表板主页 |
| `/api/health` | 健康检查 |
| `/api/dashboard` | 获取所有数据 |
| `/api/sensor/<type>/latest` | 最新传感器读数 |
| `/api/sensor/<type>/history` | 传感器历史 |
| `/api/battery` | 电池状态 |
| `/api/location/latest` | 最新位置 |
| `/api/events` | 事件列表 |

---

## 使用示例

### 示例1: 简单传感器读取

```python
from phone_controller import PhoneController

controller = PhoneController()

# 读取传感器
accel = controller.get_accelerometer()
print(f"Acceleration: X={accel[0]}, Y={accel[1]}, Z={accel[2]}")

light = controller.get_light()
print(f"Light level: {light} lux")

# 电池信息
battery = controller.get_battery()
print(f"Battery: {battery['percentage']}%")
```

### 示例2: 拍照并下载

```python
from phone_controller import PhoneController
import time

controller = PhoneController()

# 拍照
result = controller.take_photo()
filename = result['filename']
print(f"Photo taken: {filename}")

# 下载到本地
controller.download_photo(filename, f"./{filename}")
print(f"Downloaded: {filename}")
```

### 示例3: 持续数据采集

```python
from phone_controller import PhoneController
from data_collector import SensorDataCollector
import time

controller = PhoneController()
collector = SensorDataCollector(controller, collection_interval=5)

# 启动采集
collector.start(['accelerometer', 'light', 'battery'])

# 运行1小时
time.sleep(3600)

# 停止
collector.stop()

# 查看统计
stats = collector.get_database_size()
print(f"Collected {stats} readings")
```

### 示例4: 自主化监控

```python
from phone_controller import PhoneController
from autonomous_agent import AutonomousAgent

controller = PhoneController()
agent = AutonomousAgent(
    controller=controller,
    api_key="YOUR_API_KEY"
)

# 运行监控任务
agent.run_autonomous_cycle(
    task="Monitor for suspicious activity and take photos if light level changes significantly",
    cycles=0,  # 无限循环
    cycle_delay=30
)
```

### 示例5: 创建自定义任务

```python
from phone_controller import PhoneController

controller = PhoneController()

# 自定义任务：电量低时提醒
def monitor_battery():
    battery = controller.get_battery_percentage()

    if battery and battery < 20:
        controller.speak(f"Low battery: {battery}% remaining")
        controller.send_notification(
            "Battery Warning",
            f"Battery is at {battery}%"
        )

# 定时执行
import time
while True:
    monitor_battery()
    time.sleep(300)  # 每5分钟
```

---

## API参考

### enhanced_sensor_server.py API

#### GET /health

**响应：**
```json
{
  "status": "healthy",
  "service": "enhanced-sensor-server",
  "version": "3.0",
  "timestamp": "2026-03-08T10:00:00"
}
```

#### GET /sensor/{type}

**参数：**
- `type`: 传感器类型 (accelerometer, gyroscope, light等)
- `limit`: 读取次数 (默认1)

**响应：**
```json
{
  "status": "success",
  "sensor": "accelerometer",
  "data": [
    {
      "values": [0.5, 8.7, 4.3],
      "timestamp": 1234567890
    }
  ]
}
```

#### POST /camera/photo

**参数：**
- `camera`: 摄像头ID (默认"0")

**响应：**
```json
{
  "status": "success",
  "message": "Photo taken",
  "filename": "photo_1234567890.jpg",
  "path": "/sdcard/sensor_server/photo_1234567890.jpg",
  "url": "/camera/photo/photo_1234567890.jpg"
}
```

#### POST /audio/record

**参数：**
- `duration`: 录音时长（秒）
- `limit`: 是否限制时长 (true/false)

**响应：**
```json
{
  "status": "success",
  "message": "Audio recorded",
  "filename": "audio_1234567890.wav"
}
```

#### GET /location

**参数：**
- `last`: 使用最后已知位置 (true/false)

**响应：**
```json
{
  "status": "success",
  "location": {
    "latitude": 39.9042,
    "longitude": 116.4074,
    "accuracy": 10.0
  }
}
```

### phone_controller.py API

#### 类：PhoneController

**初始化：**
```python
PhoneController(
    adb_path: str = "adb",
    api_base: str = "http://127.0.0.1:9999",
    device_id: Optional[str] = None
)
```

**主要方法：**

- `health_check()` - 健康检查
- `get_sensor_data(sensor_type, limit=1)` - 获取传感器数据
- `get_accelerometer()` - 加速度计
- `get_gyroscope()` - 陀螺仪
- `get_light()` - 光线
- `take_photo(camera_id="0")` - 拍照
- `record_audio(duration=5)` - 录音
- `get_location(use_last=False)` - GPS位置
- `get_battery()` - 电池状态
- `speak(text, rate=1.0, pitch=1.0)` - 语音合成
- `send_sms(number, text)` - 发送短信
- `tap(x, y)` - 点击屏幕
- `swipe(x1, y1, x2, y2)` - 滑动
- `input_text(text)` - 输入文本
- `start_app(package_activity)` - 启动应用
- `take_screenshot(save_path)` - 截图
- `get_environment_snapshot()` - 环境快照

---

## 故障排除

### 问题1: ADB连接失败

**症状：**
```
adb devices
List of devices attached
# (空)
```

**解决方案：**
```bash
# 1. 检查USB调试
设置 → 开发者选项 → USB调试 ✓

# 2. 重启ADB
adb kill-server
adb start-server

# 3. 重新授权
# 撤销USB调试授权
# 拔掉USB，重新插入
# 勾选"始终允许" → 点击【允许】
```

### 问题2: 传感器API无响应

**症状：**
```bash
curl http://127.0.0.1:9999/health
curl: (52) Empty reply from server
```

**解决方案：**
```bash
# 1. 检查端口转发
adb forward tcp:9999 tcp:9999

# 2. 检查服务器是否运行
adb shell "ps | grep python"

# 3. 重启服务器
adb shell "killall python"
# 在Termux中重新启动
python enhanced_sensor_server.py
```

### 问题3: Termux:API命令不存在

**症状：**
```
$ termux-sensor -l
termux-sensor: command not found
```

**解决方案：**
```bash
# 1. 检查Termux:API是否安装
adb shell "pm list packages | grep termux"
# 应该看到:
# package:com.termux
# package:com.termux.api

# 2. 如果缺失，安装Termux:API
adb install termux-api-git.apk
```

### 问题4: Flask依赖缺失

**症状：**
```
ImportError: No module named 'flask'
```

**解决方案：**
```bash
pip install flask flask-socketio
```

### 问题5: 数据库锁定

**症状：**
```
sqlite3.OperationalError: database is locked
```

**解决方案：**
```python
# 使用timeout参数
conn = sqlite3.connect(db_path, check_same_thread=False, timeout=30)
```

---

## 性能优化

### 减少电池消耗

```python
# 增加采集间隔
collector = SensorDataCollector(
    controller=controller,
    collection_interval=60  # 每60秒采集一次
)

# 只采集必要的传感器
collector.start(['accelerometer', 'battery'])
```

### 减少存储空间

```python
# 定期清理旧数据
import schedule
import time

def cleanup():
    collector.cleanup_old_data(days=7)

schedule.every().day.at("02:00").do(cleanup)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### 优化采集频率

```python
# 根据传感器类型使用不同频率
collector_sensors = SensorDataCollector(
    controller=controller,
    collection_interval=1  # 高频传感器
)

collector_battery = SensorDataCollector(
    controller=controller,
    collection_interval=60  # 低频传感器
)
```

---

## 进阶功能

### 创建自定义Agent行为

```python
from autonomous_agent import AutonomousAgent, ActionType

class CustomAgent(AutonomousAgent):
    def run_custom_behavior(self):
        """自定义行为循环"""
        while self.running:
            # 收集数据
            env = self.perceive_environment()

            # 自定义决策逻辑
            light = env.get('sensors', {}).get('light')

            if light < 10:
                # 光线暗，拍照记录
                decision = {
                    "action_type": ActionType.TAKE_PHOTO.value,
                    "action_params": {},
                    "reasoning": "Low light detected"
                }
                self.execute_action(decision)

            time.sleep(60)

# 使用
agent = CustomAgent(controller, api_key)
agent.run_custom_behavior()
```

### 集成第三方服务

```python
import requests

def send_to_cloud(sensor_data):
    """发送数据到云端"""
    response = requests.post(
        "https://api.example.com/sensors",
        json=sensor_data,
        headers={"Authorization": "Bearer YOUR_TOKEN"}
    )
    return response.json()

# 添加到采集器回调
collector.add_callback(lambda s, v: send_to_cloud({s: v}))
```

---

## 总结

### 系统能力总结

| 功能 | 支持程度 | 说明 |
|------|----------|------|
| **传感器采集** | ⭐⭐⭐⭐⭐ | 11种传感器完整支持 |
| **硬件控制** | ⭐⭐⭐⭐⭐ | 摄像头、麦克风、GPS等 |
| **AI决策** | ⭐⭐⭐⭐ | AutoGLM集成 |
| **数据存储** | ⭐⭐⭐⭐⭐ | SQLite完整方案 |
| **可视化** | ⭐⭐⭐⭐⭐ | 实时Web仪表板 |
| **易用性** | ⭐⭐⭐⭐⭐ | 清晰的API封装 |
| **扩展性** | ⭐⭐⭐⭐⭐ | 模块化设计 |

### 下一步建议

1. **立即开始：** 部署传感器服务器
2. **本周完成：** 启动数据采集
3. **下周优化：** 配置自主化Agent
4. **长期目标：** 扩展更多功能

### 支持与反馈

如有问题，请查看：
- 本地测试报告文档
- 故障排除章节
- 示例代码

---

**文档版本：** 1.0
**最后更新：** 2026-03-08
**作者：** Claude Code
**许可证：** MIT
