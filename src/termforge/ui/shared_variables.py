import pprint
from tkinter import *
from tkinter import messagebox

class SharedVariableManagerWindow:
    def __init__(self, app):
        self.app = app

        self.window = Toplevel(app.root)
        self.window.title("Shared Variable Manager")
        self.window.geometry("900x560")
        self.window.transient(app.root)

        outer = Frame(self.window, padx=8, pady=8)
        outer.pack(fill=BOTH, expand=True)

        Label(
            outer,
            text="Shared Variable Manager",
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
            text="Save",
            width=14,
            bg="darkgreen",
            fg="white",
            command=self.save_variable,
        ).pack(side=LEFT, padx=(0, 6))

        Button(
            action_row,
            text="Delete",
            width=14,
            bg="#7f6000",
            fg="white",
            command=self.delete_variable,
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
            width=38,
            height=24,
            exportselection=False,
        )
        self.listbox.pack(side=LEFT, fill=BOTH, expand=True)

        scrollbar = Scrollbar(left, command=self.listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        form = Frame(right)
        form.pack(fill=X)

        Label(form, text="Name:", width=12, anchor="w").grid(row=0, column=0, sticky="w", pady=3)
        self.name_var = StringVar()
        Entry(form, textvariable=self.name_var, width=48).grid(row=0, column=1, sticky="ew", pady=3)

        Label(form, text="Value:", width=12, anchor="nw").grid(row=1, column=0, sticky="nw", pady=3)
        self.value_text = Text(form, height=8, width=58, wrap="word")
        self.value_text.grid(row=1, column=1, sticky="nsew", pady=3)

        form.columnconfigure(1, weight=1)

        self.info = Text(right, wrap="word", height=12)
        self.info.pack(fill=BOTH, expand=True, pady=(10, 0))

        self.snapshot = []
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        self.refresh()

    def refresh(self):
        variables = self.app.get_shared_variables()

        self.snapshot = []
        self.listbox.delete(0, END)

        for name in sorted(variables.keys()):
            value = str(variables.get(name, ""))
            self.snapshot.append((name, value))
            self.listbox.insert(END, f"${{{name}}} = {value[:60]}")

        self.info.delete("1.0", END)
        self.info.insert(
            "1.0",
            "Shared variables are persistent and reusable in commands.\n\n"
            "Use syntax:\n"
            "  ${name}\n\n"
            "Example:\n"
            "  project_dir = /home/mora/termforge\n\n"
            "Command:\n"
            "  cd ${project_dir} && pwd\n"
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

        name, value = item

        self.name_var.set(name)
        self.value_text.delete("1.0", END)
        self.value_text.insert("1.0", value)

    def save_variable(self):
        name = self.name_var.get().strip()
        value = self.value_text.get("1.0", END).strip()

        if not name:
            messagebox.showerror(
                "Shared Variable Manager",
                "Variable name is required.",
            )
            return

        try:
            self.app.set_shared_variable(name, value)
        except Exception as exc:
            self.app.show_traceback_window(
                "Save Shared Variable Failed",
                exc,
            )
            return

        self.app.set_status(f"Saved shared variable: {name}")
        self.refresh()

    def delete_variable(self):
        item = self.selected_item()

        if item is None:
            messagebox.showerror(
                "Shared Variable Manager",
                "Select a variable first.",
            )
            return

        name, _value = item

        if not messagebox.askokcancel(
            "Delete Shared Variable",
            f"Delete shared variable '{name}'?",
        ):
            return

        self.app.delete_shared_variable(name)
        self.name_var.set("")
        self.value_text.delete("1.0", END)
        self.refresh()

