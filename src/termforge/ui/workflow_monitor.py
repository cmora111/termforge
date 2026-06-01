import pprint
from tkinter import *
from tkinter import messagebox

class WorkflowLiveMonitorWindow:
    def __init__(self, app):
        self.app = app
        self.window = Toplevel(app.root)
        self.window.title("Workflow Live Monitor")
        self.window.geometry("980x620")
        self.window.transient(app.root)

        self.auto_refresh_enabled = True
        outer = Frame(self.window, padx=8, pady=8)
        outer.pack(fill=BOTH, expand=True)

        Label(
            outer,
            text="Workflow Live Monitor",
            bd=4,
            width=38,
            bg="lightgreen",
            fg="black",
            relief="raised",
        ).pack(pady=(0, 8))

        action_row = Frame(outer)
        action_row.pack(fill=X, pady=(0, 8))

        Button(
            action_row,
            text="Pause Auto",
            width=14,
            bg="#7f6000",
            fg="white",
            command=self.toggle_auto_refresh,
        ).pack(side=LEFT, padx=(0, 6))

        Button(
            action_row,
            text="Refresh",
            width=14,
            bg="navy",
            fg="white",
            command=self.refresh,
        ).pack(side=LEFT, padx=(0, 6))

        Button(
            action_row,
            text="Copy",
            width=14,
            bg="#2f5597",
            fg="white",
            command=self.copy_report,
        ).pack(side=LEFT, padx=(0, 6))

        Button(
            action_row,
            text="Close",
            width=14,
            bg="red",
            fg="black",
            command=self.window.destroy,
        ).pack(side=RIGHT)

        self.summary = Text(outer, wrap="word", height=7)
        self.summary.pack(fill=X, pady=(0, 8))

        self.listbox = Listbox(
            outer,
            width=130,
            height=18,
            exportselection=False,
        )
        self.listbox.pack(fill=BOTH, expand=True)

        self.details = Text(outer, wrap="word", height=10)
        self.details.pack(fill=BOTH, expand=True, pady=(8, 0))

        self.snapshot = []
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        self.refresh()
        self.auto_refresh()

    def get_state(self):
        return getattr(self.app, "current_workflow_state", None)

    def refresh(self):
        selected_index = None

        try:
            idxs = self.listbox.curselection()
            if idxs:
                selected_index = idxs[0]
        except Exception:
            pass

        state = self.get_state()

        self.summary.delete("1.0", END)
        self.listbox.delete(0, END)

        if not state:
            self.summary.insert("1.0", "No workflow is currently running.")
            self.snapshot = []
            self.details.delete("1.0", END)
            self.details.insert("1.0", "No workflow step selected.")
            return

        steps = state.get("steps", {})
        output_vars = state.get("output_vars", {})
        total = state.get("total", 0)
        output_vars = state.get("output_vars", {})

        success = sum(1 for s in steps.values() if s.get("status") == "success")
        failed = sum(1 for s in steps.values() if s.get("status") == "failed")
        skipped = sum(1 for s in steps.values() if s.get("status") == "skipped")
        running = sum(1 for s in steps.values() if s.get("status") == "running")

        self.summary.insert(
            "1.0",
            f"Workflow: {state.get('name')}\n"
            f"Mode: {state.get('mode')}\n"
            f"Status: {state.get('status')}\n"
            f"Started: {state.get('started_at')}\n"
            f"Finished: {state.get('finished_at') or '(running)'}\n"
            f"Progress: success={success}, failed={failed}, "
            f"skipped={skipped}, running={running}, total={total}\n\n"
            f"Workflow Output Variables:\n"
            f"{pprint.pformat(output_vars, indent=4)}"
        )

        self.snapshot = list(steps.values())

        for step in self.snapshot:
            self.listbox.insert(
                END,
                f"[{step.get('status', '')}] "
                f"{step.get('id', '')} "
                f"started={step.get('started_at', '')} "
                f"finished={step.get('finished_at', '')} "
                f"{step.get('message', '')}",
            )

        if not self.snapshot:
            self.details.delete("1.0", END)
            self.details.insert("1.0", "No workflow steps captured yet.")
            return

        if selected_index is None or selected_index >= len(self.snapshot):
            selected_index = 0

        self.listbox.selection_clear(0, END)
        self.listbox.selection_set(selected_index)
        self.listbox.activate(selected_index)

        self.show_step_details(selected_index)

    def toggle_auto_refresh(self):
        self.auto_refresh_enabled = not self.auto_refresh_enabled

    def show_step_details(self, index):
        if index < 0 or index >= len(self.snapshot):
            return

        step = self.snapshot[index]

        output = step.get("output", "")

        text = pprint.pformat(step, indent=4)
        text += f"\n\nDEBUG selected index: {index}"
        text += f"\nDEBUG output length: {len(output)}\n"

        if output:
            text += "\n===== CAPTURED OUTPUT =====\n"
            text += output

        self.details.delete("1.0", END)
        self.details.insert("1.0", text)


    def on_select(self, _event=None):
        idxs = self.listbox.curselection()
        if not idxs:
            return

        self.show_step_details(idxs[0])

    def copy_report(self):
        state = self.get_state() or {}

        self.window.clipboard_clear()
        self.window.clipboard_append(pprint.pformat(state, indent=4))
        self.window.update()

        messagebox.showinfo(
            "Workflow Live Monitor",
            "Workflow monitor report copied.",
        )

    def auto_refresh(self):
        try:
            if self.window.winfo_exists():
                if self.auto_refresh_enabled:
                    self.refresh()

                self.window.after(1000, self.auto_refresh)
        except Exception:
            pass

class WorkflowHistoryViewerWindow:
    def __init__(self, app):
        self.app = app

        self.window = Toplevel(app.root)
        self.window.title("Workflow History Viewer")
        self.window.geometry("1060x680")
        self.window.transient(app.root)

        outer = Frame(self.window, padx=8, pady=8)
        outer.pack(fill=BOTH, expand=True)

        Label(
            outer,
            text="Workflow History Viewer",
            bd=4,
            width=40,
            bg="lightgreen",
            fg="black",
            relief="raised",
        ).pack(pady=(0, 8))

        action_row = Frame(outer)
        action_row.pack(fill=X, pady=(0, 8))

        Button(
            action_row,
            text="Copy Selected",
            width=16,
            bg="#2f5597",
            fg="white",
            command=self.copy_selected,
        ).pack(side=LEFT, padx=(0, 6))

        Button(
            action_row,
            text="Clear History",
            width=16,
            bg="#7f6000",
            fg="white",
            command=self.clear_history,
        ).pack(side=LEFT, padx=(0, 6))

        Button(
            action_row,
            text="Close",
            width=14,
            bg="red",
            fg="black",
            command=self.window.destroy,
        ).pack(side=RIGHT)

        body = Frame(outer)
        body.pack(fill=BOTH, expand=True)

        left = Frame(body)
        left.pack(side=LEFT, fill=BOTH, expand=True)

        right = Frame(body)
        right.pack(side=RIGHT, fill=BOTH, expand=True, padx=(10, 0))

        self.listbox = Listbox(
            left,
            width=58,
            height=28,
            exportselection=False,
        )
        self.listbox.pack(side=LEFT, fill=BOTH, expand=True)

        scrollbar = Scrollbar(left, command=self.listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        self.details = Text(
            right,
            wrap="word",
            width=72,
            height=30,
        )
        self.details.pack(fill=BOTH, expand=True)

        self.snapshot = []
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        self.refresh()
        self.auto_refresh()

    def refresh(self):
        new_snapshot = list(getattr(self.app, "workflow_history", []))

        if new_snapshot == getattr(self, "snapshot", None):
            return

        self.snapshot = new_snapshot

        self.listbox.delete(0, END)
        self.details.delete("1.0", END)

        if not self.snapshot:
            self.details.insert(
                "1.0",
                "No workflow history yet.",
            )
            return

        for item in self.snapshot:
            steps = item.get("steps", {})
            success = sum(
                1 for step in steps.values()
                if step.get("status") == "success"
            )
            failed = sum(
                1 for step in steps.values()
                if step.get("status") == "failed"
            )
            skipped = sum(
                1 for step in steps.values()
                if step.get("status") == "skipped"
            )

            self.listbox.insert(
                END,
                f"{item.get('started_at', '')} "
                f"[{item.get('status', '')}] "
                f"{item.get('name', '')} "
                f"mode={item.get('mode', '')} "
                f"ok={success} fail={failed} skip={skipped}",
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

        if item is None:
            return

        self.details.delete("1.0", END)
        self.details.insert(
            "1.0",
            pprint.pformat(item, indent=4),
        )

    def copy_selected(self):
        item = self.selected_item()

        if item is None:
            messagebox.showerror(
                "Workflow History Viewer",
                "Select a workflow history entry first.",
            )
            return

        self.window.clipboard_clear()
        self.window.clipboard_append(
            pprint.pformat(item, indent=4),
        )
        self.window.update()

        messagebox.showinfo(
            "Workflow History Viewer",
            "Selected workflow history copied.",
        )

    def clear_history(self):
        if not messagebox.askokcancel(
            "Clear Workflow History",
            "Clear all workflow history entries?",
        ):
            return

        self.app.workflow_history = []
        self.refresh()

    def auto_refresh(self):
        try:
            if not self.window.winfo_exists():
                return

            current = self.listbox.curselection()

            self.refresh()

            if current:
                index = current[0]

                if 0 <= index < self.listbox.size():
                    self.listbox.selection_set(index)
                    self.listbox.activate(index)
                    self.on_select()

            self.window.after(2000, self.auto_refresh)

        except Exception:
            pass


