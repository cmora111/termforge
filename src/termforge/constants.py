from pathlib import Path
import re
from . import __version__

APP_NAME = "TermForge"
APP_SLUG = "termforge"
APP_VERSION = "0.4.0"

CONFIG_DIR = Path.home() / ".config" / APP_SLUG
CONFIG_FILE = CONFIG_DIR / "config.py"
STATE_FILE = CONFIG_DIR / "state.json"
LOG_FILE = CONFIG_DIR / "termforge.log"
PLUGIN_DIR = CONFIG_DIR / "plugins"
BACKUP_DIR = CONFIG_DIR / "backups"
PROJECT_BACKUP_DIR = BACKUP_DIR / "project"

DEFAULT_BACKEND = "x11"
DEFAULT_TMUX_SESSION = "termforge"
DEFAULT_TMUX_MODE = "pane"

DEFAULT_WINDOW_GEOMETRY = "900x650"

PLUGIN_API_VERSION = 1
MAX_HISTORY = 30

HELPER_TIMEOUT_SECONDS = 20
PLACEHOLDER_RE = re.compile(r"<([^<>]+)>")


PRIORITY_ORDER = {
    "critical": 0,
    "high": 1,
    "normal": 2,
    "low": 3,
}

