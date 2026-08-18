"""UI helpers — window creation, performance overlay, keyboard menu."""

import logging
import cv2
import numpy as np
from typing import Dict, List, Tuple, Union

from config import SettingsManager


def create_window(name: str, fullscreen: bool) -> None:
    cv2.namedWindow(name, cv2.WND_PROP_FULLSCREEN)
    if fullscreen:
        cv2.setWindowProperty(name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)


class PerformanceOverlay:
    """Draws live FPS, frame-time, and profiling metrics on the frame."""

    def __init__(self, width: int, height: int, settings_manager: SettingsManager):
        self.settings = settings_manager
        self._metrics: Dict[str, Union[float, int, str]] = {}

    def update_metrics(self, values: Dict[str, Union[float, int, str]]) -> None:
        self._metrics.update(values)

    def draw(self, frame: np.ndarray) -> np.ndarray:
        if not self.settings.get_show_performance_overlay():
            return frame

        y = 30
        for label, value in self._metrics.items():
            text = f"{label}: {value:.2f}" if isinstance(value, float) else f"{label}: {value}"
            cv2.putText(
                frame, text, (10, y),
                self.settings.get_performance_text_font(),
                self.settings.get_performance_text_scale(),
                self.settings.get_performance_text_color(),
                self.settings.get_performance_text_thickness(),
                cv2.LINE_AA,
            )
            y += 25
        return frame


class KeyboardMenu:
    """Transparent overlay menu navigated with WASD / arrow keys."""

    def __init__(self, width: int, height: int, settings_manager: SettingsManager):
        self.settings = settings_manager
        self._width = width
        self._height = height
        self.visible: bool = False
        self._items: Dict[str, dict] = {}
        self._keys: List[str] = []
        self._sel: int = 0
        self._build()

    # ── setup ───────────────────────────────────────────────────────

    def _build(self) -> None:
        palette = self.settings.get_color_palette()
        default = self.settings.get_default_brush_color()
        try:
            colour_idx = palette.index(default)
        except ValueError:
            colour_idx = 0

        self._items = {
            "brush_size": {
                "label": "Brush Size",
                "value": self.settings.get_default_brush_size(),
                "min": 1, "max": 50,
                "pos": (self._width - 300, 100),
            },
            "brush_color": {
                "label": "Brush Color",
                "value": colour_idx,
                "min": 0, "max": len(palette) - 1,
                "pos": (self._width - 300, 150),
            },
            "perf_overlay": {
                "label": "Perf Overlay",
                "value": int(self.settings.get_show_performance_overlay()),
                "min": 0, "max": 1,
                "pos": (self._width - 300, 200),
                "toggle": True,
            },
        }
        self._keys = list(self._items)
        self._sel = 0

    # ── navigation ──────────────────────────────────────────────────

    def navigate(self, direction: int) -> None:
        if not self.visible or not self._keys:
            return
        self._sel = (self._sel + direction) % len(self._keys)

    def update_selected_control(self, delta: int) -> None:
        if not self.visible or not self._keys:
            return

        key = self._keys[self._sel]
        item = self._items[key]

        if item.get("toggle"):
            new = 1 - int(item["value"])
            item["value"] = new
            if key == "perf_overlay":
                self.settings.set_show_performance_overlay(bool(new))
        else:
            new = int(np.clip(int(item["value"]) + delta,
                              item["min"], item["max"]))
            item["value"] = new
            if key == "brush_size":
                self.settings.set_default_brush_size(new)
                logging.info("Brush size: %d", new)
            elif key == "brush_color":
                self.settings.set_default_brush_color_by_index(new)
                logging.info("Brush color index: %d", new)

    # ── draw ────────────────────────────────────────────────────────

    def draw(self, frame: np.ndarray) -> np.ndarray:
        if not self.visible:
            return frame

        x1, y1 = max(0, self._width - 330), max(0, 60)
        x2, y2 = min(self._width, self._width - 30), min(self._height, 240)
        if x1 >= x2 or y1 >= y2:
            return frame

        bg = np.full(
            frame[y1:y2, x1:x2].shape, (50, 50, 50), dtype=np.uint8,
        )
        frame[y1:y2, x1:x2] = cv2.addWeighted(bg, 0.6, frame[y1:y2, x1:x2], 0.4, 0)

        palette = self.settings.get_color_palette()

        for i, key in enumerate(self._keys):
            item = self._items[key]
            px, py = item["pos"]
            label = item["label"]
            val = item["value"]

            colour = (0, 255, 255) if i == self._sel else (255, 255, 255)

            text = f"{label}: "
            if key == "brush_size":
                text += str(int(val))
            elif key == "brush_color":
                ci = int(np.clip(val, 0, len(palette) - 1))
                sw_x1 = px + 180
                sw_y1 = py - 15
                sw_x2 = px + 220
                sw_y2 = py + 5
                if sw_x2 <= self._width and sw_y2 <= self._height:
                    cv2.rectangle(frame, (sw_x1, sw_y1), (sw_x2, sw_y2),
                                  palette[ci], cv2.FILLED)
            elif key == "perf_overlay":
                text += "ON" if val else "OFF"

            cv2.putText(frame, text, (px, py),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, colour, 2, cv2.LINE_AA)

        return frame