@echo off
REM ============================================
REM 手机自主化控制系统 - 一键启动脚本
REM Mobile Autonomous Control System - Quick Start
REM ============================================

setlocal enabledelayedexpansion

REM 颜色定义
set "INFO=[92m"    % Green
set "WARN=[93m"    % Yellow
set "ERROR=[91m"   % Red
set "RESET=[0m"    % Reset

echo.
echo ============================================================
echo           手机自主化控制系统 - 快速启动
echo     Mobile Autonomous Control System - Quick Start
echo ============================================================
echo.

REM 检查ADB
echo %INFO%[1/5] 检查ADB连接...%RESET%
cd ..\工具软件\platform-tools
adb.exe devices | findstr "device" >nul
if errorlevel 1 (
    echo %ERROR%   ❌ ADB设备未连接！%RESET%
    echo.
    echo 请确保:
    echo   1. 手机已通过USB连接
    echo   2. USB调试已开启
    echo   3. 已授权此电脑进行USB调试
    echo.
    pause
    exit /b 1
)
echo %INFO%   ✅ ADB连接正常%RESET%

REM 设置端口转发
echo.
echo %INFO%[2/5] 设置端口转发...%RESET%
adb.exe forward tcp:9999 tcp:9999 2>nul
echo %INFO%   ✅ 端口转发已配置 (9999)%RESET%

REM 检查Termux服务器
echo.
echo %INFO%[3/5] 检查传感器服务器...%RESET%
cd ..\..\工具脚本
curl -s http://127.0.0.1:9999/health >nul 2>&1
if errorlevel 1 (
    echo %WARN%   ⚠️ 传感器服务器未运行！%RESET%
    echo.
    echo 请在手机Termux中执行:
    echo   cd /sdcard
    echo   python enhanced_sensor_server.py
    echo.
    choice /C YN /M "是否继续启动其他组件"
    if errorlevel 2 exit /b 1
) else (
    echo %INFO%   ✅ 传感器服务器运行正常%RESET%
)

REM 启动数据采集
echo.
echo %INFO%[4/5] 启动数据采集...%RESET%
echo.

REM 创建启动脚本
echo import sys > temp_collector.py
echo sys.path.insert(0, r'%CD%') >> temp_collector.py
echo from phone_controller import PhoneController >> temp_collector.py
echo from data_collector import SensorDataCollector >> temp_collector.py
echo. >> temp_collector.py
echo controller = PhoneController() >> temp_collector.py
echo collector = SensorDataCollector(controller, collection_interval=10) >> temp_collector.py
echo. >> temp_collector.py
echo def on_data(sensor, values): >> temp_collector.py
echo     print(f'{sensor}: {values}') >> temp_collector.py
echo. >> temp_collector.py
echo collector.add_callback(on_data) >> temp_collector.py
echo print('Starting data collection... Press Ctrl+C to stop') >> temp_collector.py
echo collector.start(['accelerometer', 'light', 'battery']) >> temp_collector.py
echo. >> temp_collector.py
echo try: >> temp_collector.py
echo     import time >> temp_collector.py
echo     while True: >> temp_collector.py
echo         time.sleep(1) >> temp_collector.py
echo except KeyboardInterrupt: >> temp_collector.py
echo     collector.stop() >> temp_collector.py
echo     print('\nStopped') >> temp_collector.py

start /MIN python temp_collector.py
echo %INFO%   ✅ 数据采集已启动%RESET%

REM 等待几秒让采集器初始化
timeout /t 3 /nobreak >nul

REM 启动Web仪表板
echo.
echo %INFO%[5/5] 启动Web仪表板...%RESET%
echo.

REM 检查Flask是否安装
python -c "import flask" 2>nul
if errorlevel 1 (
    echo %WARN%   ⚠️ Flask未安装，正在安装...%RESET%
    pip install flask flask-socketio
)

echo %INFO%   启动仪表板服务器...%RESET%
echo.
echo %INFO%   仪表板地址: http://localhost:5000%RESET%
echo %INFO%   按Ctrl+C停止服务器%RESET%
echo.

REM 清理临时文件
del temp_collector.py 2>nul

REM 启动仪表板
python dashboard.py --port 5000

endlocal
