# ADB 查找脚本
$possiblePaths = @(
    "C:\platform-tools\adb.exe",
    "D:\platform-tools\adb.exe",
    "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe",
    "$env:APPDATA\..\Local\Android\Sdk\platform-tools\adb.exe"
)

Write-Host "正在搜索 ADB..." -ForegroundColor Yellow
$found = $false

foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        Write-Host "[✓] 找到 ADB: $path" -ForegroundColor Green
        $found = $true
        & $path devices
        break
    }
}

if (-not $found) {
    Write-Host "[✗] 未找到 ADB，请手动输入 ADB 所在路径" -ForegroundColor Red
    $manualPath = Read-Host "ADB 路径 (例如 C:\platform-tools\adb.exe)"
    if (Test-Path $manualPath) {
        Write-Host "[✓] 找到 ADB" -ForegroundColor Green
        & $manualPath devices
    }
}
