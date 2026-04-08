from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Label, ProgressBar

from ..constants import mood_style, render_bar
from ..widgets.ascii_art import SnailArt
from ..widgets.speech_bubble import SpeechBubble
from ..widgets.stat_bar import StatBar

if TYPE_CHECKING:
    from ..app import JambApp


class MainScreen(Screen):

    BINDINGS = [
        ("t", "train", "Train"),
        ("d", "dungeon", "Dungeon"),
        ("c", "chat", "Chat"),
        ("f", "feed", "Feed"),
        ("r", "rest", "Rest"),
        ("p", "play", "Play"),
        ("s", "status", "Status"),
        ("i", "inventory", "Inventory"),
        ("a", "achievements", "Achievements"),
        ("dollar_sign", "shop", "$hop"),
        ("q", "quit_app", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        app: JambApp = self.app  # type: ignore[assignment]
        state = app.state

        with VerticalScroll(id="main-box"):
            # Header row
            with Horizontal(id="header-row"):
                yield Label(f"  [bold #d946ef]\\[{state.rarity}][/]", id="header-rarity")
                yield Label(f"  [bold #c084fc]{state.stage.title()}[/]", id="header-stage")
                yield Label(f"[#facc15]{state.gold}g[/]  Lv {state.level}/{state.level_cap()}  ", id="header-level")

            # Art + speech side by side
            spec = state.stats.highest() if state.stage == "adult" else None
            with Horizontal(id="art-speech"):
                yield SnailArt(state.stage, spec, id="snail-art")
                yield SpeechBubble(state.mood.value, id="speech-bubble")

            # Mood
            yield Label(id="mood-line")

            # Name divider
            yield Label(f"  ◆ {state.name} ◆", classes="name-divider")

            # Stat bars
            cap = state.stat_cap()
            native = state.native_stats or {}
            for name, value in state.stats.as_dict().items():
                base = native.get(name)
                yield StatBar(name.upper(), value, cap, f"bar-{name}", base=base, id=f"stat-{name}")

            # Title + XP
            yield Label(id="title-xp-line", classes="mt1")

            # XP bar
            xp_bar = ProgressBar(
                total=state.xp_to_next_level(),
                show_eta=False,
                show_percentage=False,
                classes="xp-bar",
                id="xp-bar",
            )
            yield xp_bar

            # Care stats (stacked vertically for narrow terminals)
            yield Label(id="care-hunger", classes="mt1")
            yield Label(id="care-energy")
            yield Label(id="care-happy")

            # Daily challenge
            yield Label(id="daily-line", classes="mt1")

        yield Footer()

    def on_mount(self) -> None:
        self._refresh_dynamic()
        app: JambApp = self.app  # type: ignore[assignment]
        xp_bar = self.query_one("#xp-bar", ProgressBar)
        xp_bar.advance(app.state.xp)

    @staticmethod
    def _care_bar(label: str, value: int, color: str) -> str:
        bar = render_bar(value, 100, 10)
        return f"  [{color} bold]{label:<10}[/] [{color}]{bar}[/] [bold]{value}%[/]"

    def _refresh_dynamic(self) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        state = app.state

        ms = mood_style(state.mood.value)
        mood_line = self.query_one("#mood-line", Label)
        mood_line.update(f"  Mood: [{ms}]{state.mood_label()}[/]")

        title_xp = self.query_one("#title-xp-line", Label)
        title_xp.update(
            f"  Title: [yellow bold]{state.title}[/]     XP: {state.xp}/{state.xp_to_next_level()}"
        )

        care = state.care
        self.query_one("#care-hunger", Label).update(
            self._care_bar("Hunger", care.hunger, "#ef4444")
        )
        self.query_one("#care-energy", Label).update(
            self._care_bar("Energy", care.energy, "#06b6d4")
        )
        self.query_one("#care-happy", Label).update(
            self._care_bar("Happy", care.happiness, "#22c55e")
        )

        self._refresh_daily()

    def _refresh_daily(self) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        state = app.state
        daily_line = self.query_one("#daily-line", Label)

        challenge = state.get_daily_challenge()
        if not challenge:
            daily_line.update("  [dim]No daily challenge[/]")
            return

        desc = challenge["description"]
        target = challenge["target"]
        progress = state.daily_progress_count()

        if state.daily_completed:
            streak_text = f"  Streak: {state.daily_streak}" if state.daily_streak > 0 else ""
            daily_line.update(
                f"  Daily: [#22c55e]* {desc}  COMPLETE![/]{streak_text}"
            )
        else:
            # Build progress dots
            filled = min(progress, target)
            empty = target - filled
            dots = "o" * filled + "-" * empty
            reward_xp = challenge["reward_xp"]
            daily_line.update(
                f"  Daily: {desc}  [{filled}/{target}] {dots}  [dim]+{reward_xp} XP[/]"
            )

    def refresh_state(self) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        state = app.state

        self.query_one("#header-rarity", Label).update(
            f"  [bold #d946ef]\\[{state.rarity}][/]"
        )
        self.query_one("#header-stage", Label).update(
            f"  [bold #c084fc]{state.stage.title()}[/]"
        )
        self.query_one("#header-level", Label).update(
            f"[#facc15]{state.gold}g[/]  Lv {state.level}/{state.level_cap()}  "
        )

        cap = state.stat_cap()
        native = state.native_stats or {}
        for name, value in state.stats.as_dict().items():
            stat_bar = self.query_one(f"#stat-{name}", StatBar)
            stat_bar.update_value(value, max_val=cap, base=native.get(name))

        xp_bar = self.query_one("#xp-bar", ProgressBar)
        xp_bar.update(total=state.xp_to_next_level(), progress=state.xp)

        self._refresh_dynamic()

        speech = self.query_one("#speech-bubble", SpeechBubble)
        speech.update_mood(state.mood.value)

        snail = self.query_one("#snail-art", SnailArt)
        spec = state.stats.highest() if state.stage == "adult" else None
        snail.set_stage(state.stage, spec)

    def animate_snail(self) -> None:
        try:
            snail = self.query_one("#snail-art", SnailArt)
            snail.next_frame()
        except Exception:
            pass

    def rotate_speech(self) -> None:
        try:
            speech = self.query_one("#speech-bubble", SpeechBubble)
            speech.rotate()
        except Exception:
            pass

    def action_train(self) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        app.show_training()

    def action_chat(self) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        app.show_chat()

    def action_feed(self) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        app.show_care("feed")

    def action_rest(self) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        app.show_care("rest")

    def action_play(self) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        app.show_care("play")

    def action_status(self) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        app.show_status()

    def action_dungeon(self) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        app.show_dungeon()

    def action_inventory(self) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        app.show_inventory()

    def action_achievements(self) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        app.show_achievements()

    def action_shop(self) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        app.show_shop()

    def action_quit_app(self) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        app.save_and_quit()
