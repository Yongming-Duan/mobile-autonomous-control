@echo off
setlocal

REM ============================================================
REM GitHub Repository Push Script
REM 手机自主化控制系统 - GitHub 推送脚本
REM ============================================================

echo.
echo ============================================================
echo           GitHub Repository Push Script
echo ============================================================
echo.

cd /d "D:\工作日常\服务器搭建\荣耀手机刷机"

echo [Step 1/5] Checking repository status...
echo.

REM Show current branch
git branch -vv
echo.

REM Check for uncommitted changes
git status --short
echo.

echo [Step 2/5] GitHub Repository Information
echo.
echo Please provide your GitHub information:
echo.
set /p GITHUB_USERNAME="GitHub username: "
set /p REPO_NAME="Repository name (default: mobile-autonomous-control): "

if "%REPO_NAME%"=="" set REPO_NAME=mobile-autonomous-control

echo.
echo Repository will be created at:
echo https://github.com/%GITHUB_USERNAME%/%REPO_NAME%
echo.

set /p CONFIRM="Continue? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo Aborted.
    pause
    exit /b 1
)

echo.
echo [Step 3/5] Creating GitHub Repository...
echo.
echo Please create the repository manually:
echo.
echo 1. Visit: https://github.com/new
echo 2. Repository name: %REPO_NAME%
echo 3. Description: Mobile Autonomous Control System - Complete Android phone control
echo 4. Choose Public or Private
echo 5. DO NOT initialize with README, .gitignore, or LICENSE
echo 6. Click "Create repository"
echo.
pause

echo.
echo [Step 4/5] Configuring remote repository...
echo.

REM Remove old origin if exists
git remote remove origin 2>nul

REM Add new remote
set REMOTE_URL=https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git
git remote add origin %REMOTE_URL%

echo Remote added: %REMOTE_URL%
echo.

echo [Step 5/5] Pushing to GitHub...
echo.
echo This may take a few minutes...
echo.

REM Push master branch
echo Pushing master branch...
git push -u origin master

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to push master branch.
    echo.
    echo You may need to authenticate. Options:
    echo.
    echo 1. Personal Access Token:
    echo    - Create at: https://github.com/settings/tokens
    echo    - Select 'repo' scope
    echo    - Use token as password when prompted
    echo.
    echo 2. SSH Key:
    echo    - Generate: ssh-keygen -t ed25519
    echo    - Add to: https://github.com/settings/keys
    echo.
    pause
    exit /b 1
)

echo Master branch pushed successfully!
echo.

REM Push feature branch
echo Pushing feature branch...
git push -u origin feature/autonomous-control-system

if errorlevel 1 (
    echo [ERROR] Failed to push feature branch.
    pause
    exit /b 1
)

echo Feature branch pushed successfully!
echo.

echo ============================================================
echo           SUCCESS! Repository pushed to GitHub
echo ============================================================
echo.
echo Repository URL: https://github.com/%GITHUB_USERNAME%/%REPO_NAME%
echo.
echo Next steps:
echo 1. Visit your repository
echo 2. Create a Pull Request:
echo    - Base: master
echo    - Compare: feature/autonomous-control-system
echo    - Title: feat: 手机自主化控制系统完整实现
echo.
pause
