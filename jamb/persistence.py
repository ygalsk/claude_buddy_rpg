from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from .models import JambState

SAVE_DIR = Path.home() / ".claude" / "jamb"
SAVE_FILE = SAVE_DIR / "save.json"
SAVE_VERSION = 1


def load_quiet() -> JambState:
    """Load state without starting a session (no decay, no session increment)."""
    if SAVE_FILE.exists():
        try:
            data = json.loads(SAVE_FILE.read_text())
            return JambState.from_dict(data.get("jamb", {}))
        except (json.JSONDecodeError, KeyError):
            pass
    return JambState()


def load() -> JambState:
    state = load_quiet()
    state.start_session()
    return state


def save(state: JambState) -> None:
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    data = {"version": SAVE_VERSION, "jamb": state.as_dict()}
    content = json.dumps(data, indent=2)
    # Atomic write: write to temp file then rename to prevent corruption
    # from concurrent writes (hooks + TUI writing simultaneously).
    fd, tmp_path = tempfile.mkstemp(dir=SAVE_DIR, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(content)
        os.replace(tmp_path, str(SAVE_FILE))
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
