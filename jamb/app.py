from __future__ import annotations

import json
import random
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Label

from . import persistence
from .models import JambState
from .screens.main_screen import MainScreen
from .screens.training_screen import TrainingScreen
from .screens.care_screen import CareOverlay
from .screens.status_screen import StatusScreen
from .screens.evolution_screen import EvolutionScreen
from .screens.chat_screen import ChatScreen
from .screens.achievements_screen import AchievementsScreen
from .screens.dungeon_screen import DungeonScreen
from .screens.battle_screen import BattleScreen
from .screens.loot_screen import LootScreen
from .screens.inventory_screen import InventoryScreen
from .screens.shop_screen import ShopScreen
from .dungeon.engine import CombatState, DungeonRun
from .activities.debugging import BugHuntActivity
from .activities.patience import MeditationActivity
from .activities.chaos import ChaosRouletteActivity
from .activities.wisdom import RiddleChallengeActivity
from .activities.snark import ComebackBattleActivity


ACTIVITY_MAP = {
    "debugging": BugHuntActivity,
    "patience": MeditationActivity,
    "chaos": ChaosRouletteActivity,
    "wisdom": RiddleChallengeActivity,
    "snark": ComebackBattleActivity,
}


class JambApp(App):
    CSS_PATH = "jamb.tcss"

    def __init__(self) -> None:
        super().__init__()
        self.state: JambState = persistence.load()
        self._session_trains: dict[str, int] = {}
        self.dungeon_run: DungeonRun | None = None
        self._last_known_mtime: float = 0.0
        self._saving: bool = False

    def on_mount(self) -> None:
        self.state.roll_daily_challenge()
        self._save_and_track()
        self.push_screen(MainScreen())
        # Start animation timers
        self.set_interval(2.0, self._animate_snail)
        self._schedule_speech_rotation()
        # File watcher: detect external changes to save.json (from hooks)
        self._last_known_mtime = self._get_save_mtime()
        self.set_interval(2.5, self._check_external_changes)

    def _get_save_mtime(self) -> float:
        try:
            return persistence.SAVE_FILE.stat().st_mtime
        except OSError:
            return 0.0

    def _save_and_track(self) -> None:
        """Save state and update mtime tracker so file watcher ignores own writes."""
        persistence.save(self.state)
        self._last_known_mtime = self._get_save_mtime()

    def _check_external_changes(self) -> None:
        """Poll save.json for external modifications (from hooks)."""
        current_mtime = self._get_save_mtime()
        if current_mtime > self._last_known_mtime:
            self._last_known_mtime = current_mtime
            self._reload_from_disk()

    def _reload_from_disk(self) -> None:
        """Reload state from save.json without starting a new session."""
        try:
            data = json.loads(persistence.SAVE_FILE.read_text())
            new_state = JambState.from_dict(data.get("jamb", {}))
        except (json.JSONDecodeError, KeyError, OSError):
            return

        # Detect meaningful changes
        old_xp = self.state.xp + self.state.level * 1000
        new_xp = new_state.xp + new_state.level * 1000
        gained_xp = new_xp > old_xp

        # Preserve session-specific state
        new_state.total_sessions = self.state.total_sessions
        self.state = new_state

        # Refresh the visible screen
        screen = self.screen
        if isinstance(screen, MainScreen):
            screen.refresh_state()

        if gained_xp:
            self.notify("Jamb earned a reward!", timeout=2)

    def _schedule_speech_rotation(self) -> None:
        self.set_timer(random.uniform(15, 45), self._rotate_speech_and_reschedule)

    def _rotate_speech_and_reschedule(self) -> None:
        self._rotate_speech()
        self._schedule_speech_rotation()

    def show_main(self) -> None:
        # Pop all screens back to MainScreen (keep default + MainScreen)
        while len(self.screen_stack) > 2:
            self.pop_screen()
        main = self.screen
        if isinstance(main, MainScreen):
            main.refresh_state()
        else:
            self.push_screen(MainScreen())

        self._check_and_notify_achievements()

    def show_training(self) -> None:
        self._push_over_main(TrainingScreen())

    def show_care(self, action: str) -> None:
        self._push_over_main(CareOverlay(action))

    def show_status(self) -> None:
        self._push_over_main(StatusScreen())

    def show_chat(self) -> None:
        self._push_over_main(ChatScreen())

    def show_achievements(self) -> None:
        self._push_over_main(AchievementsScreen())

    def show_dungeon(self) -> None:
        if not self.dungeon_run:
            self.dungeon_run = DungeonRun.new_run(
                self.state.stats.as_dict(),
                self.state.equipment,
            )
        self._push_over_main(DungeonScreen())

    def show_inventory(self) -> None:
        self._push_over_main(InventoryScreen())

    def show_shop(self) -> None:
        self._push_over_main(ShopScreen())

    def show_loot(self, loot: dict) -> None:
        # Add items to inventory (with stacking and capacity check)
        dropped = []
        if "item" in loot and loot["item"]:
            if not self.state.inventory_add(loot["item"]):
                dropped.append(loot["item"])
        for item in loot.get("items", []):
            if not self.state.inventory_add(item):
                dropped.append(item)
        if dropped:
            names = ", ".join(i.get("name", "?") for i in dropped)
            self.notify(f"Inventory full! Dropped: {names}", severity="warning", timeout=4)
        self.state.gold += loot.get("gold", 0)
        if self.dungeon_run:
            self.dungeon_run.gold_earned += loot.get("gold", 0)
        self._save_and_track()
        self._push_over_main(LootScreen(loot))

    def start_combat(self, enemy: dict) -> None:
        combat = CombatState.from_stats(
            enemy, self.state.stats.as_dict(), self.state.equipment,
        )
        if self.dungeon_run:
            combat.player_hp = self.dungeon_run.hp
            combat.player_max_hp = self.dungeon_run.max_hp
        self._push_over_main(BattleScreen(combat))

    def combat_victory(self, xp: int, gold: int, loot: list[dict]) -> None:
        run = self.dungeon_run
        if run:
            # Mark room cleared
            room = run.floor.current_room()
            room.cleared = True
            run.xp_earned += xp
            run.gold_earned += gold

        self.state.gold += gold
        self.state.add_xp(xp)
        self._save_and_track()

        self.notify(
            f"+{xp} XP  +{gold} Gold" + (f"  +{len(loot)} items!" if loot else ""),
            title="Victory!",
            timeout=3,
        )

        if loot:
            self.show_loot({"items": loot, "gold": gold, "xp": xp})
        else:
            self.show_dungeon()

    def dungeon_death(self) -> None:
        run = self.dungeon_run
        if run:
            # Keep half the XP and gold earned
            kept_xp = run.xp_earned // 2
            self.state.add_xp(kept_xp)
            if run.floor.number > self.state.dungeon_highest_floor:
                self.state.dungeon_highest_floor = run.floor.number
        self.dungeon_run = None
        self._save_and_track()
        self.notify(
            f"Jamb was defeated! Kept {kept_xp if run else 0} XP.",
            title="Dungeon Over",
            severity="warning",
            timeout=4,
        )
        self.show_main()

    def end_dungeon(self, fled: bool = False) -> None:
        run = self.dungeon_run
        if run:
            self.state.add_xp(run.xp_earned)
            if run.floor.number > self.state.dungeon_highest_floor:
                self.state.dungeon_highest_floor = run.floor.number
        self.dungeon_run = None
        self._save_and_track()
        if fled:
            self.notify("Fled the dungeon! XP and loot kept.", timeout=3)
        self.show_main()

    def start_activity(self, stat_name: str) -> None:
        if self.state.care.energy < 10:
            self._show_too_tired()
            return
        cls = ACTIVITY_MAP.get(stat_name)
        if not cls:
            return
        activity = cls(on_done=self._on_activity_done)
        self._push_over_main(activity)

    def _push_over_main(self, screen) -> None:
        """Push a screen, popping any non-main screen first."""
        while len(self.screen_stack) > 2:
            self.pop_screen()
        self.push_screen(screen)

    def _show_too_tired(self) -> None:
        self._push_over_main(TooTiredScreen())

    def _on_activity_done(self, stat_name: str, gain: int, xp: int) -> None:
        # Diminishing returns based on session training count
        self._session_trains[stat_name] = self._session_trains.get(stat_name, 0) + 1
        count = self._session_trains[stat_name]
        if count <= 2:
            fatigue = 1.0
        elif count <= 4:
            fatigue = 0.75
        elif count <= 6:
            fatigue = 0.50
        else:
            fatigue = 0.25

        multiplier = self.state.mood_multiplier() * fatigue
        actual_gain = max(1, int(gain * multiplier))
        actual_xp = max(1, int(xp * multiplier))

        self.state.stats.add(stat_name, actual_gain, self.state.stat_cap())
        evolved = self.state.add_xp(actual_xp)
        self.state.total_trainings += 1

        # Training costs a bit of energy
        self.state.care.energy = max(0, self.state.care.energy - 5)
        self.state.care.hunger = max(0, self.state.care.hunger - 3)
        self.state.compute_mood()

        self._save_and_track()

        # Notify stat gain
        self.notify(
            f"+{actual_gain} {stat_name.upper()}  |  +{actual_xp} XP",
            title="Training Complete!",
            timeout=3,
        )

        # Advance daily challenge
        daily_done = self.state.advance_daily("training")
        if not daily_done:
            daily_done = self.state.advance_daily(f"train_{stat_name}")
        if daily_done:
            self.award_daily_challenge()

        self._check_and_notify_achievements()

        if evolved:
            self._push_over_main(EvolutionScreen(evolved))

    def _check_and_notify_achievements(self) -> None:
        new_achs = self.state.check_achievements()
        if new_achs:
            self._save_and_track()
            for ach in new_achs:
                self.notify(
                    f"{ach['icon']} {ach['name']}",
                    title="Achievement Unlocked!",
                    timeout=4,
                )

    def award_daily_challenge(self) -> None:
        """Award rewards for completing the daily challenge."""
        challenge = self.state.get_daily_challenge()
        if not challenge:
            return
        reward_xp = challenge.get("reward_xp", 0)
        reward_stat = challenge.get("reward_stat")
        if reward_xp:
            self.state.add_xp(reward_xp)
        if reward_stat:
            self.state.stats.add(reward_stat, 3, self.state.stat_cap())
        self._save_and_track()
        self.notify(
            f"Daily Challenge complete! +{reward_xp} XP"
            + (f"  +3 {reward_stat.upper()}" if reward_stat else ""),
            title="Daily Challenge!",
            timeout=5,
        )

    def _animate_snail(self) -> None:
        screen = self.screen
        if isinstance(screen, MainScreen):
            screen.animate_snail()

    def _rotate_speech(self) -> None:
        screen = self.screen
        if isinstance(screen, MainScreen):
            screen.rotate_speech()

    def save_and_quit(self) -> None:
        self._save_and_track()
        self.exit()


class TooTiredScreen(Screen):
    """Shown when Jamb is too tired to train."""

    BINDINGS = [
        ("r", "rest", "Rest"),
        ("escape", "back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        app: JambApp = self.app  # type: ignore[assignment]
        with Vertical(classes="care-overlay"):
            yield Label("  [tomato bold]Jamb is too tired to train! Rest first.[/]")
            yield Label(f"  Energy: {app.state.care.energy}% (need 10%)", classes="dim mt1")
            yield Label("  [yellow bold]Press any key[/]", classes="mt1")

        yield Footer()

    def on_key(self, event) -> None:
        app: JambApp = self.app  # type: ignore[assignment]
        key = event.character or event.key
        if key in ("r", "R"):
            app.show_care("rest")
        else:
            app.show_main()
