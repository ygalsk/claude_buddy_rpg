"""Inventory screen — view, equip, sell, and inspect items."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Label

from ..constants import RARITY_COLORS, TYPE_COLORS
from ..dungeon.items import ITEMS_BY_ID

if TYPE_CHECKING:
    from ..app import JambApp

SLOT_LABELS = {"weapon": "Weapon", "armor": "Armor", "accessory": "Accessory"}
SLOT_KEYS = list(SLOT_LABELS.keys())  # ["weapon", "armor", "accessory"]


def _item_detail_lines(item: dict) -> list[str]:
    """Build detailed info lines for any item."""
    lines: list[str] = []
    rarity = item.get("rarity", "common")
    color = RARITY_COLORS.get(rarity, "white")
    item_type = item.get("type", "")
    type_label = item_type.capitalize() if item_type else "?"

    lines.append(f"  [{color} bold]{item.get('name', '?')}[/]")
    lines.append(f"  [{color}]{rarity.upper()}[/]  |  {type_label}")

    # Stats line
    stats_parts: list[str] = []
    if item.get("attack"):
        stats_parts.append(f"ATK +{item['attack']}")
    if item.get("defense"):
        stats_parts.append(f"DEF +{item['defense']}")
    dmg_type = item.get("damage_type")
    if dmg_type:
        tc = TYPE_COLORS.get(dmg_type, "#888888")
        stats_parts.append(f"[{tc}]{dmg_type.upper()}-type[/]")
    if stats_parts:
        lines.append("  " + "  |  ".join(stats_parts))

    # Bonuses
    bonus_parts: list[str] = []
    for key, label in [
        ("debug_bonus", "debugging"), ("chaos_bonus", "chaos"),
        ("patience_bonus", "patience"), ("wisdom_bonus", "wisdom"),
        ("snark_bonus", "snark"), ("all_bonus", "all stats"),
        ("speed_bonus", "speed"), ("attack_bonus", "attack"),
        ("defense_bonus", "defense"),
    ]:
        val = item.get(key)
        if val:
            bonus_parts.append(f"+{val} {label}")
    if item.get("heal_per_turn"):
        bonus_parts.append(f"+{item['heal_per_turn']} HP/turn")
    if bonus_parts:
        lines.append("  " + "  ".join(bonus_parts))

    # Consumable effects
    if item.get("heal"):
        lines.append(f"  Heals {item['heal']} HP")
    if item.get("full_heal"):
        lines.append("  Full HP restore")
    if item.get("attack_buff"):
        turns = item.get("turns", 3)
        lines.append(f"  ATK +{item['attack_buff']} for {turns} turns")
    if item.get("save_hp"):
        lines.append("  Saves current HP state")
    if item.get("revive"):
        lines.append("  Revives on defeat")

    # Description
    desc = item.get("description", "")
    if desc:
        lines.append(f"  [dim italic]\"{desc}\"[/]")

    # Sell price
    sell_price = item.get("value", 0) // 2
    if sell_price > 0:
        lines.append(f"  [dim]Sell: {sell_price}g[/]")

    return lines


class InventoryScreen(Screen):

    BINDINGS = [
        ("b", "back", "Back"),
        ("escape", "back", "Back"),
        ("1", "select_1", ""),
        ("2", "select_2", ""),
        ("3", "select_3", ""),
        ("4", "select_4", ""),
        ("5", "select_5", ""),
        ("6", "select_6", ""),
        ("7", "select_7", ""),
        ("8", "select_8", ""),
        ("9", "select_9", ""),
        ("0", "select_10", ""),
        ("e", "equip_selected", "Equip"),
        ("s", "sell_selected", "Sell"),
        ("w", "focus_weapon", ""),
        ("a", "focus_armor", ""),
        ("c", "focus_accessory", ""),
        ("u", "unequip_focused", "Unequip"),
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._selected: int | None = None
        self._equip_focus: str | None = None  # "weapon", "armor", "accessory"
        self._page: int = 0
        self._items_per_page = 10

    def compose(self) -> ComposeResult:
        with VerticalScroll(classes="screen-box"):
            yield Label("", id="inv-header")
            yield Label("", id="inv-equipped")
            yield Label("", id="inv-backpack")
            yield Label("", id="inv-selected-info")
            yield Label("", id="inv-actions")
        yield Footer()

    def on_mount(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        state = app.state

        # Header
        slots_used = state.inventory_slot_count()
        self.query_one("#inv-header", Label).update(
            f"  [bold #d946ef]╔══ INVENTORY ══╗[/]\n"
            f"  [#facc15 bold]Gold: {state.gold}[/]  "
            f"[dim]Backpack: {slots_used}/{state.inventory_capacity}[/]"
        )

        # Equipment slots
        focus = self._equip_focus
        is_equip_focused = focus is not None
        border_color = "#d946ef" if is_equip_focused else "#a78bfa"
        equip_lines = [f"  [bold {border_color}]┌── Equipped ───────────┐[/]"]
        for slot, label in SLOT_LABELS.items():
            pointer = ">> " if focus == slot else "   "
            item_id = state.equipment.get(slot)
            if item_id:
                item = ITEMS_BY_ID.get(item_id, {})
                color = RARITY_COLORS.get(item.get("rarity", ""), "white")
                stat_text = ""
                if item.get("attack"):
                    stat_text += f" ATK+{item['attack']}"
                if item.get("defense"):
                    stat_text += f" DEF+{item['defense']}"
                dmg_type = item.get("damage_type")
                type_tag = ""
                if dmg_type:
                    tc = TYPE_COLORS.get(dmg_type, "#888888")
                    type_tag = f" [{tc}][{dmg_type.upper()}][/]"
                equip_lines.append(
                    f"{pointer}{label}: [{color} bold]{item.get('name', item_id)}[/]"
                    f"[dim]{stat_text}[/]{type_tag}"
                )
            else:
                equip_lines.append(f"{pointer}{label}: [dim](empty)[/]")
        hint = "  [dim][W]eapon  [A]rmor  a[C]cessory[/]"
        equip_lines.append(hint)
        self.query_one("#inv-equipped", Label).update("\n".join(equip_lines))

        # Backpack items with pagination
        bp_lines = ["  [bold #06b6d4]┌── Backpack ───────────┐[/]"]
        if not state.inventory:
            bp_lines.append("  [dim]Empty. Find loot in the dungeon![/]")
        else:
            start = self._page * self._items_per_page
            end = min(start + self._items_per_page, len(state.inventory))
            for i in range(start, end):
                item = state.inventory[i]
                display_num = (i - start) + 1
                if display_num == 10:
                    display_key = "0"
                else:
                    display_key = str(display_num)

                color = RARITY_COLORS.get(item.get("rarity", ""), "white")
                item_type = item.get("type", "")
                type_tag = f"[dim]({item_type})[/]"

                stat_text = ""
                if item.get("attack"):
                    stat_text += f" ATK+{item['attack']}"
                if item.get("defense"):
                    stat_text += f" DEF+{item['defense']}"
                if item.get("heal"):
                    stat_text += f" HP+{item['heal']}"
                if item.get("full_heal"):
                    stat_text += " FULL HEAL"

                # Stack count for consumables
                count = item.get("count", 1) if item.get("type") == "consumable" else 1
                count_text = f" x{count}" if count > 1 else ""

                # Damage type for weapons
                dmg_type = item.get("damage_type")
                dmg_tag = ""
                if dmg_type:
                    tc = TYPE_COLORS.get(dmg_type, "#888888")
                    dmg_tag = f" [{tc}][{dmg_type.upper()}][/]"

                selected = ">> " if self._selected == i else "   "
                bp_lines.append(
                    f"{selected}[bold yellow]{display_key}[/] [{color}]{item.get('name', '?')}{count_text}[/] "
                    f"{type_tag}[dim]{stat_text}[/]{dmg_tag}"
                )

            total_pages = (len(state.inventory) + self._items_per_page - 1) // self._items_per_page
            if total_pages > 1:
                bp_lines.append(
                    f"  [dim]Page {self._page + 1}/{total_pages} "
                    f"(← prev / → next)[/]"
                )

        self.query_one("#inv-backpack", Label).update("\n".join(bp_lines))

        # Detail panel — equipped item or backpack item
        if self._equip_focus is not None:
            item_id = state.equipment.get(self._equip_focus)
            if item_id:
                item = ITEMS_BY_ID.get(item_id, {})
                detail = _item_detail_lines(item)
                self.query_one("#inv-selected-info", Label).update(
                    "\n".join(detail)
                )
                actions = ["[bold yellow]U[/]nequip"]
                sell_price = item.get("value", 0) // 2
                if sell_price > 0:
                    actions.append(f"[bold yellow]S[/]ell ({sell_price}g)")
                self.query_one("#inv-actions", Label).update(
                    "  " + "  ".join(actions)
                )
            else:
                self.query_one("#inv-selected-info", Label).update(
                    f"\n  [dim]{SLOT_LABELS[self._equip_focus]} slot is empty.[/]"
                )
                self.query_one("#inv-actions", Label).update("")
        elif self._selected is not None and 0 <= self._selected < len(state.inventory):
            item = state.inventory[self._selected]
            detail = _item_detail_lines(item)
            self.query_one("#inv-selected-info", Label).update(
                "\n".join(detail)
            )
            actions = []
            if item.get("type") in ("weapon", "armor", "accessory"):
                actions.append("[bold yellow]E[/]quip")
            sell_price = item.get("value", 0) // 2
            if sell_price > 0:
                actions.append(f"[bold yellow]S[/]ell ({sell_price}g)")
            self.query_one("#inv-actions", Label).update(
                "  " + "  ".join(actions)
            )
        else:
            self.query_one("#inv-selected-info", Label).update(
                "\n  [dim]Press 1-0 to select backpack items, W/A/C to inspect equipment[/]"
            )
            self.query_one("#inv-actions", Label).update("")

    # ── Equipment focus ──────────────────────────────────────────────

    def _focus_slot(self, slot: str) -> None:
        self._selected = None
        if self._equip_focus == slot:
            self._equip_focus = None  # toggle off
        else:
            self._equip_focus = slot
        self._refresh()

    def action_focus_weapon(self) -> None:
        self._focus_slot("weapon")

    def action_focus_armor(self) -> None:
        self._focus_slot("armor")

    def action_focus_accessory(self) -> None:
        self._focus_slot("accessory")

    def action_unequip_focused(self) -> None:
        if self._equip_focus is None:
            return
        app: JambApp = self.app  # type: ignore[assignment]
        state = app.state
        item_id = state.equipment.get(self._equip_focus)
        if not item_id:
            app.notify("Nothing equipped in that slot!", severity="warning", timeout=2)
            return
        item = ITEMS_BY_ID.get(item_id)
        if not item:
            return
        if state.inventory_full():
            app.notify("Backpack is full!", severity="warning", timeout=2)
            return
        state.equipment[self._equip_focus] = None
        state.inventory_add(dict(item))
        app.notify(f"Unequipped {item.get('name', '?')}", timeout=2)
        self._equip_focus = None
        from .. import persistence
        persistence.save(state)
        self._refresh()

    # ── Backpack selection ───────────────────────────────────────────

    def _select(self, num: int) -> None:
        """Select an item by display number (1-10, where 10 is key '0')."""
        app: JambApp = self.app  # type: ignore[assignment]
        self._equip_focus = None  # clear equipment focus
        start = self._page * self._items_per_page
        idx = start + num - 1
        if idx < len(app.state.inventory):
            if self._selected == idx:
                # Double-press = equip
                self._equip_item(idx)
                return
            self._selected = idx
        self._refresh()

    def _equip_item(self, idx: int) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        state = app.state

        if idx >= len(state.inventory):
            return

        item = state.inventory[idx]
        item_type = item.get("type", "")

        if item_type in ("weapon", "armor", "accessory"):
            old_id = state.equipment.get(item_type)
            state.equipment[item_type] = item["id"]
            state.inventory.pop(idx)
            if old_id:
                old_item = ITEMS_BY_ID.get(old_id)
                if old_item:
                    state.inventory_add(dict(old_item))
            app.notify(f"Equipped {item.get('name', '?')}!", timeout=2)
        elif item_type == "consumable":
            app.notify("Consumables can only be used in battle!", severity="warning", timeout=2)
            return

        self._selected = None
        from .. import persistence
        persistence.save(state)
        self._refresh()

    def action_equip_selected(self) -> None:
        if self._selected is not None:
            self._equip_item(self._selected)

    def action_sell_selected(self) -> None:
        # Sell from equipment slot
        if self._equip_focus is not None:
            self._sell_equipped()
            return
        # Sell from backpack
        if self._selected is None:
            return
        app: JambApp = self.app  # type: ignore[assignment]
        state = app.state
        if self._selected >= len(state.inventory):
            return

        item = state.inventory[self._selected]
        name = item.get("name", "?")

        gold_earned = state.sell_item(self._selected)
        if gold_earned > 0:
            app.notify(f"Sold {name} for {gold_earned}g!", timeout=2)
        else:
            app.notify(f"Can't sell {name}!", severity="warning", timeout=2)

        self._selected = None
        from .. import persistence
        persistence.save(state)
        self._refresh()

    def _sell_equipped(self) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        state = app.state
        item_id = state.equipment.get(self._equip_focus)
        if not item_id:
            return
        item = ITEMS_BY_ID.get(item_id, {})
        sell_price = item.get("value", 0) // 2
        if sell_price <= 0:
            app.notify("Can't sell this item!", severity="warning", timeout=2)
            return
        state.equipment[self._equip_focus] = None
        state.gold += sell_price
        app.notify(f"Sold {item.get('name', '?')} for {sell_price}g!", timeout=2)
        self._equip_focus = None
        from .. import persistence
        persistence.save(state)
        self._refresh()

    def on_key(self, event) -> None:
        if event.key == "left" and self._page > 0:
            self._page -= 1
            self._selected = None
            self._refresh()
        elif event.key == "right":
            app: JambApp = self.app  # type: ignore[assignment]
            total_pages = (len(app.state.inventory) + self._items_per_page - 1) // self._items_per_page
            if self._page < total_pages - 1:
                self._page += 1
                self._selected = None
                self._refresh()

    def action_select_1(self) -> None:
        self._select(1)

    def action_select_2(self) -> None:
        self._select(2)

    def action_select_3(self) -> None:
        self._select(3)

    def action_select_4(self) -> None:
        self._select(4)

    def action_select_5(self) -> None:
        self._select(5)

    def action_select_6(self) -> None:
        self._select(6)

    def action_select_7(self) -> None:
        self._select(7)

    def action_select_8(self) -> None:
        self._select(8)

    def action_select_9(self) -> None:
        self._select(9)

    def action_select_10(self) -> None:
        self._select(10)

    def action_back(self) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        if app.dungeon_run:
            app.show_dungeon()
        else:
            app.show_main()
