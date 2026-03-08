@echo off
REM ========================================
REM AutoGLM - ADB 安装和验证脚本
REM ========================================

echo.
echo ========================================
echo AutoGLM ADB 安装检查
echo ========================================
echo.

REM 检查 ADB 是否已安装
where adb >nul 2>nul
if %errorlevel% equ 0 (
    echo [✓] ADB 已安装
    adb version
    echo.
    echo [1] 请用 USB 数据线连接手机
    echo [2] 手机上点击"允许 USB 调试"
    echo.
    pause
    echo.
    echo 正在检查设备连接...
    adb devices
    echo.
    if %errorlevel% equ 0 (
        echo [✓] 设备连接成功！
    ) else (
        echo [✗] 设备未连接，请检查：
        echo   - USB 调试是否开启
        echo   - 数据线是否支持数据传输
        echo   - 手机上是否点击了"允许"
    )
) else (
    echo [✗] ADB 未安装
    echo.
    echo 请按以下步骤安装 ADB：
    echo [1] 访问: https://developer.android.com/tools/releases/platform-tools
    echo [2] 下载 "SDK Platform-Tools for Windows"
    echo [3] 解压到 C:\platform-tools
    echo [4] 添加 C:\platform-tools 到系统 PATH 环境变量
    echo [5] 重启命令行窗口后重新运行此脚本
)

echo.
pause
