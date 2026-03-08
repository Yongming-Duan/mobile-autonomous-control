@echo off
chcp 65001 >nul
setlocal

REM ========================================
REM AutoGLM 快速启动脚本
REM ========================================

REM 添加 ADB 到 PATH
set "PATH=%~dp0platform-tools;%PATH%"

REM 设置编码
set PYTHONIOENCODING=utf-8

REM 智谱 BigModel 配置
set PHONE_AGENT_BASE_URL=https://open.bigmodel.cn/api/paas/v4
set PHONE_AGENT_MODEL=autoglm-phone
set PHONE_AGENT_API_KEY=1b3d58e728f84e38b8872bf09e3217f8.UTF48shlSo4dYykv

echo ========================================
echo AutoGLM - Phone Agent
echo ========================================
echo.

REM 进入项目目录
cd /d "%~dp0Open-AutoGLM"

REM 检查参数
if "%~1"=="" (
    echo 使用方法:
    echo   autoglm.bat "你的任务描述"
    echo.
    echo 示例:
    echo   autoglm.bat "打开微信发消息"
    echo   autoglm.bat "打开美团搜索附近的火锅店"
    echo   autoglm.bat "打开淘宝搜索无线耳机"
    echo.
    echo 交互模式（无参数）:
    echo   autoglm.bat interactive
    echo.
    pause
    exit /b 0
)

if "%~1"=="interactive" (
    python main.py --base-url %PHONE_AGENT_BASE_URL% --model "%PHONE_AGENT_MODEL%" --apikey "%PHONE_AGENT_API_KEY%"
) else (
    python main.py --base-url %PHONE_AGENT_BASE_URL% --model "%PHONE_AGENT_MODEL%" --apikey "%PHONE_AGENT_API_KEY%" %*
)
