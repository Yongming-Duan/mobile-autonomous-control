@echo off
chcp 65001 >nul
echo ========================================
echo    荣耀7 Fastboot 救援和刷机工具
echo    设备: PLK-AL10 (荣耀7 全网通)
echo ========================================
echo.

cd /d "%~dp0\..\工具软件\platform-tools"

echo [检测] Fastboot设备状态...
.\fastboot.exe devices
echo.

echo ========================================
echo 当前设备已在 Fastboot 模式
echo 序列号: D8YDU15A14002124
echo ========================================
echo.
echo 请选择操作：
echo.
echo [1] 重启到正常模式
echo     fastboot reboot
echo.
echo [2] 重启到Recovery模式
echo     fastboot reboot recovery
echo.
echo [3] 查看设备信息
echo     fastboot getvar product
echo.
echo [4] 刷入 recovery.img (需要文件)
echo     fastboot flash recovery recovery.img
echo.
echo [5] 刷入 boot.img (需要文件)
echo     fastboot flash boot boot.img
echo.
echo [6] 刷入系统 (需要完整ROM包)
echo     fastboot flash system system.img
echo.
echo [7] 擦除数据 (恢复出厂)
echo     fastboot -w
echo.
echo [8] 刷入完整官方ROM (需要ROM文件)
echo.
echo [0] 退出
echo.
set /p choice=请输入选项:

if "%choice%"=="1" (
    echo 正在重启设备...
    .\fastboot.exe reboot
)

if "%choice%"=="2" (
    echo 正在重启到Recovery...
    .\fastboot.exe reboot recovery
)

if "%choice%"=="3" (
    echo 获取设备信息...
    .\fastboot.exe getvar product
    .\fastboot.exe getvar version
    .\fastboot.exe getvar all
)

if "%choice%"=="4" (
    echo 请将 recovery.img 放在当前目录
    set /p recovery_file=输入recovery文件名:
    if exist "%recovery_file%" (
        echo 正在刷入 recovery...
        .\fastboot.exe flash recovery %recovery_file%
        echo 完成！
    ) else (
        echo 文件不存在！
    )
)

if "%choice%"=="5" (
    echo 请将 boot.img 放在当前目录
    set /p boot_file=输入boot文件名:
    if exist "%boot_file%" (
        echo 正在刷入 boot...
        .\fastboot.exe flash boot %boot_file%
        echo 完成！
    ) else (
        echo 文件不存在！
    )
)

if "%choice%"=="6" (
    echo 警告：此操作将清除所有用户数据！
    set /p confirm=确认继续？(Y/N):
    if /i "%confirm%"=="Y" (
        echo 正在擦除数据...
        .\fastboot.exe -w
        echo 完成！
    )
)

if "%choice%"=="7" (
    echo 警告：此操作将清除所有用户数据！
    set /p confirm=确认继续？(Y/N):
    if /i "%confirm%"=="Y" (
        echo 正在擦除数据分区...
        .\fastboot.exe format data
        .\fastboot.exe format cache
        echo 完成！
    )
)

if "%choice%"=="8" (
    echo.
    echo 官方ROM下载地址：
    echo 1. ONFIX: https://onfix.cn/rom/523365
    echo 2. 奇兔刷机: rom.7to.cn
    echo.
    echo 将下载的ROM解压到当前目录
    pause
    dir /b *.img
    echo.
    echo 开始刷入系统镜像...
    set /p system_file=输入system镜像文件名:
    if exist "%system_file%" (
        echo 正在刷入 system...
        .\fastboot.exe flash system %system_file%
        echo 正在刷入 boot...
        .\fastboot.exe flash boot boot.img
        echo 擦除数据...
        .\fastboot.exe -w
        echo 重启设备...
        .\fastboot.exe reboot
        echo 刷机完成！
    )
)

pause
