@echo off
setlocal

REM ============================================
REM Mobile Autonomous Control System - Launcher
REM ============================================

echo.
echo ============================================================
echo           Mobile Autonomous Control System
echo                    Auto Launcher
echo ============================================================
echo.

REM Set paths
set "ADB_PATH=D:\工作日常\服务器搭建\荣耀手机刷机\工具软件\platform-tools"
set "SCRIPT_PATH=D:\工作日常\服务器搭建\荣耀手机刷机\工具脚本"

REM Change to script directory
cd /d "%SCRIPT_PATH%"

REM Step 1: Check ADB
echo [Step 1/6] Checking ADB connection...
echo.
cd /d "%ADB_PATH%"
adb.exe devices
echo.
if errorlevel 1 (
    echo [ERROR] ADB not connected
    echo.
    echo Please check:
    echo   1. Phone is connected via USB
    echo   2. USB debugging is enabled
    echo.
    pause
    exit /b 1
)
echo [OK] ADB connected
echo.

REM Step 2: Setup port forwarding
echo [Step 2/6] Setting up port forwarding...
adb.exe forward tcp:9999 tcp:9999
echo [OK] Port forwarding configured
echo.

REM Step 3: Check sensor server
echo [Step 3/6] Checking sensor server...
cd /d "%SCRIPT_PATH%"

REM Try to ping the server
python -c "import requests; requests.get('http://127.0.0.1:9999/health', timeout=3)" 2>nul

if errorlevel 1 (
    echo.
    echo ============================================================
    echo           SENSOR SERVER NOT RUNNING
    echo ============================================================
    echo.
    echo Please start the sensor server on your phone:
    echo.
    echo   1. Open Termux on your phone
    echo   2. Run: cd /sdcard
    echo   3. Run: python enhanced_sensor_server.py
    echo   4. Keep Termux open
    echo.
    echo ============================================================
    echo.
    echo I will wait for the server to start...
    echo Press any key when server is ready, or wait for auto-detect
    echo.

    REM Wait for 60 seconds with auto-check
    for /L %%i in (1,1,12) do (
        echo Checking... (%%i/12)
        timeout /t 5 /nobreak >nul

        REM Try to connect
        python -c "import requests; requests.get('http://127.0.0.1:9999/health', timeout=2)" 2>nul
        if not errorlevel 1 (
            echo.
            echo [OK] Server detected!
            goto :server_found
        )
    )

    echo.
    echo [WARN] Server not detected after timeout. Continuing anyway...
) else (
    echo [OK] Sensor server is running
)

:server_found
echo.

REM Step 4: Install dependencies
echo [Step 4/6] Checking dependencies...
echo.

python -c "import requests" 2>nul
if errorlevel 1 (
    echo Installing requests...
    pip install requests
)

python -c "import flask" 2>nul
if errorlevel 1 (
    echo Installing flask...
    pip install flask
)

python -c "import flask_socketio" 2>nul
if errorlevel 1 (
    echo Installing flask-socketio...
    pip install flask-socketio
)

echo [OK] Dependencies ready
echo.

REM Step 5: Test API
echo [Step 5/6] Testing API...
python -c "import requests; r=requests.get('http://127.0.0.1:9999/health'); print('[OK] Health check:', r.json().get('status'))" 2>nul
python -c "import requests; r=requests.get('http://127.0.0.1:9999/battery'); print('[OK] Battery:', r.json().get('battery',{}).get('percentage'), '%')" 2>nul
echo.

REM Step 6: Start dashboard
echo [Step 6/6] Starting Web Dashboard...
echo.
echo ============================================================
echo.
echo   Dashboard URL: http://localhost:5000
echo.
echo   Press Ctrl+C to stop the server
echo.
echo ============================================================
echo.

REM Open in browser
start http://localhost:5000

REM Start dashboard
python dashboard.py --port 5000

endlocal
