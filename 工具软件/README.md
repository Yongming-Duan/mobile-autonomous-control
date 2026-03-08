# 工具软件目录

## 📂 目录内容

### ADB Platform Tools
**目录：** `platform-tools/`
**版本：** r36.0.2
**大小：** ~7.4 MB (解压前)
**平台：** Windows

**包含工具：**
- `adb.exe` - Android Debug Bridge
- `fastboot.exe` - Fastboot 协议工具
- `etc/` - 配置文件

**下载源：** Google 官方
**下载日期：** 2026-03-07
**状态：** ✅ 正常使用

**常用命令：**
```bash
# 查看设备
./adb.exe devices

# 安装 APK
./adb.exe install app.apk

# 截图
./adb.exe shell screencap -p /sdcard/screen.png

# 传输文件
./adb.exe push local.file /sdcard/
./adb.exe pull /sdcard/remote.file
```

---

### ADB Platform Tools 安装包
**文件：** `platform-tools.zip`
**大小：** 7.4 MB
**说明：** 原始安装包备份

---

### AutoGLM 项目
**目录：** `Open-AutoGLM/`
**来源：** https://github.com/zai-org/Open-AutoGLM
**克隆日期：** 2026-03-07

**主要文件：**
- `main.py` - 主程序入口
- `phone_agent/` - Phone Agent 核心代码
- `setup.py` - 安装配置
- `requirements.txt` - Python 依赖

**Python 依赖：**
- Pillow (图像处理)
- openai (API 客户端)
- requests (HTTP 请求)

**使用方法：**
```bash
cd Open-AutoGLM
python main.py \
  --base-url https://open.bigmodel.cn/api/paas/v4 \
  --model "autoglm-phone" \
  --apikey "YOUR_API_KEY" \
  "任务描述"
```

**API 配置：**
- Base URL: `https://open.bigmodel.cn/api/paas/v4`
- Model: `autoglm-phone`
- API Key: `1b3d58e728f84e38b8872bf09e3217f8.UTF48shlSo4dYykv`

---

## 📊 工具统计

| 工具 | 版本 | 大小 | 用途 |
|------|------|------|------|
| ADB | r36.0.2 | 7.4 MB | Android 设备通信 |
| AutoGLM | Latest | ~2 MB | AI 手机自动化 |
| **总计** | - | **~9.4 MB** | - |

---

## 🚀 快速开始

### 1. 测试 ADB 连接
```bash
cd platform-tools
./adb.exe devices
```

### 2. 使用 AutoGLM
```bash
cd Open-AutoGLM
python main.py --base-url URL --model "autoglm-phone" --apikey "KEY" "任务"
```

或使用快捷脚本：
```batch
..\工具脚本\autoglm.bat "打开设置"
```

---

## 📝 维护说明

### ADB 更新
如需更新 ADB：
1. 访问 https://developer.android.com/studio/releases/platform-tools
2. 下载最新版本
3. 替换 `platform-tools/` 目录

### AutoGLM 更新
```bash
cd Open-AutoGLM
git pull origin main
pip install -r requirements.txt --upgrade
```

---

**最后更新：** 2026-03-07
