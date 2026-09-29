"""Open the computer's folder window and return the chosen path."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def pick_folder(initial: str = "") -> str | None:
    """Return a folder path, or None when the window is closed without a choice."""
    if sys.platform == "darwin":
        return _pick_folder_mac(initial)
    return _pick_folder_tk(initial)


def _applescript_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _pick_folder_mac(initial: str) -> str | None:
    prompt = "Choose the photo folder"
    location = Path(initial).expanduser() if initial.strip() else None
    if location is not None and location.is_dir():
        escaped = _applescript_string(str(location))
        script = (
            f'POSIX path of (choose folder with prompt "{prompt}" '
            f'default location POSIX file "{escaped}")'
        )
    else:
        script = f'POSIX path of (choose folder with prompt "{prompt}")'
    completed = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        return None
    path = completed.stdout.strip().rstrip("/")
    return path or None


def _pick_folder_tk(initial: str) -> str | None:
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    try:
        root.attributes("-topmost", True)
    except tk.TclError:
        pass
    location = Path(initial).expanduser() if initial.strip() else None
    chosen = filedialog.askdirectory(
        title="Choose the photo folder",
        initialdir=str(location) if location is not None and location.is_dir() else None,
        parent=root,
    )
    root.destroy()
    path = chosen.strip().rstrip("/")
    return path or None
