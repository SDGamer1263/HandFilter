#!/bin/bash
# build-appimage.sh - Package an already-built HandFilter Linux bundle
# Expects: dist/HandFilter from PyInstaller

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VERSION_FILE="$REPO_ROOT/version.py"

VERSION=$(grep -E '^__version__\s*=' "$VERSION_FILE" | sed -E 's/.*"([^"]+)".*/\1/')
if [ -z "$VERSION" ]; then
    echo "ERROR: Could not extract version from $VERSION_FILE"
    exit 1
fi

echo "Packaging HandFilter v$VERSION for Linux (x86_64)"

BUNDLE_DIR="$REPO_ROOT/dist/HandFilter"
EXECUTABLE="$BUNDLE_DIR/HandFilter"

if [ ! -f "$EXECUTABLE" ]; then
    echo "ERROR: PyInstaller executable not found at $EXECUTABLE"
    echo "Run PyInstaller with main_linux.spec before this script."
    exit 1
fi

chmod +x "$EXECUTABLE"

APPDIR="$REPO_ROOT/dist/HandFilter.AppDir"

echo "Creating AppDir at $APPDIR..."
rm -rf "$APPDIR"
mkdir -p "$APPDIR/HandFilter"

echo "Copying PyInstaller bundle..."
cp -a "$BUNDLE_DIR/." "$APPDIR/HandFilter/"

echo "Copying AppRun..."
cp "$REPO_ROOT/installer/AppRun" "$APPDIR/AppRun"
chmod +x "$APPDIR/AppRun"

if [ ! -f "$REPO_ROOT/hand_filter.png" ]; then
    echo "ERROR: hand_filter.png not found."
    echo "The workflow must generate the Linux icon before PyInstaller runs."
    exit 1
fi

echo "Copying application icon..."
cp "$REPO_ROOT/hand_filter.png" "$APPDIR/hand_filter.png"

echo "Copying desktop entry..."
cp "$REPO_ROOT/installer/handfilter.desktop" "$APPDIR/handfilter.desktop"

APPIMAGE_NAME="HandFilter-${VERSION}-Linux-x86_64.AppImage"

echo "Building AppImage: $APPIMAGE_NAME..."
cd "$REPO_ROOT/dist"
appimagetool "$APPDIR" "$APPIMAGE_NAME"

if [ ! -f "$APPIMAGE_NAME" ]; then
    echo "ERROR: AppImage was not created."
    exit 1
fi

chmod +x "$APPIMAGE_NAME"

TARBALL_NAME="HandFilter-${VERSION}-Linux-Portable.tar.gz"

echo "Creating portable tarball: $TARBALL_NAME..."
tar -czf "$TARBALL_NAME" -C "$BUNDLE_DIR" .

if [ ! -f "$TARBALL_NAME" ]; then
    echo "ERROR: Portable tarball was not created."
    exit 1
fi

echo ""
echo "=========================================="
echo "Packaging complete."
echo "  $REPO_ROOT/dist/$APPIMAGE_NAME"
echo "  $REPO_ROOT/dist/$TARBALL_NAME"
echo "=========================================="

sha256sum "$APPIMAGE_NAME" "$TARBALL_NAME"