from __future__ import annotations
import asyncio
import os
import signal
import subprocess
import sys
from pathlib import Path
from typing import Callable

from .config import Config, load as load_config
from .humanizer import Humanizer

PID_FILE = Path("/tmp/hypr-typr.pid")

KEYSYM_MAP = {
    "\n": "Return",
    "\t": "Tab",
    "\x1b": "Escape",
    "\x08": "BackSpace",
}

_DEVNULL = subprocess.DEVNULL


def _wtype_char(char: str) -> None:
    keysym = KEYSYM_MAP.get(char)
    if keysym:
        subprocess.run(
            ["wtype", "-k", keysym],
            check=False, stdout=_DEVNULL, stderr=_DEVNULL,
        )
    else:
        try:
            char.encode("utf-8")
            subprocess.run(
                ["wtype", "--", char],
                check=False, stdout=_DEVNULL, stderr=_DEVNULL,
            )
        except Exception:
            pass


def get_clipboard() -> str:
    result = subprocess.run(
        ["wl-paste", "--no-newline"],
        capture_output=True,
        text=True,
    )
    return result.stdout


async def type_text(
    text: str,
    cfg: Config,
    on_progress: Callable[[int, int], None] | None = None,
) -> None:
    humanizer = Humanizer(cfg)
    total = len(text)
    prev: str | None = None

    for i, char in enumerate(text):
        delay = humanizer.next_delay(char, prev)
        await asyncio.sleep(delay)
        _wtype_char(char)
        if on_progress:
            on_progress(i + 1, total)
        prev = char


def run_type_clipboard() -> None:
    cfg = load_config()
    text = get_clipboard()
    if not text:
        sys.exit(0)

    PID_FILE.write_text(str(os.getpid()))
    try:
        # brief pause so the keybind key-release event clears before typing starts
        asyncio.run(_type_with_delay(text, cfg))
    finally:
        PID_FILE.unlink(missing_ok=True)


async def _type_with_delay(text: str, cfg: Config) -> None:
    await asyncio.sleep(0.15)
    await type_text(text, cfg)


def run_stop() -> None:
    if not PID_FILE.exists():
        sys.exit(0)
    try:
        pid = int(PID_FILE.read_text().strip())
        os.kill(pid, signal.SIGTERM)
    except (ProcessLookupError, ValueError):
        pass
    finally:
        PID_FILE.unlink(missing_ok=True)
