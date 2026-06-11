from pathlib import Path
import pprint
import time
from tkinter import *
from tkinter import messagebox, ttk, filedialog, simpledialog
from ..constants import PLUGIN_DIR, PRIORITY_ORDER
from ..services.plugin_service import discover_plugins
from ..constants import PLUGIN_DIR

class PluginManagerWindow:
    def __init__(self, app):
        self.app = app
        self.window = Toplevel(app.root)
        self.window.title("Plugin Manager")
        self.window.geometry("920x540")
        self.window.transient(app.root)

        outer = Frame(self.window, padx=8, pady=8)
        outer.pack(fill=BOTH, expand=True)

        Label(
            outer,
            text="Plugin Manager",
            bd=4,
            width=34,
            bg="lightgreen",
            fg="black",
            relief="raised",
        ).pack(pady=(0, 8))

        body = Frame(outer)
        body.pack(fill=BOTH, expand=True)

        left = Frame(body)
        left.pack(side=LEFT, fill=Y)

        right = Frame(body)
        right.pack(side=RIGHT, fill=BOTH, expand=True, padx=(10, 0))

        self.listbox = Listbox(left, width=42, height=20)
        self.listbox.pack(side=LEFT, fill=Y)
        scrollbar = Scrollbar(left, command=self.listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        self.info = Text(right, wrap="word", height=20, width=70)
        self.info.pack(fill=BOTH, expand=True)

        button_row = Frame(outer)
        button_row.pack(fill=X, pady=(10, 0))

        Button(button_row, text="Run", width=14, bg="darkgreen", fg="white", command=self.run_selected).pack(side=LEFT, padx=(0, 6))
        Button(button_row, text="Enable", width=14, bg="#2f5597", fg="white", command=self.enable_selected).pack(side=LEFT, padx=(0, 6))
        Button(button_row, text="Disable", width=14, bg="#7f6000", fg="white", command=self.disable_selected).pack(side=LEFT, padx=(0, 6))
        Button(button_row, text="Reload", width=14, bg="navy", fg="white", command=self.reload_plugins).pack(side=LEFT, padx=(0, 6))
        Button(button_row, text="Open Folder", width=14, bg="#444444", fg="white", command=self.app.open_plugin_folder).pack(side=LEFT, padx=(0, 6))
        Button(button_row, text="Close", width=14, bg="red", fg="black", command=self.window.destroy).pack(side=RIGHT)

        self.snapshot = []
        self.listbox.bind("<<ListboxSelect>>", self.show_info)
        self.refresh()

    def collect_snapshot(self):
        rows = []
        disabled = set(self.app.get_disabled_plugins())
        discovered = sorted({p.stem for p in PLUGIN_DIR.glob("*.py")})
        for name in discovered:
            if name in disabled:
                rows.append({
                    "status": "disabled",
                    "name": name,
                    "display_name": name,
                    "version": "-",
                    "description": "Disabled by user.",
                    "error": "",
                })
                continue
            if name in self.app.plugins:
                plugin = self.app.plugins[name]
                meta = getattr(plugin, "__termforge_metadata__", {})
                rows.append({
                    "status": "loaded",
                    "name": name,
                    "display_name": meta.get("display_name", name),
                    "version": meta.get("plugin_version", "unknown"),
                    "description": meta.get("description", "(no description)"),
                    "error": "",
                })
            else:
                rows.append({
                    "status": "error",
                    "name": name,
                    "display_name": name,
                    "version": "-",
                    "description": "",
                    "error": self.app.plugin_errors.get(name, "Unknown plugin load error."),
                })
        return rows

    def refresh(self):
        self.app.load_plugins(force=False)
        self.snapshot = self.collect_snapshot()
        self.listbox.delete(0, END)
        for item in self.snapshot:
            prefix = {"loaded": "[OK]", "disabled": "[OFF]", "error": "[ERR]"}.get(item["status"], "[?]")
            self.listbox.insert(END, f"{prefix} {item['display_name']} ({item['name']})")
        self.info.delete("1.0", END)
        self.info.insert("1.0", "Select a plugin to inspect.\n")

    def current_item(self):
        idxs = self.listbox.curselection()
        if not idxs:
            return None
        return self.snapshot[idxs[0]]

    def show_info(self, _event=None):
        item = self.current_item()
        if not item:
            return
        lines = [
            f"Name: {item['display_name']}",
            f"Internal name: {item['name']}",
            f"Status: {item['status']}",
            f"Version: {item['version']}",
            "",
        ]
        if item["description"]:
            lines.extend(["Description:", item["description"], ""])
        if item["error"]:
            lines.extend(["Error:", item["error"], ""])
        self.info.delete("1.0", END)
        self.info.insert("1.0", "\n".join(lines))

    def run_selected(self):
        item = self.selected_item()

        if not item:
            messagebox.showerror(
                "Plugin Manager",
                "Select a plugin first.",
            )
            return

        name = item

        try:
            self.app.run_plugin(name)
        except Exception as exc:
            self.app.show_traceback_window(
                "Run Plugin Failed",
                exc,
            )

    def disable_selected(self):
        item = self.current_item()
        if not item:
            return
        self.app.disable_plugin(item["name"])
        self.app.set_status(f"Disabled plugin: {item['name']}")
        self.refresh()

    def enable_selected(self):
        item = self.current_item()
        if not item:
            return
        self.app.enable_plugin(item["name"])
        self.app.set_status(f"Enabled plugin: {item['name']}")
        self.refresh()

    def reload_plugins(self):
        self.app.load_plugins(force=True)
        self.app.set_status("Plugins reloaded.")
        self.refresh()

class TagManagerWindow:
    def __init__(self, app):
        self.app = app
        self.window = Toplevel(app.root)
        self.window.title("Tag Manager")
        self.window.geometry("980x560")
        self.window.transient(app.root)

        outer = Frame(self.window, padx=8, pady=8)
        outer.pack(fill=BOTH, expand=True)

        Label(
            outer,
            text="Tag Manager",
            bd=4,
            width=32,
            bg="lightgreen",
            fg="black",
            relief="raised",
        ).pack(pady=(0, 8))

        action_row = Frame(outer)
        action_row.pack(fill=X, pady=(0, 8))

        Button(action_row, text="Save Tags", width=14, bg="darkgreen", fg="white", command=self.save_tags).pack(side=LEFT, padx=(0, 6))
        Button(action_row, text="Clear Tags", width=14, bg="#7f6000", fg="white", command=self.clear_tags).pack(side=LEFT, padx=(0, 6))
        Button(action_row, text="Refresh", width=14, bg="navy", fg="white", command=self.refresh).pack(side=LEFT, padx=(0, 6))
        Button(action_row, text="Close", width=14, bg="red", fg="black", command=self.window.destroy).pack(side=RIGHT)

        search_row = Frame(outer)
        search_row.pack(fill=X, pady=(0, 8))

        Label(search_row, text="Filter:", width=10, anchor="w").pack(side=LEFT)
        self.filter_var = StringVar()
        Entry(search_row, textvariable=self.filter_var, width=40).pack(side=LEFT, fill=X, expand=True)

        body = Frame(outer)
        body.pack(fill=BOTH, expand=True)

        left = Frame(body)
        left.pack(side=LEFT, fill=BOTH, expand=True)

        right = Frame(body)
        right.pack(side=RIGHT, fill=BOTH, expand=True, padx=(10, 0))

        self.listbox = Listbox(left, width=52, height=24)
        self.listbox.pack(side=LEFT, fill=BOTH, expand=True)

        scrollbar = Scrollbar(left, command=self.listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        Label(right, text="Tags comma/space separated:", anchor="w").pack(fill=X)

        self.tags_text = Text(right, wrap="word", height=5)
        self.tags_text.pack(fill=X, pady=(4, 8))

        self.info = Text(right, wrap="word", height=18)
        self.info.pack(fill=BOTH, expand=True)

        self.snapshot = []

        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        self.filter_var.trace_add("write", lambda *_args: self.refresh())

        self.refresh()

    def collect_commands(self):
        rows = []
        categories = getattr(self.app.cfg, "Categories", {})

        for category in sorted(categories.keys()):
            commands = categories.get(category, {})
            if not isinstance(commands, dict):
                continue

            for name in sorted(commands.keys()):
                tags = self.app.get_command_tags(category, name)
                rows.append({
                    "category": category,
                    "name": name,
                    "tags": tags,
                    "key": self.app.command_key(category, name),
                })

        return rows

    def refresh(self):
        self.snapshot = []
        self.listbox.delete(0, END)

        tags = getattr(self.app.cfg, "CommandTags", {})

        if not isinstance(tags, dict):
            tags = {}
            setattr(self.app.cfg, "CommandTags", tags)

        for tag in sorted(tags.keys()):
            commands = tags.get(tag, [])

            if not isinstance(commands, list):
                commands = []

            self.snapshot.append((tag, commands))

            self.listbox.insert(
                END,
                f"{tag} ({len(commands)} command{'s' if len(commands) != 1 else ''})",
            )

        self.info.delete("1.0", END)
        self.info.insert(
            "1.0",
            f"Tags: {len(self.snapshot)}\n\n"
            "Select a tag to inspect assigned commands.",
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
        idxs = self.listbox.curselection()
        if not idxs:
            return

        index = idxs[0]

        if index < 0 or index >= len(self.snapshot):
            return

        tag, commands = self.snapshot[index]

        self.info.delete("1.0", END)

        lines = [
            f"Tag: {tag}",
            f"Commands: {len(commands)}",
            "",
        ]

        for command in commands:
            lines.append(f"  - {command}")

        self.info.insert("1.0", "\n".join(lines))

    def save_tags(self):
        item = self.selected_item()
        if not item:
            messagebox.showerror("Tag Manager", "Select a command first.")
            return

        tag_text = self.tags_text.get("1.0", END).strip()

        self.app.set_command_tags(
            item["category"],
            item["name"],
            tag_text,
        )

        self.app.set_status(f'Updated tags for {item["category"]}/{item["name"]}')
        self.refresh()

    def clear_tags(self):
        item = self.selected_item()
        if not item:
            messagebox.showerror("Tag Manager", "Select a command first.")
            return

        if not messagebox.askokcancel(
            "Clear Tags",
            f'Clear tags for {item["category"]}/{item["name"]}?',
        ):
            return

        self.app.set_command_tags(item["category"], item["name"], "")
        self.app.set_status(f'Cleared tags for {item["category"]}/{item["name"]}')
        self.refresh()

class ExecutionQueueWindow:
    def __init__(self, app):
        self.app = app
        self.window = Toplevel(app.root)
        self.window.title("Execution Queue")
        self.window.geometry("980x840")
        self.window.transient(app.root)
        self._selection_lock_until = 0
        self.app.poll_current_process()

        PRIORITY_ORDER = {
            "critical": 0,
            "high": 1,
            "normal": 2,
            "low": 3,
        }

        outer = Frame(self.window, padx=8, pady=8)
        outer.pack(fill=BOTH, expand=True)

        Label(
            outer,
            text="Execution Queue",
            bd=4,
            width=32,
            bg="lightgreen",
            fg="black",
            relief="raised",
        ).pack(pady=(0, 8))

        toolbar_top = Frame(outer)
        toolbar_top.pack(fill=X, pady=(0, 4))

        toolbar_middle = Frame(outer)
        toolbar_middle.pack(fill=X, pady=(0, 4))

        toolbar_bottom = Frame(outer)
        toolbar_bottom.pack(fill=X, pady=(0, 8))

        # Row 1: basic control
        Button(toolbar_top, text="Refresh", width=14, bg="navy", fg="white", command=self.refresh).pack(side=LEFT, padx=(0, 6))
        Button(toolbar_top, text="Pause Queue", width=14, bg="#7f6000", fg="white", command=self.pause_queue).pack(side=LEFT, padx=(0, 6))
        Button(toolbar_top, text="Resume Queue", width=14, bg="darkgreen", fg="white", command=self.resume_queue).pack(side=LEFT, padx=(0, 6))
        Button(toolbar_top, text="Run Next", width=14, bg="#2f5597", fg="white", command=self.run_next).pack(side=LEFT, padx=(0, 6))
        Button(toolbar_top, text="Run Selected Next", width=18, bg="#2f5597", fg="white", command=self.run_selected_next).pack(side=LEFT, padx=(0, 6))
        Button(toolbar_top, text="Close", width=14, bg="red", fg="black", command=self.window.destroy).pack(side=RIGHT)

        # Row 2: pending job control
        Button(toolbar_middle, text="Cancel Pending", width=16, bg="#7f6000", fg="white", command=self.cancel_pending).pack(side=LEFT, padx=(0, 6))
        Button(toolbar_middle, text="Move Up", width=14, bg="#444488", fg="white", command=self.move_pending_up).pack(side=LEFT, padx=(0, 6))
        Button(toolbar_middle, text="Move Down", width=14, bg="#444488", fg="white", command=self.move_pending_down).pack(side=LEFT, padx=(0, 6))
        Button(toolbar_middle, text="Clear Completed", width=16, bg="#555555", fg="white", command=self.clear_completed).pack(side=LEFT, padx=(0, 6))
        Button(toolbar_middle, text="Clear Queue", width=14, bg="#7f0000", fg="white", command=self.clear_queue).pack(side=LEFT, padx=(0, 6))

        # Row 3: history/process control
        Label(
            toolbar_bottom,
            text="Priority:",
            width=8,
            anchor="w",
        ).pack(side=LEFT, padx=(0, 4))

        self.priority_var = StringVar(value="normal")

        self.priority_combo = ttk.Combobox(
            toolbar_bottom,
            textvariable=self.priority_var,
            values=[
                "critical",
                "high",
                "normal",
                "low",
            ],
            width=12,
            state="readonly",
        )

        self.priority_combo.pack(side=LEFT, padx=(0, 6))

        Button(
            toolbar_bottom,
            text="Apply Priority",
            width=16,
            bg="#2f5597",
            fg="white",
            command=self.apply_selected_priority,
        ).pack(side=LEFT, padx=(0, 12))

        Button(toolbar_bottom, text="Retry Failed", width=14, bg="#2f5597", fg="white", command=self.retry_failed_job).pack(side=LEFT, padx=(0, 6))
        Button(toolbar_bottom, text="Terminate Running", width=18, bg="#7f6000", fg="white", command=self.terminate_running).pack(side=LEFT, padx=(0, 6))
        Button(toolbar_bottom, text="Kill Running", width=14, bg="#7f0000", fg="white", command=self.kill_running).pack(side=LEFT, padx=(0, 6))
        Button(toolbar_bottom, text="Export History", width=16, bg="#2f5597", fg="white", command=self.export_history,).pack(side=LEFT, padx=(0, 6))

        filter_row = Frame(outer)
        filter_row.pack(fill=X, pady=(0, 8))

        Label(filter_row, text="Status:", width=8, anchor="w").pack(side=LEFT)

        self.history_filter_var = StringVar(value="all")

        self.history_filter = ttk.Combobox(
            filter_row,
            textvariable=self.history_filter_var,
            values=[
                "all",
                "queued",
                "started",
                "success",
                "failed",
                "cancelled",
            ],
            width=14,
            state="readonly",
        )

        self.history_filter.pack(side=LEFT, padx=(0, 12))

        Label(filter_row, text="Search:", width=8, anchor="w").pack(side=LEFT)

        self.history_search_var = StringVar()

        self.history_search = Entry(
            filter_row,
            textvariable=self.history_search_var,
            width=40,
        )

        self.history_search.pack(side=LEFT, fill=X, expand=True)

        self.history_filter.bind(
            "<<ComboboxSelected>>",
            lambda _e: self.refresh(),
        )

        self.history_search_var.trace_add(
            "write",
            lambda *_args: self.refresh(),
        )

        self.info = Text(outer, wrap="word", height=5)
        self.info.pack(fill=X, pady=(0, 8))

        main_pane = PanedWindow(
            outer,
            orient="vertical",
            sashrelief="raised",
        )
        main_pane.pack(fill=BOTH, expand=True)

        lists_pane = PanedWindow(
            main_pane,
            orient="horizontal",
            sashrelief="raised",
        )

        pending_frame = Frame(lists_pane, padx=4, pady=4)
        completed_frame = Frame(lists_pane, padx=4, pady=4)

        Label(
            pending_frame,
            text="Pending Jobs",
            anchor="w",
            bg="#dddddd",
            fg="black",
        ).pack(fill=X)

        self.listbox = Listbox(
            pending_frame,
            width=50,
            height=12,
            exportselection=False,
        )
        self.listbox.pack(side=LEFT, fill=BOTH, expand=True)

        pending_scrollbar = Scrollbar(pending_frame, command=self.listbox.yview)
        pending_scrollbar.pack(side=RIGHT, fill=Y)
        self.listbox.config(yscrollcommand=pending_scrollbar.set)

        Label(
            completed_frame,
            text="Execution History",
            anchor="w",
            bg="#dddddd",
            fg="black",
        ).pack(fill=X)

        self.completed_listbox = Listbox(
            completed_frame,
            width=92,
            height=12,
            exportselection=False,
        )
        self.completed_listbox.pack(side=LEFT, fill=BOTH, expand=True)

        completed_scrollbar = Scrollbar(
            completed_frame,
            command=self.completed_listbox.yview,
        )
        completed_scrollbar.pack(side=RIGHT, fill=Y)
        self.completed_listbox.config(yscrollcommand=completed_scrollbar.set)

        lists_pane.add(pending_frame)
        lists_pane.add(completed_frame)

        lists_pane.paneconfigure(pending_frame, minsize=300)
        lists_pane.paneconfigure(completed_frame, minsize=460)

        details_frame = Frame(main_pane, padx=4, pady=4)

        Label(
            details_frame,
            text="Job Details",
            anchor="w",
            bg="#dddddd",
            fg="black",
        ).pack(fill=X)

        self.details = Text(
            details_frame,
            wrap="word",
            height=8,
        )
        self.details.pack(fill=BOTH, expand=True)

        main_pane.add(lists_pane)
        main_pane.add(details_frame)

        self.listbox.bind("<<ListboxSelect>>", self.show_pending_details)
        self.completed_listbox.bind("<<ListboxSelect>>", self.show_completed_details)

        self.listbox.bind("<Control-Return>", lambda _e: self.run_selected_next())
        self.listbox.bind("<Delete>", lambda _e: self.cancel_pending())
        self.listbox.bind("<Alt-Up>", lambda _e: self.move_pending_up())
        self.listbox.bind("<Alt-Down>", lambda _e: self.move_pending_down())

        self.completed_listbox.bind("<Control-Return>", lambda _e: self.retry_failed_job())

        self.refresh()
        self.auto_refresh()

    def auto_refresh(self):
        try:
            if self.window.winfo_exists():
                if time.time() >= getattr(self, "_selection_lock_until", 0):
                    self.refresh()
                self.window.after(1000, self.auto_refresh)
        except Exception:
            pass

    def refresh(self):
        self.app.poll_current_process()

        selected_pending_index = None
        selected_completed_index = None

        try:
            idxs = self.listbox.curselection()
            if idxs:
                selected_pending_index = idxs[0]
        except Exception:
            pass

        try:
            if hasattr(self, "completed_listbox"):
                idxs = self.completed_listbox.curselection()
                if idxs:
                    selected_completed_index = idxs[0]
        except Exception:
            pass

        self.listbox.delete(0, END)

        if hasattr(self, "completed_listbox"):
            self.completed_listbox.delete(0, END)

        completed_source = self.filtered_completed_history()

        running = getattr(self.app, "current_job", None)
        started_at = getattr(self.app, "current_job_started_at", None)

        if self.app.is_execution_queue_paused():
            running_text = "QUEUE: PAUSED"

        elif running:
            duration = ""

            if started_at:
                seconds = int(
                    (datetime.now() - started_at).total_seconds()
                )
                duration = f"{seconds}s"

            running_text = (
                f"QUEUE: RUNNING\n"
                f"[{running.get('source', 'manual')}] "
                f"{running.get('category')}/"
                f"{running.get('command')}"
            )

            if duration:
                running_text += f"\nDuration: {duration}"

        else:
            running_text = "QUEUE: IDLE"

        proc = getattr(self.app, "current_process", None)
        proc_job = getattr(self.app, "current_process_job", None)

        if proc is not None and proc_job:
            running_text += (
                f"\n\nProcess PID: {proc.pid}"
                f"\nProcess Command: "
                f"{proc_job.get('command', '')}"
            )

        self.info.delete("1.0", END)

        self.info.insert(
            "1.0",
            f"{running_text}\n\n"
            f"Pending jobs: {len(self.app.execution_queue)}\n"
            f"Completed jobs: {len(completed_source)}"
        )

        for index, job in enumerate(self.app.execution_queue):
            prefix = "▶ " if index == 0 else "  "

            priority = job.get("priority", "normal")

            display_name = (
                f'workflow/{job.get("workflow")}'
                if job.get("kind") == "workflow"
                else f'{job.get("category")}/{job.get("command")}'
            )

            self.listbox.insert(
                END,
                f'{prefix}{index + 1}. '
                f'[{priority}] '
                f'[{job.get("source", "manual")}] '
                f'{display_name} '
                f'@ {job.get("created_at", "")}'
            )

        if (
            selected_pending_index is not None
            and selected_pending_index < self.listbox.size()
        ):
            self.listbox.selection_set(selected_pending_index)
            self.listbox.activate(selected_pending_index)

        if hasattr(self, "completed_listbox"):

            for index, job in enumerate(completed_source, start=1):

                status = job.get("status", "?")
                error = job.get("error", "")
                suffix = f" — {error}" if error else ""

                self.completed_listbox.insert(
                    END,
                    f'{index}. '
                    f'[{status}] '
                    f'[{job.get("priority", "normal")}] '
                    f'[{job.get("source", "manual")}] '
                    f'{job.get("category")}/'
                    f'{job.get("command")} '
                    f'@ {job.get("timestamp", "")}'
                    f'{suffix}'
                )

            if (
                selected_completed_index is not None
                and selected_completed_index
                < self.completed_listbox.size()
            ):
                self.completed_listbox.selection_set(
                    selected_completed_index
                )

                self.completed_listbox.activate(
                    selected_completed_index
                )

        if hasattr(self, "details"):
            if (
                not self.listbox.curselection()
                and (
                    not hasattr(self, "completed_listbox")
                    or not self.completed_listbox.curselection()
                )
            ):
                self.details.delete("1.0", END)

                self.details.insert(
                    "1.0",
                    "Select a pending or completed job "
                    "to view details."
                )

    def run_next(self):
        self.app.process_execution_queue()
        self.refresh()

    def pause_queue(self):
        self.app.pause_execution_queue()
        self.refresh()

    def resume_queue(self):
        self.app.resume_execution_queue()
        self.refresh()

    def move_pending_up(self):
        index = self.selected_pending_index()

        if index is None:
            messagebox.showerror("Execution Queue", "Select a pending job first.")
            return

        if index <= 0:
            return

        queue = self.app.execution_queue
        queue[index - 1], queue[index] = queue[index], queue[index - 1]

        self.refresh()

        self.listbox.selection_clear(0, END)
        self.listbox.selection_set(index - 1)
        self.listbox.activate(index - 1)


    def move_pending_down(self):
        index = self.selected_pending_index()

        if index is None:
            messagebox.showerror("Execution Queue", "Select a pending job first.")
            return

        queue = self.app.execution_queue

        if index >= len(queue) - 1:
            return

        queue[index + 1], queue[index] = queue[index], queue[index + 1]

        self.refresh()

        self.listbox.selection_clear(0, END)
        self.listbox.selection_set(index + 1)
        self.listbox.activate(index + 1)

    def run_selected_next(self):
        index = self.selected_pending_index()

        if index is None:
            messagebox.showerror(
                "Execution Queue",
                "Select a pending job first.",
            )
            return

        queue = self.app.execution_queue

        if index < 0 or index >= len(queue):
            return

        if index != 0:
            selected = queue.pop(index)
            queue.insert(0, selected)

        self.app.set_status(
            f"Prioritized queued job: "
            f"{queue[0].get('category')}/{queue[0].get('command')}"
        )

        self.refresh()

        self.listbox.selection_clear(0, END)
        self.listbox.selection_set(0)
        self.listbox.activate(0)

        if not self.app.is_execution_queue_paused():
            self.app.root.after(10, self.app.process_execution_queue)

    def apply_selected_priority(self):
        index = self.selected_pending_index()

        if index is None:
            messagebox.showerror(
                "Execution Queue",
                "Select a pending job first.",
            )
            return

        queue = self.app.execution_queue

        if index < 0 or index >= len(queue):
            return

        priority = self.priority_var.get().strip().lower()

        if priority not in PRIORITY_ORDER:
            priority = "normal"

        queue[index]["priority"] = priority

        self.app.set_status(
            f"Set priority {priority}: "
            f"{queue[index].get('category')}/"
            f"{queue[index].get('command')}"
        )

        self.refresh()

        self.listbox.selection_clear(0, END)
        self.listbox.selection_set(index)
        self.listbox.activate(index)

    def export_history(self):
        history = self.filtered_completed_history()

        if not history:
            messagebox.showinfo("Export History", "No execution history to export.")
            return

        target = filedialog.asksaveasfilename(
            title="Export Execution History",
            defaultextension=".json",
            initialfile="termforge_execution_history.json",
            filetypes=[
                ("JSON files", "*.json"),
                ("All files", "*.*"),
            ],
        )

        if not target:
            return

        Path(target).write_text(
            json.dumps(history, indent=2),
            encoding="utf-8",
        )

        messagebox.showinfo(
            "Export History",
            f"Exported {len(history)} execution history entries to:\n\n{target}",
        )

    def set_selected_priority(self, priority: str):
        index = self.selected_pending_index()

        if index is None:
            messagebox.showerror("Execution Queue", "Select a pending job first.")
            return

        if priority not in PRIORITY_ORDER:
            priority = "normal"

        self.app.execution_queue[index]["priority"] = priority
        self.app.set_status(
            f"Set priority {priority}: "
            f"{self.app.execution_queue[index].get('category')}/"
            f"{self.app.execution_queue[index].get('command')}"
        )

        self.refresh()
        self.listbox.selection_set(index)
        self.listbox.activate(index)

    def terminate_running(self):
        self.app.terminate_current_process()
        self.refresh()


    def kill_running(self):
        self.app.kill_current_process()
        self.refresh()

    def filtered_completed_history(self):
        history = self.app.get_execution_history()

        status_filter = (
            self.history_filter_var.get().strip().lower()
            if hasattr(self, "history_filter_var")
            else "all"
        )

        search = (
            self.history_search_var.get().strip().lower()
            if hasattr(self, "history_search_var")
            else ""
        )

        results = []

        for job in history:
            status = str(job.get("status", "")).lower()

            if status_filter != "all" and status != status_filter:
                continue

            if search:
                blob = " ".join([
                    str(job.get("source", "")),
                    str(job.get("category", "")),
                    str(job.get("command", "")),
                    str(job.get("status", "")),
                    str(job.get("error", "")),
                ]).lower()

                if search not in blob:
                    continue

            results.append(job)

        return results

    def lock_selection(self, _event=None):
        self._selection_lock_until = time.time() + 3

    def show_job_details(self, job: dict, title: str = "Job Details") -> None:
        if not hasattr(self, "details"):
            return

        lines = [
            title,
            "",
            f"Source: {job.get('source', '')}",
            f"Category: {job.get('category', '')}",
            f"Command: {job.get('command', '')}",
            f"Status: {job.get('status', '')}",
            f"Priority: {job.get('priority', 'normal')}",
            f"Created: {job.get('created_at', '')}",
            f"Timestamp: {job.get('timestamp', '')}",
            f"Completed: {job.get('completed_at', '')}",
            "",
        ]

        error = job.get("error", "")
        if error:
            lines.extend([
                "Error:",
                    str(error),
                    "",
                ])

            lines.extend([
                "Raw:",
                pprint.pformat(job, indent=4),
            ])

        self.details.delete("1.0", END)
        self.details.insert("1.0", "\n".join(lines))

    def show_pending_details(self, _event=None):
        self.lock_selection()

        index = self.selected_pending_index()
        if index is None:
            return

        if index < 0 or index >= len(self.app.execution_queue):
            return

        job = self.app.execution_queue[index]

        if hasattr(self, "priority_var"):
            self.priority_var.set(
                job.get("priority", "normal")
            )

        self.show_job_details(job, "Pending Job")


    def show_completed_details(self, _event=None):
        self.lock_selection()

        idxs = self.completed_listbox.curselection()
        if not idxs:
            return

        history = self.app.get_execution_history()
        index = idxs[0]

        if index < 0 or index >= len(history):
            return

        job = history[index]
        self.show_job_details(job, "Completed Job")

    def retry_failed_job(self):
        job = self.selected_completed_job()

        if not job:
            messagebox.showerror(
                "Execution Queue",
                "Select a failed job from Recent Completed Jobs first.",
            )
            return

        if job.get("status") not in ("failed", "cancelled"):
            messagebox.showerror(
                "Execution Queue",
                "Only failed or cancelled jobs can be retried.",
            )
            return

        category = job.get("category")
        command = job.get("command")

        if not category or not command:
            messagebox.showerror(
                "Execution Queue",
                "Selected history entry does not contain a category/command.",
            )
            return

        self.app.enqueue_command(category, command, source="retry", priority="high")
        self.app.set_status(f"Retried failed job: {category}/{command}")
        self.refresh()

    def selected_completed_job(self):
        idxs = self.completed_listbox.curselection()
        if not idxs:
            return None

        history = self.app.get_execution_history()
        index = idxs[0]

        if index < 0 or index >= len(history):
            return None

        return history[index]

    def clear_queue(self):
        if not messagebox.askokcancel(
            "Clear Queue",
            "Clear all pending queued jobs?",
        ):
            return

        self.app.execution_queue.clear()
        self.app.set_status("Execution queue cleared.")
        if hasattr(self, "details"):
            self.details.delete("1.0", END)
        self.refresh()

    def clear_completed(self):
        self.app.completed_jobs.clear()
        if hasattr(self, "details"):
            self.details.delete("1.0", END)
        self.refresh()

    def selected_pending_index(self):
        idxs = self.listbox.curselection()
        if not idxs:
            return None

        index = idxs[0]
        if index < 0 or index >= len(self.app.execution_queue):
            return None

        return index


    def cancel_pending(self):
        index = self.selected_pending_index()

        if index is None:
            messagebox.showerror("Execution Queue", "Select a pending job first.")
            return

        job = self.app.execution_queue[index]

        if not messagebox.askokcancel(
            "Cancel Pending Job",
            f"Cancel pending job?\n\n{job.get('category')}/{job.get('command')}",
        ):
            return

        cancelled = self.app.execution_queue.pop(index)
        self.app.add_completed_job(cancelled, "cancelled", "")
        self.app.add_execution_history(cancelled, "cancelled", "")
        self.app.set_status(
            f"Cancelled pending job: {cancelled.get('category')}/{cancelled.get('command')}"
        )
        self.refresh()

    def selected_pending_index(self):
        idxs = self.listbox.curselection()
        if not idxs:
            return None

        index = idxs[0]
        if index < 0 or index >= len(self.app.execution_queue):
            return None

        return index

