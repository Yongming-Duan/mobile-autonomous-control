@echo off
chcp 65001 >nul
cls
echo ========================================
echo    荣耀7 开发环境一键部署
echo ========================================
echo.

cd /d "%~dp0\..\工具软件\platform-tools"

echo [准备] 请确保：
echo   1. 手机屏幕已解锁
echo   2. USB线连接稳定
echo   3. 已授权USB调试（允许）
echo.
pause

cls
echo.
echo ========================================
echo [1/6] 检测设备...
echo ========================================

.\adb.exe kill-server
timeout /t 2 /nobreak >nul
.\adb.exe start-server
timeout /t 3 /nobreak >nul

.\adb.exe devices
echo.

:check_device
.\adb.exe shell echo "Connected" >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到设备，请检查：
    echo    - USB线是否连接
    echo    - 手机是否解锁
    echo    - USB调试是否开启
    echo.
    echo 按R重试，其他键退出...
    set /p retry=
    if /i "%retry%"=="R" (
        goto check_device
    ) else (
        exit /b 1
    )
)

echo ✅ 设备已连接
echo.

echo ========================================
echo [2/6] 获取设备信息...
echo ========================================
for /f "tokens=*" %%i in ('.\adb.exe shell getprop ro.product.model') do set MODEL=%%i
for /f "tokens=*" %%i in ('.\adb.exe shell getprop ro.build.version.release') do set ANDROID=%%i
echo 设备型号: %MODEL%
echo Android版本: %ANDROID%
echo.

echo ========================================
echo [3/6] 检查已安装应用...
echo ========================================
.\adb.exe shell pm list packages | findstr "termux" >nul
if %errorlevel% equ 0 (
    echo ✓ Termux 已安装
    set TERMUX_EXISTS=1
) else (
    echo ✗ Termux 未安装
    set TERMUX_EXISTS=0
)

.\adb.exe shell pm list packages | findstr "termux-api" >nul
if %errorlevel% equ 0 (
    echo ✓ Termux:API 已安装
    set API_EXISTS=1
) else (
    echo ✗ Termux:API 未安装
    set API_EXISTS=0
)
echo.

if %TERMUX_EXISTS%==0 (
    echo ========================================
    echo [4/6] 安装 Termux v0.79...
    echo ========================================
    echo 正在安装: termux-v79-offline.apk
    .\adb.exe install -r "%~dp0\..\APK安装包\termux-v79-offline.apk"
    if %errorlevel% equ 0 (
        echo ✅ Termux 安装成功
    ) else (
        echo ⚠ Termux 安装失败
    )
    echo.
) else (
    echo [4/6] 跳过 Termux 安装（已存在）
    echo.
)

if %API_EXISTS%==0 (
    echo ========================================
    echo [5/6] 安装 Termux:API...
    echo ========================================
    echo 正在安装: termux-api-git.apk
    .\adb.exe install -r "%~dp0\..\APK安装包\termux-api-git.apk"
    if %errorlevel% equ 0 (
        echo ✅ Termux:API 安装成功
    ) else (
        echo ⚠ Termux:API 安装失败
    )
    echo.
) else (
    echo [5/6] 跳过 Termux:API 安装（已存在）
    echo.
)

echo ========================================
echo [6/6] 推送脚本文件...
echo ========================================

if exist "%~dp0\verify_termux.sh" (
    .\adb.exe push "%~dp0\verify_termux.sh" /sdcard/
    echo ✅ verify_termux.sh → /sdcard/
)

if exist "%~dp0\termux_functions_test.sh" (
    .\adb.exe push "%~dp0\termux_functions_test.sh" /sdcard/
    echo ✅ termux_functions_test.sh → /sdcard/
)

if exist "%~dp0\fix_legacy_sources.sh" (
    .\adb.exe push "%~dp0\fix_legacy_sources.sh" /sdcard/
    echo ✅ fix_legacy_sources.sh → /sdcard/
)

echo.
echo ========================================
echo 🎉 部署完成！
echo ========================================
echo.
echo 下一步操作：
echo.
echo 1️⃣ 在手机上打开 Termux
echo.
echo 2️⃣ 首次使用运行：
echo    termux-setup-storage
echo.
echo 3️⃣ 验证环境：
echo    bash /sdcard/verify_termux.sh
echo.
echo 4️⃣ 测试功能：
echo    bash /sdcard/termux_functions_test.sh
echo.
echo 5️⃣ 使用 AutoGLM：
echo    ..\autoglm.bat "打开设置"
echo.
echo ========================================
pause
