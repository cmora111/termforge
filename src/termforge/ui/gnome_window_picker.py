"""Read-only GNOME Wayland window picker."""

import pprint
from tkinter import (
    BOTH, END, LEFT, RIGHT,
    Button, Frame, Label, Listbox, Text, Toplevel,
    messagebox,
)

from ..gnome_window_discovery import list_windows


class GnomeWindowPickerWindow:
    def __init__(self, app):
        self.app = app

        self.window = Toplevel(app.root)
        self.window.title("GNOME Window Picker")
        self.window.geometry("980x520")
        self.window.transient(app.root)
        self.window.lift()
        self.window.focus_force()

        outer = Frame(self.window, padx=8, pady=8)
        outer.pack(fill=BOTH, expand=True)

        Label(
            outer,
            text="GNOME Window Discovery",
            bg="lightgreen",
            fg="black",
            relief="raised",
            width=34,
        ).pack(pady=(0, 8))

        actions = Frame(outer)
        actions.pack(fill="x", pady=(0, 8))

        Button(
            actions,
            text="Refresh",
            width=14,
            command=self.refresh,
        ).pack(side=LEFT)

        Button(
            actions,
            text="Use Selected Window",
            width=22,
            bg="darkgreen",
            fg="white",
            command=self.use_selected,
        ).pack(side=LEFT, padx=(6, 0))

        Button(
            actions,
            text="Close",
            width=14,
            bg="red",
            command=self.window.destroy,
        ).pack(side=RIGHT)

        self.listbox = Listbox(
            outer,
            width=140,
            height=18,
            exportselection=False,
        )
        self.listbox.pack(fill=BOTH, expand=True)

        self.info = Text(outer, wrap="word", height=8)
        self.info.pack(fill=BOTH, expand=True, pady=(8, 0))

        self.snapshot = []

        self.listbox.bind(
            "<<ListboxSelect>>",
            self.on_select,
        )

        self.refresh()
        self.window.after_idle(self.bring_to_front)

    def bring_to_front(self):
        if self.window.winfo_exists():
            self.window.lift()
            self.window.focus_force()

    def refresh(self):
        try:
            windows = list_windows()
        except Exception as exc:
            messagebox.showerror(
                "GNOME Window Discovery",
                str(exc),
                parent=self.window,
            )
            return

        self.snapshot = windows

        self.listbox.delete(0, END)
        self.info.delete("1.0", END)

        if not windows:
            self.info.insert(
                "1.0",
                "No GNOME windows were discovered.",
            )
            return

        for item in windows:
            focused = "*" if item.get("focus") else " "

            self.listbox.insert(
                END,
                f'{focused} '
                f'ID={item.get("id")} '
                f'PID={item.get("pid")} '
                f'CLASS={item.get("class")} '
                f'TITLE={item.get("title")}',
            )

    def on_select(self, _event=None):
        indices = self.listbox.curselection()

        if not indices:
            return

        index = indices[0]

        if index >= len(self.snapshot):
            return

        item = self.snapshot[index]

        self.info.delete("1.0", END)
        self.info.insert(
            "1.0",
            pprint.pformat(item, indent=4),
        )

    def use_selected(self):
        indices = self.listbox.curselection()

        if not indices:
            messagebox.showerror(
                "GNOME Window Picker",
                "Select a window first.",
                parent=self.window,
            )
            return

        index = indices[0]

        if index >= len(self.snapshot):
            return

        item = self.snapshot[index]

        window_id = item.get("id")

        if window_id is None:
            messagebox.showerror(
                "GNOME Window Picker",
                "Selected window has no ID.",
                parent=self.window,
            )
            return

        # GNOME graphical selection is separate from X11 and tmux targets.
        self.app.gnome_selected_window = dict(item)

        self.app.save_state()

        self.app.set_status(
            f"Selected GNOME window: {item.get('title', window_id)}"
        )

        self.window.destroy()
