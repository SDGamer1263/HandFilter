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
| **Zero Dependencies** | Bundled Python, MediaPipe, OpenCV — runs on clean Windows |

---

## 🎮 How to Use

1. **Launch** HandFilter from Start Menu or run `HandFilter.exe`
2. **Allow camera access** when Windows prompts
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

| Requirement | Details |
|-------------|---------|
| **OS** | Windows 10 / 11 (64-bit) |
| **Camera** | Any webcam (720p+ recommended) |
| **RAM** | 500 MB free |
| **Disk** | 200 MB (installer) / 150 MB (portable) |
| **GPU** | Not required (CPU-only MediaPipe) |

> **No Python, no pip, no virtual environments needed.** Everything is bundled.

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| **"Camera unavailable" dialog** | • Check camera is plugged in<br>• Windows Settings → Privacy → Camera → allow apps<br>• Close other apps using camera (Teams, Zoom, browser) |
| **App closes immediately** | • Run `HandFilter.exe` from Command Prompt to see error<br>• Reinstall — model file may be corrupted |
| **Low FPS / lag** | • Lower camera resolution in Menu → Performance<br>• Close other CPU-heavy apps<br>• Ensure good lighting |
| **Hand tracking not working** | • Face a well-lit area (avoid backlighting)<br>• Keep hands within camera frame<br>• Avoid gloves / heavy jewelry |
| **Update check fails** | • App continues normally — check manually via Menu → Check for Updates<br>• Verify internet connection |
| **Antivirus flags HandFilter** | • False positive — HandFilter is open source (MIT)<br>• Add exception for `HandFilter.exe` |

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
├── version.py           # Single version source
├── main.spec            # PyInstaller build spec
├── installer/           # Inno Setup scripts
└── scripts/             # Build utilities
```

### Building from Source
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

### Versioning
Single source of truth: `version.py` → `__version__ = "1.0.0"`
- Syncs to: EXE metadata, installer, GitHub release tags
- Run `python scripts/sync-version.py` after version bump

### Architecture Notes
- **Threaded**: Capture thread → Inference thread → Main render loop
- **MediaPipe Task API**: `HandLandmarker` in `VIDEO` mode for low latency
- **SHA-256 model verification** at startup ensures integrity
- **Settings persisted** to `%APPDATA%\HandFilter\settings.json`

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