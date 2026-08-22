#!/bin/bash
# build-dmg.sh - Build HandFilter macOS DMG
# Run on macOS (Apple Silicon)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VERSION_FILE="$REPO_ROOT/version.py"

# Extract version from version.py
VERSION=$(grep -E '^__version__\s*=' "$VERSION_FILE" | sed -E 's/.*"([^"]+)".*/\1/')
if [ -z "$VERSION" ]; then
    echo "ERROR: Could not extract version from $VERSION_FILE"
    exit 1
fi

echo "Building HandFilter v$VERSION for macOS (arm64)"

# Check architecture
ARCH=$(uname -m)
if [ "$ARCH" != "arm64" ]; then
    echo "WARNING: Building on $ARCH, expected arm64"
fi

# Install system dependencies
echo "Installing system dependencies..."
if ! command -v create-dmg >/dev/null 2>&1; then
    echo "Installing create-dmg..."
    brew install create-dmg
fi

# Create virtual environment
VENV_DIR="$REPO_ROOT/.venv-macos"
echo "Creating virtual environment at $VENV_DIR..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# Upgrade pip and install dependencies
pip install --upgrade pip -q
pip install -r "$REPO_ROOT/requirements.txt" -q
pip install pyinstaller -q

# Generate .icns icon if needed
ICNS_FILE="$REPO_ROOT/hand_filter.icns"
if [ ! -f "$ICNS_FILE" ]; then
    echo "Generating .icns icon..."
    chmod +x "$SCRIPT_DIR/make-icns.sh"
    "$SCRIPT_DIR/make-icns.sh"
fi

# Build with PyInstaller
echo "Building with PyInstaller (main_macos.spec)..."
cd "$REPO_ROOT"
pyinstaller -y main_macos.spec

# Verify build output
APP_BUNDLE="$REPO_ROOT/dist/HandFilter.app"
if [ ! -d "$APP_BUNDLE" ]; then
    echo "ERROR: .app bundle not found at $APP_BUNDLE"
    exit 1
fi

# Create DMG
DMG_NAME="HandFilter-${VERSION}-macOS-arm64.dmg"
echo "Creating DMG: $DMG_NAME..."
cd "$REPO_ROOT/dist"

# Remove old DMG if exists
rm -f "$DMG_NAME"

create-dmg \
    --volname "HandFilter ${VERSION}" \
    --volicon "$REPO_ROOT/hand_filter.icns" \
    --window-pos 200 120 \
    --window-size 800 400 \
    --icon-size 100 \
    --icon "HandFilter.app" 200 190 \
    --hide-extension "HandFilter.app" \
    --app-drop-link 600 185 \
    --no-internet-enable \
    "$DMG_NAME" \
    "HandFilter.app"

# Verify DMG
if [ ! -f "$DMG_NAME" ]; then
    echo "ERROR: DMG not created"
    exit 1
fi

# Output artifacts
echo ""
echo "=========================================="
echo "Build complete. Artifacts:"
echo "  $REPO_ROOT/dist/HandFilter.app"
echo "  $REPO_ROOT/dist/$DMG_NAME"
echo "=========================================="

# Print SHA256 for verification
shasum -a 256 "$DMG_NAME"

# Note about unsigned DMG
echo ""
echo "NOTE: This DMG is UNSIGNED (no Apple Developer ID)."
echo "Users will need to: Right-click → Open, or run:"
echo "  xattr -d com.apple.quarantine \"$DMG_NAME\""
echo "before opening."