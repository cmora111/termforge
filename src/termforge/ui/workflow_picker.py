from tkinter import *
from tkinter import messagebox, simpledialog


class WorkflowPickerWindow:
    def __init__(self, app):
        self.app = app

        self.window = Toplevel(app.root)
        self.window.title("Choose Workflow")
        self.window.geometry("850x420")
        self.window.transient(app.root)

        outer = Frame(self.window, padx=8, pady=8)
        outer.pack(fill=BOTH, expand=True)

        Label(
            outer,
            text="Choose Workflow",
            bd=4,
            width=30,
            bg="lightgreen",
            fg="black",
            relief="raised",
        ).pack(pady=(0, 8))

        self.listbox = Listbox(outer, exportselection=False)
        self.listbox.pack(fill=BOTH, expand=True)

        buttons = Frame(outer)
        buttons.pack(fill=X, pady=(8, 0))

        Button(
            buttons,
            text="Open Editor",
            width=14,
            bg="darkgreen",
            fg="white",
            command=self.open_selected,
        ).pack(side=LEFT, padx=(0, 6))

        Button(
            buttons,
            text="New Workflow",
            width=14,
            bg="#2f5597",
            fg="white",
            command=self.create_new_workflow,
        ).pack(side=LEFT, padx=(0, 6))

        Button(
            buttons,
            text="Rename",
            width=14,
            bg="#7f6000",
            fg="white",
            command=self.rename_workflow,
        ).pack(side=LEFT, padx=(0, 6))

        Button(
            buttons,
            text="Delete",
            width=14,
            bg="red",
            fg="white",
            command=self.delete_workflow,
        ).pack(side=LEFT, padx=(0, 6))

        Button(
            buttons,
            text="Close",
            width=14,
            bg="red",
            fg="black",
            command=self.window.destroy,
        ).pack(side=RIGHT)

        self.refresh()
        self.listbox.bind("<Double-Button-1>", lambda _event: self.open_selected())

    def refresh(self):
        self.names = sorted(self.app.get_workflows().keys())

        self.listbox.delete(0, END)

        for name in self.names:
            self.listbox.insert(END, name)

    def open_selected(self):
        idxs = self.listbox.curselection()

        if not idxs:
            messagebox.showerror("Workflow Picker", "Select a workflow first.")
            return

        index = idxs[0]

        if index < 0 or index >= len(self.names):
            return

        name = self.names[index]

        self.window.destroy()
        self.app.open_workflow_editor(workflow_name=name)

    def create_new_workflow(self):
        name = simpledialog.askstring(
            "New Workflow",
            "Workflow name:",
            parent=self.window,
        )

        if not name:
            return

        name = name.strip()

        if not name:
            return

        workflows = getattr(self.app.cfg, "Workflows", {})

        if not isinstance(workflows, dict):
            workflows = {}
            setattr(self.app.cfg, "Workflows", workflows)

        if name in workflows:
            messagebox.showerror(
                "New Workflow",
                f"Workflow already exists:\n\n{name}",
            )
            return

        workflows[name] = []
        setattr(self.app.cfg, "Workflows", workflows)

        self.app.persist_full_config()
        self.app.set_status(f"Created workflow: {name}")

        self.refresh()

        self.window.destroy()
        self.app.open_workflow_editor(workflow_name=name)

    def selected_workflow_name(self):
        idxs = self.listbox.curselection()

        if not idxs:
            return None

        index = idxs[0]

        if index < 0 or index >= len(self.names):
            return None

        return self.names[index]

    def rename_workflow(self):
        old_name = self.selected_workflow_name()

        if not old_name:
            messagebox.showerror(
                "Rename Workflow",
                "Select a workflow first.",
            )
            return

        new_name = simpledialog.askstring(
            "Rename Workflow",
            "New workflow name:",
            initialvalue=old_name,
            parent=self.window,
        )

        if not new_name:
            return

        new_name = new_name.strip()

        if not new_name:
            return

        workflows = getattr(self.app.cfg, "Workflows", {})

        if new_name in workflows and new_name != old_name:
            messagebox.showerror(
                "Rename Workflow",
                f"Workflow already exists:\n\n{new_name}",
            )
            return

        workflows[new_name] = workflows.pop(old_name)

        self.app.persist_full_config()
        self.refresh()

    def delete_workflow(self):
        name = self.selected_workflow_name()

        if not name:
            messagebox.showerror(
                "Delete Workflow",
                "Select a workflow first.",
            )
            return

        if not messagebox.askokcancel(
            "Delete Workflow",
            f"Delete workflow?\n\n{name}",
        ):
            return

        workflows = getattr(self.app.cfg, "Workflows", {})

        if name in workflows:
            del workflows[name]

        self.app.persist_full_config()
        self.refresh()
