import subprocess
import threading
from datetime import datetime

from .base import BackendBase, BackendError


class SubprocessBackend(BackendBase):
    name = "subprocess"
    label = "Subprocess / Direct Shell"
    description = (
        "Runs commands directly with subprocess. "
        "Works across X11, Wayland, GNOME Shell, SSH sessions, and headless use. "
        "Does not type into a selected terminal window."
    )

    def __init__(self, app):
        self.app = app

    def is_available(self):
        return True

    def select_target(self):
        self.app.set_status("Subprocess backend does not use target windows.")

    def send_text(self, text: str, record_history: bool = True):
        return self.run_detached(text, record_history=record_history)

    def run_detached(self, command: str, record_history: bool = True):
        proc = subprocess.Popen(
            command,
            shell=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

        threading.Thread(
            target=proc.wait,
            daemon=True,
        ).start()

        self.app.current_process = proc
        self.app.current_process_job = {
            "category": "",
            "command": command,
            "source": "subprocess",
            "pid": proc.pid,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        self.app.set_status(f"Started subprocess PID {proc.pid}")

        if record_history:
            self.app.add_history_entry(
                "subprocess",
                command,
                source="backend",
            )

