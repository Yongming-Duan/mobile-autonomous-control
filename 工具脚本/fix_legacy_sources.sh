#!/data/data/com.termux/files/usr/bin/bash
# Termux v0.79 Legacy 源配置脚本

echo "=========================================="
echo "  配置 Termux Legacy 源"
echo "=========================================="
echo ""

# 备份原源列表
if [ -f "$PREFIX/etc/apt/sources.list" ]; then
    cp "$PREFIX/etc/apt/sources.list" "$PREFIX/etc/apt/sources.list.bak"
    echo "✅ 已备份原源列表"
fi

# 配置 legacy 源 (适用于 Termux v0.79)
echo "配置 legacy 源..."
cat > "$PREFIX/etc/apt/sources.list" << 'EOF'
# Termux legacy repository (2019-12-24 snapshot)
# This source is compatible with Termux v0.79 and older

deb https://github.com/termux/termux-packages/releases/download/v0.79.0-2019-12-23-01-33 termux
deb https://packages.termux.org/apt/termux-main stable main
EOF

echo "✅ 源列表已更新"
echo ""

# 尝试使用不同的源
echo "尝试使用 Archive.org 镜像源..."
cat > "$PREFIX/etc/apt/sources.list" << 'EOF'
# 使用 Internet Archive 的 Termux 镜像 (2019 snapshot)
deb https://archive.org/download/termux-repositories-legacy/ termux
EOF

echo ""
echo "现在运行 apt update:"
apt update

echo ""
echo "如果 update 成功，尝试安装 termux-api:"
apt install termux-api

echo ""
echo "如果还是失败，说明 termux-api 在这个版本中不可用"
echo "请使用 Termux:API APK (termux-api-git.apk) 来获取传感器功能"
