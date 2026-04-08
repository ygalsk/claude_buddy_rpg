from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

import random

from .constants import ACHIEVEMENTS, DAILY_CHALLENGES

_DAILY_BY_ID: dict[str, dict] = {ch["id"]: ch for ch in DAILY_CHALLENGES}


class Mood(Enum):
    ECSTATIC = "ecstatic"
    HAPPY = "happy"
    CONTENT = "content"
    BORED = "bored"
    HUNGRY = "hungry"
    TIRED = "tired"
    GRUMPY = "grumpy"
    CHAOTIC = "chaotic"


MOOD_MULTIPLIER = {
    Mood.ECSTATIC: 1.5,
    Mood.HAPPY: 1.2,
    Mood.CONTENT: 1.0,
    Mood.BORED: 0.7,
    Mood.HUNGRY: 0.7,
    Mood.TIRED: 0.7,
    Mood.GRUMPY: 0.5,
    Mood.CHAOTIC: 1.1,
}

MOOD_LABEL = {
    Mood.ECSTATIC: "Ecstatic \\o/",
    Mood.HAPPY: "Happy :)",
    Mood.CONTENT: "Content :|",
    Mood.BORED: "Bored -_-",
    Mood.HUNGRY: "Hungry >.<",
    Mood.TIRED: "Tired z_z",
    Mood.GRUMPY: "Grumpy >:(",
    Mood.CHAOTIC: "Chaotic ?!?",
}

TITLE_THRESHOLDS: list[tuple[int, str | dict[str, str]]] = [
    (1, "Hatchling"),
    (5, "Trail Blazer"),
    (
        10,
        {
            "debugging": "Bug Whisperer",
            "patience": "Zen Gastropod",
            "chaos": "Chaos Agent",
            "wisdom": "Sage Snail",
            "snark": "Roast Master",
        },
    ),
    (20, "Legendary Gastropod"),
    (30, "Ascended Mollusk"),
]

STAT_CAP = 255
XP_PER_LEVEL = 50

# Rarity-based progression caps — higher rarity = higher potential
RARITY_CAPS: dict[str, dict[str, int]] = {
    "Common": {"level": 20, "stat": 150},
    "Uncommon": {"level": 30, "stat": 180},
    "Rare": {"level": 50, "stat": 220},
    "Epic": {"level": 75, "stat": 245},
    "Legendary": {"level": 100, "stat": 255},
}

DEFAULT_RARITY_CAP = {"level": 100, "stat": 255}  # fallback if unknown

EVOLUTION_STAGES = [
    (1, "hatchling"),
    (10, "juvenile"),
    (20, "adult"),
]


@dataclass
class Stats:
    debugging: int = 61
    patience: int = 15
    chaos: int = 81
    wisdom: int = 49
    snark: int = 47

    def total(self) -> int:
        return self.debugging + self.patience + self.chaos + self.wisdom + self.snark

    def highest(self) -> str:
        d = self.as_dict()
        return max(d, key=d.get)  # type: ignore[arg-type]

    def add(self, stat_name: str, amount: int, rarity_cap: int = STAT_CAP) -> int:
        current = getattr(self, stat_name)
        cap = min(STAT_CAP, rarity_cap)
        new_val = min(current + amount, cap)
        setattr(self, stat_name, new_val)
        return new_val - current

    def as_dict(self) -> dict[str, int]:
        return {
            "debugging": self.debugging,
            "patience": self.patience,
            "chaos": self.chaos,
            "wisdom": self.wisdom,
            "snark": self.snark,
        }


@dataclass
class CareState:
    hunger: int = 80
    energy: int = 80
    happiness: int = 70
    last_fed: Optional[str] = None
    last_rested: Optional[str] = None
    last_played: Optional[str] = None

    def decay(self, hours_elapsed: float) -> None:
        decay_amount = int(hours_elapsed * 5)
        self.hunger = max(0, self.hunger - decay_amount)
        self.energy = max(0, self.energy - decay_amount)
        self.happiness = max(0, self.happiness - int(hours_elapsed * 3))

    def as_dict(self) -> dict:
        return {
            "hunger": self.hunger,
            "energy": self.energy,
            "happiness": self.happiness,
            "last_fed": self.last_fed,
            "last_rested": self.last_rested,
            "last_played": self.last_played,
        }


@dataclass
class JambState:
    name: str = "Jamb"
    species: str = "Snail"
    rarity: str = "\u2605\u2605\u2605 RARE"
    level: int = 1
    xp: int = 0
    title: str = "Hatchling"
    stats: Stats = field(default_factory=Stats)
    care: CareState = field(default_factory=CareState)
    mood: Mood = Mood.HAPPY
    total_sessions: int = 0
    total_trainings: int = 0
    created_at: Optional[str] = None
    last_session: Optional[str] = None
    stage: str = "hatchling"
    personality: str = (
        "Leaves glittering trails of nonsensical comments across your "
        "debug logs while somehow always pointing at the actual bug, "
        "though with a 50/50 chance of insisting it's a feature."
    )
    chat_history: list[dict[str, str]] = field(default_factory=list)
    achievements: list[str] = field(default_factory=list)
    achievement_counters: dict[str, int] = field(default_factory=dict)
    daily_challenge_id: Optional[str] = None
    daily_challenge_date: Optional[str] = None
    daily_progress: dict[str, int] = field(default_factory=dict)
    daily_completed: bool = False
    daily_streak: int = 0
    inventory: list[dict] = field(default_factory=list)
    equipment: dict[str, str] = field(default_factory=dict)
    gold: int = 0
    dungeon_highest_floor: int = 0
    inventory_capacity: int = 15
    # Native buddy bone sync
    native_rarity: Optional[str] = None  # e.g., "Uncommon", "Rare"
    native_stats: Optional[dict[str, int]] = None  # base stats from bones (0-100)
    bones_synced: bool = False

    def rarity_cap(self) -> dict[str, int]:
        """Get level and stat caps based on native rarity."""
        if self.native_rarity:
            return RARITY_CAPS.get(self.native_rarity, DEFAULT_RARITY_CAP)
        return DEFAULT_RARITY_CAP

    def stat_cap(self) -> int:
        """Effective stat cap based on rarity."""
        return self.rarity_cap()["stat"]

    def clamp_to_caps(self) -> None:
        """Retroactively enforce rarity caps on stats and level."""
        cap = self.stat_cap()
        for stat_name in ("debugging", "patience", "chaos", "wisdom", "snark"):
            val = getattr(self.stats, stat_name)
            if val > cap:
                setattr(self.stats, stat_name, cap)
        self.level = min(self.level, self.level_cap())

    def level_cap(self) -> int:
        """Effective level cap based on rarity."""
        return self.rarity_cap()["level"]

    def xp_to_next_level(self) -> int:
        return self.level * XP_PER_LEVEL

    def add_xp(self, amount: int) -> str | None:
        """Add XP. Returns new stage name if evolved, None otherwise."""
        if self.level >= self.level_cap():
            return None
        old_stage = self.stage
        self.xp += amount
        leveled = False
        while self.xp >= self.xp_to_next_level() and self.level < self.level_cap():
            self.xp -= self.xp_to_next_level()
            self.level += 1
            leveled = True
        if leveled:
            self._update_title()
            self._update_stage()
        if self.stage != old_stage:
            return self.stage
        return None

    def _update_stage(self) -> None:
        for threshold, stage in reversed(EVOLUTION_STAGES):
            if self.level >= threshold:
                self.stage = stage
                break

    def _update_title(self) -> None:
        for threshold, title in reversed(TITLE_THRESHOLDS):
            if self.level >= threshold:
                if isinstance(title, dict):
                    self.title = title.get(self.stats.highest(), "Trail Blazer")
                else:
                    self.title = title
                break

    def compute_mood(self) -> None:
        care = self.care
        if care.hunger > 70 and care.energy > 70 and care.happiness > 80:
            self.mood = Mood.ECSTATIC
        elif care.hunger < 15:
            self.mood = Mood.HUNGRY
        elif care.energy < 15:
            self.mood = Mood.TIRED
        elif care.hunger < 30 or care.energy < 30 or care.happiness < 30:
            self.mood = Mood.GRUMPY
        elif care.happiness < 40:
            self.mood = Mood.BORED
        elif care.hunger > 50 and care.energy > 50 and care.happiness > 50:
            self.mood = Mood.HAPPY
        else:
            self.mood = Mood.CONTENT

    def mood_multiplier(self) -> float:
        return MOOD_MULTIPLIER.get(self.mood, 1.0)

    def mood_label(self) -> str:
        return MOOD_LABEL.get(self.mood, "???")

    def start_session(self) -> None:
        now = datetime.now(timezone.utc).isoformat()
        if self.created_at is None:
            self.created_at = now
        if self.last_session:
            try:
                last = datetime.fromisoformat(self.last_session)
                elapsed = (datetime.now(timezone.utc) - last).total_seconds() / 3600
                self.care.decay(elapsed)
            except (ValueError, TypeError):
                pass
        self.last_session = now
        self.total_sessions += 1
        self.compute_mood()

    MAX_STACK = 10

    def inventory_slot_count(self) -> int:
        """Count how many slots are used. Stacked consumables = 1 slot."""
        return len(self.inventory)

    def inventory_full(self) -> bool:
        return self.inventory_slot_count() >= self.inventory_capacity

    def inventory_add(self, item: dict) -> bool:
        """Try to add an item to inventory. Returns True if added, False if full.

        Consumables stack by id (up to MAX_STACK per stack).
        """
        if item.get("type") == "consumable":
            # Try to stack with existing
            for existing in self.inventory:
                if existing.get("id") == item.get("id") and existing.get("type") == "consumable":
                    count = existing.get("count", 1)
                    if count < self.MAX_STACK:
                        existing["count"] = count + 1
                        return True
                    break  # stack is full, need a new slot

        if self.inventory_full():
            return False

        # For new consumable entries, ensure count field
        new_item = dict(item)
        if new_item.get("type") == "consumable" and "count" not in new_item:
            new_item["count"] = 1
        self.inventory.append(new_item)
        return True

    def inventory_remove(self, idx: int, count: int = 1) -> dict | None:
        """Remove count items at index. Returns the item removed, or None."""
        if idx < 0 or idx >= len(self.inventory):
            return None
        item = self.inventory[idx]
        if item.get("type") == "consumable":
            current = item.get("count", 1)
            if current > count:
                item["count"] = current - count
                return dict(item)
            else:
                return self.inventory.pop(idx)
        else:
            return self.inventory.pop(idx)

    def sell_item(self, idx: int, count: int = 1) -> int:
        """Sell item(s) at index. Returns gold earned."""
        if idx < 0 or idx >= len(self.inventory):
            return 0
        item = self.inventory[idx]
        value = item.get("value", 0) // 2  # 50% sell price
        total = value * count
        self.inventory_remove(idx, count)
        self.gold += total
        return total

    def check_achievements(self) -> list[dict]:
        """Check all achievements, return list of newly earned ones."""
        newly_earned: list[dict] = []
        stats_d = self.stats.as_dict()
        counters = self.achievement_counters
        messages_sent = counters.get("messages_sent", 0)
        times_fed = counters.get("times_fed", 0)
        times_rested = counters.get("times_rested", 0)
        times_played = counters.get("times_played", 0)

        for ach in ACHIEVEMENTS:
            aid = ach["id"]
            if aid in self.achievements:
                continue

            earned = False

            # Training
            if aid == "first_blood":
                earned = self.total_trainings >= 1
            elif aid == "ten_sessions":
                earned = self.total_trainings >= 10
            elif aid == "grindstone":
                earned = self.total_trainings >= 50
            elif aid == "specialist":
                earned = any(v > 100 for v in stats_d.values())
            elif aid == "maxed_out":
                earned = any(v == 255 for v in stats_d.values())
            elif aid == "well_rounded":
                earned = all(v > 50 for v in stats_d.values())

            # Care
            elif aid == "good_owner":
                earned = times_fed >= 10
            elif aid == "full_belly":
                earned = self.care.hunger >= 100
            elif aid == "energized":
                earned = self.care.energy >= 100
            elif aid == "happy_camper":
                earned = self.care.happiness >= 100
            elif aid == "neglectful":
                earned = (
                    self.care.hunger < 10
                    or self.care.energy < 10
                    or self.care.happiness < 10
                )
            elif aid == "caretaker":
                earned = times_rested >= 10
            elif aid == "playful":
                earned = times_played >= 10

            # Social
            elif aid == "first_words":
                earned = messages_sent >= 1
            elif aid == "chatterbox":
                earned = messages_sent >= 20
            elif aid == "deep_convo":
                earned = messages_sent >= 50

            # Milestone
            elif aid == "hatchling":
                earned = self.level >= 1
            elif aid == "juvenile":
                earned = self.level >= 10
            elif aid == "adult":
                earned = self.level >= 20
            elif aid == "legend":
                earned = self.level >= 30
            elif aid == "century":
                earned = self.stats.total() > 500

            # Secret
            elif aid == "night_owl":
                now = datetime.now()
                earned = 0 <= now.hour < 5
            elif aid == "chaos_lord":
                earned = self.stats.chaos > 200
            elif aid == "zen_master":
                earned = self.stats.patience > 200
            elif aid == "bug_bounty":
                earned = self.stats.debugging > 200
            elif aid == "snark_king":
                earned = self.stats.snark > 200

            if earned:
                self.achievements.append(aid)
                newly_earned.append(ach)

        return newly_earned

    def roll_daily_challenge(self) -> dict | None:
        """Ensure a daily challenge is active. Returns the challenge dict."""
        today = datetime.now().strftime("%Y-%m-%d")
        if self.daily_challenge_date == today and self.daily_challenge_id:
            return _DAILY_BY_ID.get(self.daily_challenge_id)

        # New day - check streak
        if self.daily_challenge_date is not None:
            if self.daily_completed:
                self.daily_streak += 1
            else:
                self.daily_streak = 0

        # Pick a deterministic challenge based on date
        rng = random.Random(today)
        challenge = rng.choice(DAILY_CHALLENGES)
        self.daily_challenge_id = challenge["id"]
        self.daily_challenge_date = today
        self.daily_progress = {}
        self.daily_completed = False
        return challenge

    def get_daily_challenge(self) -> dict | None:
        """Return the current daily challenge dict, or None."""
        if not self.daily_challenge_id:
            return None
        return _DAILY_BY_ID.get(self.daily_challenge_id)

    def daily_progress_count(self) -> int:
        """Return the effective progress count for the current challenge."""
        challenge = self.get_daily_challenge()
        if not challenge:
            return 0
        ctype = challenge["type"]
        if ctype == "care_all":
            # Count distinct care types done today
            count = 0
            for key in ("feed", "rest", "play"):
                if self.daily_progress.get(key, 0) > 0:
                    count += 1
            return count
        elif ctype == "train_all":
            # Count distinct stats trained
            count = 0
            for stat in ("debugging", "patience", "chaos", "wisdom", "snark"):
                if self.daily_progress.get(f"train_{stat}", 0) > 0:
                    count += 1
            return count
        elif ctype == "mood_ecstatic":
            return self.daily_progress.get("mood_ecstatic", 0)
        elif ctype == "full_care":
            return self.daily_progress.get("full_care", 0)
        else:
            return self.daily_progress.get(ctype, 0)

    def advance_daily(self, event_type: str) -> bool:
        """Advance daily challenge progress. Returns True if just completed."""
        challenge = self.get_daily_challenge()
        if not challenge or self.daily_completed:
            return False

        ctype = challenge["type"]

        # Track the raw event
        self.daily_progress[event_type] = self.daily_progress.get(event_type, 0) + 1

        # Special: check mood_ecstatic by current mood
        if ctype == "mood_ecstatic" and self.mood == Mood.ECSTATIC:
            self.daily_progress["mood_ecstatic"] = 1

        # Special: check full_care by current care values
        if ctype == "full_care":
            if (
                self.care.hunger >= 100
                and self.care.energy >= 100
                and self.care.happiness >= 100
            ):
                self.daily_progress["full_care"] = 1

        progress = self.daily_progress_count()
        if progress >= challenge["target"]:
            self.daily_completed = True
            return True
        return False

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "species": self.species,
            "rarity": self.rarity,
            "level": self.level,
            "xp": self.xp,
            "title": self.title,
            "stats": self.stats.as_dict(),
            "care": self.care.as_dict(),
            "mood": self.mood.value,
            "total_sessions": self.total_sessions,
            "total_trainings": self.total_trainings,
            "created_at": self.created_at,
            "last_session": self.last_session,
            "stage": self.stage,
            "personality": self.personality,
            "chat_history": self.chat_history[-50:],
            "achievements": self.achievements,
            "achievement_counters": self.achievement_counters,
            "daily_challenge_id": self.daily_challenge_id,
            "daily_challenge_date": self.daily_challenge_date,
            "daily_progress": self.daily_progress,
            "daily_completed": self.daily_completed,
            "daily_streak": self.daily_streak,
            "inventory": self.inventory,
            "equipment": self.equipment,
            "gold": self.gold,
            "dungeon_highest_floor": self.dungeon_highest_floor,
            "inventory_capacity": self.inventory_capacity,
            "native_rarity": self.native_rarity,
            "native_stats": self.native_stats,
            "bones_synced": self.bones_synced,
        }

    @classmethod
    def from_dict(cls, data: dict) -> JambState:
        state = cls()
        state.name = data.get("name", state.name)
        state.species = data.get("species", state.species)
        state.rarity = data.get("rarity", state.rarity)
        state.level = data.get("level", state.level)
        state.xp = data.get("xp", state.xp)
        state.title = data.get("title", state.title)
        state.total_sessions = data.get("total_sessions", state.total_sessions)
        state.total_trainings = data.get("total_trainings", state.total_trainings)
        state.created_at = data.get("created_at", state.created_at)
        state.last_session = data.get("last_session", state.last_session)
        state.personality = data.get("personality", state.personality)
        state.chat_history = data.get("chat_history", [])
        state.achievements = data.get("achievements", [])
        state.achievement_counters = data.get("achievement_counters", {})
        state.daily_challenge_id = data.get("daily_challenge_id")
        state.daily_challenge_date = data.get("daily_challenge_date")
        state.daily_progress = data.get("daily_progress", {})
        state.daily_completed = data.get("daily_completed", False)
        state.daily_streak = data.get("daily_streak", 0)
        state.inventory = data.get("inventory", [])
        state.equipment = data.get("equipment", {})
        state.gold = data.get("gold", 0)
        state.dungeon_highest_floor = data.get("dungeon_highest_floor", 0)
        state.inventory_capacity = data.get("inventory_capacity", 15)
        state.native_rarity = data.get("native_rarity")
        state.native_stats = data.get("native_stats")
        state.bones_synced = data.get("bones_synced", False)

        if "stats" in data:
            s = data["stats"]
            state.stats = Stats(
                debugging=s.get("debugging", 61),
                patience=s.get("patience", 15),
                chaos=s.get("chaos", 81),
                wisdom=s.get("wisdom", 49),
                snark=s.get("snark", 47),
            )

        if "care" in data:
            c = data["care"]
            state.care = CareState(
                hunger=c.get("hunger", 80),
                energy=c.get("energy", 80),
                happiness=c.get("happiness", 70),
                last_fed=c.get("last_fed"),
                last_rested=c.get("last_rested"),
                last_played=c.get("last_played"),
            )

        mood_str = data.get("mood", "happy")
        try:
            state.mood = Mood(mood_str)
        except ValueError:
            state.mood = Mood.HAPPY

        # Recompute stage from level (handles old saves without stage field)
        state._update_stage()

        # Retroactively enforce rarity caps on existing saves
        state.clamp_to_caps()

        return state
