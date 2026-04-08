"""Turn-based battle screen for dungeon combat."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Label

from ..constants import TYPE_COLORS, render_bar
from ..dungeon.engine import CombatState
from ..dungeon.items import ITEMS_BY_ID
from ..dungeon.types import get_effectiveness, effectiveness_label

if TYPE_CHECKING:
    from ..app import JambApp


class BattleScreen(Screen):
    """Turn-based RPG combat."""

    BINDINGS = [
        ("a", "attack", "Attack"),
        ("d", "defend", "Defend"),
        ("s", "special", "Special"),
        ("i", "use_item", "Item"),
        ("w", "swap_weapon", "Swap"),
        ("f", "flee", "Flee"),
    ]

    def __init__(self, combat: CombatState, **kwargs) -> None:
        super().__init__(**kwargs)
        self._combat = combat
        self._awaiting_continue = False
        self._swap_selecting = False
        self._swap_weapons: list[dict] = []  # weapons available to swap to
        self._item_selecting = False
        self._item_list: list[tuple[int, dict]] = []  # (inventory_index, item)

    def compose(self) -> ComposeResult:
        with Vertical(id="battle-box"):
            yield Label("  [bold #ef4444]╔══ BATTLE ══╗[/]", classes="header")

            # Enemy display
            yield Label("", id="enemy-art", classes="mt1")
            yield Label("", id="enemy-info")

            # Player info
            yield Label("", id="player-info", classes="mt1")

            # Battle log
            yield Label("", id="battle-log", classes="mt1")

            # Actions
            yield Label("", id="action-prompt", classes="mt1")

        yield Footer()

    def on_mount(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        c = self._combat

        # Enemy display
        art = c.enemy.get("art", "  ???")
        self.query_one("#enemy-art", Label).update(f"[#ef4444]{art}[/]")

        enemy_hp_bar = render_bar(c.enemy_hp, c.enemy_max_hp)
        enemy_type = c.enemy.get("type", "???")
        type_color = TYPE_COLORS.get(enemy_type, "#888888")
        self.query_one("#enemy-info", Label).update(
            f"  [bold #ef4444]{c.enemy['name']}[/]  "
            f"[{type_color}][{enemy_type.upper()}][/]  "
            f"[#ef4444]{enemy_hp_bar}[/] {c.enemy_hp}/{c.enemy_max_hp} HP  "
            f"ATK:{c.enemy_attack} DEF:{c.enemy_defense}"
        )

        # Player info
        player_hp_bar = render_bar(c.player_hp, c.player_max_hp)
        buffs = ""
        if c.attack_buff > 0:
            buffs += f" [#facc15]ATK+{c.attack_buff}({c.buff_turns}t)[/]"
        if c.analyzed:
            buffs += " [#a78bfa]ANALYZED(2x)[/]"

        weapon_info = ""
        if c.weapon_type:
            wt_color = TYPE_COLORS.get(c.weapon_type, "#888888")
            weapon_name = ""
            weapon_data = ITEMS_BY_ID.get(c.equipment.get("weapon", ""))
            if weapon_data:
                weapon_name = weapon_data["name"] + " "
            weapon_info = f"  [{wt_color}]{weapon_name}[{c.weapon_type.upper()}][/]"

        self.query_one("#player-info", Label).update(
            f"  [bold #22c55e]Jamb[/]  "
            f"[#22c55e]{player_hp_bar}[/] {c.player_hp}/{c.player_max_hp} HP  "
            f"ATK:{c.player_attack + c.attack_buff} DEF:{c.player_defense} SPD:{c.player_speed}{buffs}{weapon_info}"
        )

        # Battle log (last 3 entries)
        log_lines = c.log[-3:] if c.log else ["Battle begins!"]
        log_text = "\n".join(f"  [dim]> {line}[/]" for line in log_lines)
        self.query_one("#battle-log", Label).update(log_text)

        # Action prompt
        if self._awaiting_continue:
            if c.victory:
                self.query_one("#action-prompt", Label).update(
                    "  [#22c55e bold]VICTORY![/] Press any key to continue."
                )
            else:
                self.query_one("#action-prompt", Label).update(
                    "  [#ef4444 bold]DEFEATED![/] Press any key to continue."
                )
        elif self._item_selecting:
            lines = ["  [bold]Use item:[/] (ESC to cancel)"]
            for i, (_, item) in enumerate(self._item_list):
                count = item.get("count", 1)
                count_text = f" x{count}" if count > 1 else ""
                effect = ""
                if item.get("heal"):
                    effect = f"HP+{item['heal']}"
                elif item.get("full_heal"):
                    effect = "FULL HEAL"
                elif item.get("attack_buff"):
                    effect = f"ATK+{item['attack_buff']} {item.get('turns', 3)}t"
                elif item.get("save_hp"):
                    effect = "SAVE STATE"
                elif item.get("revive"):
                    effect = "REVIVE"
                lines.append(
                    f"  [bold yellow]{i + 1}[/] {item['name']}{count_text} "
                    f"[dim]({effect})[/]"
                )
            self.query_one("#action-prompt", Label).update("\n".join(lines))
        elif self._swap_selecting:
            lines = ["  [bold]Swap weapon:[/] (ESC to cancel)"]
            for i, w in enumerate(self._swap_weapons):
                dt = w.get("damage_type", "???")
                color = TYPE_COLORS.get(dt, "#888888")
                lines.append(
                    f"  [bold yellow]{i + 1}[/] {w['name']} "
                    f"(ATK:{w.get('attack', 0)}) [{color}][{dt.upper()}][/]"
                )
            self.query_one("#action-prompt", Label).update("\n".join(lines))
        else:
            app: JambApp = self.app  # type: ignore[assignment]
            highest = app.state.stats.highest()
            special_names = {
                "debugging": "Debug", "patience": "Meditate",
                "chaos": "Chaos Strike", "wisdom": "Analyze", "snark": "Roast",
            }
            special_name = special_names.get(highest, "Special")
            self.query_one("#action-prompt", Label).update(
                f"  [bold yellow]A[/]ttack  [bold yellow]D[/]efend  "
                f"[bold yellow]S[/]pecial({special_name})  [bold yellow]I[/]tem  "
                f"[bold yellow]W[/]eapon  [bold yellow]F[/]lee"
            )

    def _do_enemy_turn(self) -> None:
        c = self._combat
        if c.finished:
            return

        # Enemy special first
        c.apply_enemy_special()
        if not c.finished:
            c.enemy_turn()

        c.end_of_turn()

        if c.finished:
            self._awaiting_continue = True

        self._refresh()

    def _end_battle(self) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        c = self._combat
        if c.victory:
            xp, gold, loot = c.calculate_rewards()
            app.combat_victory(xp, gold, loot)
        else:
            app.dungeon_death()

    def on_key(self, event) -> None:
        if self._awaiting_continue:
            self._end_battle()
            return

        if self._item_selecting:
            if event.key == "escape":
                self._item_selecting = False
                self._refresh()
                return
            if event.character and event.character.isdigit():
                idx = int(event.character) - 1
                if 0 <= idx < len(self._item_list):
                    inv_idx, item = self._item_list[idx]
                    app: JambApp = self.app  # type: ignore[assignment]
                    self._combat.player_use_item(item)
                    app.state.inventory_remove(inv_idx, 1)
                    self._item_selecting = False
                    self._do_enemy_turn()
            return

        if self._swap_selecting:
            if event.key == "escape":
                self._swap_selecting = False
                self._refresh()
                return
            # Number keys to pick a weapon
            if event.character and event.character.isdigit():
                idx = int(event.character) - 1
                if 0 <= idx < len(self._swap_weapons):
                    weapon = self._swap_weapons[idx]
                    app: JambApp = self.app  # type: ignore[assignment]
                    # Swap in game state: put old weapon back, equip new one
                    old_weapon_id = app.state.equipment.get("weapon")
                    app.state.equipment["weapon"] = weapon["id"]
                    # Move old weapon back to inventory, remove new from inventory
                    for i, item in enumerate(app.state.inventory):
                        if item.get("id") == weapon["id"]:
                            app.state.inventory.pop(i)
                            break
                    if old_weapon_id:
                        old_weapon = ITEMS_BY_ID.get(old_weapon_id)
                        if old_weapon:
                            app.state.inventory_add(dict(old_weapon))
                    # Update combat state
                    self._combat.swap_weapon(weapon["id"])
                    self._swap_selecting = False
                    self._do_enemy_turn()
            return

    def action_attack(self) -> None:
        if self._awaiting_continue or self._item_selecting:
            return
        c = self._combat
        c.player_turn_attack()
        if not c.finished:
            self._do_enemy_turn()
        else:
            self._awaiting_continue = True
            self._refresh()

    def action_defend(self) -> None:
        if self._awaiting_continue or self._item_selecting:
            return
        c = self._combat
        c.player_turn_defend()
        self._do_enemy_turn()

    def action_special(self) -> None:
        if self._awaiting_continue or self._item_selecting:
            return
        app: JambApp = self.app  # type: ignore[assignment]
        c = self._combat
        highest = app.state.stats.highest()
        c.player_turn_special(highest)
        if not c.finished:
            self._do_enemy_turn()
        else:
            self._awaiting_continue = True
            self._refresh()

    def action_use_item(self) -> None:
        if self._awaiting_continue or self._swap_selecting or self._item_selecting:
            return
        app: JambApp = self.app  # type: ignore[assignment]
        consumables = [
            (i, item) for i, item in enumerate(app.state.inventory)
            if item.get("type") == "consumable"
        ]
        if not consumables:
            self._combat.log.append("No consumables in inventory!")
            self._refresh()
            return
        self._item_list = consumables[:9]  # max 9 shown
        self._item_selecting = True
        self._refresh()

    def action_swap_weapon(self) -> None:
        if self._awaiting_continue or self._swap_selecting or self._item_selecting:
            return
        app: JambApp = self.app  # type: ignore[assignment]
        # Find weapons in inventory (not currently equipped)
        weapons = [
            item for item in app.state.inventory
            if item.get("type") == "weapon"
        ]
        if not weapons:
            self._combat.log.append("No other weapons in inventory!")
            self._refresh()
            return
        self._swap_weapons = weapons[:9]  # max 9 shown
        self._swap_selecting = True
        self._refresh()

    def action_flee(self) -> None:
        if self._awaiting_continue or self._item_selecting:
            return
        import random
        c = self._combat
        # Speed check
        flee_chance = 40 + c.player_speed * 2
        if random.randint(1, 100) <= flee_chance:
            c.log.append("Jamb fled successfully!")
            c.finished = True
            self._awaiting_continue = True
            self._refresh()
        else:
            c.log.append("Failed to flee!")
            self._do_enemy_turn()
