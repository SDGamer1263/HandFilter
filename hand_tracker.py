"""MediaPipe Hand Landmarker wrapper and landmark rendering."""

import os
import time
import hashlib
import cv2
import logging
import numpy as np
from typing import List, Optional, Tuple

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe import Image as MpImage, ImageFormat as MpImageFormat
from mediapipe.tasks.python.components.containers.landmark import NormalizedLandmark
from mediapipe.tasks.python.vision import HandLandmarkerResult

from config import SettingsManager

MODEL_SHA256: str = "fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1"


class HandTracker:
    """Creates and owns a MediaPipe ``HandLandmarker`` detector.

    Accepts RGB ``np.ndarray`` frames; returns
    ``HandLandmarkerResult`` or ``None`` on failure.
    """

    def __init__(self, settings_manager: SettingsManager):
        self.settings = settings_manager
        self._last_timestamp_ms: int = 0
        self.detector: Optional[vision.HandLandmarker] = self._build()

    def _build(self) -> Optional[vision.HandLandmarker]:
        model_path = self.settings.get_hand_landmarker_model()
        if not os.path.exists(model_path):
            logging.error("MediaPipe model file not found at: %s", model_path)
            return None

        # Verify model file integrity
        try:
            hasher = hashlib.sha256()
            with open(model_path, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    hasher.update(chunk)
            digest = hasher.hexdigest()
            if digest != MODEL_SHA256:
                logging.warning(
                    "Model SHA-256 mismatch (got %s, expected %s). Proceeding with caution.",
                    digest, MODEL_SHA256
                )
        except Exception as exc:
            logging.error("Failed to verify model checksum: %s", exc)
            return None

        try:
            base = python.BaseOptions(
                model_asset_path=model_path,
            )
            opts = vision.HandLandmarkerOptions(
                base_options=base,
                running_mode=vision.RunningMode.VIDEO,
                num_hands=self.settings.get_num_hands(),
                min_hand_detection_confidence=self.settings.get_min_detection_confidence(),
                min_hand_presence_confidence=self.settings.get_min_detection_confidence(),
                min_tracking_confidence=self.settings.get_min_tracking_confidence(),
            )
            return vision.HandLandmarker.create_from_options(opts)
        except Exception as exc:
            logging.error("Failed to create HandLandmarker: %s", exc)
            return None

    def detect(self, img_rgb: np.ndarray) -> Optional[HandLandmarkerResult]:
        if self.detector is None:
            return None
        mp_image = MpImage(image_format=MpImageFormat.SRGB, data=img_rgb)
        timestamp_ms = time.monotonic_ns() // 1_000_000
        if timestamp_ms <= self._last_timestamp_ms:
            timestamp_ms = self._last_timestamp_ms + 1
        self._last_timestamp_ms = timestamp_ms
        return self.detector.detect_for_video(mp_image, timestamp_ms)

    def close(self) -> None:
        if self.detector is not None:
            self.detector.close()
            logging.info("HandLandmarker closed.")


# ── landmark rendering ────────────────────────────────────────────────

HAND_CONNECTIONS: List[Tuple[int, int]] = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # thumb
    (0, 5), (5, 6), (6, 7), (7, 8),          # index
    (0, 9), (9, 10), (10, 11), (11, 12),     # middle
    (0, 13), (13, 14), (14, 15), (15, 16),   # ring
    (0, 17), (17, 18), (18, 19), (19, 20),   # pinky
    (5, 9), (9, 13), (13, 17),               # palm
]


def draw_landmarks_on_image(
    rgb_image: np.ndarray,
    detection_result: Optional[HandLandmarkerResult],
    landmark_spec: dict,
    connection_spec: dict,
    left_hand_color: Tuple[int, int, int],
    right_hand_color: Tuple[int, int, int],
) -> np.ndarray:
    """Draw landmarks + connections directly on *rgb_image* (mutated).

    Color is chosen per-hand: MediaPipe's "Right" label corresponds
    to the user's *physical* left hand (frame is flipped upstream).
    """
    h, w, _ = rgb_image.shape
    if (
        detection_result is None
        or not detection_result.hand_landmarks
        or not detection_result.handedness
    ):
        return rgb_image

    for idx, landmarks in enumerate(detection_result.hand_landmarks):
        if idx >= len(detection_result.handedness):
            continue

        handedness = detection_result.handedness[idx][0].category_name
        color = left_hand_color if handedness == "Right" else right_hand_color

        for lm in landmarks:
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(rgb_image, (cx, cy),
                       landmark_spec["circle_radius"], color,
                       landmark_spec["thickness"])

        for start, end in HAND_CONNECTIONS:
            if start >= len(landmarks) or end >= len(landmarks):
                continue
            sx = int(landmarks[start].x * w)
            sy = int(landmarks[start].y * h)
            ex = int(landmarks[end].x * w)
            ey = int(landmarks[end].y * h)
            cv2.line(rgb_image, (sx, sy), (ex, ey),
                     color, connection_spec["thickness"])

    return rgb_image