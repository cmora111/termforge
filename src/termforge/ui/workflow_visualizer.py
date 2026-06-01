import webbrowser
import html
import pprint
import webbrowser
from datetime import datetime
from pathlib import Path
from tkinter import *
from tkinter import filedialog, messagebox

class WorkflowVisualizerWindow:
    def __init__(self, app, workflow_name, steps, steps_provider=None):
        self.app = app
        self.workflow_name = workflow_name
        self.steps = steps
        self.steps_provider = steps_provider

        self.window = Toplevel(app.root)
        self.window.title(f"Workflow Visualizer — {workflow_name}")
        self.window.geometry("980x640")
        self.window.transient(app.root)

        outer = Frame(self.window, padx=8, pady=8)
        outer.pack(fill=BOTH, expand=True)

        Label(
            outer,
            text=f"Workflow Visualizer — {workflow_name}",
            bd=4,
            width=46,
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
            text="Copy",
            width=14,
            bg="#2f5597",
            fg="white",
            command=self.copy_report,
        ).pack(side=LEFT, padx=(0, 6))

        Button(
            action_row,
            text="Export HTML",
            width=14,
            bg="#3d6d3d",
            fg="white",
            command=self.export_html,
        ).pack(side=LEFT, padx=(0, 6))

        Button(
            action_row,
            text="Close",
            width=14,
            bg="red",
            fg="black",
            command=self.window.destroy,
        ).pack(side=RIGHT)

        self.output = Text(
            outer,
            wrap="word",
            width=120,
            height=34,
        )
        self.output.pack(fill=BOTH, expand=True)

        self.refresh()

    def build_report(self) -> str:
        lines = []
        lines.append(f"Refreshed: {datetime.now().strftime('%H:%M:%S')}")
        lines.append("")
        errors = self.app.validate_workflow(self.steps)

        lines.append(f"Workflow: {self.workflow_name}")
        lines.append("=" * 80)
        lines.append("")

        if errors:
            lines.append("Validation Issues:")
            for error in errors:
                lines.append(f"  - {error}")
            lines.append("")
        else:
            lines.append("Validation: OK")
            lines.append("")

        if not isinstance(self.steps, list):
            lines.append("Workflow steps are not a list.")
            return "\n".join(lines)

        ids = []

        for step in self.steps:
            if isinstance(step, dict):
                step_id = str(step.get("id", "")).strip()
                if step_id:
                    ids.append(step_id)

        for index, step in enumerate(self.steps, start=1):
            lines.append(f"{index}. Step")

            if not isinstance(step, dict):
                lines.append(f"   INVALID: {step!r}")
                lines.append("")
                continue

            step_id = str(step.get("id", f"step-{index}")).strip()
            depends_on = step.get("depends_on", [])

            if isinstance(depends_on, str):
                depends_on = [depends_on]

            run_if = str(step.get("run_if", "always")).strip().lower() or "always"

            environment = step.get("environment", "")
            profile = step.get("profile", "")
            backend = step.get("backend", "")
            tmux_session = step.get("tmux_session", "")
            tmux_pane = step.get("tmux_pane", "")
            tmux_mode = step.get("tmux_mode", "")
            command = step.get("command", "")

            lines.append(f"   id: {step_id}")
            lines.append(
                "   depends_on: "
                + (", ".join(map(str, depends_on)) if depends_on else "none")
            )
            lines.append(f"   run_if: {run_if}")

            missing = [
                dep for dep in depends_on
                if dep not in ids
            ]

            if missing:
                lines.append(
                    "   dependency_status: MISSING "
                    + ", ".join(map(str, missing))
                )
            else:
                lines.append("   dependency_status: OK")

            lines.append(f"   environment: {environment or '(none)'}")
            lines.append(f"   profile: {profile or '(none)'}")
            lines.append(f"   backend: {backend or '(global)'}")

            if backend == "tmux":
                lines.append(f"   tmux_session: {tmux_session or '(global)'}")
                lines.append(f"   tmux_pane: {tmux_pane or '(global)'}")
                lines.append(f"   tmux_mode: {tmux_mode or '(global)'}")

            if isinstance(command, str):
                lines.append(f"   command_ref: {command}")
            else:
                lines.append("   command:")
                lines.append(
                    pprint.pformat(command, indent=8)
                )

            lines.append("")

        return "\n".join(lines)

    def reload_steps(self):
        provider = getattr(self, "steps_provider", None)

        if provider is not None:
            try:
                self.steps = provider()
                return True
            except Exception as exc:
                messagebox.showerror(
                    "Workflow Visualizer",
                    f"Could not read live workflow editor JSON:\n\n{exc}",
                )
                return False

        workflows = self.app.get_workflows()
        latest = workflows.get(self.workflow_name)

        if latest is None:
            messagebox.showerror(
                "Workflow Visualizer",
                f"Workflow no longer exists:\n\n{self.workflow_name}",
            )
            return False

        self.steps = latest
        return True

    def refresh(self):
        if not self.reload_steps():
            return

        report = self.build_report()

        self.output.delete("1.0", END)
        self.output.insert("1.0", report)

    def copy_report(self):
        report = self.output.get("1.0", END).strip()

        self.window.clipboard_clear()
        self.window.clipboard_append(report)
        self.window.update()

        messagebox.showinfo(
            "Workflow Visualizer",
            "Workflow report copied to clipboard.",
        )

    def export_html(self):
        self.reload_steps()
        target = filedialog.asksaveasfilename(
            title="Export Workflow Graph HTML",
            defaultextension=".html",
            initialfile=f"workflow_{self.workflow_name}.html",
            filetypes=[
                ("HTML files", "*.html"),
                ("All files", "*.*"),
            ],
        )

        if not target:
            return

        html_text = self.build_html()

        Path(target).write_text(html_text, encoding="utf-8")

        try:
            uri = Path(target).resolve().as_uri()
            opened = webbrowser.open_new_tab(uri)

            if not opened:
                raise RuntimeError("webbrowser.open_new_tab returned False")

        except Exception as exc:
            messagebox.showwarning(
                "Workflow Visualizer",
                "HTML exported, but could not open browser automatically.\n\n"
                f"File:\n{target}\n\n"
                f"Error:\n{exc}",
            )
            return

        messagebox.showinfo(
            "Workflow Visualizer",
            f"Exported workflow graph to:\n\n{target}",
        )

    def build_html(self) -> str:
        errors = self.app.validate_workflow(self.steps)

        node_blocks = []
        edge_blocks = []

        id_set = set()

        if isinstance(self.steps, list):
            for step in self.steps:
                if isinstance(step, dict):
                    step_id = str(step.get("id", "")).strip()
                    if step_id:
                        id_set.add(step_id)

        if isinstance(self.steps, list):
            for index, step in enumerate(self.steps, start=1):
                if not isinstance(step, dict):
                    step_id = f"invalid_{index}"
                    label = f"Invalid step {index}"
                    command_text = repr(step)
                    depends_on = []
                    run_if = "always"
                    environment = ""
                    profile = ""
                else:
                    step_id = str(step.get("id", f"step-{index}")).strip()
                    label = step_id
                    command = step.get("command", "")
                    command_text = (
                        command
                        if isinstance(command, str)
                        else pprint.pformat(command, indent=4)
                    )
                    depends_on = step.get("depends_on", [])
                    run_if = str(step.get("run_if", "always")).strip() or "always"
                    environment = step.get("environment", "")
                    profile = step.get("profile", "")

                    if isinstance(depends_on, str):
                        depends_on = [depends_on]

                safe_id = html.escape(step_id)
                safe_label = html.escape(label)
                safe_command = html.escape(str(command_text))
                safe_run_if = html.escape(str(run_if))
                safe_environment = html.escape(str(environment))
                safe_profile = html.escape(str(profile))

                node_blocks.append(
                    f"""
                    <div class="node" id="node-{safe_id}">
                      <div class="node-title">{index}. {safe_label}</div>
                      <div class="meta">run_if: <b>{safe_run_if}</b></div>
                      <div class="meta">environment: {safe_environment or "<span class='muted'>(none)</span>"}</div>
                      <div class="meta">profile: {safe_profile or "<span class='muted'>(none)</span>"}</div>
                      <pre>{safe_command}</pre>
                    </div>
                    """
                )

                for dep in depends_on:
                    dep_text = str(dep)
                    edge_class = "edge"
                    if dep_text not in id_set:
                        edge_class += " missing"

                    edge_blocks.append(
                        f"""
                        <div class="{edge_class}">
                          <span>{html.escape(dep_text)}</span>
                          <span class="arrow">→</span>
                          <span>{safe_label}</span>
                        </div>
                        """
                    )

        error_html = ""
        if errors:
            error_items = "\n".join(
                f"<li>{html.escape(str(error))}</li>"
                for error in errors
            )
            error_html = f"""
            <section class="errors">
              <h2>Validation Issues</h2>
              <ul>{error_items}</ul>
            </section>
            """

        return f"""<!doctype html>
    <html>
    <head>
    <meta charset="utf-8">
    <title>Workflow Graph — {html.escape(self.workflow_name)}</title>
    <style>
    body {{
        font-family: Arial, sans-serif;
        margin: 24px;
        background: #f5f7fa;
        color: #222;
    }}
    h1 {{
        margin-bottom: 4px;
    }}
    .subtitle {{
        color: #666;
        margin-bottom: 24px;
    }}
    .layout {{
        display: grid;
        grid-template-columns: 2fr 1fr;
        gap: 18px;
    }}
    .panel {{
        background: white;
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }}
    .node {{
        border-left: 6px solid #2f5597;
        background: #fff;
        border-radius: 10px;
        margin: 12px 0;
        padding: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }}
    .node-title {{
        font-weight: bold;
        font-size: 18px;
        margin-bottom: 8px;
    }}
    .meta {{
        color: #555;
        margin: 3px 0;
    }}
    pre {{
        background: #f0f0f0;
        padding: 10px;
        border-radius: 8px;
        white-space: pre-wrap;
        overflow-x: auto;
    }}
    .edge {{
        padding: 8px 10px;
        margin: 8px 0;
        background: #eef4ff;
        border-radius: 8px;
        border-left: 4px solid #2f5597;
    }}
    .edge.missing {{
        background: #ffecec;
        border-left-color: #aa3333;
    }}
    .arrow {{
        margin: 0 8px;
        font-weight: bold;
    }}
    .errors {{
        background: #fff3f3;
        border: 1px solid #ffcccc;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 18px;
    }}
    .muted {{
        color: #888;
    }}
    </style>
    </head>
    <body>
    <h1>Workflow Graph — {html.escape(self.workflow_name)}</h1>
    <div class="subtitle">Generated by TermForge</div>

    {error_html}

    <div class="layout">
      <section class="panel">
        <h2>Steps</h2>
        {''.join(node_blocks)}
      </section>

      <section class="panel">
        <h2>Dependencies</h2>
        {''.join(edge_blocks) if edge_blocks else "<p class='muted'>No dependencies.</p>"}
      </section>
    </div>
    </body>
    </html>
    """

