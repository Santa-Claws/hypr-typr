from __future__ import annotations
import json
from dataclasses import dataclass, asdict, field
from pathlib import Path

CONFIG_PATH = Path.home() / ".config" / "hypr-typr" / "config.json"


@dataclass
class Config:
    wpm: int = 80
    humanize: bool = True
    variation_pct: float = 30.0
    word_pause_chance: float = 0.15
    word_pause_min_ms: int = 80
    word_pause_max_ms: int = 300
    burst_chance: float = 0.08
    burst_min_len: int = 2
    burst_max_len: int = 5


def load() -> Config:
    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text())
            known = {f.name for f in Config.__dataclass_fields__.values()}
            return Config(**{k: v for k, v in data.items() if k in known})
        except Exception:
            pass
    return Config()


def save(cfg: Config) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(asdict(cfg), indent=2))
