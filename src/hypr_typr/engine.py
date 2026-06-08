from __future__ import annotations
import asyncio
import subprocess
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Callable

from .config import Config, load as load_config
from .humanizer import Humanizer

KEYSYM_MAP = {
    "\n": "Return",
    "\t": "Tab",
    "\x1b": "Escape",
    "\x08": "BackSpace",
}


def _wtype_char(char: str) -> None:
    keysym = KEYSYM_MAP.get(char)
    if keysym:
        subprocess.run(["wtype", "-k", keysym], check=False)
    else:
        try:
            char.encode("utf-8")
            subprocess.run(["wtype", "--", char], check=False)
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
    asyncio.run(type_text(text, cfg))
