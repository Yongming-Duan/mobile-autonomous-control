@echo off
REM ============================================
REM 手机自主化控制系统 - 一键启动脚本 v2
REM ============================================

setlocal enabledelayedexpansion

REM 设置路径
set "PROJECT_ROOT=D:\工作日常\服务器搭建\荣耀手机刷机"
set "ADB_PATH=%PROJECT_ROOT%\工具软件\platform-tools"
set "SCRIPT_PATH=%PROJECT_ROOT%\工具脚本"

echo.
echo ============================================================
echo           手机自主化控制系统 - 快速启动
echo ============================================================
echo.

REM 检查ADB
echo [1/5] 检查ADB连接...
cd /d "%ADB_PATH%"
adb.exe devices | findstr "device" >nul
if errorlevel 1 (
    echo   ❌ ADB设备未连接！
    echo.
    echo 请确保:
    echo   1. 手机已通过USB连接
    echo   2. USB调试已开启
    echo   3. 已授权此电脑进行USB调试
    echo.
    pause
    exit /b 1
)
echo   ✅ ADB连接正常

REM 设置端口转发
echo.
echo [2/5] 设置端口转发...
adb.exe forward tcp:9999 tcp:9999 2>nul
echo   ✅ 端口转发已配置 (9999)

REM 检查Termux服务器
echo.
echo [3/5] 检查传感器服务器...
cd /d "%SCRIPT_PATH%"

REM 检查curl是否可用
where curl >nul 2>&1
if errorlevel 1 (
    echo   ⚠️ curl不可用，跳过服务器检查
) else (
    curl -s http://127.0.0.1:9999/health >nul 2>&1
    if errorlevel 1 (
        echo   ⚠️ 传感器服务器未运行！
        echo.
        echo 请在手机Termux中执行:
        echo   cd /sdcard
        echo   python enhanced_sensor_server.py
        echo.
        echo 等待3秒后继续...
        timeout /t 3 /nobreak >nul
    ) else (
        echo   ✅ 传感器服务器运行正常
    )
)

REM 检查Python依赖
echo.
echo [4/5] 检查Python依赖...

REM 检查Flask
python -c "import flask" 2>nul
if errorlevel 1 (
    echo   安装Flask...
    pip install flask flask-socketio
)

REM 检查requests
python -c "import requests" 2>nul
if errorlevel 1 (
    echo   安装requests...
    pip install requests
)

echo   ✅ Python依赖就绪

REM 启动选项
echo.
echo [5/5] 选择启动模式:
echo.
echo   1. 快速测试 (运行 quick_start.py)
echo   2. 启动Web仪表板
echo   3. 启动数据采集 (后台)
echo   4. 全部启动
echo.
choice /C 1234 /M "请选择"

if errorlevel 4 (
    echo.
    echo === 全部启动 ===
    echo.

    REM 启动数据采集
    echo 启动数据采集...
    start /MIN cmd /c "python data_collector.py"

    REM 等待初始化
    timeout /t 3 /nobreak >nul

    REM 启动仪表板
    echo 启动Web仪表板...
    echo.
    echo 仪表板地址: http://localhost:5000
    echo 按Ctrl+C停止服务器
    echo.
    python dashboard.py --port 5000

) else if errorlevel 3 (
    echo.
    echo === 启动数据采集 ===
    python data_collector.py

) else if errorlevel 2 (
    echo.
    echo === 启动Web仪表板 ===
    echo.
    echo 仪表板地址: http://localhost:5000
    echo 按Ctrl+C停止服务器
    echo.
    python dashboard.py --port 5000

) else if errorlevel 1 (
    echo.
    echo === 快速测试 ===
    echo.
    python quick_start.py
)

endlocal
