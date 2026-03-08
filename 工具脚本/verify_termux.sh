#!/data/data/com.termux/files/usr/bin/bash
# Termux 快速验证脚本
# 在 Termux 应用中运行此脚本

echo "=========================================="
echo "  Termux v0.79 环境验证"
echo "=========================================="
echo ""

# 基础环境检查
echo "【基础环境】"
echo "HOME: $HOME"
echo "USER: $USER"
echo "SHELL: $SHELL"
echo "PWD: $(pwd)"
echo "PATH: $PATH"
echo ""

# Bash 检查
echo "【Bash 检查】"
if [ -x "$0" ]; then
    echo "✅ Bash 可执行: $0"
    echo "   版本: $BASH_VERSION"
else
    echo "❌ Bash 不可执行"
fi
echo ""

# 文件系统检查
echo "【文件系统】"
echo "Prefix 目录: $PREFIX"
ls -la "$PREFIX/bin" | head -5
echo ""

# 包管理器检查
echo "【包管理器】"
if command -v apt >/dev/null 2>&1; then
    echo "✅ apt 可用: $(which apt)"
    echo "   源列表:"
    cat "$PREFIX/etc/apt/sources.list" 2>/dev/null | head -3
else
    echo "❌ apt 不可用"
fi
echo ""

echo "=========================================="
echo "验证完成！"
echo "=========================================="
