# 手机自主化控制系统 (Mobile Autonomous Control System)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Android](https://img.shields.io/badge/Android-5.0%2B-lightgrey)](https://www.android.com/)

完整的Android手机自主化控制系统，支持传感器数据采集、硬件控制、AI自主决策和Web可视化。无需Root权限，基于Termux实现。

## ✨ 特性

- 🎯 **无需Root** - 基于Termux:API实现完整硬件访问
- 🤖 **AI自主化** - 集成AutoGLM实现智能决策和闭环控制
- 📊 **实时数据采集** - 支持多种传感器的持续采集和存储
- 🌐 **Web可视化** - 实时仪表板显示传感器数据
- 🔄 **自动化脚本** - 一键启动所有组件
- 📱 **摄像头控制** - 拍照、录像功能
- 📍 **GPS定位** - 实时位置追踪
- 🔊 **语音合成** - TTS语音反馈

## 📋 目录

- [系统架构](#系统架构)
- [快速开始](#快速开始)
- [功能模块](#功能模块)
- [API文档](#api文档)
- [部署指南](#部署指南)
- [使用示例](#使用示例)
- [故障排除](#故障排除)

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────┐
│                    PC/服务器端                       │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ Web Dashboard│  │Data Collector│  │AutoGLM    │ │
│  │  (Flask)     │  │ (SQLite)      │  │Agent      │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
└─────────┬──────────────────┬─────────────────────┘
          │ HTTP             │ Python API
          │                  │
┌─────────┼──────────────────┼─────────────────────┐
│         │     Android Device (Honor 7)            │
│         ▼                  ▼                      │
│  ┌──────────────┐  ┌──────────────┐              │
│  │Termux HTTP   │  │Termux:API    │              │
│  │Server v3.0   │  │Hardware Layer │              │
│  │  Port 9999   │  │              │              │
│  └──────────────┘  └──────────────┘              │
│         │                  │                      │
│         ▼                  ▼                      │
│  ┌──────────────────────────────────┐            │
│  │  Sensors | Camera | Audio | GPS      │            │
│  └──────────────────────────────────┘            │
└─────────────────────────────────────────────────────┘
```

## 🚀 快速开始

### 前置要求

- Android 5.0+ 设备
- USB数据线
- Python 3.10+
- ADB工具

### 安装步骤

#### 1. 手机端（Termux）

```bash
# 安装Termux和Termux:API
# 从F-Droid或GitHub下载APK

# 启动传感器服务器
cd /sdcard
python enhanced_sensor_server.py
```

#### 2. PC端

```bash
# 克隆仓库
git clone https://github.com/yourusername/mobile-autonomous-control.git
cd mobile-autonomous-control

# 安装依赖
pip install -r requirements.txt

# 设置端口转发
adb forward tcp:9999 tcp:9999

# 一键启动
python go.py
# 或双击运行 SYSTEM_START.bat
```

#### 3. 访问仪表板

```
http://localhost:5000
```

## 📦 功能模块

### 1. 增强版传感器服务器

**文件:** `enhanced_sensor_server.py`

**功能:**
- HTTP API服务（端口9999）
- 支持70+硬件接口
- 多线程并发请求

**API端点:**
```
系统类:
- GET  /health              # 健康检查
- GET  /sensors            # 列出传感器
- GET  /sensor/<type>      # 读取传感器

硬件控制:
- POST /camera/photo       # 拍照
- POST /audio/record       # 录音
- GET  /location           # GPS定位
- GET  /battery            # 电池状态
- GET  /tts                # 语音合成
```

### 2. Python硬件控制库

**文件:** `phone_controller.py`

**功能:**
- 完整的硬件控制封装
- 传感器数据读取
- ADB自动化操作

**示例:**
```python
from phone_controller import PhoneController

controller = PhoneController()

# 读取传感器
accel = controller.get_accelerometer()
battery = controller.get_battery()

# 硬件控制
controller.take_photo()
controller.speak("Hello")

# ADB控制
controller.tap(500, 500)
controller.input_text("Hello")
```

### 3. AI自主化Agent

**文件:** `autonomous_agent.py`

**功能:**
- 感知→决策→执行→反馈闭环
- 集成AutoGLM智能决策
- 预设监控Agent

**工作流程:**
```python
from autonomous_agent import AutonomousAgent

agent = AutonomousAgent(controller, api_key="YOUR_KEY")

# 运行自主化循环
agent.run_autonomous_cycle(
    task="监控环境变化并拍照记录",
    cycles=5,
    cycle_delay=10
)
```

### 4. 数据采集系统

**文件:** `data_collector.py`

**功能:**
- SQLite持续存储
- 传感器数据采集
- 数据导出功能

**示例:**
```python
from data_collector import SensorDataCollector

collector = SensorDataCollector(controller, collection_interval=10)
collector.start(['accelerometer', 'light', 'battery'])

# 查询统计
stats = collector.get_statistics('accelerometer', hours=24)

# 导出数据
collector.export_to_csv(...)
```

### 5. Web可视化仪表板

**文件:** `dashboard.py` + `templates/dashboard.html`

**功能:**
- 实时数据展示
- Chart.js图表
- WebSocket更新
- 响应式设计

**访问:** http://localhost:5000

## 📖 API文档

### 基础端点

#### 健康检查
```http
GET /health
```

响应:
```json
{
  "status": "healthy",
  "service": "enhanced-sensor-server",
  "version": "3.0"
}
```

#### 传感器列表
```http
GET /sensors
```

#### 读取传感器
```http
GET /sensor/{type}?limit=1
```

支持的传感器:
- accelerometer - 加速度计
- gyroscope - 陀螺仪
- light - 光线
- pressure - 气压
- proximity - 距离
- magnetic - 磁场
- 等等...

#### 电池状态
```http
GET /battery
```

#### 拍照
```http
POST /camera/photo?camera=0
```

#### 录音
```http
POST /audio/record?duration=5
```

#### GPS定位
```http
GET /location?last=true
```

#### 语音合成
```http
GET /tts?text=Hello%20World&rate=1.0
```

## 🔧 部署指南

### 完整部署流程

#### 步骤1: 准备手机环境

```bash
# 1. 安装Termux (从F-Droid)
# 2. 安装Termux:API
# 3. 授予存储权限
termux-setup-storage

# 4. 安装Python
pkg update
pkg install python
```

#### 步骤2: 部署传感器服务器

```bash
# 将enhanced_sensor_server.py推送到手机
adb push enhanced_sensor_server.py /sdcard/

# 在Termux中启动
cd /sdcard
python enhanced_sensor_server.py
```

#### 步骤3: 配置PC环境

```bash
# 1. 安装Python依赖
pip install requests flask flask-socketio

# 2. 设置ADB
adb forward tcp:9999 tcp:9999

# 3. 测试连接
curl http://127.0.0.1:9999/health
```

#### 步骤4: 启动组件

```bash
# 方法1: 使用启动脚本
python go.py

# 方法2: 手动启动
python dashboard.py --port 5000
python data_collector.py
```

## 💡 使用示例

### 示例1: 简单传感器读取

```python
from phone_controller import PhoneController

controller = PhoneController()

# 读取加速度计
accel = controller.get_accelerometer()
print(f"加速度: X={accel[0]}, Y={accel[1]}, Z={accel[2]}")

# 读取电池
battery = controller.get_battery()
print(f"电量: {battery['percentage']}%")
```

### 示例2: 拍照并下载

```python
from phone_controller import PhoneController

controller = PhoneController()

# 拍照
result = controller.take_photo()
filename = result['filename']

# 下载到本地
controller.download_photo(filename, f"./{filename}")
print(f"照片已保存: {filename}")
```

### 示例3: 持续数据采集

```python
from phone_controller import PhoneController
from data_collector import SensorDataCollector
import time

controller = PhoneController()
collector = SensorDataCollector(controller, collection_interval=10)

# 启动采集
collector.start(['accelerometer', 'light', 'battery'])

# 运行1小时
time.sleep(3600)

# 停止采集
collector.stop()

# 查看统计
stats = collector.get_database_size()
print(f"已采集: {stats}")
```

### 示例4: AI自主化监控

```python
from autonomous_agent import SurveillanceAgent

controller = PhoneController()
agent = SurveillanceAgent(controller, api_key="YOUR_KEY")

# 运行监控循环
agent.run_surveillance_cycle()
```

## 🛠️ 故障排除

### ADB无法连接

```bash
# 检查设备
adb devices

# 重启ADB
adb kill-server
adb start-server

# 撤销授权重新连接
```

### 传感器API无响应

```bash
# 检查端口转发
adb forward tcp:9999 tcp:9999

# 测试API
curl http://127.0.0.1:9999/health

# 检查Termux中服务器是否运行
```

### Flask依赖缺失

```bash
pip install flask flask-socketio requests
```

### 数据库错误

```python
# 删除旧数据库重新初始化
import os
os.remove("sensor_data.db")
```

## 📊 支持的设备

### 已测试设备

| 设备型号 | Android版本 | 状态 |
|----------|------------|------|
| 荣耀7 PLK-AL10 | 5.0.2 | ✅ 完全支持 |

### 理论兼容

- Android 5.0+ (API 21+)
- 已安装Termux
- 已安装Termux:API

## 📝 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📧 联系方式

- 项目主页: [GitHub Repository](https://github.com/yourusername/mobile-autonomous-control)
- 问题反馈: [Issues](https://github.com/yourusername/mobile-autonomous-control/issues)

## 🙏 致谢

- [Termux](https://termux.com/) - 强大的Android终端模拟器
- [AutoGLM](https://github.com/zai-org/Open-AutoGLM) - AI自动化框架
- [Flask](https://flask.palletsprojects.com/) - Python Web框架

---

**项目状态:** ✅ 生产就绪
**最后更新:** 2026-03-08
**维护者:** Claude Code
