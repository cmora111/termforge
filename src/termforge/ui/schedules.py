import pprint
from datetime import datetime
from tkinter import *
from tkinter import messagebox
from ..constants import PRIORITY_ORDER

class ScheduleManagerWindow:
    def __init__(self, app):
        self.app = app
        self.window = Toplevel(app.root)
        self.window.title("Schedule Manager")
        self.window.geometry("1120x760")
        self.window.transient(app.root)


        outer = Frame(self.window, padx=8, pady=8)
        outer.pack(fill=BOTH, expand=True)

        Label(
            outer,
            text="Schedule Manager",
            bd=4,
            width=32,
            bg="lightgreen",
            fg="black",
            relief="raised",
        ).pack(pady=(0, 8))

        action_row = Frame(outer)
        action_row.pack(fill=X, pady=(0, 8))

        Button(action_row, text="Save", width=14, bg="darkgreen", fg="white", command=self.save_schedule).pack(side=LEFT, padx=(0, 6))
        Button(action_row, text="New / Clear", width=14, bg="#555555", fg="white", command=self.clear_form).pack(side=LEFT, padx=(0, 6))
        Button(action_row, text="Delete", width=14, bg="#7f6000", fg="white", command=self.delete_schedule).pack(side=LEFT, padx=(0, 6))
        Button(action_row, text="Enable/Disable", width=16, bg="#2f5597", fg="white", command=self.toggle_enabled).pack(side=LEFT, padx=(0, 6))
        Button(action_row, text="Run Now", width=14, bg="#3d6d3d", fg="white", command=self.run_now).pack(side=LEFT, padx=(0, 6))
        Button(action_row, text="Close", width=14, bg="red", fg="black", command=self.window.destroy).pack(side=RIGHT)

        body = Frame(outer)
        body.pack(fill=BOTH, expand=True)

        left = Frame(body)
        left.pack(side=LEFT, fill=Y)

        right = Frame(body)
        right.pack(side=RIGHT, fill=BOTH, expand=True, padx=(10, 0))

        self.listbox = Listbox(left, width=58, height=28, exportselection=False,)
        self.listbox.pack(side=LEFT, fill=Y)

        scrollbar = Scrollbar(left, command=self.listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        form = Frame(right)
        form.pack(fill=X)

        self.name_var = StringVar()
        self.target_type_var = StringVar(value="command")
        self.category_var = StringVar()
        self.command_var = StringVar()
        self.workflow_var = StringVar()
        self.profile_var = StringVar()
        self.priority_var = StringVar(value="normal")

        self.backend_var = StringVar(value="")
        self.tmux_session_var = StringVar(value=str(getattr(self.app.cfg, "TmuxSession", "termforge")))
        self.tmux_pane_var = StringVar(value=str(getattr(self.app.cfg, "TmuxPane", "")))
        self.tmux_mode_var = StringVar(value=str(getattr(self.app.cfg, "TmuxMode", "pane")))

        self.type_var = StringVar(value="interval_minutes")
        self.time_var = StringVar()
        self.minutes_var = StringVar(value="1")
        self.enabled_var = IntVar(value=1)

        Label(form, text="Target Type:", width=16, anchor="w").grid(row=0, column=0, sticky="w", pady=3)
        self.target_type_menu = OptionMenu(form, self.target_type_var, "command", "workflow")
        self.target_type_menu.config(width=38)
        self.target_type_menu.grid(row=0, column=1, sticky="w", pady=3)

        Label(form, text="Name:", width=16, anchor="w").grid(row=1, column=0, sticky="w", pady=3)
        Entry(form, textvariable=self.name_var, width=42).grid(row=1, column=1, sticky="ew", pady=3)

        Label(form, text="Category:", width=16, anchor="w").grid(row=2, column=0, sticky="w", pady=3)
        self.category_menu = OptionMenu(form, self.category_var, "")
        self.category_menu.config(width=38)
        self.category_menu.grid(row=2, column=1, sticky="w", pady=3)

        Label(form, text="Command:", width=16, anchor="w").grid(row=3, column=0, sticky="w", pady=3)
        self.command_menu = OptionMenu(form, self.command_var, "")
        self.command_menu.config(width=38)
        self.command_menu.grid(row=3, column=1, sticky="w", pady=3)

        Label(form, text="Workflow:", width=16, anchor="w").grid(row=4, column=0, sticky="w", pady=3)
        self.workflow_menu = OptionMenu(form, self.workflow_var, "")
        self.workflow_menu.config(width=38)
        self.workflow_menu.grid(row=4, column=1, sticky="w", pady=3)

        Label(form, text="Profile:", width=16, anchor="w").grid(row=5, column=0, sticky="w", pady=3)
        self.profile_menu = OptionMenu(form, self.profile_var, "")
        self.profile_menu.config(width=38)
        self.profile_menu.grid(row=5, column=1, sticky="w", pady=3)

        Label(form, text="Priority:", width=16, anchor="w").grid(row=6, column=0, sticky="w", pady=3)
        self.priority_menu = OptionMenu(form, self.priority_var, "critical", "high", "normal", "low")
        self.priority_menu.config(width=38)
        self.priority_menu.grid(row=6, column=1, sticky="w", pady=3)

        Label(form, text="Backend:", width=16, anchor="w").grid(row=7, column=0, sticky="w", pady=3)
        self.backend_menu = OptionMenu(form, self.backend_var, "", "x11", "subprocess", "tmux")
        self.backend_menu.config(width=38)
        self.backend_menu.grid(row=7, column=1, sticky="w", pady=3)

        Label(form, text="Tmux Session:", width=16, anchor="w").grid(row=8, column=0, sticky="w", pady=3)
        Entry(form, textvariable=self.tmux_session_var, width=42).grid(row=8, column=1, sticky="ew", pady=3)

        Label(form, text="Tmux Pane:", width=16, anchor="w").grid(row=9, column=0, sticky="w", pady=3)
        Entry(form, textvariable=self.tmux_pane_var, width=42).grid(row=9, column=1, sticky="ew", pady=3)

        Label(form, text="Tmux Mode:", width=16, anchor="w").grid(row=10, column=0, sticky="w", pady=3)
        self.tmux_mode_menu = OptionMenu(form, self.tmux_mode_var, "pane", "job")
        self.tmux_mode_menu.config(width=38)
        self.tmux_mode_menu.grid(row=10, column=1, sticky="w", pady=3)

        Label(form, text="Type:", width=16, anchor="w").grid(row=11, column=0, sticky="w", pady=3)
        self.type_menu = OptionMenu(form, self.type_var, "startup", "daily", "interval_minutes")
        self.type_menu.config(width=38)
        self.type_menu.grid(row=11, column=1, sticky="w", pady=3)

        Label(form, text="Daily Time HH:MM:", width=16, anchor="w").grid(row=12, column=0, sticky="w", pady=3)
        Entry(form, textvariable=self.time_var, width=42).grid(row=12, column=1, sticky="ew", pady=3)

        Label(form, text="Interval Minutes:", width=16, anchor="w").grid(row=13, column=0, sticky="w", pady=3)
        Entry(form, textvariable=self.minutes_var, width=42).grid(row=13, column=1, sticky="ew", pady=3)

        Checkbutton(form, text="Enabled", variable=self.enabled_var).grid(row=14, column=1, sticky="w", pady=3)

        self.info = Text(right, wrap="word", height=10)
        self.info.pack(fill=BOTH, expand=True, pady=(12, 0))

        form.columnconfigure(1, weight=1)

        self.snapshot = []
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        self.category_var.trace_add("write", self.refresh_command_menu)

        self.refresh_workflow_menu()
        self.update_target_type_ui()
        self.refresh_category_menu()
        self.refresh_profile_menu()
        self.refresh()

    def update_target_type_ui(self, *_args):
        target_type = self.target_type_var.get().strip()

        if target_type == "workflow":
            try:
                self.category_menu.config(state="disabled")
                self.command_menu.config(state="disabled")
                self.profile_menu.config(state="disabled")
                self.workflow_menu.config(state="normal")
            except Exception:
                pass
        else:
            try:
                self.category_menu.config(state="normal")
                self.command_menu.config(state="normal")
                self.profile_menu.config(state="normal")
                self.workflow_menu.config(state="disabled")
            except Exception:
                pass

    def refresh_workflow_menu(self):
        workflows = self.app.get_workflows()
        names = [""] + sorted(workflows.keys())

        menu = self.workflow_menu["menu"]
        menu.delete(0, "end")

        for name in names:
            label = "(none)" if not name else name
            menu.add_command(
                label=label,
                command=lambda value=name: self.workflow_var.set(value),
            )

        if self.workflow_var.get() not in names:
            self.workflow_var.set("")

    def get_schedules(self):
        return self.app.get_schedules()

    def refresh_category_menu(self):
        categories = getattr(self.app.cfg, "Categories", {})
        names = sorted(categories.keys())

        menu = self.category_menu["menu"]
        menu.delete(0, "end")

        for name in names:
            menu.add_command(label=name, command=lambda value=name: self.category_var.set(value))

        if names and self.category_var.get() not in names:
            self.category_var.set(names[0])
        elif not names:
            self.category_var.set("")

        self.refresh_command_menu()

    def refresh_command_menu(self, *_args):
        categories = getattr(self.app.cfg, "Categories", {})
        category = self.category_var.get()
        commands = categories.get(category, {})
        names = sorted(commands.keys()) if isinstance(commands, dict) else []

        menu = self.command_menu["menu"]
        menu.delete(0, "end")

        for name in names:
            full_name = f"{category}/{name}"
            menu.add_command(
                label=full_name,
                command=lambda value=full_name: self.command_var.set(value),
            )

        full_names = [f"{category}/{name}" for name in names]

        if full_names and self.command_var.get() not in full_names:
            self.command_var.set(full_names[0])
        elif not full_names:
            self.command_var.set("")
        elif not names:
            self.command_var.set("")

    def refresh(self):
        self.listbox.delete(0, END)
        self.snapshot = []

        schedules = self.get_schedules()

        for index, schedule in enumerate(schedules):
            self.snapshot.append(
                {
                    "_schedule_index": index,
                    **schedule,
                }
            )

            enabled = "on" if schedule.get("enabled", True) else "off"
            name = schedule.get("name", f"Schedule {index + 1}")
            schedule_type = schedule.get("schedule_type", "")
            target_type = str(schedule.get("target_type", "command")).strip() or "command"

            target = (
                schedule.get("target")
                or schedule.get("command")
                or schedule.get("workflow")
                or ""
            )

            self.listbox.insert(
                END,
                f"[{enabled}] [{target_type}] {name} — {schedule_type} — {target}",
            )

            category = schedule.get("category", "")
            command = schedule.get("command", "")
            workflow = schedule.get("workflow", "")

            if target_type == "workflow":
                target_text = f"workflow/{workflow}"
            else:
                target_text = f"{category}/{command}"

            profile = schedule.get("profile", "")
            profile_text = f" profile:{profile}" if profile else ""

            priority = schedule.get("priority", "normal")

            backend = schedule.get("backend", "")
            backend_text = f" backend:{backend}" if backend else ""

            run_count = int(schedule.get("_run_count", 0) or 0)
            last_status = schedule.get("_last_status", "")
            last_run = schedule.get("_last_run", "")

            status_parts = []
            if last_status:
                status_parts.append(f"status:{last_status}")
            if last_run:
                status_parts.append(f"last:{last_run}")

            status_text = " ".join(status_parts) if status_parts else "never run"

            label = (
                f"[{enabled}] {name} — {schedule_type} — "
                f"{target_text}{profile_text}{backend_text} — "
                f"priority:{priority} — {status_text} — runs:{run_count}"
            )

        self.info.delete("1.0", END)
        self.info.insert(
            "1.0",
            f"Schedules: {len(self.snapshot)}\n\n"
            "Select a schedule to edit it.\n"
            "Backend blank means use global backend."
        )

    def on_select(self, _event=None):
        idxs = self.listbox.curselection()
        if not idxs:
            return

        index = idxs[0]
        if index < 0 or index >= len(self.snapshot):
            return

        schedule = self.snapshot[index]

        self.name_var.set(schedule.get("name", ""))

        self.category_var.set(schedule.get("category", ""))
        self.refresh_command_menu()

        self.command_var.set(schedule.get("command", ""))
        self.target_type_var.set(schedule.get("target_type", "command"))
        self.update_target_type_ui()
        self.profile_var.set(schedule.get("profile", ""))
        self.priority_var.set(schedule.get("priority", "normal"))
        self.type_var.set(schedule.get("type", "interval_minutes"))
        self.time_var.set(schedule.get("time", ""))
        self.minutes_var.set(str(schedule.get("minutes", "")))
        self.enabled_var.set(1 if schedule.get("enabled") else 0)

        self.info.delete("1.0", END)
        self.info.insert("1.0", pprint.pformat(schedule, indent=4))

    def clear_form(self):
        self.name_var.set("")
        self.type_var.set("interval_minutes")
        self.profile_var.set("")
        self.time_var.set("")
        self.minutes_var.set("1")
        self.enabled_var.set(1)
        self.refresh_category_menu()
        self.listbox.selection_clear(0, END)
        self.refresh_profile_menu()

    def build_schedule_from_form(self):
        name = self.name_var.get().strip()
        target_type = self.target_type_var.get().strip() or "command"
        command_value = self.command_var.get().strip()

        if "/" in command_value:
            category, command = command_value.split("/", 1)
        else:
            category = self.category_var.get().strip()
            command = command_value
        workflow = self.workflow_var.get().strip()
        profile = self.profile_var.get().strip()
        priority = self.priority_var.get().strip().lower() or "normal"
        if priority not in PRIORITY_ORDER:
            priority = "normal"
        schedule_type = self.type_var.get().strip()
        backend = self.backend_var.get().strip()
        tmux_session = self.tmux_session_var.get().strip()
        tmux_pane = self.tmux_pane_var.get().strip()
        tmux_mode = self.tmux_mode_var.get().strip() or "pane"

        if not name:
            raise ValueError("Schedule name is required.")
        if not category or not command:
            raise ValueError("Category and command are required.")
        if schedule_type not in ("startup", "daily", "interval_minutes"):
            raise ValueError("Schedule type must be startup, daily, or interval_minutes.")

        schedule = {
            "name": name,
            "target_type": target_type,
            "category": category,
            "command": command,
            "workflow": workflow,
            "profile": profile,
            "priority": priority,
            "type": schedule_type,
            "enabled": bool(self.enabled_var.get()),
            "backend": backend,
            "tmux_session": tmux_session,
            "tmux_pane": tmux_pane,
            "tmux_mode": tmux_mode,
        }

        if target_type == "workflow":
            if not workflow:
                raise ValueError("Workflow schedule requires a workflow.")
        else:
            if not category or not command:
                raise ValueError("Category and command are required.")

        if schedule_type == "daily":
            time_value = self.time_var.get().strip()
            if not re.match(r"^\d{2}:\d{2}$", time_value):
                raise ValueError("Daily time must be HH:MM.")
            schedule["time"] = time_value

        if schedule_type == "interval_minutes":
            try:
                minutes = int(self.minutes_var.get().strip())
            except Exception:
                raise ValueError("Interval minutes must be a number.")
            if minutes <= 0:
                raise ValueError("Interval minutes must be greater than zero.")
            schedule["minutes"] = minutes

        return schedule

    def refresh_profile_menu(self):
        profiles = self.app.get_window_profiles()
        names = [""] + sorted(profiles.keys())

        menu = self.profile_menu["menu"]
        menu.delete(0, "end")

        for name in names:
            label = "(none)" if not name else name
            menu.add_command(
                label=label,
                command=lambda value=name: self.profile_var.set(value),
            )

        if self.profile_var.get() not in names:
            self.profile_var.set("")

    def selected_schedule_index(self):
        idxs = self.listbox.curselection()

        if idxs:
            list_index = idxs[0]
        else:
            try:
                list_index = self.listbox.index(ACTIVE)
            except Exception:
                return None

        if list_index < 0 or list_index >= len(self.snapshot):
            return None

        item = self.snapshot[list_index]

        if isinstance(item, dict) and "_schedule_index" in item:
            return item["_schedule_index"]

        return list_index

    def save_schedule(self):
        try:
            schedule = self.build_schedule_from_form()
        except Exception as exc:
            self.app.show_traceback_window("Schedule Manager", str(exc))
            return

        schedules = self.get_schedules()
        index = self.selected_schedule_index()

        if index is None:
            schedules.append(schedule)
        else:
            schedules[index] = schedule

        self.app.persist_full_config()
        self.app.set_status(f"Saved schedule {schedule['name']}")
        self.refresh()

    def delete_schedule(self):
        index = self.selected_schedule_index()
        if index is None:
            messagebox.showerror("Schedule Manager", "Select a schedule first.")
            return

        schedules = self.get_schedules()
        schedule = schedules[index]

        if not messagebox.askokcancel("Delete Schedule", f"Delete schedule '{schedule.get('name')}'?"):
            return

        del schedules[index]
        self.app.persist_full_config()
        self.clear_form()
        self.refresh()

    def toggle_enabled(self):
        idxs = self.listbox.curselection()

        if not idxs:
            messagebox.showerror("Schedule Manager", "Select a schedule first.")
            return

        list_index = idxs[0]
        schedules = self.get_schedules()

        # Prefer snapshot mapping if available
        schedule_index = list_index

        if hasattr(self, "snapshot") and list_index < len(self.snapshot):
            item = self.snapshot[list_index]

            if isinstance(item, dict) and "_schedule_index" in item:
                schedule_index = item["_schedule_index"]

        if schedule_index < 0 or schedule_index >= len(schedules):
            messagebox.showerror(
                "Schedule Manager",
                f"Invalid schedule index.\n\n"
                f"List index: {list_index}\n"
                f"Schedule index: {schedule_index}\n"
                f"Schedules: {len(schedules)}\n"
                f"Snapshot: {len(getattr(self, 'snapshot', []))}",
            )
            return

        schedules[schedule_index]["enabled"] = not bool(
            schedules[schedule_index].get("enabled", True)
        )

        self.app.persist_full_config()
        self.refresh()

    def run_now(self):
        index = self.selected_schedule_index()
        if index is None:
            try:
                schedule = self.build_schedule_from_form()
            except Exception as exc:
                self.app.show_traceback_window("Schedule Manager", str(exc))
                return
        else:
            schedule = self.get_schedules()[index]

        self.run_schedule_target(schedule)

    def run_schedule_target(self, schedule):
        name = schedule.get("name", "")
        target_type = str(schedule.get("target_type", "command")).strip().lower()

        target = str(
            schedule.get("target")
            or schedule.get("command")
            or schedule.get("workflow")
            or ""
        ).strip()

        started = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            if target_type == "workflow":
                workflows = self.app.get_workflows()

                if target not in workflows:
                    raise ValueError(f"Unknown workflow: {target}")

                self.app.run_workflow(target)

            else:
                category = str(schedule.get("category", "")).strip()
                command_name = str(schedule.get("command", "")).strip()

                if target and "/" in target:
                    category, command_name = target.split("/", 1)

                if not category or not command_name:
                    raise ValueError("Command schedule requires category and command.")

                self.app.select_cmd(None, category, command_name)

            status = "success"
            error = ""

        except Exception as exc:
            status = "failed"
            error = str(exc)
            self.app.show_traceback_window("Run Schedule Failed", exc)

        history = getattr(self.app, "schedule_history", None)

        if not isinstance(history, list):
            history = []
            self.app.schedule_history = history

        history.insert(
            0,
            {
                "name": name,
                "status": status,
                "target_type": target_type,
                "target": target,
                "category": schedule.get("category", ""),
                "command": schedule.get("command", ""),
                "workflow": schedule.get("workflow", ""),
                "timestamp": started,
                "error": error,
            },
        )

        del history[100:]

        if hasattr(self.app, "persist_full_config"):
            self.app.persist_full_config()

class ScheduleHistoryWindow:
    def __init__(self, app):
        self.app = app
        self.window = Toplevel(app.root)
        self.window.title("Schedule History")
        self.window.geometry("980x560")
        self.window.transient(app.root)

        outer = Frame(self.window, padx=8, pady=8)
        outer.pack(fill=BOTH, expand=True)

        Label(
            outer,
            text="Schedule History",
            bd=4,
            width=32,
            bg="lightgreen",
            fg="black",
            relief="raised",
        ).pack(pady=(0, 8))

        action_row = Frame(outer)
        action_row.pack(fill=X, pady=(0, 8))

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
            text="Clear History",
            width=14,
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

        self.listbox = Listbox(left, width=70, height=24)
        self.listbox.pack(side=LEFT, fill=BOTH, expand=True)

        scrollbar = Scrollbar(left, command=self.listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        self.info = Text(right, wrap="word", width=44, height=24)
        self.info.pack(fill=BOTH, expand=True)

        self.snapshot = []
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        self.refresh()

    def get_history(self):
        return self.app.get_schedule_history()

    def refresh(self):
        self.snapshot = list(getattr(self.app, "schedule_history", []))

        self.listbox.delete(0, END)

        for item in self.snapshot:
            name = item.get("name", "")
            status = item.get("status", "")
            target = item.get("target", "")
            timestamp = item.get("timestamp", "")

            self.listbox.insert(
                END,
                f"[{status}] {timestamp} — {name} — {target}",
            )

        self.info.delete("1.0", END)
        self.info.insert(
            "1.0",
            f"Schedule history entries: {len(self.snapshot)}\n\n"
            "Select an entry to inspect it.",
        )

    def on_select(self, _event=None):
        idxs = self.listbox.curselection()
        if not idxs:
            return

        self.target_type_var.set(schedule.get("target_type", "command"))
        self.workflow_var.set(schedule.get("workflow", ""))
        self.backend_var.set(schedule.get("backend", ""))
        self.tmux_session_var.set(
            schedule.get("tmux_session", getattr(self.app.cfg, "TmuxSession", "termforge"))
        )
        self.tmux_pane_var.set(
            schedule.get("tmux_pane", getattr(self.app.cfg, "TmuxPane", ""))
        )
        self.tmux_mode_var.set(
            schedule.get("tmux_mode", getattr(self.app.cfg, "TmuxMode", "pane"))
        )

        index = idxs[0]
        if index < 0 or index >= len(self.snapshot):
            return

        entry = self.snapshot[index]

        self.info.delete("1.0", END)
        self.info.insert("1.0", pprint.pformat(entry, indent=4))

    def clear_history(self):
        if not messagebox.askokcancel(
            "Clear Schedule History",
            "Clear all schedule history entries?",
        ):
            return

        setattr(self.app.cfg, "ScheduleHistory", [])
        self.app.persist_full_config()
        self.refresh()


