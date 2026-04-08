from __future__ import annotations

import random
from typing import TYPE_CHECKING, Callable

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Label

if TYPE_CHECKING:
    from ..app import JambApp


class ChoiceActivity(Screen):
    """Base class for pick-from-shuffled-options activities (chaos, snark, etc.)."""

    stat_name: str
    title: str
    header: str
    scenarios: list[dict]
    tiers: list[tuple[int, str, str]]  # (min_val, message_template, style)

    def __init__(self, on_done: Callable[[str, int, int], None], **kwargs) -> None:
        super().__init__(**kwargs)
        self._on_done = on_done
        self.scenario = random.choice(self.scenarios)
        self.answered = False
        self.options = list(self.scenario["options"])
        random.shuffle(self.options)

    def compose(self) -> ComposeResult:
        with Vertical(classes="activity-box"):
            yield Label(f"  ═══ {self.header} ═══\n", classes="header")
            yield Label(f"  [lightskyblue]{self.scenario['setup']}[/]\n", classes="mt1")

            for i, (text, _val) in enumerate(self.options, 1):
                yield Label(f"  \\[{i}] {text}", classes="stat-label")

            yield Label("  [yellow bold]Press 1-3 to choose[/]", id="hint-label", classes="mt1")
            yield Label("", id="result-label")

        yield Footer()

    def on_key(self, event) -> None:
        if self.answered:
            app: JambApp = self.app  # type: ignore[assignment]
            key = event.character or event.key
            if key in ("c", "C"):
                app.start_activity(self.stat_name)
            elif key in ("b", "B"):
                app.show_training()
            else:
                app.show_main()
            return

        key = event.character or ""
        if key in "123":
            self.answered = True
            idx = int(key) - 1
            if idx >= len(self.options):
                return

            text, val = self.options[idx]
            gain = val
            xp = 5 + val * 2

            # Map tier style names to Rich markup colors
            style_map = {
                "success": "lightgreen bold",
                "warning": "yellow bold",
                "error": "tomato bold",
                "dim": "dim",
            }

            msg = ""
            style = "dim"
            for min_val, tmpl, tier_style in self.tiers:
                if val >= min_val:
                    msg = tmpl.format(gain=gain, stat=self.stat_name.upper())
                    style = style_map.get(tier_style, tier_style)
                    break

            result = self.query_one("#result-label", Label)
            result.update(f"\n  [{style}]{msg}  (+{xp} XP)[/]\n  \\[C] Continue  \\[B] Training  \\[other] Main")
            self._on_done(self.stat_name, gain, xp)
