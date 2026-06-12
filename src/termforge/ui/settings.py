from tkinter import *


class SettingsWindow:
    def __init__(self, app):
        self.app = app

        self.window = Toplevel(app.root)
        self.window.title("TermForge Settings")
        self.window.geometry("560x420")
        self.window.transient(app.root)

        outer = Frame(self.window, padx=10, pady=10)
        outer.pack(fill=BOTH, expand=True)

        Label(
            outer,
            text="TermForge Settings",
            bd=4,
            width=32,
            bg="lightgreen",
            fg="black",
            relief="raised",
        ).pack(pady=(0, 10))

        form = Frame(outer)
        form.pack(fill=X)

        self.auto_backup_var = StringVar(
            value=str(getattr(app.cfg, "AutoBackupMinutes", 30))
        )
        self.max_backup_var = StringVar(
            value=str(getattr(app.cfg, "MaxBackupCount", 25))
        )
        self.backend_var = StringVar(
            value=str(getattr(app.cfg, "Backend", "x11"))
        )
        self.tmux_session_var = StringVar(
            value=str(getattr(app.cfg, "TmuxSession", "termforge"))
        )
        self.tmux_pane_var = StringVar(
            value=str(getattr(app.cfg, "TmuxPane", ""))
        )
        self.tmux_mode_var = StringVar(
            value=str(getattr(app.cfg, "TmuxMode", "pane"))
        )

        row = 0

        Label(form, text="Auto Backup Minutes:", width=22, anchor="w").grid(row=row, column=0, sticky="w", pady=4)
        Entry(form, textvariable=self.auto_backup_var, width=32).grid(row=row, column=1, sticky="ew", pady=4)
        row += 1

        Label(form, text="Max Backup Count:", width=22, anchor="w").grid(row=row, column=0, sticky="w", pady=4)
        Entry(form, textvariable=self.max_backup_var, width=32).grid(row=row, column=1, sticky="ew", pady=4)
        row += 1

        Label(form, text="Default Backend:", width=22, anchor="w").grid(row=row, column=0, sticky="w", pady=4)
        OptionMenu(form, self.backend_var, "x11", "subprocess", "tmux").grid(row=row, column=1, sticky="ew", pady=4)
        row += 1

        Label(form, text="Tmux Session:", width=22, anchor="w").grid(row=row, column=0, sticky="w", pady=4)
        Entry(form, textvariable=self.tmux_session_var, width=32).grid(row=row, column=1, sticky="ew", pady=4)
        row += 1

        Label(form, text="Tmux Pane:", width=22, anchor="w").grid(row=row, column=0, sticky="w", pady=4)
        Entry(form, textvariable=self.tmux_pane_var, width=32).grid(row=row, column=1, sticky="ew", pady=4)
        row += 1

        Label(form, text="Tmux Mode:", width=22, anchor="w").grid(row=row, column=0, sticky="w", pady=4)
        OptionMenu(form, self.tmux_mode_var, "pane", "job").grid(row=row, column=1, sticky="ew", pady=4)

        form.columnconfigure(1, weight=1)

        self.info = Text(outer, wrap="word", height=6)
        self.info.pack(fill=BOTH, expand=True, pady=(10, 8))
        self.info.insert(
            "1.0",
            "These settings are saved to your TermForge config.\n"
            "AutoBackupMinutes <= 0 disables automatic config backups.",
        )

        buttons = Frame(outer)
        buttons.pack(fill=X)

        Button(buttons, text="Save", width=14, bg="darkgreen", fg="white", command=self.save).pack(side=LEFT, padx=(0, 6))
        Button(buttons, text="Close", width=14, bg="red", fg="black", command=self.window.destroy).pack(side=RIGHT)

    def save(self):
        auto_backup = int(self.auto_backup_var.get().strip())
        max_backup = int(self.max_backup_var.get().strip())

        if max_backup < 1:
            max_backup = 1

        setattr(self.app.cfg, "AutoBackupMinutes", auto_backup)
        setattr(self.app.cfg, "MaxBackupCount", max_backup)
        setattr(self.app.cfg, "Backend", self.backend_var.get().strip() or "x11")
        setattr(self.app.cfg, "TmuxSession", self.tmux_session_var.get().strip() or "termforge")
        setattr(self.app.cfg, "TmuxPane", self.tmux_pane_var.get().strip())
        setattr(self.app.cfg, "TmuxMode", self.tmux_mode_var.get().strip() or "pane")

        self.app.persist_full_config()
        self.app.set_status("Settings saved.")

        self.info.delete("1.0", END)
        self.info.insert("1.0", "Settings saved.")
