@echo off
chcp 65001 >nul
setlocal

REM ========================================
REM AutoGLM 稳定版启动脚本
REM 解决ADB断连问题
REM ========================================

echo ========================================
echo    AutoGLM 稳定版启动器
echo ========================================
echo.

REM 设置工作目录
set "WORK_DIR=%~dp0"
cd /d "%WORK_DIR%"

REM 添加 ADB 到 PATH（使用绝对路径）
set "ADB_PATH=%~dp0platform-tools"
set "PATH=%ADB_PATH%;%PATH%"

REM 设置Python编码
set PYTHONIOENCODING=utf-8

REM 智谱 BigModel 配置
set PHONE_AGENT_BASE_URL=https://open.bigmodel.cn/api/paas/v4
set PHONE_AGENT_MODEL=autoglm-phone
set PHONE_AGENT_API_KEY=1b3d58e728f84e38b8872bf09e3217f8.UTF48shlSo4dYykv

echo [准备] 检查ADB连接...
echo.

REM 确保ADB服务正常运行
"%ADB_PATH%\adb.exe" start-server >nul 2>&1
timeout /t 2 /nobreak >nul

REM 检查设备连接
"%ADB_PATH%\adb.exe" devices | findstr "device" >nul
if errorlevel 1 (
    echo ❌ 未检测到设备
    echo.
    echo 请确保：
    echo   1. USB线已连接
    echo   2. 手机已解锁
    echo   3. USB调试已开启
    echo.
    echo 正在尝试重新连接...
    "%ADB_PATH%\adb.exe" kill-server
    timeout /t 2 /nobreak >nul
    "%ADB_PATH%\adb.exe" start-server
    timeout /t 3 /nobreak >nul

    "%ADB_PATH%\adb.exe" devices | findstr "device" >nul
    if errorlevel 1 (
        echo ❌ 仍无法连接，请运行 adb_stable_manager.bat
        pause
        exit /b 1
    )
)

echo ✅ 设备已连接
echo.

REM 获取设备信息
for /f "tokens=*" %%i in ('"%ADB_PATH%\adb.exe" shell getprop ro.product.model 2^>nul') do set MODEL=%%i
echo 设备: %MODEL%
echo.

echo ========================================
echo 准备运行 AutoGLM
echo ========================================
echo.
echo 任务: %~1
echo.

REM 检查参数
if "%~1"=="" (
    echo 使用方法:
    echo   autoglm_stable.bat "你的任务描述"
    echo.
    echo 示例:
    echo   autoglm_stable.bat "打开设置查看设备信息"
    echo   autoglm_stable.bat "打开相机拍照"
    echo   autoglm_stable.bat "打开微信"
    echo.
    pause
    exit /b 0
)

REM 进入项目目录
cd /d "%~dp0Open-AutoGLM"

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未加入PATH
    echo 请先安装Python: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ========================================
echo 执行任务中...
echo ========================================
echo.

REM 运行AutoGLM
python main.py --base-url %PHONE_AGENT_BASE_URL% --model "%PHONE_AGENT_MODEL%" --apikey "%PHONE_AGENT_API_KEY%" %*

echo.
echo ========================================
echo 任务完成
echo ========================================
echo.

REM 检查设备是否还连接
"%ADB_PATH%\adb.exe" devices | findstr "device" >nul
if errorlevel 1 (
    echo ⚠️ 设备已断开连接
    echo 正在重启ADB服务...
    "%ADB_PATH%\adb.exe" kill-server
    timeout /t 2 /nobreak >nul
    "%ADB_PATH%\adb.exe" start-server
    echo ✅ ADB服务已重启
) else (
    echo ✅ 设备连接正常
)

echo.
pause
