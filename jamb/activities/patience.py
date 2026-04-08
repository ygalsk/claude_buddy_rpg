from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Label, ProgressBar

if TYPE_CHECKING:
    from ..app import JambApp


class MeditationActivity(Screen):
    """Don't press any key for 10 seconds."""

    def __init__(self, on_done: Callable[[str, int, int], None], **kwargs) -> None:
        super().__init__(**kwargs)
        self._on_done = on_done
        self._ticks = 0
        self._target = 10
        self._done = False
        self._resets = 0
        self._timer_handle = None

    def compose(self) -> ComposeResult:
        with Vertical(classes="activity-box"):
            yield Label("  ═══ MEDITATION ═══\n", classes="header")
            yield Label("\n  Jamb is meditating... hold still...", id="status-label", classes="speech")
            bar = ProgressBar(total=self._target, show_eta=False, show_percentage=False, classes="bar-patience", id="med-bar")
            yield bar
            yield Label("  Do NOT press any key for 10 seconds.", id="hint-label", classes="dim mt1")
            yield Label("", id="result-label")

        yield Footer()

    def on_mount(self) -> None:
        self._timer_handle = self.set_interval(1.0, self._tick)

    def _tick(self) -> None:
        if self._done:
            if self._timer_handle:
                self._timer_handle.stop()
            return
        self._ticks += 1
        bar = self.query_one("#med-bar", ProgressBar)
        bar.update(progress=self._ticks)

        if self._ticks >= self._target:
            self._done = True
            if self._timer_handle:
                self._timer_handle.stop()
            gain = 5 - min(self._resets, 4)
            gain = max(gain, 1)
            xp = 15 - self._resets * 3
            xp = max(xp, 5)
            status = self.query_one("#status-label", Label)
            status.update("\n  [lightgreen bold]INNER PEACE ACHIEVED![/]")
            result = self.query_one("#result-label", Label)
            result.update(
                f"\n  [lightgreen bold]+{gain} PATIENCE  (+{xp} XP)[/]\n  \\[C] Continue  \\[B] Training  \\[other] Main"
            )
            hint = self.query_one("#hint-label", Label)
            hint.update("")
            self._on_done("patience", gain, xp)
            return

        seconds_left = self._target - self._ticks
        status = self.query_one("#status-label", Label)
        status.update(f"\n  [lightskyblue]Jamb is meditating... {seconds_left}s remain...[/]")

    def on_key(self, event) -> None:
        if self._done:
            app: JambApp = self.app  # type: ignore[assignment]
            key = event.character or event.key
            if key in ("c", "C"):
                app.start_activity("patience")
            elif key in ("b", "B"):
                app.show_training()
            else:
                app.show_main()
            return

        # Player pressed a key — reset!
        self._resets += 1
        self._ticks = 0
        bar = self.query_one("#med-bar", ProgressBar)
        bar.update(progress=0)
        status = self.query_one("#status-label", Label)
        status.update("\n  [tomato bold]You moved! Jamb lost focus. Restarting...[/]")
