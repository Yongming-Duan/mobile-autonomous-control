#!/system/bin/sh
# Termux API extraction script
cd /sdcard
mkdir -p termux-api-extract
cd termux-api-extract
ar x /sdcard/termux-api.deb

# Extract data.tar.xz
cd /sdcard/termux-api-extract
mkdir -p extracted
cd extracted
tar -xf ../data.tar.xz

# Copy binaries to Termux bin
cp -r data/data/com.termux/files/usr/bin/* /data/data/com.termux/files/usr/bin/

# Set permissions
chmod +x /data/data/com.termux/files/usr/bin/termux-*

echo "Installation complete!"
echo "Testing termux-api:"
/data/data/com.termux/files/usr/bin/termux-api --version
