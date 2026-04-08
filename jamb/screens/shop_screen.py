"""Shop screen — daily rotating stock with level-gated tiers."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Label

from .. import persistence
from ..constants import RARITY_COLORS
from ..shop import generate_daily_shop, max_tier_for_level

if TYPE_CHECKING:
    from ..app import JambApp


class ShopScreen(Screen):

    BINDINGS = [
        ("b", "back", "Back"),
        ("escape", "back", "Back"),
        ("1", "buy_1", ""), ("2", "buy_2", ""), ("3", "buy_3", ""),
        ("4", "buy_4", ""), ("5", "buy_5", ""), ("6", "buy_6", ""),
        ("7", "buy_7", ""), ("8", "buy_8", ""), ("9", "buy_9", ""),
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._shop_items: list[dict] = []

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="shop-box"):
            yield Label("", id="shop-header")
            yield Label("", id="shop-items")
            yield Label("", id="shop-footer")
        yield Footer()

    def on_mount(self) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        self._shop_items = generate_daily_shop(app.state.level)
        self._refresh()

    def _refresh(self) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        state = app.state

        tier = max_tier_for_level(state.level)
        tier_labels = {1: "Basic", 2: "Advanced", 3: "Elite"}
        today = datetime.now().strftime("%b %d")

        self.query_one("#shop-header", Label).update(
            f"  [bold #facc15]╔══ SHOP ══╗[/]\n"
            f"  [#facc15 bold]Gold: {state.gold}[/]  "
            f"[dim]Tier: {tier_labels.get(tier, '?')} (Lv.{state.level})[/]  "
            f"[dim]Refreshes daily — {today}[/]"
        )

        lines = []
        for i, item in enumerate(self._shop_items):
            if i >= 9:
                break
            num = i + 1
            color = RARITY_COLORS.get(item.get("rarity", ""), "white")
            price = item["price"]
            affordable = "[#22c55e]" if state.gold >= price else "[#ef4444]"

            type_tag = ""
            if item["type"] == "care":
                stat = item.get("care_stat", "")
                amt = item.get("care_amount", 0)
                type_tag = f"[dim]+{amt} {stat.title()}[/]"
            elif item["type"] == "stat_boost":
                stat = item.get("boost_stat", "")
                amt = item.get("boost_amount", 0)
                type_tag = f"[dim]+{amt} {stat.upper()} permanent[/]"
            elif item["type"] == "xp_boost":
                type_tag = f"[dim]+{item.get('xp_amount', 0)} XP[/]"
            elif item["type"] == "consumable":
                if item.get("heal"):
                    type_tag = f"[dim]HP+{item['heal']}[/]"
                elif item.get("full_heal"):
                    type_tag = "[dim]FULL HEAL[/]"
                elif item.get("attack_buff"):
                    type_tag = f"[dim]ATK+{item['attack_buff']} {item.get('turns', 3)}t[/]"
                elif item.get("revive"):
                    type_tag = "[dim]REVIVE[/]"
            elif item["type"] == "backpack":
                type_tag = f"[dim]Expand to {item.get('capacity_to', '?')} slots[/]"
                # Hide if already have this capacity
                if state.inventory_capacity >= item.get("capacity_to", 0):
                    type_tag = "[dim](Already owned)[/]"

            lines.append(
                f"  [bold yellow]{num}[/] [{color}]{item['name']}[/]  "
                f"{affordable}{price}g[/]  {type_tag}"
            )
            lines.append(f"    [dim]{item['description']}[/]")

        self.query_one("#shop-items", Label).update("\n".join(lines))
        self.query_one("#shop-footer", Label).update(
            "  [dim]Press 1-9 to buy.[/]"
        )

    def _buy(self, num: int) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        state = app.state

        idx = num - 1
        if idx >= len(self._shop_items):
            return

        item = self._shop_items[idx]
        price = item["price"]

        if state.gold < price:
            app.notify("Not enough gold!", severity="warning", timeout=2)
            return

        if item["type"] == "backpack":
            target = item.get("capacity_to", 0)
            if state.inventory_capacity >= target:
                app.notify("You already have this upgrade!", severity="warning", timeout=2)
                return
            state.gold -= price
            state.inventory_capacity = target
            app.notify(f"Backpack upgraded to {target} slots!", timeout=3)
        elif item["type"] == "care":
            state.gold -= price
            if item.get("care_stat") == "all":
                amt = item.get("care_amount", 0)
                state.care.hunger = min(100, state.care.hunger + amt)
                state.care.energy = min(100, state.care.energy + amt)
                state.care.happiness = min(100, state.care.happiness + amt)
            else:
                attr = item.get("care_stat", "")
                amt = item.get("care_amount", 0)
                current = getattr(state.care, attr, 0)
                setattr(state.care, attr, min(100, current + amt))
            state.compute_mood()
            app.notify(f"Used {item['name']}!", timeout=2)
        elif item["type"] == "stat_boost":
            state.gold -= price
            stat = item.get("boost_stat", "")
            amt = item.get("boost_amount", 0)
            state.stats.add(stat, amt, state.stat_cap())
            app.notify(f"+{amt} {stat.upper()} permanently!", timeout=3)
        elif item["type"] == "xp_boost":
            state.gold -= price
            xp = item.get("xp_amount", 0)
            state.add_xp(xp)
            app.notify(f"+{xp} XP!", timeout=2)
        elif item["type"] == "consumable":
            if not state.inventory_add(dict(item)):
                app.notify("Inventory full!", severity="warning", timeout=2)
                return
            state.gold -= price
            app.notify(f"{item['name']} added to inventory!", timeout=2)

        persistence.save(state)
        self._refresh()

    def action_buy_1(self) -> None: self._buy(1)
    def action_buy_2(self) -> None: self._buy(2)
    def action_buy_3(self) -> None: self._buy(3)
    def action_buy_4(self) -> None: self._buy(4)
    def action_buy_5(self) -> None: self._buy(5)
    def action_buy_6(self) -> None: self._buy(6)
    def action_buy_7(self) -> None: self._buy(7)
    def action_buy_8(self) -> None: self._buy(8)
    def action_buy_9(self) -> None: self._buy(9)

    def action_back(self) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        app.show_main()
