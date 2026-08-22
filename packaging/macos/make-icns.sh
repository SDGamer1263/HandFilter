#!/bin/bash
# make-icns.sh - Convert .ico to .icns for macOS
# Requires: imagemagick, iconutil (macOS) or png2icns (Linux)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ICO_FILE="$REPO_ROOT/hand_filter.ico"
ICNS_FILE="$REPO_ROOT/hand_filter.icns"

if [ ! -f "$ICO_FILE" ]; then
    echo "ERROR: $ICO_FILE not found"
    exit 1
fi

echo "Converting $ICO_FILE to $ICNS_FILE..."

# Create temporary iconset directory
ICONSET_DIR="$(mktemp -d)"
trap "rm -rf '$ICONSET_DIR'" EXIT

# Extract PNGs from .ico at required sizes
# macOS .icns needs: 16, 32, 64, 128, 256, 512, 1024 (and @2x variants)
SIZES=(16 32 64 128 256 512 1024)

for SIZE in "${SIZES[@]}"; do
    # Normal
    magick "$ICO_FILE" -resize "${SIZE}x${SIZE}" "$ICONSET_DIR/icon_${SIZE}x${SIZE}.png"
    # @2x (double resolution)
    magick "$ICO_FILE" -resize "$((SIZE*2))x$((SIZE*2))" "$ICONSET_DIR/icon_${SIZE}x${SIZE}@2x.png"
done

# Create .icns using iconutil (macOS only)
if command -v iconutil >/dev/null 2>&1; then
    iconutil -c icns "$ICONSET_DIR" -o "$ICNS_FILE"
    echo "Created $ICNS_FILE using iconutil"
elif command -v png2icns >/dev/null 2>&1; then
    # Linux fallback using png2icns (from libicns)
    png2icns "$ICNS_FILE" "$ICONSET_DIR"/*.png
    echo "Created $ICNS_FILE using png2icns"
else
    echo "ERROR: Neither iconutil nor png2icns found. Cannot create .icns"
    exit 1
fi

if [ ! -f "$ICNS_FILE" ]; then
    echo "ERROR: .icns file was not created"
    exit 1
fi

echo "Done. Icon saved to $ICNS_FILE"