@echo off
chcp 65001 >nul
cls
echo ========================================
echo    ADB连接诊断工具
echo ========================================
echo.

cd /d "%~dp0\..\工具软件\platform-tools"

echo [步骤1] 重启ADB服务...
.\adb.exe kill-server
timeout /t 2 /nobreak >nul
.\adb.exe start-server
timeout /t 3 /nobreak >nul
echo.

echo [步骤2] 检测设备...
.\adb.exe devices
echo.

echo [步骤3] 检查USB设备...
powershell -Command "Get-PnpDevice -Class USB | Where-Object {$_.FriendlyName -like '*Android*' -or $_.FriendlyName -like '*Huawei*' -or $_.FriendlyName -like '*Honor*'} | Format-Table FriendlyName, Status -AutoSize"
echo.

echo ========================================
echo 如果未检测到设备，请尝试以下步骤：
echo ========================================
echo.
echo 1. 手机操作：
echo    - 进入 设置 → 开发者选项
echo    - 关闭"USB调试"，等待3秒
echo    - 重新开启"USB调试"
echo    - 连接USB时，手机会弹出授权窗口
echo    - 勾选"始终允许"并点击【允许】
echo.
echo 2. 电脑操作：
echo    - 更换USB端口（尝试USB 2.0端口）
echo    - 更换USB数据线
echo    - 重新插拔USB线
echo.
echo 3. 驱动问题：
echo    - 打开设备管理器
echo    - 查找"Android"或"未知设备"
echo    - 右键 → 更新驱动程序
echo    - 浏览计算机 → 选择本目录
echo.

echo 按任意键重新检测...
pause >nul

.\adb.exe devices
echo.

if errorlevel 1 (
    echo ❌ 仍未检测到设备
    echo.
    echo 最后的尝试：
    echo.\adb.exe usb
) else (
    echo ✅ 设备已连接！
    echo.
    echo 正在获取设备信息...
    .\adb.exe shell getprop ro.build.version.release
    .\adb.exe shell getprop ro.product.model
)

pause
