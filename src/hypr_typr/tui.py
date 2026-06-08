from __future__ import annotations
import asyncio
import threading

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Button,
    Footer,
    Header,
    Label,
    ProgressBar,
    Slider,
    Switch,
    Static,
)
from textual.reactive import reactive

from .config import Config, load as load_config, save as save_config
from .engine import get_clipboard, type_text


KEYBIND_HINT = "bind = $mainMod, T, exec, hypr-typr type"


class WpmDisplay(Static):
    value: reactive[int] = reactive(80)

    def render(self) -> str:
        return f"Speed: {self.value} WPM"


class StatusBar(Static):
    message: reactive[str] = reactive("")

    def render(self) -> str:
        return self.message


class HyprTyprApp(App):
    CSS = """
    Screen {
        background: $surface;
    }

    #main {
        margin: 1 2;
        height: 100%;
    }

    #title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    .section {
        border: tall $primary;
        padding: 1 2;
        margin-bottom: 1;
    }

    .section-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    .row {
        height: 3;
        align: left middle;
    }

    .row Label {
        width: 28;
    }

    .row Slider {
        width: 1fr;
    }

    .row Switch {
        margin-left: 1;
    }

    WpmDisplay {
        width: 16;
        text-align: right;
    }

    #keybind-hint {
        color: $text-muted;
        text-style: italic;
        margin-top: 1;
    }

    #actions {
        align: center middle;
        height: 5;
        margin-top: 1;
    }

    Button {
        margin: 0 1;
    }

    #progress-area {
        height: 3;
        align: center middle;
    }

    StatusBar {
        text-align: center;
        color: $success;
    }
    """

    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+t", "type_now", "Type Now"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.cfg = load_config()
        self._typing = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Vertical(id="main"):
            yield Static("hypr-typr", id="title")

            with Container(classes="section"):
                yield Static("Speed", classes="section-title")
                with Horizontal(classes="row"):
                    yield Label("Words per minute")
                    yield Slider(
                        min=20, max=300, value=self.cfg.wpm, step=5, id="wpm"
                    )
                    yield WpmDisplay(id="wpm-display")

            with Container(classes="section"):
                yield Static("Humanizer", classes="section-title")
                with Horizontal(classes="row"):
                    yield Label("Enable humanizer")
                    yield Switch(value=self.cfg.humanize, id="humanize")
                with Horizontal(classes="row"):
                    yield Label("Variation ±%")
                    yield Slider(
                        min=0, max=80, value=int(self.cfg.variation_pct), step=5, id="variation"
                    )
                with Horizontal(classes="row"):
                    yield Label("Word pause chance")
                    yield Slider(
                        min=0, max=60, value=int(self.cfg.word_pause_chance * 100), step=5, id="pause_chance"
                    )
                with Horizontal(classes="row"):
                    yield Label("Word pause min (ms)")
                    yield Slider(
                        min=0, max=500, value=self.cfg.word_pause_min_ms, step=20, id="pause_min"
                    )
                with Horizontal(classes="row"):
                    yield Label("Word pause max (ms)")
                    yield Slider(
                        min=20, max=1000, value=self.cfg.word_pause_max_ms, step=20, id="pause_max"
                    )
                with Horizontal(classes="row"):
                    yield Label("Burst typing")
                    yield Switch(value=self.cfg.burst_chance > 0, id="burst")

            with Horizontal(id="actions"):
                yield Button("Type Clipboard Now", variant="primary", id="type-btn")
                yield Button("Save Settings", variant="success", id="save-btn")

            with Container(id="progress-area"):
                yield ProgressBar(total=100, show_eta=False, id="progress")
                yield StatusBar(id="status")

            yield Static(f"Hyprland keybind:  {KEYBIND_HINT}", id="keybind-hint")

        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#wpm-display", WpmDisplay).value = self.cfg.wpm
        self.query_one("#progress", ProgressBar).update(progress=0)

    def on_slider_changed(self, event: Slider.Changed) -> None:
        slider_id = event.slider.id
        val = event.value
        if slider_id == "wpm":
            self.query_one("#wpm-display", WpmDisplay).value = int(val)
            self.cfg.wpm = int(val)
        elif slider_id == "variation":
            self.cfg.variation_pct = float(val)
        elif slider_id == "pause_chance":
            self.cfg.word_pause_chance = val / 100.0
        elif slider_id == "pause_min":
            self.cfg.word_pause_min_ms = int(val)
        elif slider_id == "pause_max":
            self.cfg.word_pause_max_ms = int(val)

    def on_switch_changed(self, event: Switch.Changed) -> None:
        if event.switch.id == "humanize":
            self.cfg.humanize = event.value
        elif event.switch.id == "burst":
            self.cfg.burst_chance = 0.08 if event.value else 0.0

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-btn":
            self.action_save()
        elif event.button.id == "type-btn":
            self.action_type_now()

    def action_save(self) -> None:
        save_config(self.cfg)
        self.query_one("#status", StatusBar).message = "Settings saved."

    def action_type_now(self) -> None:
        if self._typing:
            return
        text = get_clipboard()
        if not text:
            self.query_one("#status", StatusBar).message = "Clipboard is empty."
            return
        self._typing = True
        total = len(text)
        progress = self.query_one("#progress", ProgressBar)
        status = self.query_one("#status", StatusBar)
        progress.update(total=total, progress=0)
        status.message = f"Typing {total} chars..."

        def _progress(done: int, tot: int) -> None:
            self.call_from_thread(progress.update, progress=done)
            if done >= tot:
                self.call_from_thread(setattr, status, "message", "Done!")
                self._typing = False

        cfg_snapshot = load_config()
        cfg_snapshot.__dict__.update(self.cfg.__dict__)

        def _run() -> None:
            asyncio.run(type_text(text, cfg_snapshot, on_progress=_progress))

        threading.Thread(target=_run, daemon=True).start()

    def action_quit(self) -> None:
        self.exit()


def run_tui() -> None:
    HyprTyprApp().run()
