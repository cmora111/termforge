import shlex
import shutil
import subprocess
from .base import BackendBase, BackendError

class TmuxBackend(BackendBase):
    name = "tmux"
    label = "tmux / Terminal Session"
    description = (
        "Sends commands to a tmux session/pane. "
        "Works on X11, Wayland, SSH, and headless systems. "
        "Best backend for terminal automation."
    )

    def __init__(self, app):
        self.app = app

    def get_mode(self) -> str:
        return str(getattr(self.app.cfg, "TmuxMode", "pane") or "pane").lower()

    def is_available(self) -> bool:
        return shutil.which("tmux") is not None

    def get_session(self) -> str:
        return str(getattr(self.app.cfg, "TmuxSession", "termforge") or "termforge")

    def get_pane(self) -> str:
        return str(getattr(self.app.cfg, "TmuxPane", "") or "")

    def list_targets(self) -> list[dict]:
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

            target = f"{session}:{win_idx}.{pane_idx}"

            targets.append(
                {
                    "session": session,
                    "window_index": win_idx,
                    "window_name": win_name,
                    "pane_index": pane_idx,
                    "pane_id": pane_id,
                    "command": command,
                    "active": active == "1",
                    "target": target,
                }
            )

        return targets

    def target(self) -> str:
        pane = self.get_pane().strip()
        if pane:
            return pane
        return self.get_session()

    def ensure_session(self) -> None:
        if shutil.which("tmux") is None:
            raise TermForgeError(
                "tmux is not installed. Install it with:\n\n"
                "sudo apt install tmux"
            )

        session = self.get_session()

        result = subprocess.run(
            ["tmux", "has-session", "-t", session],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode != 0:
            subprocess.run(
                ["tmux", "new-session", "-d", "-s", session],
                check=True,
            )

    def attach_to_selected_window(self):
        self.ensure_session()

        window_id = self.app.get_selected_window_id()

        if not window_id:
            raise TermForgeError(
                "No terminal window selected for tmux attach."
            )

        command = f"tmux attach -t {shlex.quote(self.get_session())}"

        # Reuse TermForge's existing X11 send path.
        self.app.send_to_selected_window(
            command,
            record_history=False,
        )

        self.app.set_status(
            f"Attached tmux session in selected window: {window_id}"
        )

    def select_target(self):
        self.ensure_session()

        session = self.get_session()

        result = subprocess.run(
            [
                "tmux",
                "display-message",
                "-p",
                "-t",
                session,
                "#{session_name}:#{window_index}.#{pane_index}",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode != 0:
            raise TermForgeError(
                "Could not detect tmux target:\n\n"
                f"{result.stderr}"
            )

        target = result.stdout.strip()

        setattr(self.app.cfg, "TmuxPane", target)

        self.app.persist_full_config()

        self.app.set_status(
            f"Selected tmux target: {target}"
        )

    def send_text(self, text: str, record_history: bool = True):
        self.ensure_session()

        target = self.target()

        subprocess.run(
            ["tmux", "send-keys", "-t", target, text],
            check=True,
        )

        subprocess.run(
            ["tmux", "send-keys", "-t", target, "C-m"],
            check=True,
        )

        self.app.set_status(f"Sent command to tmux pane: {target}")

        if record_history:
            self.app.add_history_entry(
                "tmux",
                text,
                source="backend",
            )

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
            raise TermForgeError(
                "tmux new-window failed:\n\n"
                f"stdout:\n{result.stdout}\n\n"
                f"stderr:\n{result.stderr}"
            )

        self.app.set_status(f"Started tmux job in session: {session}")

        if record_history:
            self.app.add_history_entry(
                "tmux",
                command,
                source="backend",
            )

    def run_detached(self, command: str, record_history: bool = True):
        mode = self.get_mode()

        if mode == "job":
            return self.run_job_window(
                command,
                record_history=record_history,
            )

        return self.send_text(
            command,
            record_history=record_history,
        )

    def attach(self):
        self.ensure_session()

        session = self.get_session()

        terminal = getattr(self.app.cfg, "terminal", {}).get(
            "application",
            "gnome-terminal",
        )

        self.app.set_status(f"Attached tmux session: {session}")

    def get_mode(self) -> str:
        return str(getattr(self.app.cfg, "TmuxMode", "pane") or "pane").lower()

