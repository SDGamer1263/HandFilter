"""Threaded camera capture for non-blocking frame reads."""

import cv2
import logging
from threading import Lock, Thread, Event
from typing import Optional
import numpy as np


class VideoStream:
    """Reads frames from ``cv2.VideoCapture`` in a background thread.

    Call ``start()`` to begin capture, ``read()`` from the main thread
    to grab the latest frame, and ``stop()`` to shut down.
    """

    def __init__(self, src: int = 0, width: int = 1280, height: int = 720):
        self.stream = cv2.VideoCapture(src)
        if not self.stream.isOpened():
            raise IOError(f"Cannot open camera {src}")

        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.stream.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        self.grabbed: bool = False
        self.frame: Optional[np.ndarray] = None
        self._stop_event = Event()
        self._lock = Lock()
        self._thread: Optional[Thread] = None
        logging.info("VideoStream opened for source %d at %dx%d.", src, width, height)

    def start(self) -> "VideoStream":
        self._thread = Thread(target=self._update, daemon=True)
        self._thread.start()
        return self

    def _update(self) -> None:
        while not self._stop_event.is_set():
            grabbed, frame = self.stream.read()
            with self._lock:
                self.grabbed = grabbed
                self.frame = frame

    def read(self) -> Optional[np.ndarray]:
        with self._lock:
            return self.frame

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)
        self.stream.release()
        logging.info("VideoStream stopped.")