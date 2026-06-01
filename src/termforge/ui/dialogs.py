
class MultiFieldPrompt:
    def __init__(
        self,
        parent,
        title: str,
        fields: list[str],
        defaults: dict[str, str] | None = None,
        heading: str = "Enter values",
    ):
        self.parent = parent
        self.fields = fields
        self.defaults = defaults or {}
        self.result: dict[str, str] | None = None

        self.window = Toplevel(parent)
        self.window.title(title)
        self.window.transient(parent)
        self.window.grab_set()
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self.cancel)

        container = Frame(self.window, padx=10, pady=10)
        container.pack(fill=BOTH, expand=True)

        Label(
            container,
            text=heading,
            bd=2,
            relief="groove",
            width=30,
            bg="lightgreen",
            fg="black",
        ).pack(pady=(0, 10))

        self.entries: dict[str, Entry] = {}
        for field in fields:
            row = Frame(container)
            row.pack(fill=X, pady=3)
            Label(row, text=f"{field}:", width=12, anchor="w").pack(side=LEFT)
            entry = Entry(row, width=40)
            entry.pack(side=RIGHT, fill=X, expand=True)
            entry.insert(0, self.defaults.get(field, ""))
            self.entries[field] = entry

        buttons = Frame(container)
        buttons.pack(fill=X, pady=(12, 0))
        Button(buttons, text="OK", width=12, bg="darkgreen", fg="white", command=self.submit).pack(side=LEFT)
        Button(buttons, text="Cancel", width=12, bg="red", fg="black", command=self.cancel).pack(side=RIGHT)

        if fields:
            self.entries[fields[0]].focus_set()

        self.window.bind("<Return>", lambda _e: self.submit())
        self.window.bind("<Escape>", lambda _e: self.cancel())

    def submit(self):
        self.result = {name: entry.get() for name, entry in self.entries.items()}
        self.window.destroy()

    def cancel(self):
        self.result = None
        self.window.destroy()

    def show(self) -> dict[str, str] | None:
        self.parent.wait_window(self.window)
        return self.result

