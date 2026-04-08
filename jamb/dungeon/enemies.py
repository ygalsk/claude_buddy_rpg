"""Enemy definitions for the Code Dungeon."""

from __future__ import annotations

# Each enemy: id, name, hp, attack, defense, speed, xp_reward, gold_reward,
#              loot_table (list of (item_id, drop_chance)), description, art

ENEMIES: list[dict] = [
    # Floor 1 - The Legacy Codebase
    {
        "id": "null_pointer", "name": "Null Pointer",
        "hp": 25, "attack": 6, "defense": 2, "speed": 5,
        "xp": 8, "gold": 5, "floor_min": 1, "type": "debugging",
        "loot": [("coffee", 0.4), ("rubber_duck", 0.1)],
        "description": "Points to absolutely nothing. Still hurts.",
        "art": " [N U L L]\n   >:( \n  /|||\\",
    },
    {
        "id": "off_by_one", "name": "Off-by-One Error",
        "hp": 20, "attack": 8, "defense": 1, "speed": 7,
        "xp": 7, "gold": 4, "floor_min": 1, "type": "snark",
        "loot": [("coffee", 0.3), ("stack_trace", 0.08)],
        "description": "Always attacks one space to the left of where you'd expect.",
        "art": "  [i+1]\n  >.< \n  /|\\",
    },
    {
        "id": "memory_leak", "name": "Memory Leak",
        "hp": 35, "attack": 4, "defense": 3, "speed": 3,
        "xp": 10, "gold": 7, "floor_min": 1, "type": "patience",
        "loot": [("pizza_slice", 0.3), ("try_catch_cloak", 0.08)],
        "description": "Slowly grows larger. Takes up more and more space.",
        "art": "  {???}\n  o . o\n ~~~~~",
        "special": "grow",  # gains +1 attack each turn
    },

    # Floor 2 - Dependency Hell
    {
        "id": "race_condition", "name": "Race Condition",
        "hp": 30, "attack": 10, "defense": 2, "speed": 12,
        "xp": 14, "gold": 10, "floor_min": 2, "type": "chaos",
        "loot": [("energy_drink", 0.3), ("ssh_key", 0.08)],
        "description": "Sometimes attacks first. Sometimes second. Never predictable.",
        "art": "  >>><\n  ?!?!\n  /\\ /\\",
    },
    {
        "id": "infinite_loop", "name": "Infinite Loop",
        "hp": 45, "attack": 5, "defense": 5, "speed": 4,
        "xp": 12, "gold": 8, "floor_min": 2, "type": "patience",
        "loot": [("coffee", 0.3), ("linter_ring", 0.08)],
        "description": "while(true) { attack(); } — never stops.",
        "art": " while(1)\n  @_@\n  /O\\",
        "special": "double_attack",  # attacks twice
    },
    {
        "id": "dependency_hell", "name": "Dep Hell Demon",
        "hp": 40, "attack": 8, "defense": 6, "speed": 5,
        "xp": 16, "gold": 12, "floor_min": 2, "type": "wisdom",
        "loot": [("code_review_scroll", 0.25), ("docker_container", 0.08)],
        "description": "Requires 47 other demons to function. All outdated.",
        "art": " [v0.0.1]\n  >:{  \n npm i",
    },

    # Floor 3 - The Production Server
    {
        "id": "segfault", "name": "Segmentation Fault",
        "hp": 50, "attack": 14, "defense": 4, "speed": 8,
        "xp": 20, "gold": 15, "floor_min": 3, "type": "chaos",
        "loot": [("energy_drink", 0.3), ("firewall_vest", 0.1)],
        "description": "Core dumped. YOUR core.",
        "art": "SEGFAULT\n  X_X \n [core]",
    },
    {
        "id": "deadlock", "name": "Deadlock",
        "hp": 55, "attack": 7, "defense": 10, "speed": 2,
        "xp": 18, "gold": 14, "floor_min": 3, "type": "debugging",
        "loot": [("git_stash", 0.2), ("ci_amulet", 0.08)],
        "description": "Waiting for you. You're waiting for it. Nobody moves.",
        "art": " [LOCK]\n  -_- \n  |||",
        "special": "lock",  # locks player, skip turn sometimes
    },
    {
        "id": "stack_overflow", "name": "Stack Overflow",
        "hp": 60, "attack": 12, "defense": 5, "speed": 6,
        "xp": 22, "gold": 18, "floor_min": 3, "type": "snark",
        "loot": [("sudo_potion", 0.15), ("regex_sword", 0.08)],
        "description": "Recursion without a base case. Growing infinitely.",
        "art": "STACK\n OVER\n FLOW\n  !!!",
        "special": "grow",
    },
]

BOSSES: list[dict] = [
    {
        "id": "spaghetti_monster", "name": "The Spaghetti Monster",
        "hp": 80, "attack": 12, "defense": 6, "speed": 4,
        "xp": 40, "gold": 30, "floor_min": 1, "type": "wisdom",
        "loot": [("git_bisect", 0.5), ("regex_sword", 0.3)],
        "description": "A tangled mass of code paths that no one dares refactor.",
        "art": " ~~~~\n(O  O)\n \\||/\n ~~~~",
        "special": "tangle",  # reduces player attack
    },
    {
        "id": "the_monolith", "name": "The Monolith",
        "hp": 120, "attack": 10, "defense": 12, "speed": 2,
        "xp": 60, "gold": 50, "floor_min": 2, "type": "patience",
        "loot": [("lint_roller", 0.4), ("kubernetes_armor", 0.25)],
        "description": "10 million lines. One file. No tests. Deployed on Friday.",
        "art": " _____\n|     |\n| 10M |\n| LOC |\n|_____|",
        "special": "fortify",  # gains defense each turn
    },
    {
        "id": "legacy_system", "name": "The Legacy System",
        "hp": 160, "attack": 15, "defense": 8, "speed": 3,
        "xp": 80, "gold": 75, "floor_min": 3, "type": "wisdom",
        "loot": [("rewrite_hammer", 0.3), ("monolith_plate", 0.2), ("github_copilot", 0.15)],
        "description": "Written in 1997. No documentation. 'It works, don't touch it.'",
        "art": " _______\n|LEGACY |\n| v0.1  |\n|  1997 |\n|_______|",
        "special": "corrupt",  # random debuffs
    },
]


def enemies_for_floor(floor: int) -> list[dict]:
    """Return enemies that can appear on this floor."""
    return [e for e in ENEMIES if e["floor_min"] <= floor]


def boss_for_floor(floor: int) -> dict:
    """Return the boss for this floor number (1-indexed)."""
    idx = min(floor - 1, len(BOSSES) - 1)
    return BOSSES[idx]
