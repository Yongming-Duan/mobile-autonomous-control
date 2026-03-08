#!/usr/bin/env sh
# Termux API Installation Script
# Run this script in Termux

echo "Installing termux-api binaries..."

cd /sdcard
mkdir -p termux-api-extract
cd termux-api-extract

# Extract deb package
ar x /sdcard/termux-api.deb

# Extract data archive
mkdir -p extracted
cd extracted
tar -xf ../data.tar.xz 2>/dev/null || tar -xf ../data.tar.gz

# Copy binaries to Termux PREFIX
echo "Copying binaries to $PREFIX/bin..."
cp -r data/data/com.termux/files/usr/bin/termux-* "$PREFIX/bin/"

# Set executable permissions
chmod +x "$PREFIX/bin/termux-"*

echo ""
echo "Installation complete!"
echo ""
echo "Testing termux-api commands:"
echo "============================"

# Test if commands are available
for cmd in termux-api termux-camera-info termux-microphone-record; do
    if command -v "$cmd" >/dev/null 2>&1; then
        echo "✓ $cmd is available"
        $cmd --help 2>&1 | head -1
    else
        echo "✗ $cmd not found"
    fi
done

echo ""
echo "You can now use termux-api commands!"
