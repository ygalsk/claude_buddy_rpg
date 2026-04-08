from __future__ import annotations

import random
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Label

from ..constants import FEED_MESSAGES, PLAY_MESSAGES, REST_MESSAGES, render_bar
from .. import persistence

if TYPE_CHECKING:
    from ..app import JambApp

CARE_ACTIONS = {
    "feed": {
        "attr": "hunger",
        "amount": 25,
        "messages": FEED_MESSAGES,
        "title": "Feeding Time!",
        "label": "Hunger",
        "timestamp_attr": "last_fed",
    },
    "rest": {
        "attr": "energy",
        "amount": 30,
        "messages": REST_MESSAGES,
        "title": "Rest Time!",
        "label": "Energy",
        "timestamp_attr": "last_rested",
    },
    "play": {
        "attr": "happiness",
        "amount": 20,
        "messages": PLAY_MESSAGES,
        "title": "Play Time!",
        "label": "Happiness",
        "timestamp_attr": "last_played",
    },
}


class CareOverlay(Screen):
    """A popup overlay for care actions (feed/rest/play)."""

    BINDINGS = [
        ("escape", "continue", "Continue"),
    ]

    def __init__(self, action: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._action = action

    def compose(self) -> ComposeResult:
        app: JambApp = self.app  # type: ignore[assignment]
        state = app.state
        now = datetime.now(timezone.utc).isoformat()

        cfg = CARE_ACTIONS[self._action]
        current = getattr(state.care, cfg["attr"])
        amount = cfg["amount"]
        gain = min(amount, 100 - current)
        setattr(state.care, cfg["attr"], min(100, current + amount))
        setattr(state.care, cfg["timestamp_attr"], now)

        # Increment achievement counters
        counter_map = {"feed": "times_fed", "rest": "times_rested", "play": "times_played"}
        counter_key = counter_map.get(self._action)
        if counter_key:
            state.achievement_counters[counter_key] = (
                state.achievement_counters.get(counter_key, 0) + 1
            )

        msg = random.choice(cfg["messages"])
        new_val = getattr(state.care, cfg["attr"])
        title = cfg["title"]

        care_colors = {"Hunger": "#ef4444", "Energy": "#06b6d4", "Happiness": "#22c55e"}
        color = care_colors.get(cfg["label"], "white")

        before_bar = render_bar(current, 100, 10)
        after_bar = render_bar(new_val, 100, 10)

        state.compute_mood()

        # Advance daily challenge for care actions
        daily_done = state.advance_daily(self._action)
        if not daily_done:
            daily_done = state.advance_daily("full_care")
        if not daily_done:
            daily_done = state.advance_daily("mood_ecstatic")
        if daily_done:
            app.award_daily_challenge()

        persistence.save(state)

        with Vertical(classes="care-overlay"):
            yield Label(f"  [bold]{title}[/]", classes="header")
            yield Label(f"  [lightskyblue]{msg}[/]", classes="mt1")
            yield Label(f"  [{color} bold]{cfg['label']}[/]", classes="mt1")
            yield Label(f"  [dim]Before:[/] [{color}]{before_bar}[/] [dim]{current}%[/]")
            yield Label(f"  [bold]After:[/]  [{color}]{after_bar}[/] [bold]{new_val}%[/]")
            yield Label(f"  [#22c55e bold]+{gain}[/]")
            yield Label(f"  Mood: {state.mood_label()}", classes="dim mt1")
            yield Label("  [yellow bold]Press any key to continue[/]", classes="mt1")

        yield Footer()

    def on_key(self, event) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        app.show_main()
