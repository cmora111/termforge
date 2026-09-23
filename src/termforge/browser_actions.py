"""Launch URLs and searches in Brave or Firefox without keyboard injection."""
from __future__ import annotations

import shutil
import subprocess
from urllib.parse import quote_plus, urlsplit

BROWSERS = {
    "firefox": ("firefox",),
    "brave": ("brave-browser", "brave", "brave-browser-stable"),
}


def resolve_address(text: str) -> str:
    """Convert an explicit URL or a search phrase to a browser-safe URL."""
    text = str(text).strip()
    if not text:
        raise ValueError("Enter a URL or search phrase.")
    if any(ord(char) < 32 or ord(char) == 127 for char in text):
        raise ValueError("Control characters are not permitted.")
    parsed = urlsplit(text)
    if parsed.scheme:
        if parsed.scheme.lower() not in ("http", "https") or not parsed.netloc:
            raise ValueError("Only HTTP and HTTPS URLs are supported.")
        return text
    if " " not in text and "." in text.split("/", 1)[0] and not text.startswith("."):
        candidate = "https://" + text
        if urlsplit(candidate).hostname:
            return candidate
    return "https://www.google.com/search?q=" + quote_plus(text)


def open_browser(text: str, browser: str = "firefox", mode: str = "new-tab") -> str:
    """Open a URL in a browser. Existing-tab replacement is not supported."""
    browser = browser.strip().lower()
    mode = mode.strip().lower().replace("_", "-")
    if browser not in BROWSERS:
        raise ValueError("Browser must be 'firefox' or 'brave'.")
    if mode != "new-tab":
        raise ValueError("Only new-tab mode is supported by browser launch commands.")
    executable = next((path for name in BROWSERS[browser]
                       if (path := shutil.which(name))), None)
    if not executable:
        raise FileNotFoundError(f"{browser} executable not found in PATH.")
    url = resolve_address(text)
    # A list of arguments avoids shell evaluation of untrusted URL/search text.
    subprocess.Popen([executable, "--new-tab", url],
                     stdin=subprocess.DEVNULL,
                     stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL,
                     start_new_session=True)
    return url
