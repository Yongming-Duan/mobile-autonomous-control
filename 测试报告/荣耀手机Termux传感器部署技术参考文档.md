# 荣耀手机 Termux 传感器部署技术参考文档

**文档版本:** 1.0
**创建日期:** 2026-03-07
**目标设备:** 荣耀 7 (Android 5.0.2, API 21)
**项目代号:** Glory-Sensor-Termux

---

## 📑 目录

1. [项目概述](#1-项目概述)
2. [系统环境](#2-系统环境)
3. [技术架构](#3-技术架构)
4. [部署流程详解](#4-部署流程详解)
5. [关键技术方案](#5-关键技术方案)
6. [工具清单](#6-工具清单)
7. [API 接口文档](#7-api-接口文档)
8. [故障排除指南](#8-故障排除指南)
9. [性能优化建议](#9-性能优化建议)
10. [未来扩展方向](#10-未来扩展方向)

---

## 1. 项目概述

### 1.1 项目目标

在旧版 Android 设备（Android 5.0.2）上部署 Termux 环境，并实现传感器数据的 HTTP API 服务，为后续 AI 应用和自动化系统提供硬件访问能力。

### 1.2 核心成果

| 功能模块 | 状态 | 技术方案 |
|---------|------|---------|
| Termux v0.79 | ✅ 已部署 | 离线 bootstrap + Legacy 源配置 |
| Termux:API | ✅ 已部署 | 手动提取 deb 包二进制文件 |
| 传感器访问 | ✅ 可用 | termux-sensor 命令行工具 |
| HTTP API 服务 | ✅ 运行中 | Python http.server (端口 9999) |
| AutoGLM 集成 | ✅ 可用 | ADB 自动化操作 |

### 1.3 技术亮点

- **绕过版本限制** - 解决 Termux v0.79 在 Android 5.0 上的兼容性问题
- **创新解压方案** - 使用 Python 自定义 AR 解析器处理 deb 包
- **混合部署方式** - 结合 ADB、AutoGLM、手动操作的优势
- **无框架 HTTP 服务** - 使用 Python 内置库，避免 Flask 依赖问题

---

## 2. 系统环境

### 2.1 硬件配置

```
设备型号: 荣耀 7 (PLK-UL00)
CPU: Kirin 930 (8核)
RAM: 3GB
存储: 16GB (可用约 8GB)
屏幕: 5.2英寸 FHD (1920x1080)
```

### 2.2 软件环境

```
Android 版本: 5.0.2 (API Level 21)
内核版本: 3.10.0-g8ffefc7
Termux 版本: v0.79 (legacy)
Python 版本: 3.10.13
pip 版本: 23.3.1
```

### 2.3 网络配置

```
ADB 端口转发: tcp:9999 -> tcp:9999
HTTP 服务地址: http://127.0.0.1:9999 (本地)
                http://0.0.0.0:9999 (局域网)
```

### 2.4 目录结构

```
/data/data/com.termux/files/
├── usr/
│   ├── bin/              # 用户命令
│   │   ├── termux-*      # API 命令 (54个)
│   │   ├── python        # Python 3.10.13
│   │   └── pip           # pip 23.3.1
│   ├── libexec/
│   │   ├── termux-api    # API 执行器
│   │   ├── termux-api-broadcast
│   │   └── termux-callback
│   └── include/
│       └── termux-api.h  # C 头文件
└── etc/                  # 配置文件

/sdcard/
├── termux-bin/           # API 二进制备份
├── termux-libexec/       # 库文件备份
├── sensor_server.py      # HTTP 服务器
├── start_server.sh       # 启动脚本
└── server.log            # 服务器日志
```

---

## 3. 技术架构

### 3.1 系统分层架构

```
┌─────────────────────────────────────────────┐
│           应用层 (HTTP API)                 │
│  /sensor /tts /battery /health 等          │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│         Python HTTP Server (9999)          │
│  http.server + subprocess + json            │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│       Termux API 命令行工具 (54个)          │
│  termux-sensor, termux-tts-speak, etc.     │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│        Termux:API Android 应用             │
│  (com.termux.api) - 权限 + Intent          │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│         Android 硬件抽象层                  │
│  SensorManager, TextToSpeech, etc.         │
└─────────────────────────────────────────────┘
```

### 3.2 数据流向

```
外部请求 → ADB端口转发 → HTTP Server → 命令执行 → 结果返回
                                              ↓
                                    Termux:API App
                                              ↓
                                    Android HAL
                                              ↓
                                    硬件传感器
```

### 3.3 通信协议

**HTTP/1.1**
- 编码: UTF-8
- 数据格式: JSON
- CORS: 允许所有来源 (`Access-Control-Allow-Origin: *`)

---

## 4. 部署流程详解

### 4.1 Termux 基础环境部署

#### 步骤 1: 安装 Termux v0.79

```bash
# Windows 端 (PC)
adb install APK安装包/termux-v79-offline.apk
```

**关键点:**
- 使用离线 bootstrap 版本，避免网络问题
- Android 5.0 不兼容最新版 Termux (v118+)

#### 步骤 2: 配置 Legacy 源

```bash
# Termux 端
mkdir -p $PREFIX/etc/apt/sources.list.d
echo "deb https://archive.org/download/termux-repositories-legacy stable main" > \
  $PREFIX/etc/apt/sources.list.d/legacy.list

pkg update
```

### 4.2 Termux:API 部署方案

#### 方案 A: 官方方法 (失败)

```bash
# 尝试使用 apt 安装
pkg install termux-api
# 错误: E: Unable to locate package termux-api
```

**失败原因:**
- Legacy 源中无 termux-api 包
- v0.79 对应的源已关闭

#### 方案 B: 手动提取 (成功)

**4.2.1 下载 deb 包**

```bash
# Windows 端
curl -L -o termux-api_0.59.1-1_aarch64.deb \
  "https://packages.termux.dev/apt/termux-main/pool/main/t/termux-api/termux-api_0.59.1-1_aarch64.deb"
```

**4.2.2 解压 deb 包 (Python AR 解析器)**

```python
# extract_deb_ar.py
import struct, tarfile, lzma, gzip

def extract_ar_archive(ar_file, extract_to='.'):
    with open(ar_file, 'rb') as f:
        magic = f.read(8)
        if magic != b'!<arch>\n':
            return False

        while True:
            header = f.read(60)
            if len(header) < 60:
                break

            name = header[:16].decode('ascii').strip()
            size = int(header[48:58].decode('ascii').strip())

            # 读取结束标记
            f.read(2)

            # 读取文件数据
            data = f.read(size)

            # 对齐到偶数字节
            if size % 2 == 1:
                f.read(1)

            # 处理 data.tar.xz
            if name.startswith('data.tar'):
                tar_content = lzma.decompress(data)
                with tarfile.open(fileobj=io.BytesIO(tar_content)) as tar:
                    tar.extractall(path=extract_to)
```

**4.2.3 推送文件到设备**

```bash
# Windows 端
adb push "termux-api-extracted/data/data/com.termux/files/usr/bin/." \
  //sdcard//termux-bin//
adb push "termux-api-extracted/data/data/com.termux/files/usr/libexec/." \
  //sdcard//termux-libexec//
```

**4.2.4 安装脚本 (install_termux_api_v2.sh)**

```bash
#!/usr/bin/env sh
# Termux API Installation Script v2

echo "Installing termux-api binaries..."
cd /sdcard

# 复制二进制文件
if [ -d "termux-bin" ]; then
    cp termux-bin/termux-* "$PREFIX/bin/"
    chmod +x "$PREFIX/bin/termux-"*
    echo "✓ Binaries installed"
fi

# 复制库文件
if [ -d "termux-libexec" ]; then
    mkdir -p "$PREFIX/libexec"
    cp termux-libexec/termux-api* "$PREFIX/libexec/"
    chmod +x "$PREFIX/libexec/termux-"*
    echo "✓ Libexec files installed"
fi

# 验证安装
echo "Testing termux-api commands:"
for cmd in termux-api termux-camera-photo termux-microphone-record \
            termux-tts-speak termux-sensor; do
    if command -v "$cmd" >/dev/null 2>&1; then
        echo "✓ $cmd is available"
    fi
done
```

### 4.3 HTTP 服务器部署

#### 4.3.1 服务器代码 (sensor_server.py)

```python
#!/usr/bin/env python3
"""
Simple Termux Sensor HTTP Server
Using Python's built-in http.server
"""

import subprocess
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# 可用传感器映射
SENSORS = {
    'accelerometer': 'Accelerometer',
    'gyroscope': 'Gyroscope',
    'light': 'Light',
    'pressure': 'Pressure',
    # ... 更多传感器
}

class SensorHandler(BaseHTTPRequestHandler):
    def send_json(self, data, status=200):
        """发送 JSON 响应"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        """处理 GET 请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)

        try:
            if path == '/':
                self.send_json({
                    'service': 'Termux Sensor HTTP Server',
                    'version': '2.0',
                    'endpoints': {...}
                })

            elif path == '/sensors':
                # 获取传感器列表
                result = subprocess.run(
                    ['termux-sensor', '-l'],
                    capture_output=True, text=True, timeout=5
                )
                sensors_list = result.stdout.strip().split('\n')
                self.send_json({
                    'status': 'success',
                    'sensors': sensors_list,
                    'count': len(sensors_list)
                })

            elif path.startswith('/sensor/'):
                # 获取特定传感器数据
                sensor_type = path[8:]
                cmd = ['termux-sensor', '-s', SENSORS.get(sensor_type), '-n', '1']
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    self.send_json({'status': 'success', 'sensor': sensor_type, 'data': data})

            elif path == '/tts':
                # 文字转语音
                text = query.get('text', ['Hello'])[0]
                subprocess.run(['termux-tts-speak', text], capture_output=True, timeout=10)
                self.send_json({'status': 'success', 'message': f'Speaking: {text}'})

            elif path == '/battery':
                # 电池状态
                result = subprocess.run(['termux-battery-status'],
                                      capture_output=True, text=True, timeout=5)
                data = json.loads(result.stdout)
                self.send_json({'status': 'success', 'battery': data})

            elif path == '/health':
                self.send_json({'status': 'healthy', 'service': 'sensor-server'})

        except Exception as e:
            self.send_json({'status': 'error', 'message': str(e)}, 500)

def run_server(port=9999):
    server = HTTPServer(('0.0.0.0', port), SensorHandler)
    print(f"Starting server on http://0.0.0.0:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()

if __name__ == '__main__':
    run_server(port=9999)
```

#### 4.3.2 启动脚本 (start_server.sh)

```bash
#!/bin/sh
echo "Starting Sensor HTTP Server..."

# 停止现有服务器
killall python 2>/dev/null
sleep 2

# 后台启动服务器
cd /sdcard
nohup python sensor_server.py > /sdcard/server.log 2>&1 &

# 等待服务器启动
sleep 3

# 检查服务器状态
if ps | grep -v grep | grep python > /dev/null; then
    echo "✓ Server started successfully"
    cat /sdcard/server.log
else
    echo "✗ Failed to start server"
    cat /sdcard/server.log
fi
```

#### 4.3.3 ADB 端口转发

```bash
# Windows 端
adb forward tcp:9999 tcp:9999

# 测试连接
curl http://127.0.0.1:9999/health
```

### 4.4 部署验证流程

```bash
# 1. 验证 Termux API 命令
termux-sensor -l
# 预期输出: 11 个传感器列表

# 2. 测试传感器读取
termux-sensor -s Accelerometer -n 1
# 预期输出: JSON 格式的传感器数据

# 3. 测试 HTTP 服务
curl http://127.0.0.1:9999/health
# 预期输出: {"status": "healthy", "service": "sensor-server"}

# 4. 测试传感器 API
curl http://127.0.0.1:9999/sensors
# 预期输出: 传感器列表 JSON

# 5. 测试 TTS
curl "http://127.0.0.1:9999/tts?text=Hello"
# 预期输出: {"status": "success", "message": "Speaking: Hello"}
```

---

## 5. 关键技术方案

### 5.1 AR 存档解析器

**问题:** Windows 缺少 `ar` 命令解压 deb 包
**解决方案:** Python 自实现 AR 格式解析

```python
# AR 文件格式 (简单版本)
"""
AR 文件结构:
- 8 字节魔数: !<arch>\n
- 文件头 (60 字节/文件):
  - 16 字节: 文件名 (空格填充)
  - 12 字节: 时间戳
  - 6 字节: 所有者 ID
  - 6 字节: 组 ID
  - 8 字节: 文件模式
  - 10 字节: 文件大小
  - 2 字节: 结束标记 (`\n)
- 文件内容 (N 字节)
- 填充 (1 字节, 如果 N 为奇数)
"""

def parse_ar_header(header):
    """解析 AR 文件头"""
    name = header[:16].decode('ascii').strip()
    size = int(header[48:58].decode('ascii').strip())
    return name, size
```

### 5.2 Termux 命令行输入自动化

**问题:** Termux v0.79 无 bash，无法通过 `adb shell` 直接执行
**解决方案:** 使用 `adb shell input` 模拟按键输入

```bash
# 输入命令 (空格用 %s 替代)
adb shell "input text 'cd%s/sdcard'"
adb shell "input keyevent 66"  # 回车键

# 后台启动 (& 符号)
adb shell "input text 'python%sserver.py%s&'"
```

**按键码参考:**
```
66 = ENTER
4 = BACK
3 = HOME
24 = VOLUME_UP
25 = VOLUME_DOWN
```

### 5.3 无框架 HTTP 服务

**问题:** Flask 依赖复杂，Termux v0.79 安装困难
**解决方案:** 使用 Python 内置 `http.server`

```python
from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 自定义路由
        if self.path == '/api':
            self.send_json({'data': 'value'})
```

**优势:**
- 无需额外依赖
- 启动速度快 (< 100ms)
- 内存占用小 (< 20MB)
- 兼容性好 (Python 3.6+)

### 5.4 跨版本兼容性处理

**问题:** Android 5.0 的各种限制
**解决方案:**

| 限制 | 解决方案 |
|-----|---------|
| 缺少 ar 命令 | Python AR 解析器 |
| 缺少 bash | 使用 /system/bin/sh |
| 权限问题 | 使用 /sdcard 临时目录 |
| 网络源不可用 | 使用 Archive.org 镜像 |
| 包依赖冲突 | 手动提取二进制文件 |

---

## 6. 工具清单

### 6.1 PC 端工具

| 工具 | 版本 | 用途 |
|------|------|------|
| ADB | 1.0.41 | 设备通信 |
| Python | 3.x | 脚本开发 |
| Git Bash | - | Windows 命令行 |
| curl | 7.55.1 | HTTP 测试 |

### 6.2 手机端工具

| 工具 | 版本 | 用途 |
|------|------|------|
| Termux | v0.79 | Linux 环境 |
| Termux:API | git-debug | API 桥接 |
| Python | 3.10.13 | HTTP 服务 |
| termux-sensor | 0.59.1 | 传感器访问 |

### 6.3 开发脚本

```
工具脚本/
├── extract_deb_ar.py         # AR 存档解析器
├── install_termux_api_v2.sh  # API 安装脚本
├── sensor_server.py           # HTTP 服务器
├── sensor_server_simple.py    # 简化版服务器
├── start_server.sh            # 服务器启动脚本
└── autoglm.bat                # AutoGLM 启动器
```

### 6.4 测试脚本

```
工具脚本/
├── verify_termux.sh           # Termux 环境验证
├── termux_functions_test.sh   # 功能测试套件
└── test_adb.bat               # ADB 连接测试
```

---

## 7. API 接口文档

### 7.1 基础信息

- **Base URL:** `http://127.0.0.1:9999`
- **编码:** UTF-8
- **响应格式:** JSON
- **超时时间:** 10秒

### 7.2 端点列表

#### 7.2.1 GET / - API 文档

**请求:**
```http
GET / HTTP/1.1
Host: 127.0.0.1:9999
```

**响应:**
```json
{
  "service": "Termux Sensor HTTP Server",
  "version": "2.0 (Simple)",
  "endpoints": {
    "GET /": "API documentation",
    "GET /sensors": "List available sensors",
    "GET /sensor/<type>": "Get sensor reading",
    "GET /tts?text=...": "Text-to-speech",
    "GET /battery": "Get battery status",
    "GET /health": "Health check"
  }
}
```

#### 7.2.2 GET /sensors - 传感器列表

**请求:**
```http
GET /sensors HTTP/1.1
Host: 127.0.0.1:9999
```

**响应:**
```json
{
  "status": "success",
  "sensors": [
    "Accelerometer",
    "Magnetic Field",
    "Gyroscope",
    "Light",
    "Pressure",
    "Ambient Temperature",
    "Proximity",
    "Gravity",
    "Linear Acceleration",
    "Rotation Vector",
    "Orientation"
  ],
  "count": 11
}
```

#### 7.2.3 GET /sensor/{type} - 传感器读数

**请求:**
```http
GET /sensor/accelerometer HTTP/1.1
Host: 127.0.0.1:9999
```

**查询参数:**
- `limit` (可选): 读取次数，默认 1

**响应:**
```json
{
  "status": "success",
  "sensor": "accelerometer",
  "data": {
    "Accelerometer": {
      "x": 0.123,
      "y": 9.81,
      "z": 0.456,
      "time": "2026-03-07T12:34:56+08:00"
    }
  }
}
```

**可用传感器:**
- `accelerometer` - 加速度计
- `gyroscope` - 陀螺仪
- `light` - 光线传感器
- `pressure` - 气压计
- `magnetic` - 磁场计
- `temperature` - 温度传感器
- `proximity` - 距离传感器
- `gravity` - 重力传感器
- `linear_acceleration` - 线性加速度
- `rotation_vector` - 旋转向量

#### 7.2.4 GET /tts - 文字转语音

**请求:**
```http
GET /tts?text=Hello%20World HTTP/1.1
Host: 127.0.0.1:9999
```

**查询参数:**
- `text` (必需): 要朗读的文本

**响应:**
```json
{
  "status": "success",
  "message": "Speaking: Hello World"
}
```

#### 7.2.5 GET /battery - 电池状态

**请求:**
```http
GET /battery HTTP/1.1
Host: 127.0.0.1:9999
```

**响应:**
```json
{
  "status": "success",
  "battery": {
    "percentage": 85,
    "status": "charging",
    "health": "good",
    "temperature": 32.5,
    "current": 1200,
    "voltage": 4200
  }
}
```

#### 7.2.6 GET /health - 健康检查

**请求:**
```http
GET /health HTTP/1.1
Host: 127.0.0.1:9999
```

**响应:**
```json
{
  "status": "healthy",
  "service": "sensor-server"
}
```

### 7.3 错误响应格式

```json
{
  "status": "error",
  "message": "Error description",
  "details": {}
}
```

**HTTP 状态码:**
- `200` - 成功
- `400` - 请求参数错误
- `404` - 资源未找到
- `500` - 服务器内部错误

### 7.4 使用示例

#### Python 示例

```python
import requests

# 获取传感器列表
response = requests.get('http://127.0.0.1:9999/sensors')
sensors = response.json()

# 读取加速度计
response = requests.get('http://127.0.0.1:9999/sensor/accelerometer')
accel_data = response.json()
print(f"X: {accel_data['data']['Accelerometer']['x']}")

# 语音合成
requests.get('http://127.0.0.1:9999/tts', params={'text': 'Hello'})

# 电池状态
response = requests.get('http://127.0.0.1:9999/battery')
battery = response.json()
print(f"Battery: {battery['battery']['percentage']}%")
```

#### JavaScript 示例

```javascript
// 获取传感器列表
fetch('http://127.0.0.1:9999/sensors')
  .then(r => r.json())
  .then(data => console.log(data.sensors));

// 读取陀螺仪
fetch('http://127.0.0.1:9999/sensor/gyroscope')
  .then(r => r.json())
  .then(data => console.log(data.data));

// 语音合成
fetch('http://127.0.0.1:9999/tts?text=你好世界')
  .then(r => r.json())
  .then(data => console.log(data.message));
```

#### curl 示例

```bash
# 健康检查
curl http://127.0.0.1:9999/health

# 获取传感器列表
curl http://127.0.0.1:9999/sensors

# 连续读取 10 次加速度计数据
curl "http://127.0.0.1:9999/sensor/accelerometer?limit=10"

# 语音合成
curl "http://127.0.0.1:9999/tts?text=测试语音"

# 电池状态
curl http://127.0.0.1:9999/battery
```

---

## 8. 故障排除指南

### 8.1 常见问题

#### 问题 1: `ar: not found`

**症状:**
```
ar: not found
```

**原因:** Termux v0.79 未包含 `ar` 命令

**解决方案:**
```bash
# 使用 Python AR 解析器
python extract_deb_ar.py package.deb extracted/
```

#### 问题 2: `Unable to start camera`

**症状:**
```
Error: Unable to start camera
```

**原因:** Termux:API 应用缺少相机权限

**解决方案:**
```bash
# Android 设置
设置 → 应用 → Termux:API → 权限 → 相机 → 允许
```

#### 问题 3: 端口被占用

**症状:**
```
OSError: [Errno 98] Address already in use
```

**解决方案:**
```bash
# 查找占用进程
ps | grep python

# 停止服务器
killall python

# 或使用其他端口
python sensor_server.py  # 修改代码中的端口号
```

#### 问题 4: ADB 连接失败

**症状:**
```
error: no devices/emulators found
```

**解决方案:**
```bash
# 1. 检查 USB 调试
adb devices

# 2. 重启 ADB 服务
adb kill-server
adb start-server

# 3. 重新授权 USB 调试
# 手机: 设置 → 开发者选项 → 撤销 USB 调试授权
# 重新连接 USB
```

#### 问题 5: `input text` 不工作

**症状:**
```
Error: Invalid arguments for command: text
```

**原因:** Git Bash 路径转换问题

**解决方案:**
```bash
# 方法 1: 使用双斜杠
adb shell "input text 'cd%s/sdcard'"

# 方法 2: 使用 cmd.exe
cmd.exe /c "adb shell input text hello"

# 方法 3: 使用 PowerShell
powershell.exe -Command "adb shell input text 'hello'"
```

### 8.2 日志调试

#### 服务器日志

```bash
# 查看服务器日志
cat /sdcard/server.log

# 实时监控
tail -f /sdcard/server.log

# 查看最近 50 行
tail -n 50 /sdcard/server.log
```

#### Termux 日志

```bash
# 查看 termux-api 执行日志
logcat | grep termux

# 查看所有错误
logcat *:E
```

#### Python 调试

```python
# 在 sensor_server.py 中添加
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

### 8.3 性能监控

```bash
# CPU 使用率
top | grep python

# 内存使用
dumpsys meminfo com.termux

# 网络连接
netstat -an | grep 9999

# 进程状态
ps aux | grep sensor
```

### 8.4 诊断脚本

```bash
#!/bin/bash
# diagnose.sh - 系统诊断脚本

echo "=== System Diagnosis ==="
echo ""

echo "1. Termux Version:"
termux-version
echo ""

echo "2. Python Version:"
python --version
echo ""

echo "3. API Commands:"
which termux-sensor termux-tts-speak termux-battery-status
echo ""

echo "4. Server Status:"
ps | grep -v grep | grep sensor_server
echo ""

echo "5. Port Listening:"
netstat -an 2>/dev/null | grep 9999 || echo "netstat not available"
echo ""

echo "6. Sensor List:"
termux-sensor -l
echo ""

echo "7. Test API:"
curl -s http://127.0.0.1:9999/health
echo ""
echo ""

echo "=== Diagnosis Complete ==="
```

---

## 9. 性能优化建议

### 9.1 服务器优化

#### 9.1.1 使用 ThreadingMixIn

```python
from socketserver import ThreadingMixIn

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """支持多线程的 HTTP 服务器"""
    daemon_threads = True

server = ThreadedHTTPServer(('0.0.0.0', 9999), SensorHandler)
```

#### 9.1.2 连接池

```python
# 复用 subprocess 进程
class SensorCache:
    def __init__(self):
        self.cache = {}
        self.timeout = 1  # 缓存 1 秒

    def get(self, sensor):
        import time
        now = time.time()
        if sensor in self.cache:
            data, timestamp = self.cache[sensor]
            if now - timestamp < self.timeout:
                return data
        return None
```

#### 9.1.3 压缩响应

```python
import gzip

def send_json_compressed(self, data):
    """发送压缩的 JSON 响应"""
    json_data = json.dumps(data).encode('utf-8')
    compressed = gzip.compress(json_data)

    self.send_response(200)
    self.send_header('Content-Encoding', 'gzip')
    self.send_header('Content-Type', 'application/json')
    self.end_headers()
    self.wfile.write(compressed)
```

### 9.2 传感器优化

#### 9.2.1 批量读取

```python
# 一次读取多个传感器
def read_multiple_sensors(sensors, count=1):
    """批量读取传感器"""
    results = {}
    for sensor in sensors:
        cmd = ['termux-sensor', '-s', sensor, '-n', str(count)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        results[sensor] = json.loads(result.stdout)
    return results
```

#### 9.2.2 降低采样率

```python
# 减少读取频率
import time

class SensorReader:
    def __init__(self, interval=0.1):  # 100ms 间隔
        self.interval = interval
        self.last_read = 0

    def read(self, sensor):
        now = time.time()
        if now - self.last_read < self.interval:
            time.sleep(self.interval - (now - self.last_read))
        self.last_read = time.time()
        return read_sensor(sensor)
```

### 9.3 内存优化

#### 9.3.1 流式响应

```python
def send_streaming_json(self, generator):
    """流式发送 JSON 数据"""
    self.send_response(200)
    self.send_header('Content-Type', 'application/json')
    self.end_headers()

    self.wfile.write(b'[')
    first = True
    for item in generator:
        if not first:
            self.wfile.write(b',')
        json.dump(item, self.wfile)
        first = False
        self.wfile.flush()  # 立即发送
    self.wfile.write(b']')
```

#### 9.3.2 限制响应大小

```python
def limit_sensor_data(data, max_points=100):
    """限制传感器数据点数量"""
    if isinstance(data, list):
        return data[:max_points]
    return data
```

### 9.4 网络优化

#### 9.4.1 Keep-Alive

```python
class SensorHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def end_headers(self):
        self.send_header('Connection', 'keep-alive')
        super().end_headers()
```

#### 9.4.2 CORS 优化

```python
# 只在需要时启用 CORS
def send_json(self, data, status=200, cors=False):
    self.send_response(status)
    self.send_header('Content-Type', 'application/json')
    if cors:
        self.send_header('Access-Control-Allow-Origin', '*')
    self.end_headers()
    self.wfile.write(json.dumps(data).encode())
```

---

## 10. 未来扩展方向

### 10.1 功能扩展

#### 10.1.1 WebSocket 支持

```python
# 实时传感器数据流
import asyncio
import websockets

async def sensor_stream(websocket, path):
    """WebSocket 传感器数据流"""
    while True:
        data = read_sensor('accelerometer')
        await websocket.send(json.dumps(data))
        await asyncio.sleep(0.1)  # 10Hz

async def main():
    async with websockets.serve(sensor_stream, "0.0.0.0", 9999):
        await asyncio.Future()  # 永久运行

asyncio.run(main())
```

#### 10.1.2 数据持久化

```python
import sqlite3

def store_sensor_data(sensor, data):
    """存储传感器数据到数据库"""
    conn = sqlite3.connect('/sdcard/sensor_data.db')
    c = conn.cursor()

    c.execute('''INSERT INTO sensor_readings
                 (sensor, data, timestamp)
                 VALUES (?, ?, datetime('now'))''',
              (sensor, json.dumps(data)))

    conn.commit()
    conn.close()
```

#### 10.1.3 数据分析

```python
import numpy as np

def analyze_sensor_data(sensor, duration=60):
    """分析传感器数据"""
    # 收集数据
    data = []
    for _ in range(duration * 10):  # 10Hz
        data.append(read_sensor(sensor))
        time.sleep(0.1)

    # 分析
    values = [d['value'] for d in data]
    return {
        'mean': np.mean(values),
        'std': np.std(values),
        'min': np.min(values),
        'max': np.max(values)
    }
```

### 10.2 架构升级

#### 10.2.1 微服务架构

```
┌─────────────────────────────────────┐
│        API Gateway (Nginx)          │
└─────────┬───────────────────────────┘
          │
    ┌─────┴─────┬─────────┬──────────┐
    │           │         │          │
┌───▼───┐ ┌───▼───┐ ┌───▼───┐ ┌───▼───┐
│Sensor  │ │  TTS  │ │Battery│ │Camera │
│Service │ │Service│ │Service│ │Service│
└────────┘ └───────┘ └───────┘ └───────┘
```

#### 10.2.2 消息队列

```python
# 使用 ZeroMQ 进行服务间通信
import zmq

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:5555")

# 发布传感器数据
while True:
    data = read_sensor('accelerometer')
    socket.send_json({'sensor': 'accelerometer', 'data': data})
```

### 10.3 安全增强

#### 10.3.1 API 认证

```python
import hmac
import hashlib

def verify_request(request):
    """验证请求签名"""
    signature = request.headers.get('X-Signature')
    if not signature:
        return False

    # 计算 HMAC
    secret = 'your-secret-key'
    payload = request.path + request.body
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)
```

#### 10.3.2 速率限制

```python
from collections import defaultdict
import time

class RateLimiter:
    def __init__(self, max_requests=60, window=60):
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(list)

    def is_allowed(self, client_id):
        """检查是否允许请求"""
        now = time.time()
        # 清理过期记录
        self.requests[client_id] = [
            t for t in self.requests[client_id]
            if now - t < self.window
        ]
        # 检查限制
        if len(self.requests[client_id]) < self.max_requests:
            self.requests[client_id].append(now)
            return True
        return False
```

### 10.4 开发工具

#### 10.4.1 API 文档生成

```python
# 使用 OpenAPI/Swagger
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Sensor API"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
```

#### 10.4.2 监控仪表盘

```python
# Prometheus 指标
from prometheus_client import Counter, Histogram, start_http_server

request_count = Counter('api_requests_total', 'Total API requests')
request_duration = Histogram('api_request_duration_seconds', 'Request duration')

@app.route('/metrics')
def metrics():
    request_count.inc()
    with request_duration.time():
        # 处理请求
        pass
```

### 10.5 部署选项

#### 10.5.1 Docker 容器化

```dockerfile
# Dockerfile
FROM python:3.10-slim

RUN apt-get update && apt-get install -y termux-api

WORKDIR /app
COPY sensor_server.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 9999
CMD ["python", "sensor_server.py"]
```

#### 10.5.2 Systemd 服务

```ini
# /etc/systemd/system/sensor-server.service
[Unit]
Description=Termux Sensor HTTP Server
After=network.target

[Service]
Type=simple
User=termux
WorkingDirectory=/sdcard
ExecStart=/data/data/com.termux/files/usr/bin/python /sdcard/sensor_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 附录

### A. 完整脚本列表

```
资源档案/
├── extract_deb_ar.py              # AR 解析器
├── termux-api_0.59.1-1_aarch64.deb
└── termux-api-extracted/

工具脚本/
├── extract_deb_simple.py          # 简单 deb 提取
├── install_termux_api.sh          # 安装脚本 v1
├── install_termux_api_v2.sh       # 安装脚本 v2 ✅
├── sensor_server.py               # HTTP 服务器 ✅
├── sensor_server_simple.py        # 简化版服务器 ✅
├── start_server.sh                # 服务器启动脚本 ✅
├── autoglm.bat                    # AutoGLM 启动器
├── test_adb.bat                   # ADB 测试
├── verify_termux.sh               # Termux 验证
└── termux_functions_test.sh       # 功能测试

测试报告/
├── AutoGLM_Termux_Bash适配报告.md
├── Termux_v79_离线Bootstrap安装报告.md
├── AutoGLM_Termux_测试报告.md
└── 荣耀手机Termux传感器部署技术参考文档.md ✅

测试截图/
├── termux_v2_result.png           # 安装成功截图 ✅
├── sensor_test.png                # 传感器列表 ✅
├── tts_test.png                   # TTS 测试
├── server_check.png               # 服务器状态
├── curl_test.png                  # curl 测试 ✅
└── final_test.png                 # 最终测试 ✅
```

### B. 命令速查表

```bash
# ADB 连接
adb devices                         # 列出设备
adb shell                           # 进入 shell
adb exit                            # 退出 shell

# 文件传输
adb push local_file //sdcard//      # 推送文件
adb pull //sdcard//file local      # 拉取文件
adb shell ls //sdcard//             # 列出文件

# 端口转发
adb forward tcp:9999 tcp:9999       # 设置转发
adb forward --list                  # 列出转发

# 输入模拟
adb shell input text 'hello'        # 输入文本
adb shell input keyevent 66         # 按键事件

# 屏幕截图
adb shell screencap -p //sdcard//shot.png
adb pull //sdcard//shot.png .

# 应用控制
adb shell am start -n package/activity
adb shell am force-stop package

# Termux 操作
termux-sensor -l                    # 列出传感器
termux-sensor -s Accelerometer -n 1 # 读取传感器
termux-tts-speak 'Hello'            # 语音合成
termux-battery-status               # 电池状态
```

### C. 相关资源

**官方资源:**
- Termux GitHub: https://github.com/termux/termux-app
- Termux:API GitHub: https://github.com/termux/termux-api
- Archive.org Termux: https://archive.org/details/termux-repositories-legacy
- AutoGLM GitHub: https://github.com/zai-org/Open-AutoGLM

**文档资源:**
- Python http.server: https://docs.python.org/3/library/http.server.html
- ADB 文档: https://developer.android.com/studio/command-line/adb
- Android HAL: https://source.android.com/devices/architecture/hal

**社区资源:**
- Reddit r/termux: https://reddit.com/r/termux
- Termux Wiki: https://wiki.termux.com
- Stack Overflow tag: termux

### D. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0 | 2026-03-07 | 初始版本，完整技术文档 |

---

**文档结束**

*本文档由 Claude Code 生成和维护*
*项目地址: D:\工作日常\服务器搭建\荣耀手机刷机*
*最后更新: 2026-03-07*
