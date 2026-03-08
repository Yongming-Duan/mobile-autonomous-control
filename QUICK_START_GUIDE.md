# 🚀 系统启动指南 - 分步骤说明

## 当前状态检测

根据测试，系统组件已就绪，但需要按正确顺序启动：

---

## 📱 步骤1: 启动手机端传感器服务器

### 在手机Termux中执行：

```bash
# 1. 进入Termux终端

# 2. 进入工作目录
cd /sdcard

# 3. 启动增强版传感器服务器
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

📋 Available endpoints:
   System: GET /, /health, /info
   Sensors: GET /sensors, /sensor/<type>
   ...
```

**保持这个终端打开！** 服务器需要持续运行。

---

## 💻 步骤2: PC端设置连接

### 打开新的命令提示符/PowerShell窗口：

```bash
# 1. 进入ADB工具目录
cd D:\工作日常\服务器搭建\荣耀手机刷机\工具软件\platform-tools

# 2. 设置端口转发
adb.exe forward tcp:9999 tcp:9999

# 3. 验证连接
adb.exe devices
# 应该看到你的设备序列号
```

---

## 🧪 步骤3: 测试连接

### 在PC端执行：

```bash
# 进入脚本目录
cd D:\工作日常\服务器搭建\荣耀手机刷机\工具脚本

# 测试健康检查
curl http://127.0.0.1:9999/health
```

**预期响应：**
```json
{
  "status": "healthy",
  "service": "enhanced-sensor-server",
  "version": "3.0",
  "timestamp": "2026-03-08T..."
}
```

---

## 🎯 步骤4: 选择启动模式

### 选项A: 快速测试所有功能

```bash
# 运行快速测试脚本
python quick_start.py
```

这会测试：
- ✅ 传感器读取
- ✅ 摄像头拍照
- ✅ GPS定位
- ✅ 电池状态
- ✅ 语音合成
- ✅ 数据采集

### 选项B: 启动Web仪表板

```bash
# 启动仪表板服务器
python dashboard.py --port 5000
```

然后访问：**http://localhost:5000**

### 选项C: 启动数据采集

```bash
# 启动数据采集系统
python data_collector.py
```

### 选项D: 运行AI自主化Agent

```python
from phone_controller import PhoneController
from autonomous_agent import AutonomousAgent

controller = PhoneController()
agent = AutonomousAgent(
    controller=controller,
    api_key="YOUR_AUTOGLM_API_KEY"
)

# 运行监控任务
agent.run_autonomous_cycle(
    task="监控环境变化并拍照记录",
    cycles=5,
    cycle_delay=10
)
```

---

## 📊 步骤5: 查看结果

### Web仪表板 (推荐)

访问：http://localhost:5000

你可以看到：
- 🔋 电池状态实时显示
- 💡 光线传感器数据
- 📱 加速度计数据
- 📍 GPS位置信息
- 📋 事件日志

### 命令行查看

```python
# 打印设备状态
from phone_controller import PhoneController

controller = PhoneController()
controller.print_status()
```

输出示例：
```
============================================================
           PHONE STATUS SNAPSHOT
============================================================
🔋 Battery: 85% (discharging)
   Temperature: 32.5°C
📍 Location: 39.9042, 116.4074
   Accuracy: 10m
💡 Light: 350.5 lux
🔊 Proximity: 5.0
📱 Accelerometer: X=0.12, Y=9.78, Z=0.45
📶 WiFi: MyNetwork (2400 MHz)
============================================================
```

---

## ❗ 常见问题

### Q: "传感器服务器未运行"

**解决方案：**
1. 确认手机Termux中 `enhanced_sensor_server.py` 正在运行
2. 检查端口转发：`adb forward tcp:9999 tcp:9999`
3. 测试连接：`curl http://127.0.0.1:9999/health`

### Q: "ADB设备未连接"

**解决方案：**
1. 检查USB线连接
2. 手机设置 → 开发者选项 → USB调试 ✓
3. 撤销USB调试授权，重新连接并授权
4. 运行：`adb devices`

### Q: "Flask模块导入错误"

**解决方案：**
```bash
pip install flask flask-socketio requests
```

### Q: "端口9999已被占用"

**解决方案：**
```bash
# Windows
netstat -ano | findstr :9999
taskkill /PID <PID号> /F

# 或修改服务器端口（在enhanced_sensor_server.py中）
```

---

## 🎉 启动成功后的下一步

### 1. 探索API

```bash
# 列出所有传感器
curl http://127.0.0.1:9999/sensors

# 读取加速度计
curl http://127.0.0.1:9999/sensor/accelerometer

# 获取电池状态
curl http://127.0.0.1:9999/battery
```

### 2. 运行示例脚本

```python
# 示例1: 持续监控电池
from phone_controller import PhoneController
import time

controller = PhoneController()

while True:
    battery = controller.get_battery_percentage()
    print(f"电量: {battery}%")

    if battery < 20:
        controller.speak(f"电量低: {battery}%")

    time.sleep(60)
```

### 3. 启动数据采集

```python
# 示例2: 采集传感器数据到数据库
from data_collector import SensorDataCollector

collector = SensorDataCollector(
    controller=controller,
    collection_interval=10
)

collector.start(['accelerometer', 'light', 'battery'])

# 运行1小时后停止
import time
time.sleep(3600)
collector.stop()
```

### 4. 部署AI监控

```python
# 示例3: 安防监控Agent
from autonomous_agent import SurveillanceAgent

agent = SurveillanceAgent(
    controller=controller,
    api_key="YOUR_API_KEY"
)

agent.run_surveillance_cycle()
```

---

## 📞 需要帮助？

### 检查清单

- [ ] 手机Termux正在运行 `enhanced_sensor_server.py`
- [ ] ADB设备已连接 (`adb devices`)
- [ ] 端口转发已设置 (`adb forward tcp:9999 tcp:9999`)
- [ ] 可以访问 http://127.0.0.1:9999/health
- [ ] Python依赖已安装 (`pip install flask flask-socketio requests`)

### 调试命令

```bash
# 1. 检查ADB连接
adb devices

# 2. 检查端口转发
adb forward --list

# 3. 测试API
curl http://127.0.0.1:9999/health

# 4. 查看服务器日志
# (在手机Termux中查看输出)

# 5. 重启ADB
adb kill-server
adb start-server
```

---

## 🎯 快速命令参考

```bash
# === 手机端 (Termux) ===
cd /sdcard
python enhanced_sensor_server.py

# === PC端 (命令提示符) ===

# ADB连接
cd D:\工作日常\服务器搭建\荣耀手机刷机\工具软件\platform-tools
adb.exe devices
adb.exe forward tcp:9999 tcp:9999

# 测试连接
curl http://127.0.0.1:9999/health

# 启动组件
cd D:\工作日常\服务器搭建\荣耀手机刷机\工具脚本
python quick_start.py           # 快速测试
python dashboard.py             # Web仪表板
python data_collector.py        # 数据采集
```

---

**准备好了吗？让我们开始！**

1. 📱 先在手机Termux中启动 `enhanced_sensor_server.py`
2. 💻 然后在PC上运行上述命令
3. 🌐 访问 http://localhost:5000 查看仪表板

**祝你成功！** 🎉
