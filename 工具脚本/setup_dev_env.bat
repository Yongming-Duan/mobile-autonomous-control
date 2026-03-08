@echo off
chcp 65001 >nul
cls
echo ========================================
echo    荣耀7 开发环境自动部署
echo ========================================
echo.
echo [提示] 请确保：
echo   1. 手机已完全启动
echo   2. USB线连接正常
echo   3. 已开启USB调试
echo   4. 已授权USB调试（手机上点允许）
echo.
pause

cd /d "%~dp0\..\工具软件\platform-tools"

echo.
echo ========================================
echo [1/5] 检查ADB连接...
echo ========================================
.\adb.exe kill-server
.\adb.exe start-server
.\adb.exe devices

echo.
set /p retry=如果设备未显示，按R重试，其他键继续...
if /i "%retry%"=="R" goto :retry

:retry
.\adb.exe devices
echo.

echo ========================================
echo [2/5] 检查已安装的应用...
echo ========================================
echo 检查 Termux...
.\adb.exe shell pm list packages | findstr "termux"
echo.

echo 检查 Termux:API...
.\adb.exe shell pm list packages | findstr "termux-api"
echo.

echo ========================================
echo [3/5] 安装 Termux v0.79...
echo ========================================
echo 正在安装: termux-v79-offline.apk
.\adb.exe install "%~dp0\..\APK安装包\termux-v79-offline.apk"
if %errorlevel% equ 0 (
    echo ✓ Termux 安装成功
) else (
    echo ⚠ Termux 安装失败或已存在
)
echo.

echo ========================================
echo [4/5] 安装 Termux:API...
echo ========================================
echo 正在安装: termux-api-git.apk
.\adb.exe install "%~dp0\..\APK安装包\termux-api-git.apk"
if %errorlevel% equ 0 (
    echo ✓ Termux:API 安装成功
) else (
    echo ⚠ Termux:API 安装失败或已存在
)
echo.

echo ========================================
echo [5/5] 推送验证脚本...
echo ========================================
if exist "%~dp0\verify_termux.sh" (
    .\adb.exe push "%~dp0\verify_termux.sh" /sdcard/
    echo ✓ 验证脚本已推送到 /sdcard/verify_termux.sh
) else (
    echo ⚠ 未找到 verify_termux.sh
)
echo.

if exist "%~dp0\termux_functions_test.sh" (
    .\adb.exe push "%~dp0\termux_functions_test.sh" /sdcard/
    echo ✓ 功能测试脚本已推送到 /sdcard/termux_functions_test.sh
)
echo.

echo ========================================
echo 部署完成！
echo ========================================
echo.
echo 下一步操作：
echo.
echo 1. 在手机上打开 Termux
echo.
echo 2. 首次使用需要初始化环境：
echo    termux-setup-storage
echo.
echo 3. 运行验证脚本：
echo    bash /sdcard/verify_termux.sh
echo.
echo 4. 使用 AutoGLM 自动化控制：
echo    ..\..\工具脚本\autoglm.bat "打开设置"
echo.
pause
