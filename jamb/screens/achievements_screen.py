"""Achievements screen — view earned and locked badges."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Label

from ..constants import ACHIEVEMENTS

if TYPE_CHECKING:
    from ..app import JambApp


CATEGORY_LABELS = {
    "training": "Training",
    "care": "Care",
    "social": "Social",
    "milestone": "Milestone",
    "secret": "Secret",
}

CATEGORY_COLORS = {
    "training": "#22c55e",
    "care": "#ef4444",
    "social": "#06b6d4",
    "milestone": "#a78bfa",
    "secret": "#facc15",
}


class AchievementsScreen(Screen):

    BINDINGS = [
        ("b", "back", "Back"),
        ("escape", "back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        app: JambApp = self.app  # type: ignore[assignment]
        state = app.state
        earned_ids = set(state.achievements)
        total_earned = len(earned_ids)
        total_available = len(ACHIEVEMENTS)

        # Group achievements by category
        by_category: dict[str, list[dict]] = {}
        for ach in ACHIEVEMENTS:
            cat = ach["category"]
            by_category.setdefault(cat, []).append(ach)

        with VerticalScroll(classes="screen-box"):
            yield Label("  [bold #d946ef]====  ACHIEVEMENTS  ====[/]\n", classes="header")
            yield Label(
                f"  [bold]{total_earned}[/] / [bold]{total_available}[/] unlocked",
                classes="dim",
            )

            for cat in ("training", "care", "social", "milestone", "secret"):
                achievements = by_category.get(cat, [])
                if not achievements:
                    continue
                color = CATEGORY_COLORS.get(cat, "white")
                label = CATEGORY_LABELS.get(cat, cat.title())
                yield Label(f"  [bold {color}]--- {label} ---[/]", classes="mt1")

                for ach in achievements:
                    if ach["id"] in earned_ids:
                        yield Label(
                            f"  [{color}]{ach['icon']}[/]  "
                            f"[bold {color}]{ach['name']}[/]  "
                            f"[dim]{ach['description']}[/]"
                        )
                    else:
                        if cat == "secret":
                            yield Label(
                                "  [dim]?  ???  (secret)[/]"
                            )
                        else:
                            yield Label(
                                f"  [dim]?  ???  ({label.lower()})[/]"
                            )

        yield Footer()

    def action_back(self) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        app.show_main()
