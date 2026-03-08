@echo off
REM ============================================
REM 快速测试脚本 - 测试所有组件
REM Quick Test Script - Test All Components
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ============================================
echo      组件测试 - Component Test
echo ============================================
echo.

cd /d "%~dp0"

REM 运行Python测试脚本
echo 运行快速测试...
echo.
python quick_start.py

echo.
echo ============================================
echo 测试完成
echo ============================================
echo.

pause
