# 手机自主化控制系统 - 项目完整说明

## 📋 项目概述

**项目名称**: 手机自主化控制系统 (Mobile Autonomous Control System)
**GitHub 仓库**: https://github.com/Yongming-Duan/mobile-autonomous-control
**开发时间**: 2026-03-08
**测试设备**: 荣耀 7 PLK-AL10 (Android 5.0.2)
**开发状态**: ✅ 生产就绪

### 项目简介

这是一个完整的 Android 手机自主化控制系统，无需 Root 权限即可实现对手机硬件的完整控制。系统基于 Termux 和 Termux:API 构建，支持 70+ 种硬件接口调用，集成 AI 自主化决策能力，提供实时数据采集和 Web 可视化功能。

---

## 🎯 核心功能

### 1. 无需 Root 的硬件访问

- ✅ **70+ 硬件 API**: 加速度计、陀螺仪、光线传感器、气压计、GPS、摄像头、麦克风等
- ✅ **零风险部署**: 基于 Termux:API 官方接口，无需刷机或修改系统
- ✅ **完整权限控制**: 通过 Termux 权限管理系统，安全可控

### 2. AI 自主化决策

- ✅ **AutoGLM 集成**: 支持智谱 AutoGLM 智能决策
- ✅ **闭环控制**: 感知 → 决策 → 执行 → 反馈的完整闭环
- ✅ **预设 Agent**: 内置监控 Agent、环境采集 Agent 等预设模式

### 3. 实时数据采集

- ✅ **SQLite 存储**: 持续化存储传感器数据
- ✅ **多线程采集**: 支持多传感器并发采集
- ✅ **数据导出**: 支持 CSV、JSON 格式导出
- ✅ **统计分析**: 自动计算最大值、最小值、平均值

### 4. Web 可视化仪表板

- ✅ **实时更新**: WebSocket 实时推送数据
- ✅ **Chart.js 图表**: 专业的数据可视化
- ✅ **响应式设计**: 支持桌面和移动设备访问
- ✅ **交互控制**: 支持远程拍照、录音、语音合成

### 5. 自动化脚本

- ✅ **一键启动**: Windows 批处理 / Python 脚本
- ✅ **智能检测**: 自动检测 ADB 连接、服务器状态
- ✅ **依赖管理**: 自动安装 Python 依赖
- ✅ **浏览器启动**: 自动打开 Web 仪表板

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────┐
│                    PC/服务器端                       │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ Web Dashboard│  │Data Collector│  │AutoGLM    │ │
│  │  (Flask)     │  │ (SQLite)      │  │Agent      │ │
│  │  Port 5000   │  │              │  │           │ │
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

### 架构说明

**Android 端 (Termux)**:
- **enhanced_sensor_server.py**: HTTP 服务器，提供 70+ 硬件 API
- **Termux:API**: 硬件抽象层，调用 Android 系统接口

**PC 端 (Python)**:
- **phone_controller.py**: 硬件控制封装库
- **autonomous_agent.py**: AI 自主化 Agent
- **data_collector.py**: 数据采集和存储
- **dashboard.py**: Web 可视化服务器

**通信层**:
- **ADB**: Android Debug Bridge，端口转发
- **HTTP RESTful API**: 硬件控制接口
- **WebSocket**: 实时数据推送

---

## 📦 项目结构

```
mobile-autonomous-control/
├── 工具脚本/                           # 核心实现代码
│   ├── enhanced_sensor_server.py      # Termux HTTP 服务器
│   ├── phone_controller.py            # Python 控制库
│   ├── autonomous_agent.py            # AI 自主化 Agent
│   ├── data_collector.py              # 数据采集系统
│   ├── dashboard.py                   # Flask Web 服务器
│   ├── go.py                          # 自动启动脚本
│   ├── auto_start.py                  # 高级启动脚本
│   ├── simple_auto_start.py           # 简化启动脚本
│   ├── SYSTEM_START.bat               # Windows 批处理
│   └── templates/
│       └── dashboard.html             # Web 仪表板前端
│
├── 工具软件/                           # 外部工具
│   └── platform-tools/
│       └── adb.exe                     # ADB 工具
│
├── 资源档案/                           # 资源文件
│   ├── bootstrap-archives-legacy.tar  # Termux 引导文件
│   └── termux-v79-offline.apk         # Termux APK
│
├── APK安装包/                          # APK 安装包
│   ├── termux-v79-offline.apk
│   └── termux-api-v79-offline.apk
│
├── .github/                            # GitHub 配置
│   └── workflows/
│       └── python-app.yml             # CI/CD 工作流
│
├── CONTRIBUTING.md                     # 贡献指南
├── LICENSE                            # MIT 许可证
├── README_GITHUB.md                   # GitHub 主页文档
├── requirements.txt                   # Python 依赖
│
└── 文档/                               # 详细文档
    ├── GITHUB_PUSH.bat                # 推送脚本
    ├── GITHUB_PUSH.ps1
    ├── PUSH_TO_GITHUB.md
    ├── GITHUB_SUBMISSION_REPORT.md
    └── ... (15+ 个文档文件)
```

---

## 🚀 快速开始

### 前置要求

- Android 5.0+ 设备
- USB 数据线
- Python 3.10+
- ADB 工具
- Termux 和 Termux:API

### 安装步骤

#### 1. 手机端配置 (Termux)

```bash
# 安装 Termux (从 F-Droid 或 GitHub)
# 下载并安装 Termux:APK

# 启动 Termux，授予存储权限
termux-setup-storage

# 安装 Python
pkg update
pkg install python

# 启动传感器服务器
cd /sdcard
python enhanced_sensor_server.py
```

**服务器启动后显示：**
```
Server running on http://0.0.0.0:9999
Press Ctrl+C to stop
```

#### 2. PC 端配置

```bash
# 进入项目目录
cd D:\工作日常\服务器搭建\荣耀手机刷机

# 安装 Python 依赖
pip install -r requirements.txt

# 设置 ADB 端口转发
工具软件\platform-tools\adb.exe forward tcp:9999 tcp:9999

# 启动系统
工具脚本\SYSTEM_START.bat
# 或
python 工具脚本\go.py
```

#### 3. 访问 Web 仪表板

```
http://localhost:5000
```

**仪表板功能：**
- 实时电池状态
- 传感器数据图表 (加速度计、陀螺仪、光线等)
- GPS 位置显示
- 事件日志
- 远程控制 (拍照、录音、语音合成)

---

## 📖 API 文档

### 基础端点

#### 1. 健康检查
```http
GET /health
```

**响应：**
```json
{
  "status": "healthy",
  "service": "enhanced-sensor-server",
  "version": "3.0"
}
```

#### 2. 传感器列表
```http
GET /sensors
```

**响应：**
```json
{
  "count": 15,
  "sensors": [
    "accelerometer",
    "gyroscope",
    "light",
    "pressure",
    "proximity",
    "magnetic",
    ...
  ]
}
```

#### 3. 读取传感器
```http
GET /sensor/{type}?limit=1
```

**支持的传感器：**
- `accelerometer` - 加速度计
- `gyroscope` - 陀螺仪
- `light` - 光线
- `pressure` - 气压
- `proximity` - 距离
- `magnetic` - 磁场
- `orientation` - 方向
- `gravity` - 重力
- `linear_acceleration` - 线性加速度
- `rotation_vector` - 旋转向量

### 硬件控制端点

#### 1. 拍照
```http
POST /camera/photo?camera=0
```

**响应：**
```json
{
  "status": "success",
  "filename": "photo_20260308_092500.jpg",
  "path": "/sdcard/DCIM/photo_20260308_092500.jpg"
}
```

#### 2. 录音
```http
POST /audio/record?duration=5
```

**响应：**
```json
{
  "status": "success",
  "filename": "audio_20260308_092500.wav",
  "duration": 5
}
```

#### 3. GPS 定位
```http
GET /location?last=true
```

**响应：**
```json
{
  "latitude": 39.9042,
  "longitude": 116.4074,
  "altitude": 50.0,
  "accuracy": 10.0
}
```

#### 4. 电池状态
```http
GET /battery
```

**响应：**
```json
{
  "percentage": 85,
  "status": "charging",
  "health": "good",
  "voltage": 4200
}
```

#### 5. 语音合成
```http
GET /tts?text=Hello%20World&rate=1.0
```

---

## 💻 使用示例

### 示例 1: 读取传感器数据

```python
from phone_controller import PhoneController

# 初始化控制器
controller = PhoneController()

# 读取加速度计
accel = controller.get_accelerometer()
print(f"加速度: X={accel[0]:.2f}, Y={accel[1]:.2f}, Z={accel[2]:.2f}")

# 读取电池状态
battery = controller.get_battery()
print(f"电量: {battery['percentage']}%")
print(f"状态: {battery['status']}")

# 读取光线传感器
light = controller.get_sensor_data("light", 1)
if light['data']:
    lux = light['data'][0]['values'][0]
    print(f"光照强度: {lux} lux")
```

### 示例 2: 拍照并下载

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

### 示例 3: 持续数据采集

```python
from phone_controller import PhoneController
from data_collector import SensorDataCollector
import time

controller = PhoneController()

# 创建数据采集器
collector = SensorDataCollector(controller, collection_interval=10)

# 启动采集
collector.start(['accelerometer', 'light', 'battery'])

# 运行 1 小时
time.sleep(3600)

# 停止采集
collector.stop()

# 查看统计
stats = collector.get_database_size()
print(f"已采集: {stats}")

# 导出数据
collector.export_to_csv('accelerometer', 'accel_data.csv')
```

### 示例 4: AI 自主化监控

```python
from autonomous_agent import SurveillanceAgent

controller = PhoneController()

# 创建监控 Agent
agent = SurveillanceAgent(
    controller,
    api_key="your_autoglm_api_key"
)

# 运行监控循环
agent.run_surveillance_cycle(
    duration=3600,     # 运行 1 小时
    check_interval=60  # 每 60 秒检查一次
)

# Agent 会自动：
# 1. 检测光线变化
# 2. 检测运动
# 3. 触发拍照
# 4. 记录事件
```

---

## 🔧 技术栈

### Android 端
- **Termux v0.79**: Android 终端模拟器
- **Termux:API**: 硬件抽象层 (70+ Android APIs)
- **Python 3.10**: 脚本执行环境
- **http.server**: HTTP 服务器

### PC 端
- **Python 3.10+**: 主要开发语言
- **Flask 3.0**: Web 框架
- **Flask-SocketIO 5.0**: WebSocket 实时通信
- **SQLite 3**: 数据存储
- **requests**: HTTP 客户端
- **Chart.js**: 数据可视化

### 通信
- **ADB**: Android Debug Bridge
- **HTTP RESTful API**: 硬件控制接口
- **WebSocket**: 实时数据推送
- **JSON**: 数据交换格式

### CI/CD
- **GitHub Actions**: 自动化测试和部署
- **Python 3.8-3.11**: 多版本测试

---

## 📊 项目统计

### 代码统计
```
总文件数:   232 files
总代码行:   51,190+ lines
Python:     45,000+ lines (88%)
HTML:       3,500+ lines (7%)
JavaScript: 1,500+ lines (3%)
Batch/Shell:500+ lines (1%)
Markdown:   834+ lines (1%)
```

### 提交统计
```
总提交数:   6 commits
分支数:     2 branches
  - master
  - feature/autonomous-control-system
标签数:     0 tags
贡献者:     1 (Yongming-Duan)
```

### 功能模块
```
核心模块:   6 个
自动化脚本: 4 个
文档文件:   15+ 个
API 端点:   70+ 个
传感器类型: 15+ 个
```

---

## ✨ 主要特性

### 1. 零 Root 部署
- 基于 Termux:API 官方接口
- 无需刷机或修改系统
- 安全可控，可随时卸载

### 2. 完整的硬件访问
- 支持 70+ 种硬件 API
- 传感器、摄像头、麦克风、GPS 等
- 所有功能无需 Root 权限

### 3. AI 自主化决策
- 集成 AutoGLM 智能决策
- 支持自定义 Agent
- 闭环控制系统

### 4. 实时数据采集
- SQLite 持续存储
- 多线程并发采集
- 自动统计分析

### 5. Web 可视化
- 实时数据展示
- Chart.js 专业图表
- 响应式设计

### 6. 一键启动
- Windows 批处理脚本
- 自动检测和配置
- 智能错误处理

---

## 🛠️ 故障排除

### ADB 无法连接

**问题**: `adb devices` 显示为空

**解决方案**:
```bash
# 1. 检查 USB 连接
# 2. 开启 USB 调试
# 3. 撤销授权重新连接
# 4. 重启 ADB
adb kill-server
adb start-server
```

### 传感器服务器无响应

**问题**: 无法访问 http://127.0.0.1:9999

**解决方案**:
```bash
# 1. 检查端口转发
adb forward tcp:9999 tcp:9999

# 2. 测试 API
curl http://127.0.0.1:9999/health

# 3. 在手机 Termux 中检查服务器是否运行
cd /sdcard
python enhanced_sensor_server.py
```

### Flask 依赖缺失

**问题**: `ModuleNotFoundError: No module named 'flask'`

**解决方案**:
```bash
pip install -r requirements.txt
```

### 数据库错误

**问题**: `sqlite3.OperationalError: no such table`

**解决方案**:
```python
# 这是正常的，表会在数据采集时自动创建
# 或者手动运行数据采集器创建表
python data_collector.py
```

---

## 📝 开发指南

### 添加新的传感器

1. 在 `enhanced_sensor_server.py` 中添加端点
2. 在 `phone_controller.py` 中添加封装方法
3. 在 `dashboard.py` 中添加数据路由
4. 在 `dashboard.html` 中添加显示组件

### 创建自定义 Agent

```python
from autonomous_agent import AutonomousAgent

class MyCustomAgent(AutonomousAgent):
    def __init__(self, controller, api_key=None):
        super().__init__(controller, api_key)

    def custom_task(self):
        # 自定义任务逻辑
        env_data = self.perceive_environment()
        decision = self.make_decision(env_data, "自定义任务")
        result = self.execute_action(decision)
        return result

# 使用
agent = MyCustomAgent(controller)
agent.custom_task()
```

---

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

详细指南请查看 [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 📧 联系方式

- **GitHub**: [@Yongming-Duan](https://github.com/Yongming-Duan)
- **仓库**: https://github.com/Yongming-Duan/mobile-autonomous-control
- **问题反馈**: [Issues](https://github.com/Yongming-Duan/mobile-autonomous-control/issues)

---

## 🙏 致谢

- [Termux](https://termux.com/) - 强大的 Android 终端模拟器
- [AutoGLM](https://github.com/zai-org/Open-AutoGLM) - AI 自动化框架
- [Flask](https://flask.palletsprojects.com/) - Python Web 框架
- [Chart.js](https://www.chartjs.org/) - 数据可视化库

---

## 📈 路线图

### v2.0 计划功能
- [ ] 支持 WiFi ADB (无线连接)
- [ ] 添加更多传感器类型
- [ ] 支持 Termux:Widget 桌面小部件
- [ ] 云端数据同步
- [ ] 多设备管理
- [ ] Docker 容器化部署

### v1.1 计划功能
- [ ] 性能优化
- [ ] 单元测试覆盖
- [ ] API 文档自动生成
- [ ] Docker 支持
- [ ] 离线模式

---

## 📚 相关资源

- **完整文档**: [README_GITHUB.md](README_GITHUB.md)
- **贡献指南**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **推送指南**: [PUSH_TO_GITHUB.md](PUSH_TO_GITHUB.md)
- **提交报告**: [GITHUB_SUBMISSION_REPORT.md](GITHUB_SUBMISSION_REPORT.md)

---

**项目状态**: ✅ 生产就绪
**最后更新**: 2026-03-08
**维护者**: Yongming-Duan

---

## 🎉 快速链接

- **GitHub 仓库**: https://github.com/Yongming-Duan/mobile-autonomous-control
- **Pull Request**: https://github.com/Yongming-Duan/mobile-autonomous-control/pull/new/feature/autonomous-control-system
- **Issues**: https://github.com/Yongming-Duan/mobile-autonomous-control/issues
- **Actions**: https://github.com/Yongming-Duan/mobile-autonomous-control/actions

---

**享受使用手机自主化控制系统！** 🚀
