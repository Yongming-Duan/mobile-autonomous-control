# 工具脚本目录

## 🚀 快速启动脚本

### AutoGLM 启动器
```batch
autoglm.bat (1.3 KB)
```
**使用方法：**
```batch
.\autoglm.bat "你的任务描述"
```
**示例：**
```batch
.\autoglm.bat "打开设置查看设备信息"
.\autoglm.bat "打开微信发送消息"
```

### AutoGLM 运行脚本
```batch
run_autoglm.bat (1.1 KB)
```
**说明：** 包含 API 密钥配置，直接运行即可

---

## 🔧 ADB 工具脚本

### ADB 安装
```batch
install_adb.bat (1.3 KB)
```
**功能：** 自动下载并安装 ADB Platform Tools

### ADB 测试
```batch
test_adb.bat (940 B)
```
**功能：** 测试 ADB 连接状态

---

## 📱 Termux 安装脚本

### Termux 安装
```batch
install_termux.bat (1.4 KB)
```
**功能：** 自动安装 Termux APK

---

## 🧪 测试脚本

### Termux 环境验证 ⭐ 推荐
```bash
verify_termux.sh (1.1 KB)
```
**功能：** 验证 Termux Bash 环境是否正常
**使用：**
```bash
bash /sdcard/verify_termux.sh
```

### 完整功能测试 ⭐ 推荐
```bash
termux_functions_test.sh (4.1 KB)
```
**功能：** 测试摄像头、麦克风、传感器等所有功能
**使用：**
```bash
bash /sdcard/termux_functions_test.sh
```

### 基础测试
```bash
termux_test.sh (2.0 KB)
```
**功能：** 基础功能测试

---

## ⚙️ 配置脚本

### Bootstrap 离线安装
```bash
bootstrap_install.sh (3.9 KB)
```
**功能：** 手动安装 bootstrap 包（离线环境）

### Legacy 源配置
```bash
fix_legacy_sources.sh (1.4 KB)
```
**功能：** 配置 Termux legacy 软件源（旧版本）

---

## 🛠️ 其他工具

### PowerShell ADB 查找
```powershell
find_adb.ps1 (826 B)
```
**功能：** 在系统中查找 ADB 工具路径

---

## 📝 脚本使用说明

### 1. Windows 批处理文件 (.bat)
双击运行或在命令行执行

### 2. Shell 脚本 (.sh)
需要推送到手机后执行：
```bash
adb push script.sh /sdcard/
adb shell "bash /sdcard/script.sh"
```

### 3. PowerShell 脚本 (.ps1)
在 PowerShell 中运行：
```powershell
.\script.ps1
```

---

## ⭐ 常用命令

### 安装 Termux 完整流程
```batch
REM 1. 安装 ADB
install_adb.bat

REM 2. 测试连接
test_adb.bat

REM 3. 安装 Termux
install_termux.bat

REM 4. 验证安装
REM 在手机 Termux 中运行：
adb shell "am start -n com.termux/.app.TermuxActivity"
REM 然后输入：bash /sdcard/verify_termux.sh
```

### 使用 AutoGLM 自动化
```batch
REM 直接启动
autoglm.bat "打开 Termux 并输入 ls"

REM 或使用完整版本
run_autoglm.bat
```

---

**最后更新：** 2026-03-07
