@echo off
chcp 65001 >nul
echo ========================================
echo    荣耀手机救援和恢复工具
echo ========================================
echo.

cd /d "%~dp0\..\工具软件\platform-tools"

echo [1/5] 检查ADB服务...
.\adb.exe start-server
echo.

echo [2/5] 检测设备连接...
.\adb.exe devices
echo.

echo [3/5] 获取设备信息...
for /f "tokens=*" %%i in ('.\adb.exe shell getprop ro.product.model 2^>nul') do set MODEL=%%i
for /f "tokens=*" %%i in ('.\adb.exe shell getprop ro.build.version.release 2^>nul') do set ANDROID_VER=%%i
for /f "tokens=*" %%i in ('.\adb.exe shell getprop ro.product.androidhints 2^>nul') do set API_LEVEL=%%i

if not "%MODEL%"=="" (
    echo 设备型号: %MODEL%
    echo Android版本: %ANDROID_VER%
    echo API级别: %API_LEVEL%
    echo.
) else (
    echo ⚠️ 未检测到设备，请检查：
    echo    1. USB线是否连接
    echo    2. 手机是否开启USB调试
    echo    3. 是否已允许USB调试
    echo.
    pause
    exit /b 1
)

echo [4/5] 检查已安装应用...
echo 检查 Termux...
.\adb.exe shell pm list packages | findstr "termux" && (
    echo ✓ Termux 已安装
) || (
    echo ✗ Termux 未安装
)

echo.
echo 检查 Termux:API...
.\adb.exe shell pm list packages | findstr "termux-api" && (
    echo ✓ Termux:API 已安装
) || (
    echo ✗ Termux:API 未安装
)

echo.
echo [5/5] 设备状态诊断...
echo.
echo === 电池状态 ===
.\adb.exe shell dumpsys battery | findstr "level status"
echo.
echo === 存储状态 ===
.\adb.exe shell df /sdcard | findstr "/sdcard"
echo.

echo ========================================
echo 诊断完成！
echo ========================================
echo.
echo 可用命令：
echo   - 安装Termux:     install_termux.bat
echo   - 验证Termux:     运行 bash /sdcard/verify_termux.sh
echo   - 启动AutoGLM:    autoglm.bat "任务描述"
echo   - 查看截图:      .\adb.exe shell screencap -p /sdcard/screen.png
echo.
pause
