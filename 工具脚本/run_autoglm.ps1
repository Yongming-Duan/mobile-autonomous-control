$env:PATH = "D:\工作日常\服务器搭建\荣耀手机刷机\工具软件\platform-tools;" + $env:PATH
$env:PYTHONIOENCODING = "utf-8"

$projectPath = "D:\工作日常\服务器搭建\荣耀手机刷机\工具软件\Open-AutoGLM"

Write-Host "Running AutoGLM to test Termux sensor..." -ForegroundColor Green
Write-Host ""

Set-Location $projectPath

python main.py --base-url https://open.bigmodel.cn/api/paas/v4 --model autoglm-phone --apikey 1b3d58e728f84e38b8872bf09e3217f8.UTF48shlSo4dYykv "Open Termux app, type command termux-sensor -l, press enter, wait 5 seconds, read the sensor list on screen, then type termux-sensor -s Accelerometer -n 1, press enter, wait 3 seconds, tell me the accelerometer values shown"

Write-Host ""
Write-Host "AutoGLM execution completed." -ForegroundColor Cyan
