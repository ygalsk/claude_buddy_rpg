"""Combat engine and dungeon state management."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Optional

from .generator import Floor
from .items import CONSUMABLES, ITEMS_BY_ID, items_by_rarity
from .types import get_effectiveness, effectiveness_label

def _weapon_attack_bonus(weapon: dict) -> int:
    """Sum all attack-related bonuses from a weapon."""
    return (
        weapon.get("attack", 0)
        + weapon.get("debug_bonus", 0)
        + weapon.get("chaos_bonus", 0)
        + weapon.get("patience_bonus", 0)
    )


@dataclass
class CombatState:
    """Tracks state during a single combat encounter."""
    enemy: dict
    enemy_hp: int = 0
    enemy_max_hp: int = 0
    enemy_attack: int = 0
    enemy_defense: int = 0
    player_hp: int = 0
    player_max_hp: int = 0
    player_attack: int = 0
    player_defense: int = 0
    player_speed: int = 0
    crit_chance: int = 0
    dodge_chance: int = 0
    turn: int = 0
    attack_buff: int = 0
    buff_turns: int = 0
    defending: bool = False
    analyzed: bool = False  # wisdom special: next attack 2x
    weapon_type: str | None = None  # damage type of equipped weapon
    equipment: dict = field(default_factory=dict)  # current equipment ids
    log: list[str] = field(default_factory=list)
    finished: bool = False
    victory: bool = False

    @classmethod
    def from_stats(cls, enemy: dict, stats: dict, equipment: dict) -> CombatState:
        """Create combat state from Jamb's stats and equipped items."""
        debugging = stats.get("debugging", 0)
        patience = stats.get("patience", 0)
        chaos = stats.get("chaos", 0)
        wisdom = stats.get("wisdom", 0)
        snark = stats.get("snark", 0)

        base_attack = 5 + debugging // 10
        base_defense = 2 + patience // 15
        base_speed = 3 + chaos // 12

        # Equipment bonuses
        attack_bonus = 0
        defense_bonus = 0
        speed_bonus = 0

        weapon_type = None
        weapon = ITEMS_BY_ID.get(equipment.get("weapon", ""))
        if weapon:
            attack_bonus += _weapon_attack_bonus(weapon)
            weapon_type = weapon.get("damage_type")

        armor = ITEMS_BY_ID.get(equipment.get("armor", ""))
        if armor:
            defense_bonus += armor.get("defense", 0)
            defense_bonus += armor.get("wisdom_bonus", 0)

        accessory = ITEMS_BY_ID.get(equipment.get("accessory", ""))
        if accessory:
            attack_bonus += accessory.get("attack_bonus", 0)
            defense_bonus += accessory.get("defense_bonus", 0)
            speed_bonus += accessory.get("speed_bonus", 0)
            ab = accessory.get("all_bonus", 0)
            attack_bonus += ab
            defense_bonus += ab
            speed_bonus += ab

        max_hp = 50 + patience * 2

        return cls(
            enemy=enemy,
            enemy_hp=enemy["hp"],
            enemy_max_hp=enemy["hp"],
            enemy_attack=enemy["attack"],
            enemy_defense=enemy["defense"],
            player_hp=max_hp,
            player_max_hp=max_hp,
            player_attack=base_attack + attack_bonus,
            player_defense=base_defense + defense_bonus,
            player_speed=base_speed + speed_bonus,
            crit_chance=min(50, chaos // 5),
            dodge_chance=min(25, snark // 10),
            weapon_type=weapon_type,
            equipment=dict(equipment),
        )

    def player_turn_attack(self) -> str:
        """Execute player attack."""
        self.defending = False
        attack_power = self.player_attack + self.attack_buff

        if self.analyzed:
            attack_power *= 2
            self.analyzed = False

        # Crit check
        is_crit = random.randint(1, 100) <= self.crit_chance
        if is_crit:
            attack_power = int(attack_power * 1.5)

        raw_damage = max(1, attack_power - self.enemy_defense + random.randint(-2, 3))

        # Type effectiveness
        enemy_type = self.enemy.get("type")
        multiplier = get_effectiveness(self.weapon_type, enemy_type)
        damage = max(1, int(raw_damage * multiplier))
        self.enemy_hp = max(0, self.enemy_hp - damage)

        msg = f"Jamb attacks for {damage} damage!"
        if is_crit:
            msg = f"CRITICAL HIT! Jamb attacks for {damage} damage!"

        eff_label = effectiveness_label(multiplier)
        if eff_label:
            msg += f" {eff_label}"
        self.log.append(msg)

        if self.enemy_hp <= 0:
            self.finished = True
            self.victory = True
            self.log.append(f"{self.enemy['name']} is defeated!")

        return msg

    def player_turn_defend(self) -> str:
        """Player defends this turn."""
        self.defending = True
        self.analyzed = False
        msg = "Jamb braces for impact! (Defense doubled this turn)"
        self.log.append(msg)
        return msg

    def player_turn_special(self, highest_stat: str) -> str:
        """Use special ability based on dominant stat."""
        self.defending = False
        self.analyzed = False

        # Special type matches the stat it's based on
        special_type = highest_stat
        enemy_type = self.enemy.get("type")
        multiplier = get_effectiveness(special_type, enemy_type)
        eff_label = effectiveness_label(multiplier)

        if highest_stat == "debugging":
            # Guaranteed hit, bonus damage
            raw_damage = self.player_attack + 5
            damage = max(1, int(raw_damage * multiplier))
            self.enemy_hp = max(0, self.enemy_hp - damage)
            msg = f"DEBUG MODE! Jamb traces the bug for {damage} guaranteed damage!"
        elif highest_stat == "patience":
            # Heal 25% HP (healing is not affected by type)
            heal = self.player_max_hp // 4
            self.player_hp = min(self.player_max_hp, self.player_hp + heal)
            msg = f"MEDITATE! Jamb retreats into shell and heals {heal} HP!"
            eff_label = None  # no type effectiveness on heals
        elif highest_stat == "chaos":
            # Random damage: could be huge or tiny
            raw_damage = random.randint(1, self.player_attack * 3)
            damage = max(1, int(raw_damage * multiplier))
            self.enemy_hp = max(0, self.enemy_hp - damage)
            msg = f"CHAOS STRIKE! Unpredictable blast for {damage} damage!"
        elif highest_stat == "wisdom":
            # Next attack does 2x
            self.analyzed = True
            msg = "ANALYZE! Jamb studies the enemy. Next attack deals 2x damage!"
            eff_label = None  # no direct damage
        elif highest_stat == "snark":
            # Taunt: enemy attack reduced, small damage
            raw_damage = max(1, self.player_attack // 2)
            damage = max(1, int(raw_damage * multiplier))
            self.enemy_hp = max(0, self.enemy_hp - damage)
            self.enemy_attack = max(1, self.enemy_attack - 2)
            msg = f"ROAST! Jamb trash-talks for {damage} damage! Enemy attack reduced!"
        else:
            raw_damage = self.player_attack
            damage = max(1, int(raw_damage * multiplier))
            self.enemy_hp = max(0, self.enemy_hp - damage)
            msg = f"Jamb attacks for {damage} damage!"

        if eff_label:
            msg += f" {eff_label}"
        self.log.append(msg)

        if self.enemy_hp <= 0:
            self.finished = True
            self.victory = True
            self.log.append(f"{self.enemy['name']} is defeated!")

        return msg

    def swap_weapon(self, new_weapon_id: str) -> str:
        """Swap equipped weapon mid-combat. Costs the player's turn."""
        self.defending = False
        self.analyzed = False

        weapon = ITEMS_BY_ID.get(new_weapon_id)
        if not weapon or weapon.get("type") != "weapon":
            msg = "Invalid weapon!"
            self.log.append(msg)
            return msg

        # Recalculate attack with new weapon
        old_weapon = ITEMS_BY_ID.get(self.equipment.get("weapon", ""))
        if old_weapon:
            self.player_attack -= _weapon_attack_bonus(old_weapon)

        self.player_attack += _weapon_attack_bonus(weapon)

        self.weapon_type = weapon.get("damage_type")
        self.equipment["weapon"] = new_weapon_id

        type_label = self.weapon_type.upper() if self.weapon_type else "???"
        msg = f"Swapped to {weapon['name']}! ({type_label}-type)"
        self.log.append(msg)
        return msg

    def player_use_item(self, item: dict) -> str:
        """Use a consumable item."""
        self.defending = False
        self.analyzed = False

        if item.get("heal"):
            heal = item["heal"]
            self.player_hp = min(self.player_max_hp, self.player_hp + heal)
            msg = f"Used {item['name']}! Healed {heal} HP."
        elif item.get("full_heal"):
            self.player_hp = self.player_max_hp
            msg = f"Used {item['name']}! Fully restored!"
        elif item.get("attack_buff"):
            self.attack_buff += item["attack_buff"]
            self.buff_turns = item.get("turns", 3)
            msg = f"Used {item['name']}! Attack +{item['attack_buff']} for {self.buff_turns} turns."
        else:
            msg = f"Used {item['name']}!"

        self.log.append(msg)
        return msg

    def enemy_turn(self) -> str:
        """Execute enemy turn."""
        # Dodge check
        if random.randint(1, 100) <= self.dodge_chance:
            msg = f"Jamb dodges {self.enemy['name']}'s attack!"
            self.log.append(msg)
            return msg

        effective_defense = self.player_defense * (2 if self.defending else 1)
        damage = max(1, self.enemy_attack - effective_defense + random.randint(-1, 2))
        self.player_hp = max(0, self.player_hp - damage)

        msg = f"{self.enemy['name']} attacks for {damage} damage!"
        if self.defending:
            msg += " (Blocked!)"
        self.log.append(msg)

        if self.player_hp <= 0:
            self.finished = True
            self.victory = False
            self.log.append("Jamb has been defeated!")

        return msg

    def apply_enemy_special(self) -> str | None:
        """Apply enemy special ability. Returns message or None."""
        special = self.enemy.get("special")
        if not special:
            return None

        if special == "grow":
            self.enemy_attack += 1
            msg = f"{self.enemy['name']} grows stronger! (ATK +1)"
        elif special == "double_attack":
            # Second attack
            msg = self.enemy_turn()
            return f"Double attack! " + msg
        elif special == "lock" and random.random() < 0.3:
            msg = "DEADLOCKED! Jamb can't move this turn!"
        elif special == "tangle":
            if self.player_attack > 3:
                self.player_attack -= 1
                msg = f"Tangled! Jamb's attack reduced! (ATK -{1})"
            else:
                msg = None
        elif special == "fortify":
            self.enemy_defense += 1
            msg = f"{self.enemy['name']} fortifies! (DEF +1)"
        elif special == "corrupt":
            effect = random.choice(["attack", "defense", "speed"])
            if effect == "attack" and self.player_attack > 3:
                self.player_attack -= 1
                msg = "Corrupted! Attack reduced!"
            elif effect == "defense" and self.player_defense > 1:
                self.player_defense -= 1
                msg = "Corrupted! Defense reduced!"
            else:
                msg = "Corruption fizzles..."
        else:
            msg = None

        if msg:
            self.log.append(msg)
        return msg

    def end_of_turn(self) -> None:
        """Process end-of-turn effects."""
        self.turn += 1
        if self.buff_turns > 0:
            self.buff_turns -= 1
            if self.buff_turns <= 0:
                self.attack_buff = 0

        # Equipment heal-per-turn effects are checked at the screen level
        self.defending = False

    def calculate_rewards(self) -> tuple[int, int, list[dict]]:
        """Return (xp, gold, loot_items) for victory."""
        if not self.victory:
            return 0, 0, []

        xp = self.enemy.get("xp", 10)
        gold = self.enemy.get("gold", 5)
        loot = []

        for item_id, chance in self.enemy.get("loot", []):
            if random.random() < chance:
                item = ITEMS_BY_ID.get(item_id)
                if item:
                    loot.append(dict(item))

        return xp, gold, loot


@dataclass
class DungeonRun:
    """State for an active dungeon run."""
    floor: Floor
    hp: int
    max_hp: int
    gold_earned: int = 0
    xp_earned: int = 0
    items_found: list[dict] = field(default_factory=list)
    floors_cleared: int = 0
    alive: bool = True

    @classmethod
    def new_run(cls, stats: dict, equipment: dict) -> DungeonRun:
        patience = stats.get("patience", 0)
        max_hp = 50 + patience * 2
        floor = Floor(number=1)
        floor.generate()
        return cls(floor=floor, hp=max_hp, max_hp=max_hp)

    def next_floor(self) -> None:
        self.floors_cleared += 1
        new_floor = Floor(number=self.floor.number + 1)
        new_floor.generate()
        self.floor = new_floor

    def apply_trap(self, stats: dict) -> tuple[int, str]:
        """Apply trap damage. Returns (damage, message)."""
        # Wisdom reduces trap damage
        wisdom = stats.get("wisdom", 0)
        base_damage = random.randint(5, 15)
        reduction = wisdom // 20
        damage = max(1, base_damage - reduction)
        self.hp = max(0, self.hp - damage)
        if self.hp <= 0:
            self.alive = False
        return damage, f"Trap deals {damage} damage!" + (f" (Wisdom reduced by {reduction})" if reduction else "")

    def rest(self) -> int:
        """Rest at a rest point. Returns HP healed."""
        heal = min(self.max_hp // 3, self.max_hp - self.hp)
        self.hp += heal
        return heal

    def generate_treasure(self) -> dict:
        """Generate random treasure loot."""
        roll = random.random()
        if roll < 0.4:
            pool = items_by_rarity("common")
        elif roll < 0.75:
            pool = items_by_rarity("uncommon")
        elif roll < 0.92:
            pool = items_by_rarity("rare")
        else:
            pool = items_by_rarity("legendary")

        if not pool:
            pool = items_by_rarity("common")

        item = random.choice(pool)
        gold = random.randint(5, 20)
        self.gold_earned += gold
        return {"item": dict(item), "gold": gold}
