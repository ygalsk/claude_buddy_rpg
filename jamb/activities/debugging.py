from __future__ import annotations

import random
from typing import TYPE_CHECKING, Callable

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Label, Static

from ..constants import BUG_HUNT_SNIPPETS

if TYPE_CHECKING:
    from ..app import JambApp


class BugHuntActivity(Screen):
    """Find the buggy line! Pick 1-5."""

    def __init__(self, on_done: Callable[[str, int, int], None], **kwargs) -> None:
        super().__init__(**kwargs)
        self._on_done = on_done
        self.snippet = random.choice(BUG_HUNT_SNIPPETS)
        self.answered = False
        self._ticks = 0
        self._max_ticks = 15
        self._timer_handle = None

    def compose(self) -> ComposeResult:
        with Vertical(classes="activity-box"):
            yield Label("  ═══ BUG HUNT ═══\n", classes="header")
            yield Label("  Find the buggy line! Press 1-5:\n", classes="dim")

            for i, line in enumerate(self.snippet["lines"], 1):
                yield Label(f"  {i}. {line}", classes="stat-label")

            yield Label(f"\n  Time: {self._max_ticks}s", id="timer-label", classes="warning mt1")
            yield Label("", id="result-label")
            yield Label("  [yellow bold]Press 1-5 to pick the buggy line[/]", id="hint-label")

        yield Footer()

    def on_mount(self) -> None:
        self._timer_handle = self.set_interval(1.0, self._tick)

    def _tick(self) -> None:
        if self.answered:
            if self._timer_handle:
                self._timer_handle.stop()
            return
        self._ticks += 1
        remaining = self._max_ticks - self._ticks
        if remaining <= 0:
            self._timeout()
            return
        style = "tomato bold" if remaining <= 5 else "yellow bold"
        timer = self.query_one("#timer-label", Label)
        timer.update(f"\n  [{style}]Time: {remaining}s[/]")

    def _timeout(self) -> None:
        self.answered = True
        if self._timer_handle:
            self._timer_handle.stop()
        timer = self.query_one("#timer-label", Label)
        timer.update("\n  [tomato bold]TIME'S UP![/]")
        result = self.query_one("#result-label", Label)
        result.update(
            f"\n  {self.snippet['explanation']}\n  \\[C] Continue  \\[B] Training  \\[other] Main"
        )
        self._on_done("debugging", 1, 5)

    def on_key(self, event) -> None:
        if self.answered:
            app: JambApp = self.app  # type: ignore[assignment]
            key = event.character or event.key
            if key in ("c", "C"):
                app.start_activity("debugging")
            elif key in ("b", "B"):
                app.show_training()
            else:
                app.show_main()
            return

        key = event.character or ""
        if key in "12345":
            self.answered = True
            if self._timer_handle:
                self._timer_handle.stop()
            pick = int(key) - 1
            correct = self.snippet["buggy"]

            result = self.query_one("#result-label", Label)
            timer = self.query_one("#timer-label", Label)
            timer.update("")

            if pick == correct:
                speed_bonus = max(0, (self._max_ticks - self._ticks)) // 3
                gain = 3 + min(speed_bonus, 2)
                xp = 10 + speed_bonus
                result.update(
                    f"\n  [lightgreen bold]CORRECT! +{gain} DEBUGGING[/]\n  {self.snippet['explanation']}\n  \\[C] Continue  \\[B] Training  \\[other] Main"
                )
            else:
                gain = 1
                xp = 5
                result.update(
                    f"\n  [tomato bold]WRONG! The bug was on line {correct + 1}.[/]\n  {self.snippet['explanation']}\n  +{gain} DEBUGGING\n  \\[C] Continue  \\[B] Training  \\[other] Main"
                )

            self._on_done("debugging", gain, xp)
