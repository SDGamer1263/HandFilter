"""Application mode state machine."""

from enum import Enum, auto


class ApplicationMode(Enum):
    FILTERS = auto()
    DRAWING = auto()
    MENU = auto()


class StateManager:
    """Single source of truth for the app's current operating mode.

    Modes are mutually exclusive. Toggling drawing or menu switches
    modes atomically so that render logic never processes two modes
    simultaneously on a single frame.
    """

    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        self.current_mode: ApplicationMode = ApplicationMode.FILTERS
        self.drawing_enabled: bool = False

    def is_mode(self, mode: ApplicationMode) -> bool:
        return self.current_mode == mode

    def set_mode(self, mode: ApplicationMode) -> None:
        self.current_mode = mode

    def toggle_menu(self) -> None:
        if self.is_mode(ApplicationMode.MENU):
            next_mode = (ApplicationMode.DRAWING if self.drawing_enabled
                         else ApplicationMode.FILTERS)
            self.set_mode(next_mode)
        else:
            self.set_mode(ApplicationMode.MENU)

    def update_drawing_status(self, drawing_enabled: bool) -> None:
        self.drawing_enabled = drawing_enabled
        if not self.is_mode(ApplicationMode.MENU):
            self.set_mode(ApplicationMode.DRAWING if drawing_enabled
                          else ApplicationMode.FILTERS)

    def get_current_mode_name(self) -> str:
        if self.is_mode(ApplicationMode.MENU):
            return "Menu"
        if self.is_mode(ApplicationMode.DRAWING):
            return "Drawing"
        return "Filters"