"""Alpha-blended drawing canvas controlled by hand gestures."""

import cv2
import logging
import numpy as np
from typing import List, Optional, Tuple

from mediapipe.tasks.python.components.containers.landmark import NormalizedLandmark

from config import SettingsManager


class DrawingCanvas:
    """4-channel overlay canvas (BGRA) blended on top of the camera feed.

    When drawing is enabled, the right index fingertip acts as a pen.
    Stroke colour and size come from ``SettingsManager``.
    """

    def __init__(self, width: int, height: int, settings_manager: SettingsManager):
        self.width = width
        self.height = height
        self.settings = settings_manager
        self._canvas = np.zeros((height, width, 4), dtype=np.uint8)
        self._has_content: bool = False
        self._prev: Optional[Tuple[int, int]] = None
        self._drawing_enabled: bool = False

    def update(
        self,
        frame: np.ndarray,
        right_hand_lm: Optional[List[NormalizedLandmark]],
        left_hand_lm: Optional[List[NormalizedLandmark]],
        left_fingers_count: int,
        settings_manager: SettingsManager,
        drawing_enabled: bool,
        is_drawing_hand_fist: bool = False,
    ) -> Tuple[np.ndarray, bool]:
        """Draw a stroke if enabled and not making a fist, then alpha-blend canvas.

        Returns ``(blended_frame, drawing_enabled)``.
        """
        h, w = frame.shape[:2]
        if h != self.height or w != self.width:
            new_canvas = np.zeros((h, w, 4), dtype=np.uint8)
            min_h, min_w = min(h, self.height), min(w, self.width)
            new_canvas[:min_h, :min_w] = self._canvas[:min_h, :min_w]
            self._canvas = new_canvas
            self.height, self.width = h, w

        self._drawing_enabled = drawing_enabled

        if self._drawing_enabled and right_hand_lm and not is_drawing_hand_fist:
            size = self.settings.get_default_brush_size()
            colour = (*self.settings.get_default_brush_color(), 255)
            try:
                tip_idx = settings_manager.get_index_finger_tip_landmark_id()
                if len(right_hand_lm) > tip_idx:
                    pt = right_hand_lm[tip_idx]
                    current = (int(pt.x * w), int(pt.y * h))
                    if self._prev is not None:
                        cv2.line(self._canvas, self._prev, current,
                                 colour, size, cv2.LINE_AA)
                    else:
                        cv2.circle(self._canvas, current, max(1, size // 2),
                                   colour, -1, cv2.LINE_AA)
                    self._has_content = True
                    self._prev = current
                else:
                    self._prev = None
            except Exception as exc:
                logging.warning("Draw error: %s", exc)
                self._prev = None
        else:
            self._prev = None

        if self._has_content:
            mask = self._canvas[:, :, 3] > 0
            if np.any(mask):
                alpha = (self._canvas[mask, 3:4] / 255.0).astype(np.float32)
                fg = self._canvas[mask, :3].astype(np.float32)
                bg = frame[mask].astype(np.float32)
                frame[mask] = (bg * (1.0 - alpha) + fg * alpha).astype(np.uint8)
            else:
                self._has_content = False

        return frame, self._drawing_enabled

    def clear_canvas(self) -> None:
        self._canvas.fill(0)
        self._has_content = False
        self._prev = None
        logging.info("Canvas cleared.")