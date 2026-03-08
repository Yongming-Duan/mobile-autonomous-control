@echo off
chcp 65001 >nul
setlocal

set "ADB_PATH=D:\工作日常\服务器搭建\荣耀手机刷机\工具软件\platform-tools"
set "PROJECT_PATH=D:\工作日常\服务器搭建\荣耀手机刷机\工具软件\Open-AutoGLM"
set "PYTHONIOENCODING=utf-8"

set "PATH=%ADB_PATH%;%PATH%"

echo Running AutoGLM to test Termux sensor...
echo.
echo ADB Path: %ADB_PATH%
echo Project Path: %PROJECT_PATH%
echo.

pushd "%PROJECT_PATH%"
python main.py --base-url https://open.bigmodel.cn/api/paas/v4 --model autoglm-phone --apikey 1b3d58e728f84e38b8872bf09e3217f8.UTF48shlSo4dYykv "Open Termux app, type command termux-sensor -l, press enter, wait 5 seconds, read the sensor list on screen, then type termux-sensor -s Accelerometer -n 1, press enter, wait 3 seconds, tell me the accelerometer values shown"
popd

echo.
echo AutoGLM execution completed.
pause
