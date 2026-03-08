@echo off
chcp 65001 >nul
cls
echo ========================================
echo    ADB连接完整诊断工具
echo ========================================
echo.

cd /d "%~dp0\..\工具软件\platform-tools"

echo [诊断1] 检查ADB服务状态...
.\adb.exe version
echo.

echo [诊断2] 重启ADB服务...
.\adb.exe kill-server
timeout /t 2 /nobreak >nul
.\adb.exe start-server
timeout /t 3 /nobreak >nul
echo.

echo [诊断3] 检测设备连接...
.\adb.exe devices
echo.

echo [诊断4] 尝试列出所有设备...
.\adb.exe devices -l
echo.

echo ========================================
echo 故障排除建议
echo ========================================
echo.
echo 如果设备未显示，请检查：
echo.
echo 📱 手机端检查：
echo   1. USB线是否插紧
echo   2. 设置 → 开发者选项 → USB调试 (开启)
echo   3. USB调试安全设置 → 撤销USB调试授权 (重试)
echo   4. 屏幕是否解锁
echo.
echo 💻 电脑端检查：
echo   1. 设备管理器 → 查看便携设备
echo   2. 尝试更换USB端口（建议USB 2.0）
echo   3. 尝试更换USB数据线
echo   4. 重新安装ADB驱动
echo.
echo 🔧 手动尝试：
echo   1. 在手机上：关闭USB调试 → 等待3秒 → 开启USB调试
echo   2. 拔掉USB线 → 重新插入
echo   3. 手机弹出授权窗口 → 勾选"始终允许" → 点击允许
echo   4. 解锁手机屏幕
echo.
echo ========================================
echo 按任意键重新检测...
pause >nul

cls
.\adb.exe devices
echo.

if errorlevel 1 (
    echo ❌ 仍未检测到设备
    echo.
    echo 请尝试以下操作：
    echo.
    echo 1. 打开设备管理器
    echo    Win + X → 设备管理器
    echo.
    echo 2. 查找 Android ADB Interface 或便携设备
    echo.
    echo 3. 右键 → 更新驱动程序
    echo.
    echo 4. 选择：浏览计算机以查找驱动程序
    echo.
    echo 5. 指向：%~dp0
    echo.
) else (
    echo ✅ 设备已连接！
    echo.
    echo 正在获取设备信息...
    .\adb.exe shell "getprop ro.product.model && getprop ro.build.version.release"
    echo.
    echo 现在可以运行 AutoGLM：
    echo   ..\..\工具脚本\autoglm.bat "打开设置"
)

echo.
pause
