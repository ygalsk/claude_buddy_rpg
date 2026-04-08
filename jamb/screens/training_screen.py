from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Label

from ..constants import STAT_COLORS
from ..widgets.menu import Menu

if TYPE_CHECKING:
    from ..app import JambApp


def _fatigue_dots(count: int) -> str:
    if count <= 2:
        return " [#22c55e]●●●[/]"
    if count <= 4:
        return " [#facc15]●●[/][dim]●[/]"
    if count <= 6:
        return " [#ef4444]●[/][dim]●●[/]"
    return " [#ef4444 bold]✕✕✕[/]"


def _training_item(key: str, stat: str, activity: str, value: int, fatigue_count: int) -> str:
    color = STAT_COLORS.get(stat, "white")
    return (
        f"\\[{key}] [{color} bold]{stat.upper():<10}[/] "
        f"[dim]{activity:<18}[/] ({value})"
        f"{_fatigue_dots(fatigue_count)}"
    )


class TrainingScreen(Screen):

    BINDINGS = [
        ("b", "back", "Back"),
        ("escape", "back", "Back"),
        ("d", "debug", "Debug"),
        ("p", "patience", "Patience"),
        ("c", "chaos", "Chaos"),
        ("w", "wisdom", "Wisdom"),
        ("s", "snark", "Snark"),
    ]

    def compose(self) -> ComposeResult:
        app: JambApp = self.app  # type: ignore[assignment]
        state = app.state
        stats = state.stats.as_dict()
        trains = app._session_trains

        mood_pct = int(state.mood_multiplier() * 100)
        mood_str = f"Mood bonus: {mood_pct}% ({state.mood_label()})"
        energy_str = f"Energy: {state.care.energy}%"

        items = [
            (_training_item("D", "debugging", "Bug Hunt", stats["debugging"], trains.get("debugging", 0)), lambda: app.start_activity("debugging")),
            (_training_item("P", "patience", "Meditation", stats["patience"], trains.get("patience", 0)), lambda: app.start_activity("patience")),
            (_training_item("C", "chaos", "Chaos Roulette", stats["chaos"], trains.get("chaos", 0)), lambda: app.start_activity("chaos")),
            (_training_item("W", "wisdom", "Riddle Challenge", stats["wisdom"], trains.get("wisdom", 0)), lambda: app.start_activity("wisdom")),
            (_training_item("S", "snark", "Comeback Battle", stats["snark"], trains.get("snark", 0)), lambda: app.start_activity("snark")),
        ]

        with Vertical(classes="screen-box"):
            yield Menu(items, title="TRAINING GROUND")
            yield Label(f"  [lightskyblue]{mood_str}    {energy_str}[/]", classes="mt1")

        yield Footer()

    def action_back(self) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        app.show_main()

    def action_debug(self) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        app.start_activity("debugging")

    def action_patience(self) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        app.start_activity("patience")

    def action_chaos(self) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        app.start_activity("chaos")

    def action_wisdom(self) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        app.start_activity("wisdom")

    def action_snark(self) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        app.start_activity("snark")
