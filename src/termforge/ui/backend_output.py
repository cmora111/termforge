import pprint
from tkinter import *
from tkinter import messagebox


class BackendOutputViewerWindow:
    def __init__(self, app):
        self.app = app

        self.window = Toplevel(app.root)
        self.window.title("Backend Output Viewer")
        self.window.geometry("1100x650")
        self.window.transient(app.root)

        outer = Frame(self.window, padx=8, pady=8)
        outer.pack(fill=BOTH, expand=True)

        action_row = Frame(outer)
        action_row.pack(fill=X, pady=(0, 8))

        Button(
            action_row,
            text="Refresh",
            bg="navy",
            fg="white",
            command=self.refresh,
        ).pack(side=LEFT, padx=(0, 6))

        Button(
            action_row,
            text="Copy Selected",
            bg="#5b4b8a",
            fg="white",
            command=self.copy_selected,
        ).pack(side=LEFT, padx=(0, 6))

        Button(
            action_row,
            text="Clear",
            bg="#7f6000",
            fg="white",
            command=self.clear_outputs,
        ).pack(side=LEFT, padx=(0, 6))

        Button(
            action_row,
            text="Close",
            bg="red",
            fg="white",
            command=self.window.destroy,
        ).pack(side=RIGHT)

        body = Frame(outer)
        body.pack(fill=BOTH, expand=True)

        left = Frame(body)
        left.pack(side=LEFT, fill=Y)

        right = Frame(body)
        right.pack(side=RIGHT, fill=BOTH, expand=True, padx=(10, 0))

        self.listbox = Listbox(left, width=48, height=28, exportselection=False)
        self.listbox.pack(side=LEFT, fill=Y)

        scroll = Scrollbar(left, command=self.listbox.yview)
        scroll.pack(side=RIGHT, fill=Y)
        self.listbox.config(yscrollcommand=scroll.set)

        self.output = Text(right, wrap="none")
        self.output.pack(fill=BOTH, expand=True)

        self.snapshot = []
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        self.refresh()

    def get_outputs(self):
        outputs = getattr(self.app, "backend_outputs", None)

        if not isinstance(outputs, list):
            outputs = []
            self.app.backend_outputs = outputs

        return outputs

    def refresh(self):
        self.snapshot = list(self.get_outputs())

        self.listbox.delete(0, END)

        for item in self.snapshot:
            backend = item.get("backend", "unknown")
            rc = item.get("returncode", "")
            finished = item.get("finished_at", "")
            command = item.get("command", "")

            self.listbox.insert(
                END,
                f"[{backend}] rc={rc} {finished} — {command[:60]}",
            )

        self.output.delete("1.0", END)
        self.output.insert(
            "1.0",
            f"Backend outputs: {len(self.snapshot)}\n\n"
            "Select an entry to view stdout/stderr.",
        )

    def selected_item(self):
        idxs = self.listbox.curselection()
        if not idxs:
            return None

        index = idxs[0]

        if index < 0 or index >= len(self.snapshot):
            return None

        return self.snapshot[index]

    def on_select(self, _event=None):
        item = self.selected_item()

        self.output.delete("1.0", END)

        if item is None:
            return

        text = [
            f"Backend: {item.get('backend')}",
            f"Command: {item.get('command')}",
            f"Return Code: {item.get('returncode')}",
            f"Started: {item.get('started_at')}",
            f"Finished: {item.get('finished_at')}",
            "",
            "=" * 80,
            "STDOUT",
            "=" * 80,
            item.get("stdout", ""),
            "",
            "=" * 80,
            "STDERR",
            "=" * 80,
            item.get("stderr", ""),
            "",
            "=" * 80,
            "RAW",
            "=" * 80,
            pprint.pformat(item, indent=4),
        ]

        self.output.insert("1.0", "\n".join(text))

    def copy_selected(self):
        text = self.output.get("1.0", END).strip()

        if not text:
            return

        self.window.clipboard_clear()
        self.window.clipboard_append(text)

        messagebox.showinfo(
            "Backend Output Viewer",
            "Output copied to clipboard.",
        )

    def clear_outputs(self):
        if not messagebox.askokcancel(
            "Clear Backend Outputs",
            "Clear all captured backend outputs?",
        ):
            return

        self.app.backend_outputs = []
        self.refresh()
