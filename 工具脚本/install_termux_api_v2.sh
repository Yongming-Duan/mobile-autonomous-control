#!/usr/bin/env sh
# Termux API Installation Script v2
# Run this in Termux

echo "========================================="
echo "Termux API Installation Script v2"
echo "========================================="
echo ""

# Check if running in Termux
if [ ! -d "$PREFIX" ]; then
    echo "Error: Not running in Termux!"
    exit 1
fi

echo "Installing termux-api binaries..."
echo ""

# Copy binaries from sdcard
cd /sdcard

if [ -d "termux-bin" ]; then
    echo "Copying binaries to $PREFIX/bin..."
    cp termux-bin/termux-* "$PREFIX/bin/"
    chmod +x "$PREFIX/bin/termux-"*
    echo "✓ Binaries installed"
else
    echo "Error: termux-bin directory not found!"
    exit 1
fi

# Copy libexec files
if [ -d "termux-libexec" ]; then
    echo ""
    echo "Copying libexec files to $PREFIX/libexec/..."
    mkdir -p "$PREFIX/libexec"
    cp termux-libexec/termux-api* "$PREFIX/libexec/"
    cp termux-libexec/termux-callback "$PREFIX/libexec/"
    chmod +x "$PREFIX/libexec/termux-"*
    echo "✓ Libexec files installed"
fi

echo ""
echo "========================================="
echo "Installation complete!"
echo "========================================="
echo ""

# Test if commands are available
echo "Testing termux-api commands:"
echo "----------------------------"

test_count=0
pass_count=0

for cmd in termux-api termux-camera-photo termux-microphone-record termux-tts-speak termux-sensor; do
    test_count=$((test_count + 1))
    if command -v "$cmd" >/dev/null 2>&1; then
        echo "✓ $cmd is available"
        pass_count=$((pass_count + 1))
    else
        echo "✗ $cmd not found"
    fi
done

echo ""
echo "========================================="
echo "Summary: $pass_count/$test_count commands available"
echo "========================================="
echo ""

if [ $pass_count -gt 0 ]; then
    echo "You can now use termux-api commands!"
    echo ""
    echo "Examples:"
    echo "  termux-camera-photo /sdcard/test.jpg"
    echo "  termux-microphone-record -f /sdcard/test.wav -l 5"
    echo "  termux-tts-speak 'Hello World'"
    echo "  termux-sensor -l"
else
    echo "Warning: No commands found. Installation may have failed."
    exit 1
fi
