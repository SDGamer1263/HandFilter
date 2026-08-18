"""Centralized application settings via a thread-safe singleton."""

import os
import sys
import threading
import cv2
import logging
import numpy as np
from typing import Any, List, Optional, Tuple, Union


class SettingsManager:
    """Singleton that holds every configurable value for the app.

    All setters validate input ranges. Getters return immutable copies where
    the value is compound (tuples); scalars and dicts are returned directly.

    Access via ``SettingsManager()`` — the first call initializes defaults,
    subsequent calls return the same instance.
    """

    _instance: "SettingsManager | None" = None
    _lock = threading.Lock()

    def __new__(cls) -> "SettingsManager":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    # ── initialisation ────────────────────────────────────────────────

    def _initialize(self) -> None:
        # Camera
        self._cam_index: int = 0
        self._cam_width: int = 1280
        self._cam_height: int = 720
        self._fullscreen: bool = True

        # Hand detection
        self._num_hands: int = 2
        self._min_detection_confidence: float = 0.7
        self._min_tracking_confidence: float = 0.5

        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        self._hand_landmarker_model: str = os.path.join(base_dir, "hand_landmarker.task")
        self._process_every_n_frames: int = 2

        # UI
        self._window_name: str = "Hand Filter"
        self._portal_border_color: Tuple[int, int, int] = (255, 0, 255)  # BGR
        self._portal_border_thickness: int = 2
        self._left_hand_color: Tuple[int, int, int] = (255, 0, 0)   # blue
        self._right_hand_color: Tuple[int, int, int] = (0, 0, 255)  # red
        self._landmark_drawing_spec: dict = {"thickness": 2, "circle_radius": 2}
        self._connection_drawing_spec: dict = {"thickness": 2}

        # Drawing
        self._drawing_enabled_finger_count: int = 5
        self._default_brush_size: int = 10
        self._default_brush_color: Tuple[int, int, int] = (0, 0, 255)  # red BGR
        self._color_palette: List[Tuple[int, int, int]] = [
            (0, 0, 255),    # red
            (0, 255, 0),    # green
            (255, 0, 0),    # blue
            (0, 255, 255),  # yellow
            (255, 0, 255),  # magenta
            (255, 255, 0),  # cyan
            (255, 255, 255),# white
        ]
        self._eraser_color: Tuple[int, int, int] = (0, 0, 0)
        self._canvas_alpha: float = 0.6

        # Gesture recognition
        self._thumb_tip_lm: int = 4
        self._index_tip_lm: int = 8
        self._middle_tip_lm: int = 12
        self._ring_tip_lm: int = 16
        self._pinky_tip_lm: int = 20
        self._pinch_distance_threshold: float = 0.05
        self._pinch_hold_duration: float = 1.0

        # Controls
        self._clear_canvas_finger_count: int = 5
        self._clear_canvas_hand: str = "Left"

        # Performance overlay
        self._show_performance_overlay: bool = True
        self._perf_text_color: Tuple[int, int, int] = (0, 255, 0)
        self._perf_text_font: Any = cv2.FONT_HERSHEY_SIMPLEX
        self._perf_text_scale: float = 0.7
        self._perf_text_thickness: int = 2

        # Keyboard controls
        self._exit_key: str = "q"
        self._clear_canvas_key: str = "c"

    # ── getters ───────────────────────────────────────────────────────

    def get_cam_index(self) -> int: return self._cam_index
    def get_cam_width(self) -> int: return self._cam_width
    def get_cam_height(self) -> int: return self._cam_height
    def get_fullscreen(self) -> bool: return self._fullscreen

    def get_num_hands(self) -> int: return self._num_hands
    def get_min_detection_confidence(self) -> float: return self._min_detection_confidence
    def get_min_tracking_confidence(self) -> float: return self._min_tracking_confidence
    def get_hand_landmarker_model(self) -> str: return self._hand_landmarker_model
    def get_process_every_n_frames(self) -> int: return self._process_every_n_frames

    def get_window_name(self) -> str: return self._window_name
    def get_portal_border_color(self) -> Tuple[int, int, int]: return self._portal_border_color
    def get_portal_border_thickness(self) -> int: return self._portal_border_thickness
    def get_left_hand_color(self) -> Tuple[int, int, int]: return self._left_hand_color
    def get_right_hand_color(self) -> Tuple[int, int, int]: return self._right_hand_color
    def get_landmark_drawing_spec(self) -> dict: return self._landmark_drawing_spec
    def get_connection_drawing_spec(self) -> dict: return self._connection_drawing_spec

    def get_drawing_enabled_finger_count(self) -> int: return self._drawing_enabled_finger_count
    def get_default_brush_size(self) -> int: return self._default_brush_size
    def get_default_brush_color(self) -> Tuple[int, int, int]: return self._default_brush_color
    def get_color_palette(self) -> List[Tuple[int, int, int]]: return self._color_palette
    def get_eraser_color(self) -> Tuple[int, int, int]: return self._eraser_color
    def get_canvas_alpha(self) -> float: return self._canvas_alpha

    def get_thumb_tip_landmark_id(self) -> int: return self._thumb_tip_lm
    def get_index_finger_tip_landmark_id(self) -> int: return self._index_tip_lm
    def get_middle_finger_tip_landmark_id(self) -> int: return self._middle_tip_lm
    def get_ring_finger_tip_landmark_id(self) -> int: return self._ring_tip_lm
    def get_pinky_finger_tip_landmark_id(self) -> int: return self._pinky_tip_lm
    def get_pinch_distance_threshold(self) -> float: return self._pinch_distance_threshold
    def get_pinch_hold_duration(self) -> float: return self._pinch_hold_duration

    def get_show_performance_overlay(self) -> bool: return self._show_performance_overlay
    def get_performance_text_color(self) -> Tuple[int, int, int]: return self._perf_text_color
    def get_performance_text_font(self) -> Any: return self._perf_text_font
    def get_performance_text_scale(self) -> float: return self._perf_text_scale
    def get_performance_text_thickness(self) -> int: return self._perf_text_thickness

    def get_exit_key(self) -> str: return self._exit_key
    def get_clear_canvas_key(self) -> str: return self._clear_canvas_key

    # ── setters (with bounds validation) ──────────────────────────────

    def set_cam_index(self, value: int) -> None:
        self._cam_index = int(np.clip(value, 0, 10))

    def set_cam_width(self, value: int) -> None:
        self._cam_width = int(np.clip(value, 640, 1920))

    def set_cam_height(self, value: int) -> None:
        self._cam_height = int(np.clip(value, 480, 1080))

    def set_fullscreen(self, value: bool) -> None:
        self._fullscreen = bool(value)

    def set_min_detection_confidence(self, value: float) -> None:
        self._min_detection_confidence = float(np.clip(value, 0.0, 1.0))

    def set_min_tracking_confidence(self, value: float) -> None:
        self._min_tracking_confidence = float(np.clip(value, 0.0, 1.0))

    def set_process_every_n_frames(self, value: int) -> None:
        self._process_every_n_frames = int(np.clip(value, 1, 10))

    def set_portal_border_thickness(self, value: int) -> None:
        self._portal_border_thickness = int(np.clip(value, 1, 10))

    def set_default_brush_size(self, value: int) -> None:
        self._default_brush_size = int(np.clip(value, 1, 50))

    def set_default_brush_color(self, value: Union[int, Tuple[int, int, int]]) -> None:
        if isinstance(value, tuple) and len(value) == 3:
            self._default_brush_color = value
        elif isinstance(value, int) and 0 <= value < len(self._color_palette):
            self._default_brush_color = self._color_palette[value]
        else:
            logging.warning("Invalid brush color value: %s. Keeping current.", value)

    def set_default_brush_color_by_index(self, index: int) -> None:
        if 0 <= index < len(self._color_palette):
            self._default_brush_color = self._color_palette[index]
        else:
            logging.warning("Invalid brush color index: %d. Keeping current.", index)

    def set_pinch_distance_threshold(self, value: float) -> None:
        self._pinch_distance_threshold = float(np.clip(value, 0.01, 0.1))

    def set_show_performance_overlay(self, value: bool) -> None:
        self._show_performance_overlay = bool(value)

    def set_performance_text_scale(self, value: float) -> None:
        self._perf_text_scale = float(np.clip(value, 0.1, 2.0))

    def set_performance_text_thickness(self, value: int) -> None:
        self._perf_text_thickness = int(np.clip(value, 1, 5))

    def set_exit_key(self, value: str) -> None:
        self._exit_key = value

    def set_clear_canvas_key(self, value: str) -> None:
        self._clear_canvas_key = value