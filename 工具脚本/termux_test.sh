#!/data/data/com.termux/files/usr/bin/bash

echo "=== Termux 环境测试 ==="
echo "Termux 版本:"
termux --version 2>/dev/null || echo "无法获取版本信息"

echo ""
echo "=== 存储权限测试 ==="
termux-setup-storage 2>&1 | head -5

echo ""
echo "=== 摄像头测试 ==="
echo "尝试使用 termux-camera-photo..."
if command -v termux-camera-photo &> /dev/null; then
    echo "termux-camera-photo 命令存在"
    termux-camera-photo /sdcard/termux_photo_test.jpg 2>&1 &
    CAMERA_PID=$!
    sleep 3
    kill $CAMERA_PID 2>/dev/null
    if [ -f /sdcard/termux_photo_test.jpg ]; then
        echo "✅ 摄像头测试成功 - 照片已保存"
        ls -lh /sdcard/termux_photo_test.jpg
    else
        echo "❌ 摄像头测试失败 - 照片未保存"
    fi
else
    echo "❌ termux-camera-photo 命令不存在 - 需要安装 termux-api 包"
fi

echo ""
echo "=== 音频测试 ==="
echo "尝试使用 termux-microphone-record..."
if command -v termux-microphone-record &> /dev/null; then
    echo "termux-microphone-record 命令存在"
    timeout 2 termux-microphone-record -f /sdcard/termux_audio_test.mp3 2>&1 || true
    if [ -f /sdcard/termux_audio_test.mp3 ]; then
        echo "✅ 音频测试成功 - 录音已保存"
        ls -lh /sdcard/termux_audio_test.mp3
    else
        echo "⚠️ 音频测试 - 录音文件未创建 (可能需要手动授权)"
    fi
else
    echo "❌ termux-microphone-record 命令不存在 - 需要安装 termux-api 包"
fi

echo ""
echo "=== 传感器信息 ==="
echo "可用的传感器命令:"
command -v termux-sensor &> /dev/null && echo "  - termux-sensor" || echo "  - termux-sensor (未安装)"
command -v termux-location &> /dev/null && echo "  - termux-location" || echo "  - termux-location (未安装)"
command -v termux-battery-status &> /dev/null && echo "  - termux-battery-status" || echo "  - termux-battery-status (未安装)"

echo ""
echo "=== 测试完成 ==="
