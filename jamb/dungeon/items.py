"""Item definitions for the Code Dungeon."""

from __future__ import annotations

# Item types: weapon, armor, accessory, consumable
# Rarity: common, uncommon, rare, legendary

WEAPONS: list[dict] = [
    {"id": "rubber_duck", "name": "Rubber Duck", "type": "weapon", "rarity": "common", "attack": 3, "damage_type": "debugging", "description": "The classic debugging companion. Surprisingly pointy.", "value": 10},
    {"id": "stack_trace", "name": "Stack Trace", "type": "weapon", "rarity": "common", "attack": 5, "damage_type": "debugging", "description": "A sharp printout of exactly where things went wrong.", "value": 15},
    {"id": "todo_dagger", "name": "// TODO Dagger", "type": "weapon", "rarity": "common", "attack": 4, "damage_type": "snark", "description": "A passive-aggressive reminder that cuts deep.", "value": 12},
    {"id": "regex_sword", "name": "Regex Sword", "type": "weapon", "rarity": "uncommon", "attack": 8, "damage_type": "chaos", "chaos_bonus": 3, "description": "Powerful but unpredictable. Even the wielder isn't sure what it matches.", "value": 30},
    {"id": "git_bisect", "name": "Git Bisect Blade", "type": "weapon", "rarity": "uncommon", "attack": 7, "damage_type": "debugging", "debug_bonus": 2, "description": "Cuts the problem space in half with every swing.", "value": 35},
    {"id": "design_doc", "name": "Design Doc", "type": "weapon", "rarity": "uncommon", "attack": 6, "damage_type": "wisdom", "wisdom_bonus": 3, "description": "Heavy with forethought. Crushes problems before they start.", "value": 32},
    {"id": "code_review_pen", "name": "Code Review Pen", "type": "weapon", "rarity": "uncommon", "attack": 7, "damage_type": "snark", "snark_bonus": 2, "description": "'Nit: this variable name is a war crime.'", "value": 28},
    {"id": "lint_roller", "name": "The Linter", "type": "weapon", "rarity": "rare", "attack": 12, "damage_type": "patience", "patience_bonus": 2, "description": "Ruthlessly removes anything that doesn't conform.", "value": 60},
    {"id": "architecture_wand", "name": "Architecture Wand", "type": "weapon", "rarity": "rare", "attack": 11, "damage_type": "wisdom", "wisdom_bonus": 3, "description": "Draws boxes and arrows. Enemies become well-structured.", "value": 65},
    {"id": "rewrite_hammer", "name": "Rewrite Hammer", "type": "weapon", "rarity": "legendary", "attack": 18, "damage_type": "chaos", "description": "When all else fails, rewrite from scratch.", "value": 120},
]

ARMORS: list[dict] = [
    {"id": "try_catch_cloak", "name": "Try-Catch Cloak", "type": "armor", "rarity": "common", "defense": 3, "description": "Wraps you in exception handling. Errors bounce off.", "value": 10},
    {"id": "type_safety_shield", "name": "Type Safety Shield", "type": "armor", "rarity": "common", "defense": 4, "description": "Blocks unexpected types from hurting you.", "value": 15},
    {"id": "firewall_vest", "name": "Firewall Vest", "type": "armor", "rarity": "uncommon", "defense": 7, "description": "Only allows authorized damage through.", "value": 35},
    {"id": "docker_container", "name": "Docker Container", "type": "armor", "rarity": "uncommon", "defense": 6, "wisdom_bonus": 2, "description": "Isolates you from the hostile environment.", "value": 40},
    {"id": "kubernetes_armor", "name": "K8s Armor", "type": "armor", "rarity": "rare", "defense": 10, "description": "Self-healing armor. Restores 2 HP per turn.", "heal_per_turn": 2, "value": 70},
    {"id": "monolith_plate", "name": "Monolith Plate", "type": "armor", "rarity": "legendary", "defense": 15, "description": "Massive, tightly coupled, impossible to break.", "value": 130},
]

ACCESSORIES: list[dict] = [
    {"id": "linter_ring", "name": "Linter Ring", "type": "accessory", "rarity": "common", "patience_bonus": 3, "description": "Constantly whispers style suggestions.", "value": 12},
    {"id": "ci_amulet", "name": "CI/CD Amulet", "type": "accessory", "rarity": "uncommon", "heal_per_turn": 1, "description": "Continuous integration of health points.", "value": 30},
    {"id": "ssh_key", "name": "SSH Key", "type": "accessory", "rarity": "uncommon", "speed_bonus": 3, "description": "Grants remote access to anywhere.", "value": 35},
    {"id": "env_file", "name": ".env File", "type": "accessory", "rarity": "rare", "all_bonus": 1, "description": "Contains secrets that boost everything.", "value": 55},
    {"id": "github_copilot", "name": "AI Pair Programmer", "type": "accessory", "rarity": "legendary", "attack_bonus": 5, "defense_bonus": 3, "description": "An AI that autocompletes your attacks.", "value": 100},
]

CONSUMABLES: list[dict] = [
    {"id": "coffee", "name": "Coffee Potion", "type": "consumable", "heal": 20, "description": "Hot, dark, and fixes everything temporarily.", "value": 8},
    {"id": "energy_drink", "name": "Energy Drink", "type": "consumable", "heal": 40, "description": "Pure liquid productivity. Side effects include jitters.", "value": 15},
    {"id": "pizza_slice", "name": "Pizza Slice", "type": "consumable", "heal": 30, "description": "The programmer's fuel. Still warm from the Sprint Review.", "value": 10},
    {"id": "code_review_scroll", "name": "Code Review Scroll", "type": "consumable", "attack_buff": 5, "turns": 3, "description": "Reveals weaknesses in any codebase... or enemy.", "value": 20},
    {"id": "git_stash", "name": "Git Stash", "type": "consumable", "save_hp": True, "description": "Saves your current state. Can restore later.", "value": 25},
    {"id": "sudo_potion", "name": "Sudo Potion", "type": "consumable", "full_heal": True, "description": "With great power comes great restoration.", "value": 50},
    {"id": "rollback_scroll", "name": "Rollback Scroll", "type": "consumable", "revive": True, "description": "Reverts to last known good state. One-time use.", "value": 60},
]

ALL_ITEMS = WEAPONS + ARMORS + ACCESSORIES + CONSUMABLES

ITEMS_BY_ID: dict[str, dict] = {item["id"]: item for item in ALL_ITEMS}

_ITEMS_BY_RARITY: dict[str, list[dict]] = {}
for _item in ALL_ITEMS:
    if "rarity" in _item:
        _ITEMS_BY_RARITY.setdefault(_item["rarity"], []).append(_item)


def get_item(item_id: str) -> dict | None:
    return ITEMS_BY_ID.get(item_id)


def items_by_rarity(rarity: str) -> list[dict]:
    return _ITEMS_BY_RARITY.get(rarity, [])
