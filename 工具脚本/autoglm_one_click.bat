@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ========================================
REM AutoGLM 一键启动（带ADB稳定管理）
REM ========================================

cls
echo ========================================
echo    AutoGLM 一键启动器
echo    （含ADB连接优化）
echo ========================================
echo.

cd /d "%~dp0"

REM 设置路径
set "ADB_PATH=%~dp0platform-tools"
set "PATH=%ADB_PATH%;%PATH%"

REM ========================================
REM 第一阶段：ADB连接优化
REM ========================================

echo [阶段1] 优化ADB连接...
echo.

echo [1/5] 清理旧进程...
taskkill /F /IM adb.exe >nul 2>&1
timeout /t 1 /nobreak >nul
echo ✅ 完成
echo.

echo [2/5] 启动ADB服务...
"%ADB_PATH%\adb.exe" kill-server >nul 2>&1
timeout /t 2 /nobreak >nul
"%ADB_PATH%\adb.exe" start-server
timeout /t 3 /nobreak >nul
echo ✅ 完成
echo.

echo [3/5] 检测设备...
"%ADB_PATH%\adb.exe" devices
echo.

:device_check
"%ADB_PATH%\adb.exe" shell "echo test" >nul 2>&1
if errorlevel 1 (
    echo ❌ 设备未连接
    echo.
    echo 请检查：
    echo   - USB线是否连接
    echo   - 手机是否解锁
    echo   - USB调试是否开启
    echo.
    set /p retry=设备准备好后按R重试，其他键退出...
    if /i "!retry!"=="R" (
        goto device_check
    ) else (
        exit /b 1
    )
)

echo ✅ 设备已连接
echo.

echo [4/5] 优化连接参数...
REM 保持设备唤醒
"%ADB_PATH%\adb.exe" shell settings put global stay_on_while_plugged_in 7 2>nul
REM 延长ADB超时
"%ADB_PATH%\adb.exe" shell settings put global adb_timeout 7200000 2>nul
echo ✅ 完成
echo.

echo [5/5] 获取设备信息...
for /f "tokens=*" %%i in ('"%ADB_PATH%\adb.exe" shell getprop ro.product.model 2^>nul') do set MODEL=%%i
for /f "tokens=*" %%i in ('"%ADB_PATH%\adb.exe" shell getprop ro.build.version.release 2^>nul') do set ANDROID=%%i
echo   设备: %MODEL%
echo   Android: %ANDROID%
echo ✅ 完成
echo.

REM ========================================
REM 第二阶段：运行AutoGLM
REM ========================================

echo ========================================
echo [阶段2] 准备运行 AutoGLM
echo ========================================
echo.

REM 检查参数
if "%~1"=="" (
    echo 请输入任务描述（或直接回车使用默认任务）:
    set /p TASK=
    if "!TASK!"=="" set TASK=打开设置查看设备信息
) else (
    set TASK=%~1
)

echo 任务: !TASK!
echo.

REM 进入AutoGLM目录
cd /d "%~dp0Open-AutoGLM"

REM 配置API
set PHONE_AGENT_BASE_URL=https://open.bigmodel.cn/api/paas/v4
set PHONE_AGENT_MODEL=autoglm-phone
set PHONE_AGENT_API_KEY=1b3d58e728f84e38b8872bf09e3217f8.UTF48shlSo4dYykv
set PYTHONIOENCODING=utf-8

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装
    echo 请先安装Python: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ========================================
echo 正在执行任务...
echo ========================================
echo.

REM 运行AutoGLM
python main.py --base-url %PHONE_AGENT_BASE_URL% --model "%PHONE_AGENT_MODEL%" --apikey "%PHONE_AGENT_API_KEY%" "!TASK"

set EXIT_CODE=%errorlevel%

echo.
echo ========================================
echo 任务执行完成
echo ========================================
echo.

REM 检查连接状态
"%ADB_PATH%\adb.exe" shell "echo test" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ 设备已断开，正在恢复连接...
    "%ADB_PATH%\adb.exe" kill-server
    timeout /t 2 /nobreak >nul
    "%ADB_PATH%\adb.exe" start-server
    echo ✅ ADB服务已重启
) else (
    echo ✅ 设备连接正常
)

echo.
echo 返回代码: %EXIT_CODE%
echo.

REM 询问是否继续
set /p continue=继续运行其他任务？(Y/N):
if /i "!continue!"=="Y" (
    cls
    goto :device_check
)

echo.
echo 感谢使用！
timeout /t 2 /nobreak >nul
