@echo off
chcp 65001 >nul
REM ========================================
REM Termux 安装脚本
REM ========================================

echo.
echo ========================================
echo Termux 安装指南
echo ========================================
echo.
echo 由于网络限制，请选择以下方式之一安装 Termux：
echo.
echo [方式 1] 从应用商店安装（推荐）
echo   - 打开手机应用商店（华为应用市场、应用宝等）
echo   - 搜索 "Termux" 并安装
echo   - 搜索 "Termux:API" 并安装
echo.
echo [方式 2] 手动下载 APK
echo   Termux: https://f-droid.org/packages/com.termux/
echo   Termux:API: https://f-droid.org/packages/com.termux.api/
echo.
echo [方式 3] 通过 ADB 安装（如果你已有 APK 文件）
echo   将 APK 文件放到当前目录，然后运行此脚本
echo.
echo ========================================
echo.

set "PATH=%~dp0platform-tools;%PATH%"

REM 检查是否有 APK 文件
if exist "termux.apk" (
    echo [!] 发现 termux.apk，正在安装...
    adb install -r termux.apk
)

if exist "termux-api.apk" (
    echo [!] 发现 termux-api.apk，正在安装...
    adb install -r termux-api.apk
)

echo.
echo 安装完成后，请运行以下命令配置 Termux：
echo   1. 打开 Termux 应用
echo   2. 运行: pkg update && pkg upgrade
echo   3. 运行: pkg install termux-api
echo   4. 给予 Termux 存储和相机权限
echo.

pause
