"""Discover GNOME Shell windows through Window Calls Extended."""

import json
import subprocess


DBUS_DESTINATION = "org.gnome.Shell"
DBUS_PATH = "/org/gnome/Shell/Extensions/WindowsExt"
DBUS_METHOD = "org.gnome.Shell.Extensions.WindowsExt.List"


class GnomeWindowDiscoveryError(RuntimeError):
    pass


def list_windows() -> list[dict]:
    """Return GNOME windows as structured dictionaries."""

    result = subprocess.run(
        [
            "gdbus",
            "call",
            "--session",
            "--dest",
            DBUS_DESTINATION,
            "--object-path",
            DBUS_PATH,
            "--method",
            DBUS_METHOD,
        ],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    if result.returncode != 0:
        raise GnomeWindowDiscoveryError(
            result.stderr.strip() or "GNOME window discovery failed."
        )

    # gdbus prints a GVariant tuple containing a JSON string.
    # Parse the tuple without evaluating arbitrary Python expressions.
    import ast

    try:
        response = ast.literal_eval(result.stdout.strip())
        if not isinstance(response, tuple) or len(response) != 1:
            raise ValueError("Unexpected D-Bus response structure.")

        windows = json.loads(response[0])

        if not isinstance(windows, list):
            raise ValueError("Expected a list of windows.")

        if not all(isinstance(window, dict) for window in windows):
            raise ValueError("Window records must be dictionaries.")

        return windows

    except (ValueError, SyntaxError, TypeError) as exc:
        raise GnomeWindowDiscoveryError(
            f"Invalid GNOME window response: {exc}"
        ) from exc

def validate_window(saved_window: dict) -> dict | None:
    """Return a current matching window, or None if not uniquely found."""

    if not isinstance(saved_window, dict):
        return None

    window_id = saved_window.get("id")
    pid = saved_window.get("pid")
    window_class = saved_window.get("class")

    if window_id is None or pid is None or not window_class:
        return None

    matches = [
        window
        for window in list_windows()
        if str(window.get("id")) == str(window_id)
        and str(window.get("pid")) == str(pid)
        and window.get("class") == window_class
    ]

    return matches[0] if len(matches) == 1 else None
