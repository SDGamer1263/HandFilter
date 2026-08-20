"""Main application loop for Hand Filter — webcam + hand tracking + filters + drawing."""

import os
import time
import logging
import cv2
import sys
from typing import Dict, List, Optional, Tuple, Union

from mediapipe.tasks.python.components.containers.landmark import NormalizedLandmark
from mediapipe.tasks.python.vision import HandLandmarkerResult

from config import SettingsManager
from state import StateManager, ApplicationMode
from hand_tracker import HandTracker, draw_landmarks_on_image
from gestures import HandGestureController
from filters import FilterManager
from ui import PerformanceOverlay, KeyboardMenu, create_window
from drawing import DrawingCanvas
from video import VideoStream
from worker import DetectionWorker
import error_dialog
from updater import UpdateChecker

# ── logging ────────────────────────────────────────────────────────────

log_level_name = os.environ.get("HAND_FILTER_LOG_LEVEL", "INFO").upper()
log_level = getattr(logging, log_level_name, logging.INFO)
logging.basicConfig(
    level=log_level, format="%(asctime)s - %(levelname)s - %(message)s"
)

# ── helpers ────────────────────────────────────────────────────────────

def _resolve_hands(
    detection_result: Optional[HandLandmarkerResult],
) -> Tuple[
    Optional[List[NormalizedLandmark]],
    Optional[List[NormalizedLandmark]],
    Optional[str],
    Optional[str],
]:
    """Extract physical left/right landmarks from a (flipped) detection.

    Because the frame is mirrored, MediaPipe "Right" → user's physical
    left hand, and vice versa.
    """
    left_lm = right_lm = None
    left_str = right_str = None

    if detection_result is None or not detection_result.hand_landmarks:
        return left_lm, right_lm, left_str, right_str

    for i, handedness in enumerate(detection_result.handedness):
        cat = handedness[0].category_name
        if cat == "Left":   # MediaPipe Left → appears on right → physical right
            right_lm = detection_result.hand_landmarks[i]
            right_str = "Right"
        else:               # MediaPipe Right → physical left
            left_lm = detection_result.hand_landmarks[i]
            left_str = "Left"

    return left_lm, right_lm, left_str, right_str


# ── main loop ──────────────────────────────────────────────────────────

def main() -> None:
    logging.info("Starting Hand Filter.")

    # ---- bootstrap components ----
    settings = SettingsManager()
    state = StateManager(settings)

    tracker = HandTracker(settings)
    if tracker.detector is None:
        error_dialog.show_model_error("HandTracker detector failed to initialise.")

    vs = None
    while vs is None:
        try:
            vs = VideoStream(
                src=settings.get_cam_index(),
                width=settings.get_cam_width(),
                height=settings.get_cam_height(),
            ).start()
            logging.info("Video stream started.")
        except Exception as exc:
            logging.error("Failed to initialize camera: %s", exc)
            if not error_dialog.show_camera_error():
                tracker.close()
                sys.exit(0)
            # User clicked Retry - loop continues

    worker = DetectionWorker(tracker).start()
    logging.info("Detection worker started.")

    create_window(settings.get_window_name(), settings.get_fullscreen())

    # Start background update checker after window is up (non-blocking)
    update_checker = UpdateChecker()
    update_checker.start(delay=5)

    # Components that need frame dimensions → created lazily.
    drawing: Optional[DrawingCanvas] = None
    keyboard_menu: Optional[KeyboardMenu] = None
    overlay: Optional[PerformanceOverlay] = None

    controller = HandGestureController(settings)
    filters = FilterManager(settings)

    #  state
    canvas_cleared_at: float = -2.0  # negative to avoid initial toast
    CLEAR_MESSAGE_DURATION = 2.0

    prev_time = time.time()
    fps_history: List[float] = []
    profiling: Dict[str, float] = {}
    active_filter = "None"
    frame_counter: int = 0

    logging.info("Entering main loop.")

    while True:
        t0 = time.time()

        frame = vs.read()
        if frame is None:
            time.sleep(0.005)
            continue

        frame = cv2.flip(frame, 1)
        frame_counter += 1
        if frame_counter % settings.get_process_every_n_frames() == 0:
            worker.update_frame(frame.copy())

        # Lazy init of size-dependent components.
        h, w = frame.shape[:2]
        if drawing is None:
            drawing = DrawingCanvas(w, h, settings)
            keyboard_menu = KeyboardMenu(w, h, settings)
            overlay = PerformanceOverlay(w, h, settings)
            logging.info("First frame initialised (%dx%d).", w, h)

        detection = worker.read_result()
        left_lm, right_lm, left_hs, right_hs = _resolve_hands(detection)

        # Left-hand gestures
        left_fingers = controller.count_fingers(left_lm, left_hs) if left_lm else 0

        if controller.should_toggle_drawing_mode(left_lm, left_fingers):
            state.update_drawing_status(not state.drawing_enabled)

        # Landmarks rendering (on RGB; convert back)
        t_lm = time.time()
        if detection is not None and detection.hand_landmarks:
            annotated = draw_landmarks_on_image(
                cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                detection,
                settings.get_landmark_drawing_spec(),
                settings.get_connection_drawing_spec(),
                settings.get_left_hand_color(),
                settings.get_right_hand_color(),
            )
            frame = cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR)
        profiling["landmarks_ms"] = (time.time() - t_lm) * 1000

        # ── menu mode ────────────────────────────────────────────────
        t_menu = time.time()
        if state.is_mode(ApplicationMode.MENU):
            frame = keyboard_menu.draw(frame)
        profiling["menu_draw_ms"] = (time.time() - t_menu) * 1000

        # ── drawing / filters (only when not in menu) ────────────────
        if not state.is_mode(ApplicationMode.MENU):
            t_draw = time.time()
            right_is_fist = controller.is_fist(right_lm, right_hs) if right_lm else False
            frame, _ = drawing.update(
                frame, right_lm, left_lm, left_fingers,
                settings, state.is_mode(ApplicationMode.DRAWING),
                is_drawing_hand_fist=right_is_fist,
            )
            profiling["drawing_update_ms"] = (time.time() - t_draw) * 1000

            # Fist-and-hold (1s) = clear canvas
            if (
                left_lm
                and controller.is_fist_and_hold(left_lm, "Left")
                and state.is_mode(ApplicationMode.DRAWING)
            ):
                drawing.clear_canvas()
                canvas_cleared_at = time.time()

            # Filters
            t_filt = time.time()
            if state.is_mode(ApplicationMode.FILTERS) and left_lm and right_lm:
                active_filter = filters.process_portal_region(
                    frame, left_lm, right_lm, left_hs, right_hs, controller,
                )
            else:
                active_filter = "None"
            profiling["filter_processing_ms"] = (time.time() - t_filt) * 1000

        # ── "Canvas Cleared" toast ───────────────────────────────────
        if time.time() - canvas_cleared_at < CLEAR_MESSAGE_DURATION:
            cv2.putText(
                frame, "Canvas Cleared", (w // 2 - 100, h // 2),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA,
            )

        # ── FPS / metrics ────────────────────────────────────────────
        now = time.time()
        dt = now - prev_time
        prev_time = now

        current_fps = 1.0 / dt if dt > 0 else 0.0
        fps_history.append(current_fps)
        if len(fps_history) > 30:
            fps_history.pop(0)
        avg_fps = sum(fps_history) / len(fps_history) if fps_history else 0

        metrics: Dict[str, Union[float, int, str]] = {
            "FPS (Current)": current_fps,
            "FPS (Average)": avg_fps,
            "Frame Time (ms)": dt * 1000,
            "Hands": len(detection.hand_landmarks)
            if detection and detection.hand_landmarks
            else 0,
            "Mode": state.get_current_mode_name(),
            "Active Filter": active_filter,
            "CPU Time (ms)": (time.time() - t0) * 1000,
        }
        metrics.update(profiling)

        t_ov = time.time()
        overlay.update_metrics(metrics)
        frame = overlay.draw(frame)
        profiling["overlay_draw_ms"] = (time.time() - t_ov) * 1000

        cv2.imshow(settings.get_window_name(), frame)

        # ── keyboard input ───────────────────────────────────────────
        key = cv2.waitKey(1) & 0xFF

        if key == ord(settings.get_exit_key()):
            break
        elif key == ord("m"):  # toggle menu
            state.toggle_menu()
            keyboard_menu.visible = not keyboard_menu.visible
        elif (
            key == ord(settings.get_clear_canvas_key())
            and state.is_mode(ApplicationMode.DRAWING)
        ):
            drawing.clear_canvas()
            canvas_cleared_at = time.time()
        elif state.is_mode(ApplicationMode.MENU):
            if key == ord("w"):
                keyboard_menu.navigate(-1)
            elif key == ord("s"):
                keyboard_menu.navigate(1)
            elif key == ord("a"):
                keyboard_menu.update_selected_control(-1)
            elif key == ord("d"):
                keyboard_menu.update_selected_control(1)
            elif key == 27:  # ESC
                state.toggle_menu()
                keyboard_menu.visible = not keyboard_menu.visible

    # ── cleanup ─────────────────────────────────────────────────────
    logging.info("Shutting down...")
    vs.stop()
    worker.stop()
    time.sleep(0.3)
    cv2.destroyAllWindows()
    tracker.close()
    logging.info("Exit clean.")


if __name__ == "__main__":
    main()