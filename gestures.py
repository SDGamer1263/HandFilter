"""Hand gesture recognition — finger counting and pinch detection."""

import time
import math
import logging
from typing import Dict, List, Optional

from mediapipe.tasks.python.components.containers.landmark import NormalizedLandmark

from config import SettingsManager


class HandGestureController:
    """Counts raised fingers and detects pinch-and-hold gestures.

    All logic accounts for the horizontally flipped camera frame:
    MediaPipe's "Right" label = user's physical left hand, and
    vice versa.
    """

    def __init__(self, settings_manager: SettingsManager):
        self.settings = settings_manager
        self._pinch_timers: Dict[str, float] = {"Left": 0.0, "Right": 0.0}
        self._pinch_triggered: Dict[str, bool] = {"Left": False, "Right": False}
        self._drawing_gesture_was_active: bool = False

    # ── finger counting ────────────────────────────────────────────

    def count_fingers(
        self,
        hand_landmarks: Optional[List[NormalizedLandmark]],
        handedness: Optional[str],
    ) -> int:
        """Return number of extended fingers (0-5)."""
        if not hand_landmarks:
            return 0

        tip_ids = [4, 8, 12, 16, 20]
        fingers = []

        # Thumb: compare x against the landmark just below the tip.
        if handedness == "Right":  # MediaPipe "Right" -> user's physical left
            fingers.append(1 if hand_landmarks[4].x < hand_landmarks[3].x else 0)
        else:                      # MediaPipe "Left" -> user's physical right
            fingers.append(1 if hand_landmarks[4].x > hand_landmarks[3].x else 0)

        # Index / middle / ring / pinky: tip above PIP joint.
        for i in range(1, 5):
            fingers.append(
                1 if hand_landmarks[tip_ids[i]].y < hand_landmarks[tip_ids[i] - 2].y
                else 0,
            )

        return sum(fingers)

    # ── pinch-and-hold ──────────────────────────────────────────────

    def is_pinch_and_hold(
        self,
        hand_landmarks: Optional[List[NormalizedLandmark]],
        handedness_label: str,
    ) -> bool:
        """True when thumb + index pinch while middle/ring/pinky are extended,
        held for ``pinch_hold_duration`` seconds. Requires release before refiring."""
        if not hand_landmarks:
            self._pinch_timers[handedness_label] = 0.0
            self._pinch_triggered[handedness_label] = False
            return False

        s = self.settings
        if len(hand_landmarks) <= s.get_pinky_finger_tip_landmark_id():
            self._pinch_timers[handedness_label] = 0.0
            self._pinch_triggered[handedness_label] = False
            return False

        thumb = hand_landmarks[s.get_thumb_tip_landmark_id()]
        index = hand_landmarks[s.get_index_finger_tip_landmark_id()]
        middle = hand_landmarks[s.get_middle_finger_tip_landmark_id()]
        ring = hand_landmarks[s.get_ring_finger_tip_landmark_id()]
        pinky = hand_landmarks[s.get_pinky_finger_tip_landmark_id()]

        dx = thumb.x - index.x
        dy = thumb.y - index.y
        dist = math.hypot(dx, dy)
        is_pinching = dist < s.get_pinch_distance_threshold()

        # At least one other finger extended (not a fist)
        middle_extended = middle.y < hand_landmarks[s.get_middle_finger_tip_landmark_id() - 2].y
        ring_extended = ring.y < hand_landmarks[s.get_ring_finger_tip_landmark_id() - 2].y
        pinky_extended = pinky.y < hand_landmarks[s.get_pinky_finger_tip_landmark_id() - 2].y
        not_fist = middle_extended or ring_extended or pinky_extended

        now = time.monotonic()
        if is_pinching and not_fist:
            if self._pinch_triggered[handedness_label]:
                return False
            if self._pinch_timers[handedness_label] == 0.0:
                self._pinch_timers[handedness_label] = now
            elif (now - self._pinch_timers[handedness_label]) >= s.get_pinch_hold_duration():
                self._pinch_triggered[handedness_label] = True
                self._pinch_timers[handedness_label] = 0.0
                return True
        else:
            self._pinch_timers[handedness_label] = 0.0
            self._pinch_triggered[handedness_label] = False

        return False

    def is_fist(
        self,
        hand_landmarks: Optional[List[NormalizedLandmark]],
        handedness: Optional[str],
    ) -> bool:
        """Return True if hand is present and in a fist position (0 extended fingers)."""
        if not hand_landmarks:
            return False
        return self.count_fingers(hand_landmarks, handedness) == 0

    # ── drawing-mode toggle ─────────────────────────────────────────

    def should_toggle_drawing_mode(
        self,
        left_hand_lm: Optional[List[NormalizedLandmark]],
        left_fingers_count: int,
    ) -> bool:
        if left_hand_lm and left_fingers_count == self.settings.get_drawing_enabled_finger_count():
            if not self._drawing_gesture_was_active:
                self._drawing_gesture_was_active = True
                return True
        else:
            self._drawing_gesture_was_active = False
        return False