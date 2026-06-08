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
            def worker():
                started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                result = subprocess.run(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                finished_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                output = {
                    "backend": "subprocess",
                    "command": command,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode,
                    "started_at": started_at,
                    "finished_at": finished_at,
                }

                if hasattr(self.app, "record_backend_output"):
                    self.app.record_backend_output(output)

            threading.Thread(
                target=worker,
                daemon=True,
            ).start()

            self.app.set_status("Started subprocess command")

    def run_capture(self, command: str) -> dict:
        started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        result = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        finished_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        output = {
            "backend": "subprocess",
            "command": command,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "started_at": started_at,
            "finished_at": finished_at,
        }

        if hasattr(self.app, "record_backend_output"):
            self.app.record_backend_output(output)

        return output
