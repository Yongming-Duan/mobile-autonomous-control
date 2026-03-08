@echo off
setlocal EnableDelayedExpansion

set "ADB_DIR=D:\工作日常\服务器搭建\荣耀手机刷机\工具软件\platform-tools"
set "AUTOGLM_DIR=D:\工作日常\服务器搭建\荣耀手机刷机\工具软件\Open-AutoGLM"
set "PYTHONIOENCODING=utf-8"

set "PATH=!ADB_DIR!;!PATH!"

cd /d "!AUTOGLM_DIR!"

python main.py --base-url https://open.bigmodel.cn/api/paas/v4 --model autoglm-phone --apikey 1b3d58e728f84e38b8872bf09e3217f8.UTF48shlSo4dYykv %*
