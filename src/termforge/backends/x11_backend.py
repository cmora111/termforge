import shutil
from .base import BackendBase, BackendError


class X11Backend(BackendBase):
    name = "x11"
    label = "X11 / xdotool / libxdo"
    description = (
        "Uses the current X11 target-window behavior. "
        "Best for Ubuntu Xorg/X11 sessions."
    )

    def __init__(self, app):
        self.app = app

    def is_available(self):
        return shutil.which("xdotool") is not None

    def select_target(self):
        return self.app.select_target_window()

    def send_text(self, text: str, record_history: bool = True):
        return self.app.send_to_selected_window(
            text,
            record_history=record_history,
        )

    def run_detached(self, command: str, record_history: bool = True):
        return self.app.run_detached(
            command,
            record_history=record_history,
        )

