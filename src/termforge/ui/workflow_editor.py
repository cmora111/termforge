import json
import pprint
from tkinter import *
from tkinter import messagebox


class WorkflowEditorWindow:
    def __init__(self, app, workflow_name: str):
        self.app = app
        self.workflow_name = workflow_name
        self.steps = list(app.get_workflows().get(workflow_name, []))
        self.current_index = None

        self.window = Toplevel(app.root)
        self.window.title(f"Workflow Editor — {workflow_name}")
        self.window.geometry("1350x760")
        self.window.transient(app.root)

        outer = Frame(self.window, padx=8, pady=8)
        outer.pack(fill=BOTH, expand=True)

        Label(
            outer,
            text=f"Workflow Editor: {workflow_name}",
            bd=4,
            width=48,
            bg="lightgreen",
            fg="black",
            relief="raised",
        ).pack(pady=(0, 8))

        Label(
            outer,
            text=f"Editing workflow: {self.workflow_name}",
            anchor="w",
            bg="#eeeeee",
            relief="sunken",
        ).pack(fill=X, pady=(0, 8))

        action_row1 = Frame(outer)
        action_row1.pack(fill=X, pady=(0, 4))

        action_row2 = Frame(outer)
        action_row2.pack(fill=X, pady=(0, 8))

        Button(action_row1, text="Add Step", width=14, bg="darkgreen", fg="white", command=self.add_step).pack(side=LEFT, padx=(0, 6))
        Button(action_row1, text="Update Step", width=14, bg="#2f5597", fg="white", command=self.update_step).pack(side=LEFT, padx=(0, 6))
        Button(action_row1, text="Delete Step", width=14, bg="#7f6000", fg="white", command=self.delete_step).pack(side=LEFT, padx=(0, 6))
        Button(action_row1, text="Duplicate", width=12, bg="#3d6d3d", fg="white", command=self.duplicate_step).pack(side=LEFT, padx=(0, 6))
        Button(action_row1, text="Move Up", width=12, bg="#555555", fg="white", command=self.move_step_up).pack(side=LEFT, padx=(0, 6))
        Button(action_row1, text="Move Down", width=12, bg="#555555", fg="white", command=self.move_step_down).pack(side=LEFT, padx=(0, 6))

        Button(action_row2, text="Load Raw", width=12, bg="#555555", fg="white", command=self.load_raw_json).pack(side=LEFT, padx=(0, 6))
        Button(action_row2, text="Validate", width=12, bg="navy", fg="white", command=self.validate_workflow).pack(side=LEFT, padx=(0, 6))
        Button(action_row2, text="Apply Raw", width=12, bg="#7f6000", fg="white", command=self.apply_raw_json).pack(side=LEFT, padx=(0, 6))
        Button(action_row2, text="Run", width=12, bg="#3d6d3d", fg="white", command=self.run_workflow).pack(side=LEFT, padx=(0, 6))
        Button(action_row2, text="Save Workflow", width=16, bg="#5b4b8a", fg="white", command=self.save_workflow).pack(side=LEFT, padx=(0, 6))
        Button(action_row2, text="Close", width=14, bg="red", fg="black", command=self.window.destroy).pack(side=RIGHT)

        body = PanedWindow(outer, orient=HORIZONTAL, sashrelief=RAISED, sashwidth=6)
        body.pack(fill=BOTH, expand=True)

        left = Frame(body)
        middle = Frame(body)
        right = Frame(body)

        body.add(left, minsize=280)
        body.add(middle, minsize=420)
        body.add(right, minsize=420)

        Label(left, text=f"Steps — {len(self.steps)}", bg="#dddddd", relief="raised").pack(fill=X)

        list_frame = Frame(left)
        list_frame.pack(fill=BOTH, expand=True)

        self.listbox = Listbox(list_frame, width=38, exportselection=False)
        self.listbox.pack(side=LEFT, fill=BOTH, expand=True)

        scroll = Scrollbar(list_frame, command=self.listbox.yview)
        scroll.pack(side=RIGHT, fill=Y)
        self.listbox.config(yscrollcommand=scroll.set)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        self.id_var = StringVar()
        self.backend_var = StringVar(value="subprocess")
        self.command_type_var = StringVar(value="3")
        self.command_text_var = StringVar()
        self.depends_var = StringVar()
        self.run_if_var = StringVar(value="success")
        self.retry_count_var = StringVar(value="0")
        self.retry_delay_var = StringVar(value="0")
        self.capture_var = StringVar()

        props = LabelFrame(
            middle,
            text="Step Properties",
            padx=8,
            pady=8,
        )
        props.pack(fill=X)

        form = Frame(props)
        form.pack(fill=X)

        row = 0

        Label(form, text="ID:", width=18, anchor="w").grid(row=row, column=0, sticky="w", pady=3)
        Entry(form, textvariable=self.id_var, width=52).grid(row=row, column=1, sticky="ew", pady=3)
        row += 1

        Label(form, text="Backend:", width=18, anchor="w").grid(row=row, column=0, sticky="w", pady=3)
        OptionMenu(form, self.backend_var, "", "x11", "subprocess", "tmux").grid(row=row, column=1, sticky="ew", pady=3)
        row += 1

        Label(form, text="Command Type:", width=18, anchor="w").grid(row=row, column=0, sticky="w", pady=3)
        OptionMenu(form, self.command_type_var, "1", "2", "3").grid(row=row, column=1, sticky="ew", pady=3)
        row += 1

        Label(form, text="Command Text:", width=18, anchor="w").grid(row=row, column=0, sticky="w", pady=3)
        Entry(form, textvariable=self.command_text_var, width=52).grid(row=row, column=1, sticky="ew", pady=3)
        row += 1

        Label(form, text="Depends On:", width=18, anchor="w").grid(row=row, column=0, sticky="w", pady=3)
        Entry(form, textvariable=self.depends_var, width=52).grid(row=row, column=1, sticky="ew", pady=3)
        row += 1

        Label(form, text="Run If:", width=18, anchor="w").grid(row=row, column=0, sticky="w", pady=3)
        OptionMenu(form, self.run_if_var, "success", "failed", "always", "never").grid(row=row, column=1, sticky="ew", pady=3)
        row += 1

        Label(form, text="Retry Count:", width=18, anchor="w").grid(row=row, column=0, sticky="w", pady=3)
        Entry(form, textvariable=self.retry_count_var, width=52).grid(row=row, column=1, sticky="ew", pady=3)
        row += 1

        Label(form, text="Retry Delay:", width=18, anchor="w").grid(row=row, column=0, sticky="w", pady=3)
        Entry(form, textvariable=self.retry_delay_var, width=52).grid(row=row, column=1, sticky="ew", pady=3)
        row += 1

        Label(form, text="Capture Variable:", width=18, anchor="w").grid(row=row, column=0, sticky="w", pady=3)
        Entry(form, textvariable=self.capture_var, width=52).grid(row=row, column=1, sticky="ew", pady=3)

        form.columnconfigure(1, weight=1)

        Label(right, text="Raw Step Preview", bg="#dddddd", relief="raised").pack(fill=X)

        preview_frame = Frame(right)
        preview_frame.pack(fill=BOTH, expand=True)

        preview_scroll_y = Scrollbar(preview_frame)
        preview_scroll_y.pack(side=RIGHT, fill=Y)

        preview_scroll_x = Scrollbar(preview_frame, orient=HORIZONTAL)
        preview_scroll_x.pack(side=BOTTOM, fill=X)

        self.preview = Text(
            preview_frame,
            wrap="none",
            height=8,
            yscrollcommand=preview_scroll_y.set,
            xscrollcommand=preview_scroll_x.set,
        )
        self.preview.pack(side=LEFT, fill=BOTH, expand=True)

        preview_scroll_y.config(command=self.preview.yview)
        preview_scroll_x.config(command=self.preview.xview)

        Label(right, text="Raw Workflow JSON", bg="#dddddd", relief="raised").pack(fill=X, pady=(10, 0))

        raw_frame = Frame(right)
        raw_frame.pack(fill=BOTH, expand=True)

        raw_scroll_y = Scrollbar(raw_frame)
        raw_scroll_y.pack(side=RIGHT, fill=Y)

        raw_scroll_x = Scrollbar(raw_frame, orient=HORIZONTAL)
        raw_scroll_x.pack(side=BOTTOM, fill=X)

        self.raw_json = Text(
            raw_frame,
            wrap="none",
            height=12,
            yscrollcommand=raw_scroll_y.set,
            xscrollcommand=raw_scroll_x.set,
        )
        self.raw_json.pack(side=LEFT, fill=BOTH, expand=True)

        raw_scroll_y.config(command=self.raw_json.yview)
        raw_scroll_x.config(command=self.raw_json.xview)

        self.refresh()

    def refresh(self):
        self.listbox.delete(0, END)

        for index, step in enumerate(self.steps):
            step_id = step.get("id", f"step-{index + 1}") if isinstance(step, dict) else f"step-{index + 1}"
            run_if = step.get("run_if", "") if isinstance(step, dict) else ""
            backend = step.get("backend", "") if isinstance(step, dict) else ""
            self.listbox.insert(END, f"{index + 1}. {step_id} [{backend}] run_if={run_if}")

        self.refresh_preview()
        self.load_raw_json()

    def select_index(self, index):
        self.listbox.selection_clear(0, END)
        self.listbox.selection_set(index)
        self.listbox.activate(index)
        self.listbox.see(index)
        self.on_select()


    def move_step_up(self):
        index = self.selected_index()

        if index is None:
            messagebox.showerror("Workflow Editor", "Select a step first.")
            return

        if index <= 0:
            return

        self.steps[index - 1], self.steps[index] = self.steps[index], self.steps[index - 1]

        self.refresh()
        self.select_index(index - 1)

    def move_step_down(self):
        index = self.selected_index()

        if index is None:
            messagebox.showerror("Workflow Editor", "Select a step first.")
            return

        if index >= len(self.steps) - 1:
            return

        self.steps[index + 1], self.steps[index] = self.steps[index], self.steps[index + 1]

        self.refresh()
        self.select_index(index + 1)

    def duplicate_step(self):
        import copy

        index = self.selected_index()

        if index is None:
            messagebox.showerror("Workflow Editor", "Select a step first.")
            return

        step = copy.deepcopy(self.steps[index])

        if isinstance(step, dict):
            old_id = str(step.get("id", f"step-{index + 1}")).strip()
            new_id = f"{old_id}_copy"
            existing = {
                str(item.get("id", ""))
                for item in self.steps
                if isinstance(item, dict)
            }

            counter = 2
            while new_id in existing:
                new_id = f"{old_id}_copy_{counter}"
                counter += 1

            step["id"] = new_id

        self.steps.insert(index + 1, step)

        self.refresh()
        self.select_index(index + 1)

    def selected_index(self):
        idxs = self.listbox.curselection()
        if not idxs:
            return None

        index = idxs[0]
        if index < 0 or index >= len(self.steps):
            return None

        return index

    def on_select(self, _event=None):
        index = self.selected_index()
        if index is None:
            return

        self.current_index = index
        step = self.steps[index]

        if not isinstance(step, dict):
            return

        self.id_var.set(str(step.get("id", "")))
        self.backend_var.set(str(step.get("backend", "")))

        command = step.get("command", [3, ""])

        if isinstance(command, (list, tuple)) and len(command) >= 2:
            self.command_type_var.set(str(command[0]))
            self.command_text_var.set(str(command[1]))
        elif isinstance(command, str):
            self.command_type_var.set("2")
            self.command_text_var.set(command)
        else:
            self.command_type_var.set("3")
            self.command_text_var.set("")

        depends_on = step.get("depends_on", [])
        if isinstance(depends_on, str):
            depends_on = [depends_on]

        self.depends_var.set(", ".join(depends_on))
        self.run_if_var.set(str(step.get("run_if", "success")))
        self.retry_count_var.set(str(step.get("retry_count", 0)))
        self.retry_delay_var.set(str(step.get("retry_delay", 0)))
        self.capture_var.set(str(step.get("capture_variable", "")))

        self.refresh_preview()

    def build_step_from_form(self):
        step_id = self.id_var.get().strip()

        if not step_id:
            raise ValueError("Step ID is required.")

        command_type = int(self.command_type_var.get().strip() or "3")
        command_text = self.command_text_var.get().strip()

        step = {
            "id": step_id,
            "command": [command_type, command_text],
        }

        backend = self.backend_var.get().strip()
        if backend:
            step["backend"] = backend

        depends = [
            item.strip()
            for item in self.depends_var.get().split(",")
            if item.strip()
        ]
        if depends:
            step["depends_on"] = depends

        run_if = self.run_if_var.get().strip()
        if run_if:
            step["run_if"] = run_if

        retry_count = int(self.retry_count_var.get().strip() or 0)
        retry_delay = int(self.retry_delay_var.get().strip() or 0)

        if retry_count:
            step["retry_count"] = retry_count

        if retry_delay:
            step["retry_delay"] = retry_delay

        capture = self.capture_var.get().strip()
        if capture:
            step["capture_variable"] = capture

        return step

    def add_step(self):
        try:
            step = self.build_step_from_form()
        except Exception as exc:
            messagebox.showerror("Workflow Editor", str(exc))
            return

        self.steps.append(step)
        self.refresh()

    def update_step(self):
        index = self.selected_index()

        if index is None:
            messagebox.showerror("Workflow Editor", "Select a step first.")
            return

        try:
            step = self.build_step_from_form()
        except Exception as exc:
            messagebox.showerror("Workflow Editor", str(exc))
            return

        self.steps[index] = step
        self.refresh()
        self.listbox.selection_set(index)

    def delete_step(self):
        index = self.selected_index()

        if index is None:
            messagebox.showerror("Workflow Editor", "Select a step first.")
            return

        del self.steps[index]
        self.current_index = None
        self.clear_form()
        self.refresh()

    def clear_form(self):
        self.id_var.set("")
        self.backend_var.set("subprocess")
        self.command_type_var.set("3")
        self.command_text_var.set("")
        self.depends_var.set("")
        self.run_if_var.set("success")
        self.retry_count_var.set("0")
        self.retry_delay_var.set("0")
        self.capture_var.set("")

    def refresh_preview(self):
        try:
            step = self.build_step_from_form()
            text = pprint.pformat(step, indent=4)
        except Exception as exc:
            text = f"[preview unavailable]\n{exc}"

        self.preview.delete("1.0", END)
        self.preview.insert("1.0", text)

    def save_workflow(self):
        errors = self.app.validate_workflow(self.steps)

        if errors:
            if not messagebox.askokcancel(
                "Workflow Validation",
                "Workflow has problems:\n\n"
                + "\n".join(errors)
                + "\n\nSave anyway?",
            ):
                return

        workflows = self.app.get_workflows()
        workflows[self.workflow_name] = self.steps

        setattr(self.app.cfg, "Workflows", workflows)

        self.app.persist_full_config()
        self.app.set_status(f"Saved workflow: {self.workflow_name}")

        messagebox.showinfo(
            "Workflow Editor",
            f"Saved workflow: {self.workflow_name}",
        )

    def run_workflow(self):
        errors = self.app.validate_workflow(self.steps)

        if errors:
            if not messagebox.askokcancel(
                "Run Workflow",
                "Workflow has problems:\n\n"
                + "\n".join(errors)
                + "\n\nRun anyway?",
            ):
                return

        self.save_workflow()

        try:
            self.app.run_workflow(self.workflow_name, source="workflow_editor")
        except Exception as exc:
            self.app.show_traceback_window(
                f"Run Workflow Failed: {self.workflow_name}",
                exc,
            )

    def validate_workflow(self):
        errors = self.app.validate_workflow(self.steps)

        if not errors:
            messagebox.showinfo(
                "Workflow Validation",
                "Workflow is valid.",
            )
            return

        messagebox.showerror(
            "Workflow Validation",
            "Workflow has problems:\n\n" + "\n".join(errors),
        )

    def load_raw_json(self):
        self.raw_json.delete("1.0", END)
        self.raw_json.insert(
            "1.0",
            json.dumps(self.steps, indent=4),
        )

    def apply_raw_json(self):
        try:
            steps = json.loads(self.raw_json.get("1.0", END).strip())

            if not isinstance(steps, list):
                raise ValueError("Workflow JSON must be a list of steps.")

            self.steps = steps
            self.current_index = None
            self.clear_form()
            self.refresh()

            messagebox.showinfo("Workflow Editor", "Raw JSON applied.")

        except Exception as exc:
            messagebox.showerror("Workflow Editor", str(exc))
