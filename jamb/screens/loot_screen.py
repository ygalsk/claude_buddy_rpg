"""Loot screen — shown when finding treasure or winning a battle."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Label

from ..constants import RARITY_COLORS

if TYPE_CHECKING:
    from ..app import JambApp


class LootScreen(Screen):
    """Display loot from treasure or battle."""

    def __init__(self, loot: dict, **kwargs) -> None:
        super().__init__(**kwargs)
        self._loot = loot  # {"item": dict, "gold": int} or {"items": [...], "gold": int, "xp": int}

    def compose(self) -> ComposeResult:
        loot = self._loot

        with Vertical(classes="care-overlay"):
            yield Label("  [bold #facc15]╔══ LOOT ══╗[/]", classes="header")

            # Gold
            gold = loot.get("gold", 0)
            if gold > 0:
                yield Label(f"  [#facc15 bold]+{gold} Gold[/]", classes="mt1")

            # XP
            xp = loot.get("xp", 0)
            if xp > 0:
                yield Label(f"  [#a78bfa bold]+{xp} XP[/]")

            # Items
            items = loot.get("items", [])
            if "item" in loot and loot["item"]:
                items = [loot["item"]]

            if items:
                for item in items:
                    color = RARITY_COLORS.get(item.get("rarity", ""), "white")
                    rarity = item.get("rarity", "").upper()
                    yield Label(f"  [{color} bold]{item.get('name', '?')}[/] [{color}]({rarity})[/]", classes="mt1")
                    yield Label(f"  [dim]{item.get('description', '')}[/]")

                yield Label("  [dim]Items added to inventory.[/]", classes="mt1")
            else:
                yield Label("  [dim]No items found.[/]", classes="mt1")

            yield Label("  [yellow bold]Press any key to continue[/]", classes="mt1")

        yield Footer()

    def on_key(self, event) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        app.show_dungeon()
