import pprint
import json
from datetime import datetime
from pathlib import Path
from tkinter import *
from tkinter import filedialog, messagebox

class WorkflowLiveMonitorWindow:
    def __init__(self, app):
        self.app = app

        self.window = Toplevel(app.root)
        self.window.title("Workflow Live Monitor")
        self.window.geometry("1200x720")
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

        paned = PanedWindow(
            outer,
            orient=HORIZONTAL,
            sashrelief=RAISED,
            sashwidth=6,
        )
        paned.pack(fill=BOTH, expand=True)

        left = Frame(paned)
        middle = Frame(paned)
        right = Frame(paned)

        paned.add(left, minsize=260)
        paned.add(middle, minsize=320)
        paned.add(right, minsize=520)

        Label(
            left,
            text="Steps",
            bg="#dddddd",
            relief="raised",
        ).pack(fill=X)

        list_frame = Frame(left)
        list_frame.pack(fill=BOTH, expand=True)

        list_frame.columnconfigure(0, weight=1)
        list_frame.columnconfigure(1, weight=0)
        list_frame.rowconfigure(0, weight=1)

        self.listbox = Listbox(
            list_frame,
            width=42,
            exportselection=False,
        )

        list_scroll = Scrollbar(
            list_frame,
            orient=VERTICAL,
            command=self.listbox.yview,
        )

        self.listbox.configure(yscrollcommand=list_scroll.set)

        self.listbox.grid(row=0, column=0, sticky="nsew")
        list_scroll.grid(row=0, column=1, sticky="ns")

        Label(
            middle,
            text="Summary",
            bg="#dddddd",
            relief="raised",
        ).pack(fill=X)

        summary_frame = Frame(middle)
        summary_frame.pack(fill=BOTH, expand=True)

        summary_frame.columnconfigure(0, weight=1)
        summary_frame.columnconfigure(1, weight=0)
        summary_frame.rowconfigure(0, weight=1)

        self.summary = Text(
            summary_frame,
            wrap="word",
        )

        summary_scroll = Scrollbar(
            summary_frame,
            orient=VERTICAL,
            command=self.summary.yview,
        )

        self.summary.configure(yscrollcommand=summary_scroll.set)

        self.summary.grid(row=0, column=0, sticky="nsew")
        summary_scroll.grid(row=0, column=1, sticky="ns")

        Label(
            right,
            text="Details",
            bg="#dddddd",
            relief="raised",
        ).pack(fill=X)

        details_frame = Frame(right)
        details_frame.pack(fill=BOTH, expand=True)

        details_frame.columnconfigure(0, weight=1)
        details_frame.columnconfigure(1, weight=0)
        details_frame.rowconfigure(0, weight=1)

        self.details = Text(
            details_frame,
            wrap="none",
        )

        details_scroll_y = Scrollbar(
            details_frame,
            orient=VERTICAL,
            command=self.details.yview,
        )

        self.details.configure(
            yscrollcommand=details_scroll_y.set,
        )

        self.details.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        details_scroll_y.grid(
            row=0,
            column=1,
            sticky="ns",
        )

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
            details_view = self.details.yview()
            self.details.delete("1.0", END)
            self.details.insert("1.0", "No workflow step selected.")
            self.details.yview_moveto(details_view[0])
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
            return

        selected = self.listbox.curselection()
        selected_index = selected[0] if selected else None

        # rebuild listbox here

        if selected_index is not None and selected_index < self.listbox.size():
            self.listbox.selection_set(selected_index)

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
        self.window.geometry("1250x720")
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

        Button(action_row, text="Refresh", width=14, bg="navy", fg="white", command=self.refresh).pack(side=LEFT, padx=(0, 6))
        Button(action_row, text="Copy Selected", width=16, bg="#2f5597", fg="white", command=self.copy_selected).pack(side=LEFT, padx=(0, 6))
        Button(action_row, text="Export Selected", width=16, bg="#5b4b8a", fg="white", command=self.export_selected,).pack(side=LEFT, padx=(0, 6))
        Button(action_row, text="Clear History", width=16, bg="#7f6000", fg="white", command=self.clear_history).pack(side=LEFT, padx=(0, 6))
        Button(action_row, text="Close", width=14, bg="red", fg="black", command=self.window.destroy).pack(side=RIGHT)

        paned = PanedWindow(
            outer,
            orient=HORIZONTAL,
            sashrelief=RAISED,
            sashwidth=6,
        )
        paned.pack(fill=BOTH, expand=True)

        left = Frame(paned)
        middle = Frame(paned)
        right = Frame(paned)

        paned.add(left, minsize=260)
        paned.add(middle, minsize=320)
        paned.add(right, minsize=520)

        Label(left, text="Runs", bg="#dddddd", relief="raised").pack(fill=X)
        run_frame = Frame(left)
        run_frame.pack(fill=BOTH, expand=True)

        self.listbox = Listbox(
            run_frame,
            width=42,
            exportselection=False,
        )
        self.listbox.pack(side=LEFT, fill=BOTH, expand=True)

        run_scroll = Scrollbar(run_frame, command=self.listbox.yview)
        run_scroll.pack(side=RIGHT, fill=Y)
        self.listbox.config(yscrollcommand=run_scroll.set)

        Label(middle, text="Steps", bg="#dddddd", relief="raised").pack(fill=X)
        step_frame = Frame(middle)
        step_frame.pack(fill=BOTH, expand=True)

        self.step_list = Listbox(
            step_frame,
            width=42,
            exportselection=False,
        )
        self.step_list.pack(side=LEFT, fill=BOTH, expand=True)

        step_scroll = Scrollbar(step_frame, command=self.step_list.yview)
        step_scroll.pack(side=RIGHT, fill=Y)
        self.step_list.config(yscrollcommand=step_scroll.set)

        Label(right, text="Details", bg="#dddddd", relief="raised").pack(fill=X)
        details_frame = Frame(right)
        details_frame.pack(fill=BOTH, expand=True)

        details_frame.columnconfigure(0, weight=1)
        details_frame.columnconfigure(1, weight=0)
        details_frame.rowconfigure(0, weight=1)

        self.details = Text(
            details_frame,
            wrap="none",
        )
        self.details.grid(row=0, column=0, sticky="nsew")

        details_scroll = Scrollbar(details_frame, orient=VERTICAL, command=self.details.yview)
        details_scroll.grid(row=0, column=1, sticky="ns")
        self.details.config(yscrollcommand=details_scroll.set)

        self.snapshot = []
        self.current_steps = []

        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        self.step_list.bind("<<ListboxSelect>>", self.on_step_select)

        self.refresh()

    def refresh(self):
        new_snapshot = list(getattr(self.app, "workflow_history", []))

        if new_snapshot == getattr(self, "snapshot", None):
            return

        self.snapshot = new_snapshot

        self.listbox.delete(0, END)
#        self.details.delete("1.0", END)

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

        self.step_list.delete(0, END)
        self.details.delete("1.0", END)
        self.current_steps = []

        if not item:
            return

        steps = item.get("steps", {})

        if isinstance(steps, dict):
            self.current_steps = list(steps.values())
        elif isinstance(steps, list):
            self.current_steps = steps

        for step in self.current_steps:
            self.step_list.insert(
                END,
                f"{step.get('status')} — {step.get('id')}"
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

    def export_selected(self):
        run = self.selected_item()

        if not run:
            messagebox.showerror(
                "Export Workflow Run",
                "Select a workflow run first.",
            )
            return

        workflow_name = str(run.get("name", "workflow")).strip() or "workflow"
        safe_name = "".join(
            ch if ch.isalnum() or ch in ("-", "_") else "_"
            for ch in workflow_name
        )

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        default_dir = Path.home() / "Documents" / "termforge-workflows"
        default_dir.mkdir(parents=True, exist_ok=True)

        target = filedialog.asksaveasfilename(
            title="Export Workflow Run",
            initialdir=str(default_dir),
            initialfile=f"{safe_name}-{timestamp}.json",
            defaultextension=".json",
            filetypes=[
                ("JSON files", "*.json"),
                ("All files", "*.*"),
            ],
        )

        if not target:
            return

        try:
            Path(target).write_text(
                json.dumps(run, indent=4, sort_keys=True),
                encoding="utf-8",
            )

            messagebox.showinfo(
                "Export Workflow Run",
                f"Workflow run exported:\n\n{target}",
            )

        except Exception as exc:
            self.app.show_traceback_window(
                "Export Workflow Run Failed",
                exc,
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

    def selected_step(self):
        idxs = self.step_list.curselection()
        if not idxs:
            return None

        index = idxs[0]

        if index < 0 or index >= len(self.current_steps):
            return None

        return self.current_steps[index]


    def on_step_select(self, _event=None):
        run = self.selected_item()
        step = self.selected_step()

        self.details.delete("1.0", END)

        if not run or not step:
            return

        step_id = step.get("id")
        outputs = run.get("outputs", [])

        matched = [
            item for item in outputs
            if item.get("step_id") == step_id
        ]

        lines = [
            f"Workflow: {run.get('name')}",
            f"Step: {step_id}",
            f"Status: {step.get('status')}",
            f"Message: {step.get('message')}",
            f"Started: {step.get('started_at')}",
            f"Finished: {step.get('finished_at')}",
            "",
            "=" * 80,
            "Latest Step Output",
            "=" * 80,
            step.get("output", ""),
            "",
            "=" * 80,
            "Output Events",
            "=" * 80,
        ]

        for item in matched:
            lines.extend(
                [
                    f"Time: {item.get('timestamp')}",
                    f"Status: {item.get('status')}",
                    f"Message: {item.get('message')}",
                    "",
                    item.get("output", ""),
                    "-" * 80,
                ]
            )

        self.details.insert("1.0", "\n".join(lines))
