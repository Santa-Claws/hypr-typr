from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from pathlib import Path

CONFIG_PATH = Path.home() / ".config" / "hypr-typr" / "config.json"


@dataclass
class Config:
    wpm: int = 120
    humanize: bool = False
    variation_pct: float = 12.0
    word_pause_chance: float = 0.08
    word_pause_min_ms: int = 20
    word_pause_max_ms: int = 60
    burst_chance: float = 0.05
    burst_min_len: int = 2
    burst_max_len: int = 4


def load() -> Config:
    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text())
            known = {f for f in Config.__dataclass_fields__}
            return Config(**{k: v for k, v in data.items() if k in known})
        except Exception:
            pass
    return Config()


def save(cfg: Config) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(asdict(cfg), indent=2))
