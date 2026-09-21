"""Best-effort Tilix tab activation for the fixed TermForge workspace order.

Set TERMFORGE_TILIX_WINDOW_ID to the Tilix D-Bus window object number.
The number is transient and must be rechecked after restarting Tilix.
"""

import os
import re
import shutil
import subprocess

WORKSPACE_ORDER = (
    'forge-main', 'forge-secondary', 'stage-main', 'stage-secondary',
    'marlin-main', 'marlin-secondary', 'bible-main', 'bible-secondary',
    'termforge-main', 'termforge-secondary',
)


def activate_for_target(target: str) -> tuple[bool, str]:
    """Request the matching tab; never interrupt command delivery on failure."""
    session = str(target).split(':', 1)[0].strip()
    if session not in WORKSPACE_ORDER:
        return False, f'No Tilix tab mapping for {session!r}'
    window_id = os.environ.get('TERMFORGE_TILIX_WINDOW_ID', '').strip()
    if not re.fullmatch(r'[0-9]+', window_id):
        return False, 'Set TERMFORGE_TILIX_WINDOW_ID to the verified Tilix window ID'
    if not shutil.which('gdbus'):
        return False, 'gdbus is unavailable'
    position = WORKSPACE_ORDER.index(session) + 1
    # Tilix uses actions 1..9 for tabs 1..9, and 0 for tab 10.
    action = f'switch-to-session-{position % 10}'
    result = subprocess.run(
        ['gdbus', 'call', '--session', '--dest', 'com.gexperts.Tilix',
         '--object-path', f'/com/gexperts/Tilix/window/{window_id}',
         '--method', 'org.gtk.Actions.Activate', action, '[]', '{}'],
        capture_output=True, text=True, timeout=3, check=False,
    )
    if result.returncode:
        return False, result.stderr.strip() or 'Tilix tab activation failed'
    # D-Bus success means the action was accepted, not that the visible tab changed.
    return True, f'Requested Tilix tab {position} for {session}'
