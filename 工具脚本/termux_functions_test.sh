#!/data/data/com.termux/files/usr/bin/bash
# Termux v0.79 功能测试脚本
# 在 Termux 中运行此脚本来测试所有功能

echo "=========================================="
echo "  Termux v0.79 功能测试"
echo "=========================================="
echo ""

# 1. 基础环境测试
echo "【1】基础环境"
echo "Bash 版本: $BASH_VERSION"
echo "PATH: $PATH"
echo "HOME: $HOME"
echo "当前目录: $(pwd)"
which bash && echo "✅ Bash 可用" || echo "❌ Bash 不可用"
echo ""

# 2. 包管理器测试
echo "【2】包管理器 (apt)"
if command -v apt >/dev/null 2>&1; then
    echo "✅ apt 可用: $(which apt)"
    echo "软件源:"
    cat /data/data/com.termux/files/usr/etc/apt/sources.list 2>/dev/null | grep -v "^#" | head -3
else
    echo "❌ apt 不可用"
fi
echo ""

# 3. 存储权限测试
echo "【3】存储权限"
if [ -d ~/storage ]; then
    echo "✅ 存储已挂载"
    ls -la ~/storage/ 2>/dev/null | head -5
else
    echo "⚠️  存储未挂载，运行: termux-setup-storage"
fi
echo ""

# 4. Termux:API 测试
echo "【4】Termux:API"
echo "检查 API 命令:"
API_COMMANDS="termux-camera-photo termux-microphone-record termux-sensor termux-location termux-battery-status"
for cmd in $API_COMMANDS; do
    if command -v $cmd >/dev/null 2>&1; then
        echo "  ✅ $cmd"
    else
        echo "  ❌ $cmd (未安装，运行: apt install termux-api)"
    fi
done
echo ""

# 5. 摄像头测试
echo "【5】摄像头测试"
if command -v termux-camera-photo >/dev/null 2>&1; then
    echo "拍摄测试照片..."
    termux-camera-photo ~/storage/shared/test_photo.jpg 2>&1 &
    CAMERA_PID=$!
    echo "等待 3 秒..."
    sleep 3
    kill $CAMERA_PID 2>/dev/null

    if [ -f ~/storage/shared/test_photo.jpg ]; then
        SIZE=$(ls -lh ~/storage/shared/test_photo.jpg | awk '{print $5}')
        echo "✅ 摄像头测试成功 - 照片已保存 (大小: $SIZE)"
    else
        echo "⚠️  摄像头测试 - 可能需要手动授权"
    fi
else
    echo "⚠️  termux-camera-photo 命令不存在"
    echo "   安装: apt install termux-api"
fi
echo ""

# 6. 音频测试
echo "【6】音频测试"
if command -v termux-microphone-record >/dev/null 2>&1; then
    echo "录制 3 秒测试音频..."
    timeout 3 termux-microphone-record -f ~/storage/shared/test_audio.mp3 2>&1 || true

    if [ -f ~/storage/shared/test_audio.mp3 ]; then
        SIZE=$(ls -lh ~/storage/shared/test_audio.mp3 | awk '{print $5}')
        echo "✅ 音频测试成功 - 录音已保存 (大小: $SIZE)"
    else
        echo "⚠️  音频测试 - 可能需要手动授权"
    fi
else
    echo "⚠️  termux-microphone-record 命令不存在"
    echo "   安装: apt install termux-api"
fi
echo ""

# 7. 传感器测试
echo "【7】传感器测试"
if command -v termux-sensor >/dev/null 2>&1; then
    echo "可用传感器列表:"
    timeout 2 termux-sensor -l 2>&1 || true
    echo ""
    echo "读取加速度计 (2秒):"
    timeout 2 termux-sensor -a accelerometer 2>&1 || true
else
    echo "⚠️  termux-sensor 命令不存在"
fi
echo ""

# 8. GPS 测试
echo "【8】GPS 定位测试"
if command -v termux-location >/dev/null 2>&1; then
    echo "获取位置信息:"
    timeout 5 termux-location 2>&1 || true
else
    echo "⚠️  termux-location 命令不存在"
fi
echo ""

# 9. 电池测试
echo "【9】电池状态测试"
if command -v termux-battery-status >/dev/null 2>&1; then
    echo "电池信息:"
    termux-battery-status
else
    echo "⚠️  termux-battery-status 命令不存在"
fi
echo ""

# 10. 系统信息
echo "【10】系统信息"
echo "CPU 信息:"
TERMUX_CPU_INFO=$(getprop ro.product.cpu.abi)
echo "  架构: $TERMUX_CPU_INFO"
echo "  核心: $(grep -c ^processor /proc/cpuinfo) cores"
echo ""
echo "内存信息:"
free -h 2>/dev/null || echo "  无法获取"
echo ""
echo "存储空间:"
df -h ~/ 2>/dev/null | grep -v "^Filesystem" || echo "  无法获取"
echo ""

echo "=========================================="
echo "  测试完成！"
echo "=========================================="
echo ""
echo "生成的测试文件:"
ls -la ~/storage/shared/test_*.* 2>/dev/null
echo ""
