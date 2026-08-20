"""Background update checker and downloader for HandFilter."""
import json
import os
import sys
import threading
import time
import urllib.request
import ssl
import tempfile
import subprocess
import shutil
from pathlib import Path
from typing import Optional
import tkinter as tk
from tkinter import messagebox

import version


GITHUB_REPO = "SDGamer1263/HandFilter"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
UPDATE_CHECK_INTERVAL = 24 * 60 * 60  # 24 hours
TEMP_UPDATE_DIR = Path(tempfile.gettempdir()) / "HandFilter-update"


def parse_version(version_str: str) -> tuple:
    """Parse semantic version string into tuple of ints."""
    # Strip 'v' prefix if present
    version_str = version_str.lstrip('v')
    parts = version_str.split('.')
    return tuple(int(p) for p in parts[:3])


def is_newer_version(current: str, latest: str) -> bool:
    """Compare semantic versions."""
    try:
        return parse_version(latest) > parse_version(current)
    except Exception:
        return False


def get_latest_release() -> Optional[dict]:
    """Fetch latest release info from GitHub API."""
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(
            GITHUB_API_URL,
            headers={"User-Agent": "HandFilter-Updater", "Accept": "application/vnd.github.v3+json"}
        )
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            return json.load(response)
    except Exception as e:
        print(f"Update check failed: {e}", file=sys.stderr)
        return None


def find_installer_asset(release: dict) -> Optional[str]:
    """Find the Windows installer asset URL in release assets."""
    for asset in release.get("assets", []):
        name = asset.get("name", "").lower()
        if name.endswith("-windows-setup.exe"):
            return asset["browser_download_url"]
    return None


def download_file(url: str, dest: Path) -> bool:
    """Download file with TLS verification."""
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, headers={"User-Agent": "HandFilter-Updater"})
        with urllib.request.urlopen(req, context=ctx, timeout=60) as response:
            total = int(response.headers.get("Content-Length", 0))
            downloaded = 0
            with open(dest, "wb") as f:
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
        return True
    except Exception as e:
        print(f"Download failed: {e}", file=sys.stderr)
        return False


def prune_stale_installers() -> None:
    """Remove old installer files from temp update directory."""
    try:
        if TEMP_UPDATE_DIR.exists():
            for f in TEMP_UPDATE_DIR.glob("*.exe"):
                try:
                    f.unlink()
                except Exception:
                    pass
    except Exception:
        pass


def launch_update_installer(installer_path: Path) -> None:
    """Launch the update launcher batch file."""
    bat_path = TEMP_UPDATE_DIR / "update_launcher.bat"
    bat_content = f'''@echo off
timeout /t 3 /nobreak >nul
"{installer_path}" /VERYSILENT /CURRENTUSER /NORESTART /SP-
start "" "{os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "HandFilter", "HandFilter.exe")}"
del "{installer_path}"
del "%~f0"
'''
    try:
        TEMP_UPDATE_DIR.mkdir(parents=True, exist_ok=True)
        with open(bat_path, "w") as f:
            f.write(bat_content)
        # Detach and run
        subprocess.Popen(["cmd", "/c", str(bat_path)], creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS)
    except Exception as e:
        print(f"Failed to launch updater: {e}", file=sys.stderr)


class UpdateChecker:
    """Background update checker."""

    def __init__(self):
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._last_check = 0

    def start(self, delay: int = 5) -> None:
        """Start background update check after initial delay."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, args=(delay,), daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the background checker."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)

    def _run(self, initial_delay: int) -> None:
        time.sleep(initial_delay)
        while not self._stop_event.is_set():
            self._check_and_notify()
            # Sleep in small increments to allow stop
            for _ in range(UPDATE_CHECK_INTERVAL):
                if self._stop_event.is_set():
                    break
                time.sleep(1)

    def _check_and_notify(self) -> None:
        """Check for updates and notify if available."""
        self._last_check = time.time()
        release = get_latest_release()
        if not release:
            return

        latest_version = release.get("tag_name", "").lstrip("v")
        if not latest_version:
            return

        current_version = version.__version__
        if not is_newer_version(current_version, latest_version):
            return

        # Show update dialog on main thread
        installer_url = find_installer_asset(release)
        if not installer_url:
            return

        # Use tkinter on main thread
        root = tk.Tk()
        root.withdraw()
        msg = (
            f"HandFilter {latest_version} is available!\n"
            f"You are running {current_version}.\n\n"
            "Would you like to download and install the update now?"
        )
        result = messagebox.askyesno("HandFilter - Update Available", msg)
        root.destroy()

        if result:
            self._download_and_install(installer_url, latest_version)

    def _download_and_install(self, url: str, version_str: str) -> None:
        """Download installer and launch update."""
        prune_stale_installers()
        TEMP_UPDATE_DIR.mkdir(parents=True, exist_ok=True)

        installer_path = TEMP_UPDATE_DIR / f"HandFilter-{version_str}-Windows-Setup.exe"

        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo(
            "HandFilter - Downloading Update",
            f"Downloading HandFilter {version_str}...\n\nThis may take a moment."
        )
        root.destroy()

        if download_file(url, installer_path):
            root = tk.Tk()
            root.withdraw()
            messagebox.showinfo(
                "HandFilter - Update Ready",
                f"HandFilter {version_str} has been downloaded.\n\n"
                "The update will install now. HandFilter will restart automatically."
            )
            root.destroy()

            launch_update_installer(installer_path)
            sys.exit(0)
        else:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "HandFilter - Update Failed",
                "Failed to download the update.\n\n"
                "Please try again later or download manually from GitHub."
            )
            root.destroy()


def check_for_updates_now() -> None:
    """Manual update check (for menu option)."""
    release = get_latest_release()
    if not release:
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning(
            "HandFilter - Update Check Failed",
            "Couldn't check for updates.\n\n"
            "HandFilter will continue normally.\n"
            "Please check your internet connection and try again later."
        )
        root.destroy()
        return

    latest_version = release.get("tag_name", "").lstrip("v")
    current_version = version.__version__

    if not latest_version:
        return

    if is_newer_version(current_version, latest_version):
        installer_url = find_installer_asset(release)
        if installer_url:
            root = tk.Tk()
            root.withdraw()
            msg = (
                f"HandFilter {latest_version} is available!\n"
                f"You are running {current_version}.\n\n"
                "Would you like to download and install the update now?"
            )
            result = messagebox.askyesno("HandFilter - Update Available", msg)
            root.destroy()
            if result:
                checker = UpdateChecker()
                checker._download_and_install(installer_url, latest_version)
        else:
            root = tk.Tk()
            root.withdraw()
            messagebox.showinfo(
                "HandFilter - Update Not Ready",
                f"HandFilter {latest_version} is available, but no Windows installer "
                "was found for this release.\n\n"
                "Please download it manually from GitHub."
            )
            root.destroy()
    else:
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo(
            "HandFilter - Up to Date",
            f"You are running the latest version ({current_version})."
        )
        root.destroy()