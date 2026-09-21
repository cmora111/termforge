# TermForge

TermForge is the reference implementation used throughout *The Forge* to
demonstrate and validate engineering principles. This repository contains
source code, tests, documentation, and engineering decision records.

**TermForge — Terminal Virtual Macropad** is a Python/Tkinter macro pad and
terminal automation engine for Linux. It provides programmable command buttons,
chains, shared variables, window profiles, plugins, favorites, and command
history. Its original X11 workflow uses `xdotool`; a separately configured
tmux/Tilix workflow has also been tested on GNOME Wayland.

[PyPI](https://pypi.org/project/termforge/) ·
[License](LICENSE) ·
[Commit history](https://github.com/cmora111/termforge/commits/main)

## Preview

![TermForge main window](docs/main.png)

## Features

| Feature | Purpose |
| --- | --- |
| Chains | Automate multi-step workflows. |
| Shared variables | Prompt once and reuse values. |
| Window profiles | Select specific terminal targets. |
| Delays | Control timing between chain steps. |
| Plugins | Extend application functionality. |
| Favorites | Access frequently used commands. |
| History | Reuse previous commands. |
| tmux backend | Send commands to a selected tmux pane. |
| Tilix integration | Request activation of a mapped workspace tab. |
| GNOME window discovery | Discover and select windows separately from tmux targets. |

## Quick example

A chain can collect variables, select a profile, and execute commands in order:

```python
'Deploy': ['chain', [
    ['vars', ['path', 'user', 'host']],
    ['select_profile', 'server'],
    [2, 'cd <path>'],
    ['sleep', 1],
    [2, 'git pull'],
    ['sleep', 1],
    [2, 'ssh -T <user>@<host>'],
]]
```

This illustrates the existing chain syntax; the deployment example is not part
of the September 2026 workspace-routing verification.

## Installation

Clone the repository and install it in a virtual environment:

```bash
git clone https://github.com/cmora111/termforge.git
cd termforge
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python -m termforge
```

Alternatively, launch the installed `termforge` command when it is available.
For the X11 command-injection workflow, install `xdotool` on a supported Linux
system, for example with `sudo apt install xdotool` on Ubuntu. That X11 method
is not a general Wayland command-injection solution.

The local source installation used during the tmux/Tilix tests was refreshed
with:

```bash
pipx install --force .
```

## Verified tmux and Tilix workflow

On September 21, 2026, TermForge was tested with one Tilix window containing
ten tabs in a fixed order. The application selects a tmux target, requests the
matching Tilix tab, and sends the command to the target pane.

| Tilix tab | tmux target |
| --- | --- |
| 1 | `forge-main:0.0` |
| 2 | `forge-secondary:0.0` |
| 3 | `stage-main:0.0` |
| 4 | `stage-secondary:0.0` |
| 5 | `marlin-main:0.0` |
| 6 | `marlin-secondary:0.0` |
| 7 | `bible-main:0.0` |
| 8 | `bible-secondary:0.0` |
| 9 | `termforge-main:0.0` |
| 10 | `termforge-secondary:0.0` |

Launch the tested configuration with:

```bash
TERMFORGE_TILIX_WINDOW_ID=<verified-window-id> \
TERMFORGE_TMUX_SOCKET=empty \
termforge
```

Replace `<verified-window-id>` with the current Tilix D-Bus window object
number. It was `8` during testing, but the number is transient. The `empty`
socket setting selects the tmux server addressed by `tmux -S ''`, rather than
the default server. Do not kill or recreate an existing tmux server merely to
troubleshoot tab activation.

Select the **tmux** backend and a pane such as `stage-main:0.0`. Use a regular
**Command / Send** button or the menu-selection/test-popout workflow. **Spawn**
and **Detached** commands take different dispatch paths and are not covered by
the routing tests.

The mapping is positional: changing Tilix tab order without updating the
mapping can activate the wrong tab. Activation is best-effort; a successful
D-Bus request alone does not prove the visible tab changed.

### Verification status

The following tests were reported as passing on September 21, 2026:

- Startup with the tmux backend and selected target.
- Direct Backend Manager delivery and Tilix activation.
- Normal command-button delivery and activation.
- Selected-target persistence after restarting TermForge.
- Command routing and observed tab activation for all ten destinations.
- Forge/Stage main and secondary routing in both directions; additional
  Marlin, Bible, and TermForge destination tests.

See [Workspace Routing Verification](docs/verification/WORKSPACE-ROUTING.md)
for the procedure, results, and limitations. The implementation checkpoint
associated with the integration is commit `be50630`. These tests do **not**
certify every application feature or every possible workspace transition.

## Project structure

```text
src/termforge/
    app.py
    cli.py
    default_config.py
    xdo_helper.py
    backends/
        tmux_backend.py
        tilix_tabs.py
    gnome_window_discovery.py
    ui/
        backend_manager.py
        gnome_window_picker.py
examples/
    config.py
    plugins/
docs/
    verification/
        WORKSPACE-ROUTING.md
```

The layout above highlights relevant files; it is not an exhaustive directory
listing. The GNOME window picker is separate from X11 and tmux target selection.
Its presence in the code does not imply it passed the workspace-routing tests.

## Plugin example

```python
TermForge_PLUGIN_API_VERSION = 1


def run(app, context):
    app.set_status("Hello from plugin!")
```

For additional integration details, consult the repository's plugin API
documentation where available.

## Development and verification

Before replacing a source module, keep a backup. Check Python syntax and
reinstall the local package before retesting. Record each tested workflow
separately from unverified features; passing the ten-workspace routing tests
does not establish overall release readiness.

## License

MIT. See [LICENSE](LICENSE) for the repository's license text.
