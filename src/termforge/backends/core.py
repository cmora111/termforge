import os
import shlex
import shutil
import subprocess
import threading
from datetime import datetime


class BackendError(Exception):
    pass


class X11Backend:
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


class SubprocessBackend:
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

class TmuxBackend:
    name = "tmux"
    label = "tmux / Terminal Session"
    description = (
        "Sends commands to a tmux session/pane. "
        "Works on X11, Wayland, SSH, and headless systems. "
        "Best backend for terminal automation."
    )

    def __init__(self, app):
        self.app = app

    def is_available(self):
        return shutil.which("tmux") is not None

    def get_session(self):
        return str(getattr(self.app.cfg, "TmuxSession", "termforge") or "termforge")

    def get_pane(self):
        return str(getattr(self.app.cfg, "TmuxPane", "") or "")

    def get_mode(self):
        return str(getattr(self.app.cfg, "TmuxMode", "pane") or "pane").lower()

    def target(self):
        pane = self.get_pane().strip()
        return pane if pane else self.get_session()

    def ensure_session(self):
        if shutil.which("tmux") is None:
            raise BackendError("tmux is not installed. Install it with: sudo apt install tmux")

        session = self.get_session()

        result = subprocess.run(
            ["tmux", "has-session", "-t", session],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode != 0:
            subprocess.run(
                ["tmux", "new-session", "-d", "-s", session, "bash"],
                check=True,
            )

    def select_target(self):
        self.ensure_session()
        self.app.set_status(f"tmux target: {self.target()}")

    def attach_to_selected_window(self):
        self.ensure_session()

        window_id = self.app.get_selected_window_id()
        if not window_id:
            raise BackendError("No terminal window selected for tmux attach.")

        command = f"tmux attach -t {shlex.quote(self.get_session())}"

        self.app.send_to_selected_window(
            command,
            record_history=False,
        )

        self.app.set_status(
            f"Attached tmux session in selected window: {window_id}"
        )

    def send_text(self, text: str, record_history: bool = True):
        self.ensure_session()

        target = self.target()

        result = subprocess.run(
            ["tmux", "send-keys", "-l", "-t", target, text],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode != 0:
            raise BackendError(
                "tmux send-keys text failed:\n\n"
                f"target: {target}\n"
                f"command: {text}\n\n"
                f"stderr:\n{result.stderr}"
            )

        result = subprocess.run(
            ["tmux", "send-keys", "-t", target, "C-m"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode != 0:
            raise BackendError(
                "tmux send-keys Enter failed:\n\n"
                f"target: {target}\n"
                f"stderr:\n{result.stderr}"
            )

        self.app.set_status(f"Sent command to tmux pane: {target}")

        if record_history:
            self.app.add_history_entry("tmux", text, source="backend")

    def run_detached(self, command: str, record_history: bool = True):
        if self.get_mode() == "job":
            return self.run_job_window(command, record_history=record_history)

        return self.send_text(command, record_history=record_history)

    def run_job_window(self, command: str, record_history: bool = True):
        self.ensure_session()

        session = self.get_session()

        result = subprocess.run(
            [
                "tmux",
                "new-window",
                "-t",
                f"{session}:",
                "-n",
                "termforge-job",
                "bash",
                "-lc",
                f"{command}; echo; echo '[TermForge job complete]'; exec bash",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode != 0:
            raise BackendError(
                "tmux new-window failed:\n\n"
                f"stdout:\n{result.stdout}\n\n"
                f"stderr:\n{result.stderr}"
            )

        self.app.set_status(f"Started tmux job in session: {session}")

        if record_history:
            self.app.add_history_entry("tmux", command, source="backend")

    def capture_output(self, lines: int = 200):
        self.ensure_session()

        target = self.target()

        result = subprocess.run(
            [
                "tmux",
                "capture-pane",
                "-t",
                target,
                "-p",
                "-S",
                f"-{int(lines)}",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode != 0:
            raise BackendError(
                "tmux capture-pane failed:\n\n"
                f"{result.stderr}"
            )

        return result.stdout

    def list_targets(self):
        if shutil.which("tmux") is None:
            return []

        result = subprocess.run(
            [
                "tmux",
                "list-panes",
                "-a",
                "-F",
                "#{session_name}|#{window_index}|#{window_name}|#{pane_index}|#{pane_id}|#{pane_current_command}|#{pane_active}",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode != 0:
            return []

        targets = []

        for line in result.stdout.splitlines():
            parts = line.split("|")
            if len(parts) != 7:
                continue

            session, win_idx, win_name, pane_idx, pane_id, command, active = parts

            targets.append(
                {
                    "session": session,
                    "window_index": win_idx,
                    "window_name": win_name,
                    "pane_index": pane_idx,
                    "pane_id": pane_id,
                    "command": command,
                    "active": active == "1",
                    "target": f"{session}:{win_idx}.{pane_idx}",
                }
            )

        return targets
