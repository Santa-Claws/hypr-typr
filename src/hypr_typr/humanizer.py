from __future__ import annotations
import random
from .config import Config


class Humanizer:
    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self._burst_remaining = 0

    def next_delay(self, char: str, prev_char: str | None) -> float:
        cfg = self.cfg
        base = 60.0 / (cfg.wpm * 5)

        if not cfg.humanize:
            return base

        if self._burst_remaining > 0:
            self._burst_remaining -= 1
            return base * random.uniform(0.3, 0.6)

        if random.random() < cfg.burst_chance:
            self._burst_remaining = random.randint(cfg.burst_min_len, cfg.burst_max_len) - 1
            return base * random.uniform(0.3, 0.6)

        sigma = base * (cfg.variation_pct / 100.0)
        delay = random.gauss(base, sigma)
        delay = max(base * 0.4, min(delay, base * 2.0))

        if char in (" ", "\n", "\t") and random.random() < cfg.word_pause_chance:
            pause = random.uniform(cfg.word_pause_min_ms / 1000, cfg.word_pause_max_ms / 1000)
            delay += pause

        return delay
