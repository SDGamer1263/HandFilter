"""Platform abstraction layer for HandFilter.

Centralizes OS-specific paths, asset naming, update launching, and user-facing hints.
All platform-dependent logic should route through this module.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Optional


def get_platform() -> str:
    """Return normalized platform identifier: 'windows', 'linux', or 'macos'."""
    if sys.platform.startswith("win"):
        return "windows"
    if sys.platform == "darwin":
        return "macos"
    if sys.platform.startswith("linux"):
        return "linux"
    return "unknown"


def is_windows() -> bool:
    return get_platform() == "windows"


def is_linux() -> bool:
    return get_platform() == "linux"


def is_macos() -> bool:
    return get_platform() == "macos"


def get_app_data_dir(app_name: str = "HandFilter") -> Path:
    """Return the per-user application data directory for config, logs, cache.

    Windows: %LOCALAPPDATA%\\HandFilter
    Linux:   ~/.local/share/HandFilter  (XDG_DATA_HOME)
    macOS:   ~/Library/Application Support/HandFilter
    """
    plat = get_platform()
    if plat == "windows":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        return Path(base) / app_name
    if plat == "macos":
        return Path.home() / "Library" / "Application Support" / app_name
    # Linux / other Unix: XDG Base Directory Specification
    xdg_data = os.environ.get("XDG_DATA_HOME")
    if xdg_data:
        return Path(xdg_data) / app_name
    return Path.home() / ".local" / "share" / app_name


def get_config_dir(app_name: str = "HandFilter") -> Path:
    """Return the per-user configuration directory.

    Windows: same as app data (LOCALAPPDATA\\HandFilter)
    Linux:   ~/.config/HandFilter  (XDG_CONFIG_HOME)
    macOS:   ~/Library/Preferences/HandFilter
    """
    plat = get_platform()
    if plat == "windows":
        return get_app_data_dir(app_name)
    if plat == "macos":
        return Path.home() / "Library" / "Preferences" / app_name
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config:
        return Path(xdg_config) / app_name
    return Path.home() / ".config" / app_name


def get_cache_dir(app_name: str = "HandFilter") -> Path:
    """Return the per-user cache directory.

    Windows: %LOCALAPPDATA%\\HandFilter\\cache
    Linux:   ~/.cache/HandFilter  (XDG_CACHE_HOME)
    macOS:   ~/Library/Caches/HandFilter
    """
    plat = get_platform()
    if plat == "windows":
        return get_app_data_dir(app_name) / "cache"
    if plat == "macos":
        return Path.home() / "Library" / "Caches" / app_name
    xdg_cache = os.environ.get("XDG_CACHE_HOME")
    if xdg_cache:
        return Path(xdg_cache) / app_name
    return Path.home() / ".cache" / app_name


def get_install_dir(app_name: str = "HandFilter") -> Path:
    """Return the typical installation directory for the bundled application.

    Windows: %LOCALAPPDATA%\\Programs\\HandFilter (Inno Setup default)
    Linux:   /opt/HandFilter (system) or ~/.local/bin/HandFilter (user AppImage extract)
    macOS:   /Applications/HandFilter.app (system) or ~/Applications/HandFilter.app (user)
    """
    plat = get_platform()
    if plat == "windows":
        localappdata = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        return Path(localappdata) / "Programs" / app_name
    if plat == "macos":
        # User-level preferred for unsigned apps
        return Path.home() / "Applications" / f"{app_name}.app"
    # Linux: AppImage extracts to a temp dir; we return the extracted bundle path if detectable
    # Fallback to a reasonable default
    return Path.home() / ".local" / "bin" / app_name


def get_asset_suffix() -> str:
    """Return the platform-specific asset filename suffix for GitHub release matching.

    Windows: -Windows-Setup.exe
    Linux:   -Linux-x86_64.AppImage
    macOS:   -macOS-arm64.dmg
    """
    plat = get_platform()
    if plat == "windows":
        return "-Windows-Setup.exe"
    if plat == "macos":
        return "-macOS-arm64.dmg"
    return "-Linux-x86_64.AppImage"


def get_portable_asset_suffix() -> str:
    """Return the platform-specific portable (no-install) asset suffix.

    Windows: -Windows-Portable.zip
    Linux:   -Linux-Portable.tar.gz
    macOS:   -macOS-arm64.dmg (same as installer for unsigned .app)
    """
    plat = get_platform()
    if plat == "windows":
        return "-Windows-Portable.zip"
    if plat == "macos":
        return "-macOS-arm64.dmg"
    return "-Linux-Portable.tar.gz"


def get_executable_name(app_name: str = "HandFilter") -> str:
    """Return the executable filename for the platform.

    Windows: HandFilter.exe
    Linux:   HandFilter
    macOS:   HandFilter (inside .app/Contents/MacOS/)
    """
    if is_windows():
        return f"{app_name}.exe"
    return app_name


def get_update_launcher_script_content(installer_path: Path, app_name: str = "HandFilter") -> str:
    """Return the content of the platform-specific update launcher script.

    Windows: .bat with timeout + silent Inno install + relaunch + self-delete
    Linux:   .sh with sleep + AppImage replace + relaunch + self-delete
    macOS:   .sh with sleep + DMG mount + .app replace + relaunch + self-delete
    """
    plat = get_platform()
    installer_str = str(installer_path)

    if plat == "windows":
        # Use forward slashes in the path for the batch file
        installer_str = installer_str.replace("\\", "/")
        exe_path = str(get_install_dir(app_name) / get_executable_name(app_name)).replace("\\", "/")
        return f'''@echo off
timeout /t 3 /nobreak >nul
"{installer_str}" /VERYSILENT /CURRENTUSER /NORESTART /SP-
start "" "{exe_path}"
del "{installer_str}"
del "%~f0"
'''

    if plat == "linux":
        # For AppImage: replace the AppImage file and relaunch
        # The AppImage is typically the running executable itself
        appimage_path = shutil.which(app_name)
        if appimage_path and appimage_path.endswith(".AppImage"):
            target = appimage_path
        else:
            # Fallback: assume it's in the same directory as the script
            target = str(Path(installer_path).parent / f"{app_name}-Linux-x86_64.AppImage")
        return f'''#!/bin/bash
sleep 3
chmod +x "{installer_str}"
cp "{installer_str}" "{target}"
chmod +x "{target}"
exec "{target}"
rm -f "{installer_str}"
rm -f "$0"
'''

    # macOS
    # For DMG: we need to mount, copy .app to /Applications or ~/Applications, unmount, relaunch
    app_dest = get_install_dir(app_name)
    return f'''#!/bin/bash
sleep 3
# Mount DMG
hdiutil attach "{installer_str}" -nobrowse -quiet
# Find the mounted volume
VOLUME=$(hdiutil info | grep -E "/Volumes/.*HandFilter" | head -1 | awk '{{print $1}}')
if [ -n "$VOLUME" ]; then
    MOUNT_POINT=$(df | grep "$VOLUME" | awk '{{print $NF}}')
    if [ -d "$MOUNT_POINT/HandFilter.app" ]; then
        rm -rf "{app_dest}"
        cp -R "$MOUNT_POINT/HandFilter.app" "{app_dest}"
    fi
    hdiutil detach "$VOLUME" -quiet
fi
# Relaunch
open "{app_dest}"
rm -f "{installer_str}"
rm -f "$0"
'''


def write_update_launcher(installer_path: Path, app_name: str = "HandFilter") -> Path:
    """Write the platform-specific update launcher script to the temp update directory.

    Returns the path to the written launcher script.
    """
    from tempfile import gettempdir
    temp_dir = Path(gettempdir()) / "HandFilter-update"
    temp_dir.mkdir(parents=True, exist_ok=True)

    if is_windows():
        launcher_path = temp_dir / "update_launcher.bat"
    else:
        launcher_path = temp_dir / "update_launcher.sh"

    content = get_update_launcher_script_content(installer_path, app_name)
    launcher_path.write_text(content, encoding="utf-8")

    if not is_windows():
        launcher_path.chmod(0o755)

    return launcher_path


def launch_update_installer(installer_path: Path, app_name: str = "HandFilter") -> None:
    """Launch the platform-specific update installer in a detached process.

    Windows: subprocess.Popen with CREATE_NEW_PROCESS_GROUP | DETACHED_PROCESS
    Linux:   subprocess.Popen with start_new_session=True
    macOS:   subprocess.Popen with start_new_session=True
    """
    launcher_path = write_update_launcher(installer_path, app_name)

    if is_windows():
        subprocess.Popen(
            ["cmd", "/c", str(launcher_path)],
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
        )
    else:
        subprocess.Popen(
            [str(launcher_path)],
            start_new_session=True,
        )


def get_camera_permission_hint() -> str:
    """Return platform-specific camera permission guidance text."""
    plat = get_platform()
    if plat == "windows":
        return (
            "• Camera permissions are enabled in Windows Settings → Privacy → Camera\n"
            "• Another application isn't using the camera (Teams, Zoom, browser)"
        )
    if plat == "macos":
        return (
            "• Camera permission is granted in System Settings → Privacy & Security → Camera\n"
            "• The app is allowed in System Settings → Privacy & Security → Screen Recording (for window capture)\n"
            "• Another application isn't using the camera (FaceTime, Zoom, browser)"
        )
    # Linux
    return (
        "• Your user is in the 'video' group (run: sudo usermod -aG video $USER, then re-login)\n"
        "• Camera permissions are not blocked by a desktop portal (Flatpak/Snap)\n"
        "• Another application isn't using the camera (Cheese, Zoom, browser)\n"
        "• The camera device exists at /dev/video* (run: v4l2-ctl --list-devices)"
    )


def get_model_path() -> Path:
    """Return the path to the bundled MediaPipe model file.

    Uses sys._MEIPASS when running from a PyInstaller bundle,
    otherwise the directory of this module.
    """
    base_dir = getattr(sys, "_MEIPASS", Path(__file__).parent)
    return Path(base_dir) / "hand_landmarker.task"


def get_icon_path() -> Path:
    """Return the path to the application icon.

    Windows: .ico
    Linux:   .png
    macOS:   .icns
    """
    plat = get_platform()
    base_dir = getattr(sys, "_MEIPASS", Path(__file__).parent)
    if plat == "windows":
        return Path(base_dir) / "hand_filter.ico"
    if plat == "macos":
        return Path(base_dir) / "hand_filter.icns"
    return Path(base_dir) / "hand_filter.png"


__all__ = [
    "get_platform",
    "is_windows",
    "is_linux",
    "is_macos",
    "get_app_data_dir",
    "get_config_dir",
    "get_cache_dir",
    "get_install_dir",
    "get_asset_suffix",
    "get_portable_asset_suffix",
    "get_executable_name",
    "get_update_launcher_script_content",
    "write_update_launcher",
    "launch_update_installer",
    "get_camera_permission_hint",
    "get_model_path",
    "get_icon_path",
]