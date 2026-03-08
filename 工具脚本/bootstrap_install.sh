#!/system/bin/sh
# Termux Bootstrap 离线安装脚本
# 适用于未 Root 设备 (Android 5.0 - 6.0)
# 使用方法：将此脚本放到 /sdcard/，然后在 Termux 中执行

echo "=========================================="
echo "  Termux Bootstrap 离线安装工具"
echo "=========================================="
echo ""
echo "检测设备信息..."
echo "Android 版本: $(getprop ro.build.version.release)"
echo "CPU 架构: $(getprop ro.product.cpu.abi)"
echo ""

# 检查 bootstrap 文件是否存在
if [ ! -f /sdcard/bootstrap-aarch64.zip ]; then
    echo "❌ 错误：找不到 /sdcard/bootstrap-aarch64.zip"
    echo "请确保已通过 ADB 推送文件到手机："
    echo "  adb push bootstrap-aarch64.zip /sdcard/"
    exit 1
fi

echo "✅ 找到 bootstrap 文件"
echo "文件大小: $(ls -lh /sdcard/bootstrap-aarch64.zip | awk '{print $5}')"
echo ""

# 检查 Termux 安装目录
TERMUX_PREFIX="/data/data/com.termux/files/usr"

if [ ! -d "$TERMUX_PREFIX" ]; then
    echo "⚠️  Termux 目录尚未创建，正在创建..."
    # 由于权限限制，无法直接创建
    # 用户需要先手动启动 Termux 应用一次
    echo ""
    echo "请按以下步骤操作："
    echo "1. 返回主屏幕"
    echo "2. 打开 Termux 应用"
    echo "3. 等待初始化（如果失败，关闭后重试）"
    echo "4. 初始化完成后，再次运行此脚本"
    echo ""
    exit 1
fi

echo "✅ Termux 目录已存在"
echo ""

# 检查当前是否在 Termux 环境中运行
if [ -x "$TERMUX_PREFIX/bin/unzip" ]; then
    echo "✅ 在 Termux 环境中运行"
    UNZIP="$TERMUX_PREFIX/bin/unzip"
elif command -v unzip >/dev/null 2>&1; then
    echo "⚠️  使用系统 unzip 命令"
    UNZIP="unzip"
else
    echo "❌ 错误：找不到 unzip 命令"
    exit 1
fi

echo "开始解压 bootstrap 文件..."
echo ""

# 备份现有文件（如果存在）
if [ -d "$TERMUX_PREFIX.bak" ]; then
    echo "删除旧备份..."
    rm -rf "$TERMUX_PREFIX.bak"
fi

if [ -d "$TERMUX_PREFIX" ] && [ "$(ls -A $TERMUX_PREFIX 2>/dev/null)" ]; then
    echo "备份现有文件..."
    cp -a "$TERMUX_PREFIX" "$TERMUX_PREFIX.bak"
    echo "✅ 备份完成: $TERMUX_PREFIX.bak"
fi

# 解压 bootstrap
echo "解压中..."
$UNZIP -o /sdcard/bootstrap-aarch64.zip -d "$TERMUX_PREFIX/" 2>&1

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Bootstrap 解压成功！"
    echo ""
    echo "设置文件权限..."
    chmod -R 755 "$TERMUX_PREFIX/bin" 2>/dev/null
    chmod -R 755 "$TERMUX_PREFIX/lib" 2>/dev/null
    chmod 755 "$TERMUX_PREFIX/bin/"* 2>/dev/null

    echo "✅ 权限设置完成"
    echo ""
    echo "=========================================="
    echo "  安装完成！"
    echo "=========================================="
    echo ""
    echo "请执行以下操作："
    echo "1. 完全关闭 Termux 应用"
    echo "2. 重新打开 Termux"
    echo "3. 验证安装："
    echo "   which bash"
    echo "   ls ~"
    echo ""
else
    echo ""
    echo "❌ 解压失败！"
    echo "请检查："
    echo "1. bootstrap 文件是否完整"
    echo "2. 存储空间是否充足"
    echo "3. 文件权限是否正确"
    echo ""
    if [ -d "$TERMUX_PREFIX.bak" ]; then
        echo "恢复备份..."
        rm -rf "$TERMUX_PREFIX"
        mv "$TERMUX_PREFIX.bak" "$TERMUX_PREFIX"
        echo "✅ 已恢复到安装前的状态"
    fi
    exit 1
fi

# 验证安装
echo "验证安装..."
if [ -x "$TERMUX_PREFIX/bin/bash" ]; then
    echo "✅ Bash 已安装: $TERMUX_PREFIX/bin/bash"
else
    echo "⚠️  Bash 不可执行"
fi

if [ -d "$TERMUX_PREFIX/lib" ]; then
    LIB_COUNT=$(ls -1 "$TERMUX_PREFIX/lib" | wc -l)
    echo "✅ 库文件: $LIB_COUNT 个"
else
    echo "⚠️  库目录不存在"
fi

echo ""
echo "安装完成！现在可以："
echo "1. 退出 Termux"
echo "2. 重新打开 Termux"
echo "3. 运行: apt update"
echo "4. 运行: apt install termux-api"
echo ""
