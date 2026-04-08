"""Dungeon crawler map screen — explore the Code Dungeon."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Label

from ..dungeon.engine import DungeonRun
from ..dungeon.generator import BOSS, EMPTY, ENEMY, ENTRANCE, REST, STAIRS, TRAP, TREASURE

if TYPE_CHECKING:
    from ..app import JambApp


class DungeonScreen(Screen):
    """Main dungeon exploration screen with map and movement."""

    BINDINGS = [
        ("w", "move_up", "Up"),
        ("up", "move_up", "Up"),
        ("s", "move_down", "Down"),
        ("down", "move_down", "Down"),
        ("a", "move_left", "Left"),
        ("left", "move_left", "Left"),
        ("d", "move_right", "Right"),
        ("right", "move_right", "Right"),
        ("i", "inventory", "Inventory"),
        ("escape", "flee_dungeon", "Flee"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(classes="screen-box"):
            yield Label("  [bold #d946ef]╔══ CODE DUNGEON ══╗[/]", classes="header")
            yield Label("", id="floor-info")
            yield Label("", id="dungeon-map", classes="mt1")
            yield Label("", id="room-desc", classes="mt1")
            yield Label("", id="dungeon-stats", classes="mt1")

        yield Footer()

    def on_mount(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        run = app.dungeon_run
        if not run:
            return

        floor = run.floor

        # Floor info
        self.query_one("#floor-info", Label).update(
            f"  [bold]Floor {floor.number}[/]  │  "
            f"[#ef4444]HP: {run.hp}/{run.max_hp}[/]  │  "
            f"[#facc15]Gold: {run.gold_earned}[/]  │  "
            f"[#a78bfa]XP: {run.xp_earned}[/]"
        )

        # Map
        self.query_one("#dungeon-map", Label).update(floor.render_map())

        # Room description
        room = floor.current_room()
        desc = room.description or "An empty room."
        room_type_label = {
            ENEMY: "[#ef4444 bold]ENEMY[/]",
            BOSS: "[#ef4444 bold]BOSS[/]",
            TREASURE: "[#facc15 bold]TREASURE[/]",
            REST: "[#06b6d4 bold]REST POINT[/]",
            TRAP: "[#a78bfa bold]TRAP[/]",
            STAIRS: "[#d946ef bold]STAIRS DOWN[/]",
        }.get(room.room_type if not room.cleared else EMPTY, "")

        self.query_one("#room-desc", Label).update(
            f"  {room_type_label} {desc}" if room_type_label else f"  {desc}"
        )

        # Legend
        self.query_one("#dungeon-stats", Label).update(
            "  [#22c55e]@[/]=You  [#ef4444]![/]=Enemy  [#ef4444]B[/]=Boss  "
            "[#facc15]?[/]=Loot  [#06b6d4]+[/]=Rest  [#a78bfa]^[/]=Trap  "
            "[#d946ef]>[/]=Stairs  [dim]░[/]=Unknown"
        )

    def _handle_room(self) -> None:
        """Handle entering a new room."""
        app: JambApp = self.app  # type: ignore[assignment]
        run = app.dungeon_run
        if not run:
            return

        room = run.floor.current_room()

        if room.room_type in (ENEMY, BOSS) and not room.cleared:
            app.start_combat(room.enemy)
        elif room.room_type == TREASURE and not room.cleared:
            room.cleared = True
            loot = run.generate_treasure()
            app.show_loot(loot)
        elif room.room_type == REST and not room.cleared:
            room.cleared = True
            healed = run.rest()
            app.notify(f"Rested! Healed {healed} HP.", title="Rest Point", timeout=3)
            self._refresh()
        elif room.room_type == TRAP and not room.cleared:
            room.cleared = True
            damage, msg = run.apply_trap(app.state.stats.as_dict())
            app.notify(msg, title="Trap!", severity="warning", timeout=3)
            if not run.alive:
                app.dungeon_death()
            else:
                self._refresh()
        elif room.room_type == STAIRS:
            run.next_floor()
            app.notify(
                f"Descending to Floor {run.floor.number}...",
                title="Deeper!",
                timeout=2,
            )
            self._refresh()
        else:
            self._refresh()

    def _move(self, dx: int, dy: int) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        run = app.dungeon_run
        if not run:
            return

        room = run.floor.move_player(dx, dy)
        if room:
            self._handle_room()
        else:
            self._refresh()

    def action_move_up(self) -> None:
        self._move(0, -1)

    def action_move_down(self) -> None:
        self._move(0, 1)

    def action_move_left(self) -> None:
        self._move(-1, 0)

    def action_move_right(self) -> None:
        self._move(1, 0)

    def action_inventory(self) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        app.show_inventory()

    def action_flee_dungeon(self) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        app.end_dungeon(fled=True)
