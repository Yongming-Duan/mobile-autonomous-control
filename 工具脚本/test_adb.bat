@echo off
chcp 65001 >nul
echo Searching for ADB...

set ADB_FOUND=0

if exist "C:\platform-tools\adb.exe" (
    echo [OK] Found ADB at C:\platform-tools\adb.exe
    "C:\platform-tools\adb.exe" devices
    set ADB_FOUND=1
    goto :end
)

if exist "D:\platform-tools\adb.exe" (
    echo [OK] Found ADB at D:\platform-tools\adb.exe
    "D:\platform-tools\adb.exe" devices
    set ADB_FOUND=1
    goto :end
)

if exist "%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe" (
    echo [OK] Found ADB in Android SDK
    "%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe" devices
    set ADB_FOUND=1
    goto :end
)

if %ADB_FOUND%==0 (
    echo [ERROR] ADB not found in common locations
    echo Please enter ADB path (e.g., C:\platform-tools\adb.exe):
    set /p ADB_PATH=
    if exist "%ADB_PATH%" (
        echo [OK] Testing ADB...
        "%ADB_PATH%" devices
    ) else (
        echo [ERROR] File not found: %ADB_PATH%
    )
)

:end
pause
