@echo off
chcp 65001 >nul
REM ========================================
REM AutoGLM 运行脚本
REM ========================================

echo.
echo ========================================
echo AutoGLM - Phone Agent
echo ========================================
echo.

REM 设置环境变量
set PYTHONIOENCODING=utf-8

REM 智谱 BigModel 配置
set PHONE_AGENT_BASE_URL=https://open.bigmodel.cn/api/paas/v4
set PHONE_AGENT_MODEL=autoglm-phone

REM 请输入你的 API Key
set /p APIKEY="请输入智谱 BigModel API Key: "

echo.
echo 已配置:
echo - API 地址: %PHONE_AGENT_BASE_URL%
echo - 模型: %PHONE_AGENT_MODEL%
echo - 设备: Android (ADB)
echo.

REM 进入项目目录
cd /d "%~dp0Open-AutoGLM"

REM 运行测试
echo ========================================
echo 正在运行测试任务...
echo ========================================
echo.

python main.py --base-url %PHONE_AGENT_BASE_URL% --model "%PHONE_AGENT_MODEL%" --apikey "%APIKEY%" "打开设置查看设备信息"

echo.
echo ========================================
echo 测试完成
echo ========================================
pause
