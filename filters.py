"""Image-processing filters and the FilterManager that routes them."""

import cv2
import logging
import numpy as np
from typing import Callable, List, Optional, Tuple

from mediapipe.tasks.python.components.containers.landmark import NormalizedLandmark

from config import SettingsManager


# ── individual filter functions ───────────────────────────────────────

def apply_retro_film(img: np.ndarray) -> np.ndarray:
    """S-curve tone-map + warm tint + film grain."""
    try:
        if not hasattr(apply_retro_film, "_lut"):
            lut = np.arange(256, dtype=np.float32)
            lut = np.where(
                lut / 255.0 <= 0.5,
                2 * (lut / 255.0) ** 2,
                1 - 2 * (1 - lut / 255.0) ** 2,
            )
            apply_retro_film._lut = np.clip(lut * 255, 0, 255).astype(np.uint8)

        b, g, r = cv2.split(img)
        b = cv2.LUT(b, apply_retro_film._lut)
        g = cv2.LUT(g, apply_retro_film._lut)
        r = cv2.LUT(r, apply_retro_film._lut)
        toned = cv2.merge((b, g, r)).astype(np.float32)

        tint = np.array([[1, 0, 0], [0, 1.05, 0], [0, 0, 1.1]])
        toned = cv2.transform(toned, tint)

        noise = np.random.randint(-10, 11, img.shape, dtype=np.int16)
        toned += noise

        return np.clip(toned, 0, 255).astype(np.uint8)
    except Exception as exc:
        logging.error("apply_retro_film failed: %s", exc)
        return img


def apply_black_and_white(img: np.ndarray) -> np.ndarray:
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, bw = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        return cv2.cvtColor(bw, cv2.COLOR_GRAY2BGR)
    except Exception as exc:
        logging.error("apply_black_and_white failed: %s", exc)
        return img


def apply_invert(img: np.ndarray) -> np.ndarray:
    return cv2.bitwise_not(img)


def apply_pixelate(img: np.ndarray, pixels: int = 10) -> np.ndarray:
    h, w = img.shape[:2]
    if h <= 0 or w <= 0:
        return img
    try:
        small_w = max(1, w // pixels)
        small_h = max(1, h // pixels)
        small = cv2.resize(img, (small_w, small_h), interpolation=cv2.INTER_LINEAR)
        return cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
    except Exception as exc:
        logging.error("apply_pixelate failed: %s", exc)
        return img


def apply_blur(img: np.ndarray, ksize: Tuple[int, int] = (15, 15)) -> np.ndarray:
    try:
        return cv2.GaussianBlur(img, ksize, 0)
    except Exception as exc:
        logging.error("apply_blur failed: %s", exc)
        return img


def apply_sketch(img: np.ndarray) -> np.ndarray:
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2,
        )
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    except Exception as exc:
        logging.error("apply_sketch failed: %s", exc)
        return img


# ── filter manager ────────────────────────────────────────────────────

class FilterManager:
    """Picks a filter from the registered list via finger count and
    applies it to the portal region defined by two index fingertips."""

    def __init__(self, settings_manager: SettingsManager):
        self.settings = settings_manager
        self.filters: List[Callable[[np.ndarray], np.ndarray]] = [
            apply_retro_film,
            apply_black_and_white,
            apply_invert,
            apply_pixelate,
            apply_blur,
            apply_sketch,
        ]
        self._active: Optional[Callable[[np.ndarray], np.ndarray]] = None

    # ── selection ─────────────────────────────────────────────────

    def select_filter(self, num_fingers: int) -> None:
        if num_fingers > 0:
            idx = (num_fingers - 1) % len(self.filters)
            self._active = self.filters[idx]
        else:
            self._active = None

    def get_active_filter_name(self) -> str:
        return self._active.__name__ if self._active else "None"

    # ── portal processing ──────────────────────────────────────────

    def process_portal_region(
        self,
        frame: np.ndarray,
        left_hand_lm: Optional[List[NormalizedLandmark]],
        right_hand_lm: Optional[List[NormalizedLandmark]],
        left_handedness_str: Optional[str],
        right_handedness_str: Optional[str],
        gesture_controller,
    ) -> str:
        h, w = frame.shape[:2]

        if not left_hand_lm or not right_hand_lm:
            self.select_filter(0)
            return "None"

        try:
            idx_id = self.settings.get_index_finger_tip_landmark_id()
            if len(left_hand_lm) <= idx_id or len(right_hand_lm) <= idx_id:
                self.select_filter(0)
                return "None"

            lx = int(left_hand_lm[idx_id].x * w)
            ly = int(left_hand_lm[idx_id].y * h)
            rx = int(right_hand_lm[idx_id].x * w)
            ry = int(right_hand_lm[idx_id].y * h)

            x1, x2 = min(lx, rx), max(lx, rx)
            y1, y2 = min(ly, ry), max(ly, ry)

            num = gesture_controller.count_fingers(right_hand_lm, right_handedness_str)
            self.select_filter(num)

            if self._active and x1 < x2 and y1 < y2:
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)

                region = frame[y1:y2, x1:x2]
                if region.size > 0:
                    filtered = self._active(region)
                    if filtered.ndim == 2:
                        filtered = cv2.cvtColor(filtered, cv2.COLOR_GRAY2BGR)
                    if filtered.shape == region.shape:
                        frame[y1:y2, x1:x2] = filtered

            cv2.rectangle(
                frame, (x1, y1), (x2, y2),
                self.settings.get_portal_border_color(),
                self.settings.get_portal_border_thickness(),
            )
            return self.get_active_filter_name()
        except Exception as exc:
            logging.error("process_portal_region failed: %s", exc)
            self.select_filter(0)
            return "None"