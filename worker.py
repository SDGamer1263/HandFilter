"""Background-threaded MediaPipe hand detection."""

import time
import logging
import numpy as np
import cv2
from threading import Lock, Thread, Event
from typing import Optional

from hand_tracker import HandTracker
from mediapipe.tasks.python.vision import HandLandmarkerResult


class DetectionWorker:
    """Runs hand detection in a background thread so the main loop
    never blocks on MediaPipe inference.

    Call ``update_frame()`` each iteration from the main thread,
    then ``read_result()`` to get the latest detection.
    """

    def __init__(self, tracker: HandTracker):
        self.tracker = tracker
        self._stop_event = Event()
        self._frame: Optional[np.ndarray] = None
        self._result: Optional[HandLandmarkerResult] = None
        self._lock = Lock()
        self._new_frame = False
        self._thread: Optional[Thread] = None
        logging.info("DetectionWorker initialised.")

    def start(self) -> "DetectionWorker":
        self._thread = Thread(target=self._run, daemon=True)
        self._thread.start()
        return self

    def _run(self) -> None:
        while not self._stop_event.is_set():
            with self._lock:
                if self._new_frame and self._frame is not None:
                    frame = self._frame
                    self._new_frame = False
                else:
                    frame = None

            if frame is not None:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = self.tracker.detect(rgb)
                with self._lock:
                    self._result = result
            else:
                time.sleep(0.005)

    def update_frame(self, frame: np.ndarray) -> None:
        with self._lock:
            self._frame = frame
            self._new_frame = True

    def read_result(self) -> Optional[HandLandmarkerResult]:
        with self._lock:
            return self._result

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)
        logging.info("DetectionWorker stopped.")