# Hand Filter

Real-time hand tracking application with drawing, filters, and gesture controls built with OpenCV and MediaPipe.

## Features

- **Hand Tracking**: MediaPipe HandLandmarker (VIDEO mode) with 21 3D landmarks per hand
- **Drawing Mode**: Right index finger acts as a pen (5 fingers up to enable)
- **Portal Filters**: Region between index fingertips applies filters (retro, B&W, invert, pixelate, blur, sketch) selected by right-hand finger count
- **Gesture Controls**:
  - Pinch-and-hold (1s) on left hand: toggle modes
  - Fist on right hand: inhibits drawing
  - 5 fingers on left hand: clear canvas
- **Multi-threaded**: Separate capture, inference, and render threads with thread-safe synchronization
- **Performance Overlay**: Real-time FPS and latency display

## Requirements

- Python 3.8+
- Webcam

## Installation

```bash
pip install opencv-python mediapipe numpy
```

Download the MediaPipe hand landmarker model:
```bash
# Place hand_landmarker.task in the project root
# Download from: https://developers.google.com/mediapipe/solutions/vision/hand_landmarker
```

## Usage

```bash
python main.py
```

### Controls

| Key | Action |
|-----|--------|
| `q` | Quit |
| `c` | Clear canvas |

### Gestures

| Gesture | Hand | Action |
|---------|------|--------|
| 5 fingers up | Right | Enable drawing mode |
| Pinch + hold (1s) | Left | Cycle mode: Filters → Drawing → Menu |
| Fist | Right | Disable drawing (while held) |
| 5 fingers up | Left | Clear canvas |
| Finger count (1-6) | Right | Select filter in Filters mode |

## Architecture

```
main.py              # Application entry point, main loop
video.py             # VideoStream (capture thread)
worker.py            # DetectionWorker (inference thread)
hand_tracker.py      # HandTracker (MediaPipe wrapper)
gestures.py          # HandGestureController (finger count, pinch, fist)
filters.py           # FilterManager (portal region filters)
drawing.py           # DrawingCanvas (alpha-blended overlay)
config.py            # SettingsManager (thread-safe singleton)
state.py             # StateManager (mode state machine)
```

## Model Verification

The `hand_landmarker.task` file is verified via SHA-256 at startup to ensure integrity.

## License

MIT