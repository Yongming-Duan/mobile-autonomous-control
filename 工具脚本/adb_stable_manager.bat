@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ========================================
REM ADB稳定连接管理器
REM 解决AutoGLM运行时ADB断连问题
REM ========================================

echo ========================================
echo    ADB稳定连接管理器
echo ========================================
echo.

cd /d "%~dp0\..\工具软件\platform-tools"

echo [步骤1] 清理旧的ADB进程...
taskkill /F /IM adb.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo ✅ 旧进程已清理
echo.

echo [步骤2] 设置ADB环境变量...
set "ADB_PATH=%~dp0"
set "PATH=%ADB_PATH%;%PATH%"
echo ✅ ADB路径: %ADB_PATH%
echo.

echo [步骤3] 启动ADB服务...
.\adb.exe kill-server >nul 2>&1
timeout /t 2 /nobreak >nul
.\adb.exe start-server
timeout /t 3 /nobreak >nul
echo ✅ ADB服务已启动
echo.

echo [步骤4] 检测设备连接...
.\adb.exe devices
echo.

:check_device
.\adb.exe shell "echo connected" >nul 2>&1
if errorlevel 1 (
    echo ❌ 设备未连接或已断开
    echo.
    echo 请确保：
    echo   1. USB线已连接
    echo   2. 手机已解锁
    echo   3. USB调试已开启
    echo   4. 已授权USB调试
    echo.
    echo 按R重试，其他键退出...
    set /p retry=
    if /i "!retry!"=="R" (
        .\adb.exe kill-server
        timeout /t 2 /nobreak >nul
        .\adb.exe start-server
        timeout /t 3 /nobreak >nul
        goto check_device
    ) else (
        exit /b 1
    )
)

echo ✅ 设备已连接
echo.

echo [步骤5] 获取设备信息...
for /f "tokens=*" %%i in ('.\adb.exe shell getprop ro.product.model') do set MODEL=%%i
for /f "tokens=*" %%i in ('.\adb.exe shell getprop ro.build.version.release') do set ANDROID_VER=%%i
for /f "tokens=*" %%i in ('.\adb.exe shell getprop ro.build.version.sdk') do set API_LEVEL=%%i
echo   设备型号: %MODEL%
echo   Android版本: %ANDROID_VER%
echo   API级别: %API_LEVEL%
echo.

echo [步骤6] 优化ADB连接参数...
REM 设置更长的超时时间
.\adb.exe shell settings put global adb_allowed_connection_time 86400000 2>nul
REM 禁用省电模式对ADB的影响
.\adb.exe shell settings put global stay_on_while_plugged_in 7 2>nul
echo ✅ ADB参数已优化
echo.

echo ========================================
echo 连接优化完成！
echo ========================================
echo.
echo 现在可以安全地运行：
echo   1. .\autoglm.bat "任务描述"
echo   2. AutoGLM不会断开ADB连接
echo.
echo 保持此窗口打开以维持连接
echo ========================================
echo.
echo 按Q退出，其他键保持连接...
set /p keep_open=
if /i "!keep_open!"=="Q" (
    .\adb.exe kill-server
    exit /b 0
)

REM 保持连接模式
echo.
echo [保持连接模式] 每30秒检测一次连接状态...
echo 按Ctrl+C退出
echo.

:keep_alive
.\adb.exe shell "echo ping" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ 连接断开，尝试重连...
    .\adb.exe kill-server
    timeout /t 2 /nobreak >nul
    .\adb.exe start-server
    timeout /t 3 /nobreak >nul
) else (
    echo ✓ [%time%] 连接正常
)
timeout /t 30 /nobreak >nul
goto keep_alive
