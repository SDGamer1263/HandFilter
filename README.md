# 🖐️ HandFilter

**Real-time hand tracking with drawing, filters, and gestures — no Python required.**

HandFilter turns your webcam into an interactive canvas. Control it entirely with your hands: draw with your finger, apply visual filters by pinching, and navigate menus without touching a keyboard.

---

## 🚀 Download

### Windows (Recommended)
| Version | Download |
|---------|----------|
| **Installer** (Start Menu, auto-updates) | [HandFilter-1.0.0-Windows-Setup.exe](https://github.com/SDGamer1263/HandFilter/releases/download/v1.0.0/HandFilter-1.0.0-Windows-Setup.exe) |
| **Portable** (no install, run anywhere) | [HandFilter-1.0.0-Windows-Portable.zip](https://github.com/SDGamer1263/HandFilter/releases/download/v1.0.0/HandFilter-1.0.0-Windows-Portable.zip) |

> **First time?** Download the **Installer** — it adds a Start Menu shortcut and checks for updates automatically.

### Linux (x86_64)
| Version | Download |
|---------|----------|
| **AppImage** | [HandFilter-1.0.0-Linux-x86_64.AppImage](https://github.com/SDGamer1263/HandFilter/releases/download/v1.0.0/HandFilter-1.0.0-Linux-x86_64.AppImage) |
| **Portable** (tarball, run anywhere) | [HandFilter-1.0.0-Linux-Portable.tar.gz](https://github.com/SDGamer1263/HandFilter/releases/download/v1.0.0/HandFilter-1.0.0-Linux-Portable.tar.gz) |

> **Tested on:** Build verified in CI. Runtime testing on Linux is pending.
> **Install:** `chmod +x HandFilter-*.AppImage && ./HandFilter-*.AppImage`

### macOS (Apple Silicon / arm64)
| Version | Download |
|---------|----------|
| **DMG** (drag to Applications) | [HandFilter-1.0.0-macOS-arm64.dmg](https://github.com/SDGamer1263/HandFilter/releases/download/v1.0.0/HandFilter-1.0.0-macOS-arm64.dmg) |

> **Tested on:** Build verified in CI. Runtime testing on macOS is pending..
> **Unsigned:** No Apple Developer ID. On first launch: **Right-click → Open** or run `xattr -d com.apple.quarantine HandFilter-*.dmg`.
> **Intel Macs:** Not supported in v1.x (no MediaPipe Intel wheels for Python 3.11).

### From Source (Developers)
```bash
git clone https://github.com/SDGamer1263/HandFilter.git
cd HandFilter
pip install -r requirements.txt
python main.py
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Hand Tracking** | MediaPipe HandLandmarker (VIDEO mode) — 21 3D landmarks per hand at 30+ FPS |
| **Drawing Mode** | Right index finger = pen. Enable with 5 fingers up on LEFT hand |
| **Portal Filters** | Pinch both index fingers to create a filter region. Right-hand finger count selects: Retro, B&W, Invert, Pixelate, Blur, Sketch |
| **Gesture Controls** | Intuitive gestures for all major actions (see [Gestures](#-gestures)) |
| **Performance Overlay** | Real-time FPS, latency, and mode display |
| **Keyboard Menu** | Press `M` for visual menu (WASD navigation) — brush size, color, performance settings |
| **Zero Dependencies** | Bundled Python, MediaPipe, OpenCV — runs on clean Windows/Linux/macOS |

---

## 🎮 How to Use

1. **Launch** HandFilter from your application menu / Applications folder
2. **Allow camera access** when your OS prompts
3. **Show your hands** to the camera — you'll see landmarks appear
4. **Use gestures** to control the app (no keyboard needed for basics)

### Basic Workflow
- **Draw**: Hold up 5 fingers on LEFT hand → draw with RIGHT index finger
- **Filter**: Pinch both index fingers → move hands apart to resize portal → RIGHT hand finger count changes filter
- **Clear canvas**: Make a fist with LEFT hand and hold for 1 second (while in Drawing mode)
- **Menu**: Press `M` on keyboard → navigate with `W`/`S` (up/down), `A`/`D` (change value), `Esc` to close

---

## 🎥 Gestures

| Gesture | Hand | Action |
|---------|------|--------|
| ✋ 5 fingers up | Left | Toggle Drawing ↔ Filters mode |
| ✊ Fist (hold) | Right | Pause drawing (while held) |
| ✊ Fist (hold 1s) | Left | Clear canvas (Drawing mode only) |
| ☝️ 1 finger up | Right | Filter: Retro |
| ✌️ 2 fingers up | Right | Filter: Black & White |
| 🤟 3 fingers up | Right | Filter: Invert |
| 🖖 4 fingers up | Right | Filter: Pixelate |
| 🖐️ 5 fingers up | Right | Filter: Blur |
| 🤘 6 fingers (thumb+pinky) | Right | Filter: Sketch |

> **Tip**: The portal filter appears between your two index fingertips. Move hands closer/further to resize it.

### Gesture Guide Diagram

![Gestures](docs/gestures.svg)

---

## 📸 Screenshots

*Screenshots coming soon. In the meantime, see the gesture guide below and launch the app to try it live.*

---

## ⚙️ Requirements

### Windows
| Requirement | Details |
|-------------|---------|
| **OS** | Windows 10 / 11 (64-bit) |
| **Camera** | Any webcam (720p+ recommended) |
| **RAM** | 500 MB free |
| **Disk** | 200 MB (installer) / 150 MB (portable) |
| **GPU** | Not required (CPU-only MediaPipe) |

### Linux
| Requirement | Details |
|-------------|---------|
| **OS** | Ubuntu 22.04+, Debian 12+, Fedora 38+, Arch (glibc 2.35+) |
| **Camera** | Any V4L2 webcam (720p+ recommended) |
| **RAM** | 500 MB free |
| **Disk** | 150 MB |
| **GPU** | Not required (CPU-only MediaPipe) |
| **Desktop** | X11 or Wayland (XWayland required for some compositors) |
| **Groups** | User must be in `video` group (`sudo usermod -aG video $USER`) |

### macOS
| Requirement | Details |
|-------------|---------|
| **OS** | macOS 14+ (Sonoma) |
| **Architecture** | Apple Silicon (M1/M2/M3) only |
| **Camera** | Built-in or USB webcam (720p+ recommended) |
| **RAM** | 500 MB free |
| **Disk** | 200 MB |
| **GPU** | Not required (CPU-only MediaPipe) |

> **No Python, no pip, no virtual environments needed.** Everything is bundled.

---

## 🐛 Troubleshooting

### Windows
| Problem | Solution |
|---------|----------|
| **"Camera unavailable" dialog** | • Check camera is plugged in<br>• Windows Settings → Privacy → Camera → allow apps<br>• Close other apps using camera (Teams, Zoom, browser) |
| **App closes immediately** | • Run `HandFilter.exe` from Command Prompt to see error<br>• Reinstall — model file may be corrupted |
| **Low FPS / lag** | • Lower camera resolution in Menu → Performance<br>• Close other CPU-heavy apps<br>• Ensure good lighting |
| **Hand tracking not working** | • Face a well-lit area (avoid backlighting)<br>• Keep hands within camera frame<br>• Avoid gloves / heavy jewelry |
| **Update check fails** | • App continues normally — check manually via Menu → Check for Updates<br>• Verify internet connection |
| **Antivirus flags HandFilter** | • False positive — HandFilter is open source (MIT)<br>• Add exception for `HandFilter.exe` |

### Linux
| Problem | Solution |
|---------|----------|
| **"Camera unavailable" dialog** | • `sudo usermod -aG video $USER` then re-login<br>• Check camera device: `v4l2-ctl --list-devices`<br>• Close other apps using camera (Cheese, Zoom, browser)<br>• Flatpak/Snap: check desktop portal permissions |
| **AppImage won't run** | • `chmod +x HandFilter-*.AppImage`<br>• Install FUSE: `sudo apt install fuse libfuse2` (Ubuntu/Debian) |
| **Low FPS / lag** | • Lower camera resolution in Menu → Performance<br>• Ensure good lighting<br>• Try X11 session instead of Wayland |
| **Hand tracking not working** | • Face a well-lit area (avoid backlighting)<br>• Keep hands within camera frame<br>• Avoid gloves / heavy jewelry |
| **Desktop entry missing** | • AppImage should auto-integrate; or copy `handfilter.desktop` to `~/.local/share/applications/` |

### macOS
| Problem | Solution |
|---------|----------|
| **"Camera unavailable" dialog** | • System Settings → Privacy & Security → Camera → enable HandFilter<br>• System Settings → Privacy & Security → Screen Recording → enable HandFilter (for window capture)<br>• Close other apps using camera (FaceTime, Zoom, browser) |
| **"App is damaged / can't be opened"** | • Unsigned app — Right-click → Open, or run:<br>`xattr -d com.apple.quarantine /Applications/HandFilter.app` |
| **DMG won't mount** | • `xattr -d com.apple.quarantine HandFilter-*.dmg` then double-click |
| **Low FPS / lag** | • Lower camera resolution in Menu → Performance<br>• Ensure good lighting<br>• Close other CPU-heavy apps |
| **Hand tracking not working** | • Face a well-lit area (avoid backlighting)<br>• Keep hands within camera frame<br>• Avoid gloves / heavy jewelry |

---

## 👨‍💻 Development

### Project Structure
```
HandFilter/
├── main.py              # Entry point, main loop
├── video.py             # VideoStream (capture thread)
├── worker.py            # DetectionWorker (inference thread)
├── hand_tracker.py      # HandTracker (MediaPipe wrapper)
├── gestures.py          # HandGestureController
├── filters.py           # FilterManager (portal filters)
├── drawing.py           # DrawingCanvas (alpha overlay)
├── config.py            # SettingsManager (thread-safe)
├── state.py             # StateManager (mode state machine)
├── ui.py                # PerformanceOverlay, KeyboardMenu
├── error_dialog.py      # User-facing error dialogs
├── updater.py           # Auto-update system
├── platform_utils.py    # Cross-platform abstraction layer
├── version.py           # Single version source
├── main.spec            # PyInstaller build spec (Windows)
├── main_linux.spec      # PyInstaller build spec (Linux)
├── main_macos.spec      # PyInstaller build spec (macOS)
├── installer/           # Inno Setup (Windows) + desktop entry (Linux)
├── packaging/           # Linux AppImage + macOS DMG scripts
└── scripts/             # Build utilities
```

### Building from Source

#### Windows
```bash
# Install build dependencies
pip install pyinstaller

# Build portable executable (onedir)
pyinstaller -y main.spec

# Output: dist/HandFilter/HandFilter.exe

# Build installer (requires Inno Setup 6)
iscc installer/handfilter.iss
# Output: HandFilter-1.0.0-Windows-Setup.exe
```

#### Linux
```bash
# Install system dependencies
sudo apt install python3-tk python3-venv python3-pip \
    libglib2.0-0 libgl1 libegl1 libx11-6 libxext6 libxrender1 \
    appimagetool patchelf desktop-file-utils

# Create venv and install Python deps
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install pyinstaller

# Build portable executable
pyinstaller -y main_linux.spec

# Output: dist/HandFilter/HandFilter

# Build AppImage + tarball
chmod +x packaging/linux/build-appimage.sh
./packaging/linux/build-appimage.sh
# Output: dist/HandFilter-<ver>-Linux-x86_64.AppImage
#         dist/HandFilter-<ver>-Linux-Portable.tar.gz
```

#### macOS
```bash
# Install system dependencies
brew install create-dmg imagemagick

# Create venv and install Python deps
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install pyinstaller

# Generate .icns icon
chmod +x packaging/macos/make-icns.sh
./packaging/macos/make-icns.sh

# Build .app bundle
pyinstaller -y main_macos.spec

# Output: dist/HandFilter.app

# Build DMG
chmod +x packaging/macos/build-dmg.sh
./packaging/macos/build-dmg.sh
# Output: dist/HandFilter-<ver>-macOS-arm64.dmg
```

### Versioning
Single source of truth: `version.py` → `__version__ = "1.0.0"`
- Syncs to: EXE metadata, installer, GitHub release tags
- Run `python scripts/sync-version.py` after version bump

### Architecture Notes
- **Threaded**: Capture thread → Inference thread → Main render loop
- **MediaPipe Task API**: `HandLandmarker` in `VIDEO` mode for low latency
- **SHA-256 model verification** at startup ensures integrity
- **Settings persisted** to:
  - Windows: `%LOCALAPPDATA%\HandFilter\settings.json`
  - Linux: `~/.config/HandFilter/settings.json`
  - macOS: `~/Library/Preferences/HandFilter/settings.json`

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🔗 Links

- **Repository**: https://github.com/SDGamer1263/HandFilter
- **Releases**: https://github.com/SDGamer1263/HandFilter/releases
- **Issues**: https://github.com/SDGamer1263/HandFilter/issues

---

*HandFilter v1.0.0 — Built with OpenCV, MediaPipe, and Python.*