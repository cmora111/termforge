import json
import pprint
from tkinter import *
from tkinter import messagebox, simpledialog
from .workflow_visualizer import WorkflowVisualizerWindow

class WorkflowManagerWindow:
    def __init__(self, app):
        self.app = app
        self.window = Toplevel(app.root)
        self.window.title("Workflow Manager")
        self.window.geometry("1040x680")
        self.window.transient(app.root)

        outer = Frame(self.window, padx=8, pady=8)
        outer.pack(fill=BOTH, expand=True)

        Label(
            outer,
            text="Workflow Manager",
            bd=4,
            width=36,
            bg="lightgreen",
            fg="black",
            relief="raised",
        ).pack(pady=(0, 8))

        action_outer = Frame(outer)
        action_outer.pack(fill=X, pady=(0, 8))

        action_row1 = Frame(action_outer)
        action_row1.pack(fill=X)

        Button(action_row1, text="Run Workflow", width=14, bg="#2f5597", fg="white", command=self.run_workflow).pack(side=LEFT, padx=(0, 6))
        Button(action_row1, text="Queue", width=14, bg="#2f5597", fg="white", command=self.queue_workflow,).pack(side=LEFT, padx=(0, 6))
        Button(action_row1, text="Run Parallel", width=14, bg="#3d6d3d", fg="white", command=self.run_parallel_workflow,).pack(side=LEFT, padx=(0, 6))
        Button(action_row1, text="Retry From Step", width=16, bg="#2f5597", fg="white", command=self.retry_from_step,).pack(side=LEFT, padx=(0, 6))
        Button(action_row1, text="Visualizer", width=14, bg="#555577", fg="white", command=self.visualize_workflow,).pack(side=LEFT, padx=(0,6))

        action_row2 = Frame(action_outer)
        action_row2.pack(fill=X, pady=(4, 0))

        Button(action_row2, text="Save", width=14, bg="darkgreen", fg="white", command=self.save_workflow).pack(side=LEFT, padx=(0, 6))
        Button(action_row2, text="Validate", width=14, bg="#555577", fg="white", command=self.validate_workflow).pack(side=LEFT, padx=(0, 6))
        Button(action_row2, text="Delete", width=14, bg="#7f6000", fg="white", command=self.delete_workflow).pack(side=LEFT, padx=(0, 6))
        Button(action_row2, text="Refresh", width=14, bg="navy", fg="white", command=self.refresh).pack(side=LEFT, padx=(0, 6))
        Button(action_row2, text="Close", width=14, bg="red", fg="black", command=self.window.destroy).pack(side=RIGHT)


        body = Frame(outer)
        body.pack(fill=BOTH, expand=True)

        left = Frame(body)
        left.pack(side=LEFT, fill=BOTH, expand=True)

        right = Frame(body)
        right.pack(side=RIGHT, fill=BOTH, expand=True, padx=(10, 0))

        self.listbox = Listbox(left, width=38, height=26, exportselection=False)
        self.listbox.pack(side=LEFT, fill=BOTH, expand=True)

        scrollbar = Scrollbar(left, command=self.listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        form = Frame(right)
        form.pack(fill=X)

        Label(form, text="Workflow Name:", width=16, anchor="w").grid(row=0, column=0, sticky="w", pady=3)
        self.name_var = StringVar()
        Entry(form, textvariable=self.name_var, width=52).grid(row=0, column=1, sticky="ew", pady=3)

        Label(form, text="Steps JSON:", width=16, anchor="nw").grid(row=1, column=0, sticky="nw", pady=3)
        self.steps_text = Text(form, height=20, width=76, wrap="none")
        self.steps_text.grid(row=1, column=1, sticky="nsew", pady=3)

        form.columnconfigure(1, weight=1)

        self.info = Text(right, wrap="word", height=10)
        self.info.pack(fill=BOTH, expand=True, pady=(10, 0))

        self.snapshot = []
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        self.refresh()

    def refresh(self):
        workflows = self.app.get_workflows()
        self.snapshot = []

        self.listbox.delete(0, END)

        for name in sorted(workflows.keys()):
            steps = workflows.get(name, [])
            count = len(steps) if isinstance(steps, list) else 0
            self.snapshot.append((name, steps))
            self.listbox.insert(END, f"{name} ({count} steps)")

        self.info.delete("1.0", END)
        self.info.insert(
            "1.0",
            "Workflow step example:\n\n"
            "[\n"
            "  {\n"
            '    \"id\": \"pwd\",\n'
            '    \"environment\": \"local-dev\",\n'
            '    \"profile\": \"server\",\n'
            '    \"command\": [2, \"cd ${repo} && pwd\"]\n'
            "  }\n"
            "]\n\n"
            "command can be [type, command, options] or \"Category/Command\"."
        )

    def on_select(self, _event=None):
        idxs = self.listbox.curselection()
        if not idxs:
            return

        name, steps = self.snapshot[idxs[0]]

        self.name_var.set(name)
        self.steps_text.delete("1.0", END)
        self.steps_text.insert(
            "1.0",
            json.dumps(steps, indent=4),
        )

        self.info.delete("1.0", END)
        self.info.insert("1.0", pprint.pformat(steps, indent=4))

    def parse_steps(self):
        raw = self.steps_text.get("1.0", END).strip()
        if not raw:
            return []

        data = json.loads(raw)

        if not isinstance(data, list):
            raise ValueError("Workflow JSON must be a list.")

        return data

    def retry_from_step(self):
        name = self.name_var.get().strip()

        if not name:
            messagebox.showerror(
                "Workflow Manager",
                "Select or enter a workflow name.",
            )
            return

        try:
            steps = self.parse_steps()
        except Exception as exc:
            self.app.show_traceback_window(
                "Retry Workflow Failed",
                exc,
            )
            return

        ids = [
            str(step.get("id", "")).strip()
            for step in steps
            if isinstance(step, dict) and str(step.get("id", "")).strip()
        ]

        if not ids:
            messagebox.showerror(
                "Workflow Manager",
                "Workflow has no step ids.",
            )
            return

        prompt = MultiFieldPrompt(
            self.window,
            "Retry Workflow From Step",
            ["step_id"],
            defaults={"step_id": ids[0]},
            heading="Enter step id to retry from",
        )

        values = prompt.show()
        if values is None:
            return

        step_id = values.get("step_id", "").strip()

        if step_id not in ids:
            messagebox.showerror(
                "Workflow Manager",
                "Unknown step id.\n\nAvailable:\n"
                + "\n".join(ids),
            )
            return

        try:
            self.app.run_workflow(
                name,
                source="workflow-retry",
                start_at=step_id,
            )
        except Exception as exc:
            self.app.show_traceback_window(
                "Retry Workflow Failed",
                exc,
            )

    def run_parallel_workflow(self):
        name = self.name_var.get().strip()

        if not name:
            messagebox.showerror(
                "Workflow Manager",
                "Select or enter a workflow name.",
            )
            return

        try:
            self.app.run_workflow_parallel(name)
        except Exception as exc:
            self.app.show_traceback_window(
                "Run Parallel Workflow Failed",
                exc,
            )

    def visualize_workflow(self):
        name = self.name_var.get().strip()

        if not name:
            messagebox.showerror(
                "Workflow Manager",
                "Select or enter a workflow name.",
            )
            return

        try:
            steps = self.parse_steps()
        except Exception as exc:
            self.app.show_traceback_window(
                "Workflow Visualizer Failed",
                exc,
            )
            return

        WorkflowVisualizerWindow(
            self.app,
            name,
            steps,
            steps_provider=self.parse_steps,
        )

    def queue_workflow(self):
        name = self.name_var.get().strip()

        if not name:
            messagebox.showerror(
                "Workflow Manager",
                "Select or enter a workflow name.",
            )
            return

        try:
            self.app.enqueue_workflow(
                name,
                source="workflow-manager",
                priority="normal",
            )
        except Exception as exc:
            self.app.show_traceback_window(
                "Queue Workflow Failed",
                exc,
            )
            return

        self.app.set_status(f"Queued workflow: {name}")

    def save_workflow(self):
        name = self.name_var.get().strip()

        if not name:
            messagebox.showerror("Workflow Manager", "Workflow name is required.")
            return

        try:
            steps = self.parse_steps()
            errors = self.app.validate_workflow(steps)
            if errors:
                messagebox.showerror(
                    "Workflow Validation",
                    "\n".join(errors),
                )
                return
            self.app.set_workflow(name, steps)

        except Exception as exc:
            self.app.show_traceback_window("Save Workflow Failed", exc)
            return

        self.app.set_status(f"Saved workflow: {name}")
        self.refresh()

    def run_workflow(self):
        name = self.name_var.get().strip()

        if not name:
            messagebox.showerror("Workflow Manager", "Select or enter a workflow name.")
            return

        try:
            self.app.run_workflow(name)
        except Exception as exc:
            self.app.show_traceback_window("Run Workflow Failed", exc)

    def validate_workflow(self):
        try:
            steps = self.parse_steps()
            errors = self.app.validate_workflow(steps)
        except Exception as exc:
            self.app.show_traceback_window("Workflow Validation Failed", exc)
            return

        if errors:
            messagebox.showerror("Workflow Validation", "\n".join(errors))
        else:
            messagebox.showinfo("Workflow Validation", "Workflow looks valid.")

    def delete_workflow(self):
        name = self.name_var.get().strip()

        if not name:
            messagebox.showerror("Workflow Manager", "Select or enter a workflow name.")
            return

        if not messagebox.askokcancel("Delete Workflow", f"Delete workflow '{name}'?"):
            return

        self.app.delete_workflow(name)
        self.name_var.set("")
        self.steps_text.delete("1.0", END)
        self.refresh()

