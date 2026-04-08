from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Label

from ..widgets.stat_bar import StatBar

if TYPE_CHECKING:
    from ..app import JambApp


def _care_color(val: int) -> str:
    if val >= 60:
        return "#22c55e"
    if val >= 30:
        return "#facc15"
    return "#ef4444"


class StatusScreen(Screen):

    BINDINGS = [
        ("b", "back", "Back"),
        ("escape", "back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        app: JambApp = self.app  # type: ignore[assignment]
        state = app.state

        with VerticalScroll(classes="screen-box"):
            yield Label("  [bold #d946ef]╔══ DETAILED STATUS ══╗[/]\n", classes="header")
            yield Label(f"  [bold #d946ef]\\[{state.rarity}][/]  {state.species}", classes="dim")
            yield Label(f"  [yellow bold]{state.name}[/]  — \"{state.title}\"")
            yield Label(f"  Level {state.level}  |  XP: {state.xp}/{state.xp_to_next_level()}", classes="dim")
            yield Label("  [bold #a78bfa]┌── Stats ──────────────┐[/]", classes="mt1")

            cap = state.stat_cap()
            for name, value in state.stats.as_dict().items():
                yield StatBar(name.upper(), value, cap, f"bar-{name}", id=f"status-stat-{name}")

            yield Label("  [bold #06b6d4]┌── Care ───────────────┐[/]", classes="mt1")
            care = state.care
            yield Label(f"  [bold #ef4444]Hunger:[/]    [{_care_color(care.hunger)}]{care.hunger}%[/]")
            yield Label(f"  [bold #06b6d4]Energy:[/]    [{_care_color(care.energy)}]{care.energy}%[/]")
            yield Label(f"  [bold #22c55e]Happiness:[/] [{_care_color(care.happiness)}]{care.happiness}%[/]")
            yield Label(f"  Mood:      [bold]{state.mood_label()}[/]")
            yield Label("  [bold #94a3b8]┌── History ────────────┐[/]", classes="mt1")
            yield Label(f"  Total sessions:  {state.total_sessions}", classes="dim")
            yield Label(f"  Total trainings: {state.total_trainings}", classes="dim")
            yield Label(f"  Created: {state.created_at or 'unknown'}", classes="dim")
            yield Label("  [bold #facc15]┌── Personality ────────┐[/]", classes="mt1")
            yield Label(f"  [lightskyblue]\"{state.personality}\"[/]")

        yield Footer()

    def action_back(self) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        app.show_main()
